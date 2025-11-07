from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.exceptions import HomeAssistantError

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.application.voltalis_client import VoltalisClient
from custom_components.voltalis.lib.domain.exceptions import VoltalisAuthenticationException, VoltalisException
from custom_components.voltalis.lib.infrastructure.voltalis_client_aiohttp import VoltalisClientAiohttp


class VoltalisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Voltalis."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    class ConfigFlowError(HomeAssistantError):
        """Base error for Voltalis config flow."""

    class AuthError(ConfigFlowError):
        """Raised when authentication fails."""

    class ConnectionError(ConfigFlowError):
        """Raised when unable to connect to the Voltalis API."""

    def __init__(self, client_class: type[VoltalisClient] = VoltalisClientAiohttp) -> None:
        self.__client_class = client_class

    async def _validate_input(self, user_input: dict[str, Any]) -> None:
        """Validate provided user input."""
        if not isinstance(user_input, dict):
            raise self.ConfigFlowError("invalid_input")

        username: str | None = user_input.get("username")
        password: str | None = user_input.get("password")

        if not username or not password:
            raise self.ConfigFlowError("missing_fields")

        try:
            async with self.__client_class() as client:
                await client.get_access_token(
                    username=username,
                    password=password,
                )
        except VoltalisAuthenticationException as err:
            raise self.AuthError("invalid_auth") from err
        except VoltalisException as err:
            raise self.ConnectionError("cannot_connect") from err
        except Exception as err:
            raise self.ConfigFlowError("unknown") from err

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        """Handle the initial step of the config flow."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await self._validate_input(user_input)
            except self.AuthError:
                errors["base"] = "invalid_auth"
            except self.ConnectionError:
                errors["base"] = "cannot_connect"
            except self.ConfigFlowError as err:
                errors["base"] = str(err)
            except Exception:
                errors["base"] = "unknown"

            if not errors:
                await self.async_set_unique_id(user_input["username"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=user_input["username"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        """Handle reconfiguration of an existing entry."""
        errors: dict[str, str] = {}

        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        assert entry is not None

        if user_input is not None:
            try:
                await self._validate_input(user_input)
            except self.AuthError:
                errors["base"] = "invalid_auth"
            except self.ConnectionError:
                errors["base"] = "cannot_connect"
            except self.ConfigFlowError as err:
                errors["base"] = str(err)
            except Exception:
                errors["base"] = "unknown"

            if not errors:
                self.hass.config_entries.async_update_entry(
                    entry,
                    title=user_input["username"],
                    data=user_input,
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reconfigure_successful")

        data_schema = vol.Schema(
            {
                vol.Required("username", default=entry.data.get("username", "")): str,
                vol.Required("password"): str,
            }
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=data_schema,
            errors=errors,
        )
