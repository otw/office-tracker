import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.const import CONF_ENTITY_ID

from . import DOMAIN, CONF_OFFICE_ZONES

class RTOTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for RTO Tracker."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_ENTITY_ID])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"RTO Tracker", 
                data=user_input
            )

        data_schema = vol.Schema({
            vol.Required(CONF_ENTITY_ID): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["person", "device_tracker"])
            ),
            vol.Required(CONF_OFFICE_ZONES): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="zone", multiple=True)
            ),
            vol.Optional("required_hours", default=0.0): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0.0, max=24.0, step=0.1, mode="box")
            ),
            vol.Required("target_days", default=2): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, max=7, step=1, mode="box")
            ),
            vol.Optional("holiday_calendar"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="calendar")
            )
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors
        )
