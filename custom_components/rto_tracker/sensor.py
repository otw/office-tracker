import logging
from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.entity import DeviceInfo

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the RTO sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        RTO12WeekSensor(data, entry.entry_id),
        RTOQuarterSensor(data, entry.entry_id),
        RTOTimeInOfficeTodaySensor(data, entry.entry_id)
    ])

class RTOBaseSensor(SensorEntity):
    """Base sensor for RTO Tracker."""
    def __init__(self, rto_data, entry_id):
        self._rto_data = rto_data
        self._entry_id = entry_id
        self._state = 0
        self._attr_native_value = 0

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="RTO Tracker",
            manufacturer="Home Assistant Community",
        )

    async def async_added_to_hass(self):
        """Register callbacks when entity is added."""
        self._rto_data["listeners"].append(self._update_and_write_state)
        
        # Also recalculate every day at midnight
        self.async_on_remove(
            async_track_time_change(
                self.hass, self._update_and_write_state, hour=0, minute=0, second=1
            )
        )
        self._update_state()

    @callback
    def _update_and_write_state(self, *args):
        """Update state and write to HA."""
        self._update_state()
        self.async_write_ha_state()

    def _get_all_credited_dates(self):
        """Combine office days, vacation days, and holidays."""
        office = set(self._rto_data["data"].get("office_days", []))
        vacation = set(self._rto_data["data"].get("vacation_days", []))
        holidays = set(self._rto_data["data"].get("holiday_days", []))
        return office.union(vacation).union(holidays)

class RTO12WeekSensor(RTOBaseSensor):
    """Sensor for 12-week RTO count."""
    
    @property
    def name(self):
        return "RTO 12 Week Count"
        
    @property
    def unique_id(self):
        return f"{self._entry_id}_12_week_count"
        
    @property
    def native_value(self):
        return self._state

    @property
    def icon(self):
        return "mdi:briefcase-check"

    @property
    def unit_of_measurement(self):
        return "days"

    @property
    def extra_state_attributes(self):
        # Target for 12 weeks is (target_days_per_week * 12)
        target = self._rto_data.get("target_days", 2) * 12
        return {"target": target}

    def _update_state(self):
        today = datetime.now().date()
        start_date = today - timedelta(days=83)
        
        credited_dates = self._get_all_credited_dates()
        count = 0
        for date_str in credited_dates:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                if start_date <= date_obj <= today:
                    count += 1
            except ValueError:
                pass
        self._state = count

class RTOQuarterSensor(RTOBaseSensor):
    """Sensor for Quarterly RTO count."""
    
    @property
    def name(self):
        return "RTO Quarter Count"
        
    @property
    def unique_id(self):
        return f"{self._entry_id}_quarter_count"
        
    @property
    def native_value(self):
        return self._state

    @property
    def icon(self):
        return "mdi:calendar-check"

    @property
    def unit_of_measurement(self):
        return "days"

    @property
    def extra_state_attributes(self):
        # Target for ~13 week quarter
        target = self._rto_data.get("target_days", 2) * 13
        return {"target": target}

    def _update_state(self):
        today = datetime.now().date()
        quarter_month = ((today.month - 1) // 3) * 3 + 1
        start_date = datetime(today.year, quarter_month, 1).date()
        
        credited_dates = self._get_all_credited_dates()
        count = 0
        for date_str in credited_dates:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                if start_date <= date_obj <= today:
                    count += 1
            except ValueError:
                pass
        self._state = count

class RTOTimeInOfficeTodaySensor(RTOBaseSensor):
    """Sensor for tracking live time in office today."""

    @property
    def name(self):
        return "RTO Time in Office Today"
        
    @property
    def unique_id(self):
        return f"{self._entry_id}_time_today"
        
    @property
    def native_value(self):
        return self._state

    @property
    def icon(self):
        return "mdi:timer-sand"

    @property
    def unit_of_measurement(self):
        return "h"

    @property
    def extra_state_attributes(self):
        t_state = self._rto_data["tracker_state"]
        return {
            "required_hours": self._rto_data.get("required_hours", 0.0),
            "is_in_office": t_state.get("is_currently_in_office", False)
        }

    def _update_state(self):
        t_state = self._rto_data["tracker_state"]
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        if t_state["current_day"] == today_str:
            # Add up daily seconds, plus any uncommitted time if they are currently in the office
            total_seconds = t_state["daily_seconds"]
            if t_state["is_currently_in_office"] and t_state["last_entry_ts"]:
                total_seconds += (datetime.now().timestamp() - t_state["last_entry_ts"])
            
            hours = total_seconds / 3600.0
            self._state = round(hours, 2)
        else:
            self._state = 0.0
