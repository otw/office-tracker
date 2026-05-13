import logging
from datetime import datetime
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.storage import Store
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.const import CONF_ENTITY_ID

DOMAIN = "rto_tracker"
_LOGGER = logging.getLogger(__name__)

CONF_OFFICE_ZONES = "office_zones"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_ENTITY_ID): cv.entity_id,
                vol.Required(CONF_OFFICE_ZONES): vol.All(cv.ensure_list, [cv.entity_id]),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.storage"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the RTO Tracker component."""
    conf = config.get(DOMAIN)
    if conf is None:
        _LOGGER.warning("RTO Tracker configuration not found in configuration.yaml")
        return True

    entity_id = conf[CONF_ENTITY_ID]
    office_zones = conf[CONF_OFFICE_ZONES]

    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    
    # Load existing data
    data = await store.async_load()
    if data is None:
        data = {"office_days": [], "vacation_days": []}
        
    # Ensure lists exist in case of migration or corruption
    if "office_days" not in data:
        data["office_days"] = []
    if "vacation_days" not in data:
        data["vacation_days"] = []

    hass.data[DOMAIN] = {
        "store": store,
        "data": data,
        "entity_id": entity_id,
        "office_zones": office_zones,
        "listeners": []
    }

    async def async_save_data():
        """Save data to storage."""
        await store.async_save(hass.data[DOMAIN]["data"])
        # Notify listeners (sensors) to update
        for listener in hass.data[DOMAIN]["listeners"]:
            listener()

    @callback
    def async_add_date(date_str, date_type):
        """Add a date to the tracker."""
        if date_str not in hass.data[DOMAIN]["data"][date_type]:
            hass.data[DOMAIN]["data"][date_type].append(date_str)
            hass.async_create_task(async_save_data())
            _LOGGER.info(f"Added {date_str} to {date_type}")

    @callback
    def async_remove_date(date_str, date_type):
        """Remove a date from the tracker."""
        if date_str in hass.data[DOMAIN]["data"][date_type]:
            hass.data[DOMAIN]["data"][date_type].remove(date_str)
            hass.async_create_task(async_save_data())
            _LOGGER.info(f"Removed {date_str} from {date_type}")

    @callback
    def async_location_changed(event):
        """Handle location changes."""
        new_state = event.data.get("new_state")
        if not new_state:
            return

        current_state_str = new_state.state

        # Check if the current state matches any of the office zones' friendly names
        is_in_office = False
        for zone_id in office_zones:
            zone_state = hass.states.get(zone_id)
            # If state equals zone's friendly name (e.g. 'Office') or just the zone ID in some cases
            if zone_state and zone_state.attributes.get("friendly_name") == current_state_str:
                is_in_office = True
                break
            # Fallback if zone entity friendly name is not available but state is the zone object id
            elif current_state_str.lower() == zone_id.split('.')[1].replace('_', ' ').lower():
                is_in_office = True
                break
        
        if is_in_office:
            today_str = datetime.now().strftime("%Y-%m-%d")
            async_add_date(today_str, "office_days")

    async_track_state_change_event(hass, [entity_id], async_location_changed)

    # Register services
    async def handle_add_vacation(call: ServiceCall):
        date_str = call.data.get("date", datetime.now().strftime("%Y-%m-%d"))
        async_add_date(date_str, "vacation_days")

    async def handle_remove_vacation(call: ServiceCall):
        date_str = call.data.get("date", datetime.now().strftime("%Y-%m-%d"))
        async_remove_date(date_str, "vacation_days")
        
    async def handle_add_office(call: ServiceCall):
        date_str = call.data.get("date", datetime.now().strftime("%Y-%m-%d"))
        async_add_date(date_str, "office_days")

    async def handle_remove_office(call: ServiceCall):
        date_str = call.data.get("date", datetime.now().strftime("%Y-%m-%d"))
        async_remove_date(date_str, "office_days")

    hass.services.async_register(DOMAIN, "add_vacation_day", handle_add_vacation)
    hass.services.async_register(DOMAIN, "remove_vacation_day", handle_remove_vacation)
    hass.services.async_register(DOMAIN, "add_office_day", handle_add_office)
    hass.services.async_register(DOMAIN, "remove_office_day", handle_remove_office)

    # Forward setup to sensor platform
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform("sensor", DOMAIN, {}, config)
    )

    return True
