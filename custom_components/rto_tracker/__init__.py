import logging
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.storage import Store
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
from homeassistant.const import CONF_ENTITY_ID, Platform

DOMAIN = "rto_tracker"
_LOGGER = logging.getLogger(__name__)

CONF_OFFICE_ZONES = "office_zones"
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.CALENDAR]

STORAGE_VERSION = 1

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up RTO Tracker from a config entry."""
    
    entity_id = entry.data[CONF_ENTITY_ID]
    office_zones = entry.data[CONF_OFFICE_ZONES]
    required_hours = entry.data.get("required_hours", 0.0)
    target_days = entry.data.get("target_days", 2)
    holiday_calendar = entry.data.get("holiday_calendar")
    
    # Use entity_id for storage key so data persists across reinstalls
    storage_key = f"{DOMAIN}_{entity_id}.storage"
    store = Store(hass, STORAGE_VERSION, storage_key)
    
    # Load existing data
    data = await store.async_load()
    if data is None:
        data = {"office_days": [], "vacation_days": [], "holiday_days": []}
        
    for key in ["office_days", "vacation_days", "holiday_days"]:
        if key not in data:
            data[key] = []

    # New tracker state for cumulative time
    tracker_state = {
        "current_day": datetime.now().strftime("%Y-%m-%d"),
        "daily_seconds": 0.0,
        "last_entry_ts": None,
        "is_currently_in_office": False
    }

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "store": store,
        "data": data,
        "tracker_state": tracker_state,
        "entity_id": entity_id,
        "office_zones": office_zones,
        "required_hours": required_hours,
        "target_days": target_days,
        "holiday_calendar": holiday_calendar,
        "listeners": []
    }

    async def async_save_data():
        """Save data to storage."""
        await store.async_save(hass.data[DOMAIN][entry.entry_id]["data"])
        # Notify listeners (sensors) to update
        for listener in hass.data[DOMAIN][entry.entry_id]["listeners"]:
            listener()

    @callback
    def async_add_date(date_str, date_type):
        if date_str not in hass.data[DOMAIN][entry.entry_id]["data"][date_type]:
            hass.data[DOMAIN][entry.entry_id]["data"][date_type].append(date_str)
            hass.async_create_task(async_save_data())

    @callback
    def async_remove_date(date_str, date_type):
        if date_str in hass.data[DOMAIN][entry.entry_id]["data"][date_type]:
            hass.data[DOMAIN][entry.entry_id]["data"][date_type].remove(date_str)
            hass.async_create_task(async_save_data())

    @callback
    def check_office_time(*args):
        """Called periodically and on location changes to tally time."""
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        now_ts = now.timestamp()
        
        t_state = hass.data[DOMAIN][entry.entry_id]["tracker_state"]
        
        # Handle day rollover
        if t_state["current_day"] != today_str:
            t_state["current_day"] = today_str
            t_state["daily_seconds"] = 0.0
            # If they are still in office, reset entry to midnight of new day
            if t_state["is_currently_in_office"]:
                t_state["last_entry_ts"] = now_ts

        # If they are in the office, tally elapsed time
        if t_state["is_currently_in_office"] and t_state["last_entry_ts"] is not None:
            duration = now_ts - t_state["last_entry_ts"]
            t_state["daily_seconds"] += duration
            t_state["last_entry_ts"] = now_ts # reset anchor to now
            
        # Notify listeners so Live Sensor updates
        for listener in hass.data[DOMAIN][entry.entry_id]["listeners"]:
            listener()
            
        # Check if threshold met
        if t_state["daily_seconds"] >= required_hours * 3600:
            async_add_date(today_str, "office_days")

        # Holiday check
        if holiday_calendar:
            cal_state = hass.states.get(holiday_calendar)
            if cal_state and cal_state.state == "on":
                async_add_date(today_str, "holiday_days")

    @callback
    def async_location_changed(event):
        new_state = event.data.get("new_state")
        if not new_state:
            return

        current_state_str = new_state.state
        is_in_office = False
        
        for zone_id in office_zones:
            zone_state = hass.states.get(zone_id)
            if zone_state and zone_state.attributes.get("friendly_name") == current_state_str:
                is_in_office = True
                break
            elif current_state_str.lower() == zone_id.split('.')[1].replace('_', ' ').lower():
                is_in_office = True
                break
        
        t_state = hass.data[DOMAIN][entry.entry_id]["tracker_state"]
        
        if is_in_office and not t_state["is_currently_in_office"]:
            # Just entered office
            t_state["is_currently_in_office"] = True
            t_state["last_entry_ts"] = datetime.now().timestamp()
            # If threshold is 0, credit immediately
            check_office_time()
            
        elif not is_in_office and t_state["is_currently_in_office"]:
            # Just left office
            check_office_time()
            t_state["is_currently_in_office"] = False
            t_state["last_entry_ts"] = None
            for listener in hass.data[DOMAIN][entry.entry_id]["listeners"]:
                listener()

    entry.async_on_unload(
        async_track_state_change_event(hass, [entity_id], async_location_changed)
    )
    
    # Run a periodic check every 5 minutes to credit days and trigger live sensor updates
    entry.async_on_unload(
        async_track_time_interval(hass, check_office_time, timedelta(minutes=5))
    )

    # Register services
    if not hass.services.has_service(DOMAIN, "add_vacation_day"):
        async def handle_add_vacation(call: ServiceCall):
            date_str = call.data.get("date", datetime.now().strftime("%Y-%m-%d"))
            async_add_date(date_str, "vacation_days")

        async def handle_remove_vacation(call: ServiceCall):
            date_str = call.data.get("date", datetime.now().strftime("%Y-%m-%d"))
            async_remove_date(date_str, "vacation_days")
            
        async def handle_add_vacation_range(call: ServiceCall):
            start = datetime.strptime(call.data.get("start_date"), "%Y-%m-%d")
            end = datetime.strptime(call.data.get("end_date"), "%Y-%m-%d")
            delta = end - start
            for i in range(delta.days + 1):
                day = start + timedelta(days=i)
                async_add_date(day.strftime("%Y-%m-%d"), "vacation_days")
            
        async def handle_add_office(call: ServiceCall):
            date_str = call.data.get("date", datetime.now().strftime("%Y-%m-%d"))
            async_add_date(date_str, "office_days")

        async def handle_remove_office(call: ServiceCall):
            date_str = call.data.get("date", datetime.now().strftime("%Y-%m-%d"))
            async_remove_date(date_str, "office_days")

        async def handle_add_office_range(call: ServiceCall):
            start = datetime.strptime(call.data.get("start_date"), "%Y-%m-%d")
            end = datetime.strptime(call.data.get("end_date"), "%Y-%m-%d")
            delta = end - start
            for i in range(delta.days + 1):
                day = start + timedelta(days=i)
                # Skip weekends automatically for convenience
                if day.weekday() < 5:
                    async_add_date(day.strftime("%Y-%m-%d"), "office_days")

        hass.services.async_register(DOMAIN, "add_vacation_day", handle_add_vacation)
        hass.services.async_register(DOMAIN, "remove_vacation_day", handle_remove_vacation)
        hass.services.async_register(DOMAIN, "add_vacation_range", handle_add_vacation_range)
        hass.services.async_register(DOMAIN, "add_office_day", handle_add_office)
        hass.services.async_register(DOMAIN, "remove_office_day", handle_remove_office)
        hass.services.async_register(DOMAIN, "add_office_day_range", handle_add_office_range)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
