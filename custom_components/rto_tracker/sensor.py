import logging
from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass: HomeAssistant, config, async_add_entities, discovery_info=None):
    """Set up the RTO sensors."""
    if discovery_info is None:
        return

    data = hass.data[DOMAIN]
    async_add_entities([
        RTO12WeekSensor(data),
        RTOQuarterSensor(data)
    ])

class RTOBaseSensor(SensorEntity):
    """Base sensor for RTO Tracker."""
    def __init__(self, rto_data):
        self._rto_data = rto_data
        self._state = 0
        self._attr_native_value = 0

    async def async_added_to_hass(self):
        """Register callbacks when entity is added."""
        # Listen for data changes from the tracker
        self._rto_data["listeners"].append(self._update_and_write_state)
        
        # Also recalculate every day at midnight since rolling windows change based on current day
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
        """Combine office days and vacation days, return set of unique dates."""
        office = set(self._rto_data["data"].get("office_days", []))
        vacation = set(self._rto_data["data"].get("vacation_days", []))
        return office.union(vacation)

class RTO12WeekSensor(RTOBaseSensor):
    """Sensor for 12-week RTO count."""
    
    @property
    def name(self):
        return "RTO 12 Week Count"
        
    @property
    def unique_id(self):
        return "rto_tracker_12_week_count"
        
    @property
    def native_value(self):
        return self._state

    @property
    def icon(self):
        return "mdi:briefcase-check"

    @property
    def unit_of_measurement(self):
        return "days"

    def _update_state(self):
        today = datetime.now().date()
        # 12 weeks = 84 days. The window includes today and the previous 83 days.
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
        return "rto_tracker_quarter_count"
        
    @property
    def native_value(self):
        return self._state

    @property
    def icon(self):
        return "mdi:calendar-check"

    @property
    def unit_of_measurement(self):
        return "days"

    def _update_state(self):
        today = datetime.now().date()
        # Determine quarter start date (Jan 1, Apr 1, Jul 1, Oct 1)
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
