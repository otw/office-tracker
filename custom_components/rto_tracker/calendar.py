import logging
from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
import homeassistant.util.dt as dt_util

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the RTO calendar from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RTOCalendar(data, entry.entry_id)])

class RTOCalendar(CalendarEntity):
    """Calendar entity for RTO Tracker."""

    def __init__(self, rto_data, entry_id):
        self._rto_data = rto_data
        self._entry_id = entry_id

    @property
    def name(self):
        return "RTO Tracker Calendar"
        
    @property
    def unique_id(self):
        return f"{self._entry_id}_calendar"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="RTO Tracker",
            manufacturer="Home Assistant Community",
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        for key, summary in [("office_days", "Office Day"), ("vacation_days", "Vacation Day"), ("holiday_days", "Holiday")]:
            if today in self._rto_data["data"].get(key, []):
                date_obj = datetime.strptime(today, "%Y-%m-%d").date()
                return CalendarEvent(
                    summary=summary,
                    start=date_obj,
                    end=date_obj + timedelta(days=1),
                    location="Office" if key == "office_days" else None
                )
        return None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events = []
        
        start_d = start_date.date()
        end_d = end_date.date()
        
        categories = {
            "office_days": "Office Day",
            "vacation_days": "Vacation Day",
            "holiday_days": "Holiday"
        }
        
        for key, summary in categories.items():
            for date_str in self._rto_data["data"].get(key, []):
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if start_d <= date_obj <= end_d:
                        events.append(
                            CalendarEvent(
                                summary=summary,
                                start=date_obj,
                                end=date_obj + timedelta(days=1),
                                location="Office" if key == "office_days" else None
                            )
                        )
                except ValueError:
                    pass
                    
        return events
