import voluptuous as vol
from homeassistant import config_entries

from custom_components.voltalis.const import CONF_PASSWORD, CONF_USERNAME, DOMAIN

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class VoltalisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow pour Voltalis."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        errors: dict = {}
        if user_input is not None:
            print(user_input)

            if not errors:
                return self.async_create_entry(title=user_input[CONF_USERNAME], data=user_input)

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)
