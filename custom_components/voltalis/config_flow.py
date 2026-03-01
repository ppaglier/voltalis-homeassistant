import asyncio
from typing import cast

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pydantic import SecretStr

from custom_components.voltalis.const import (
    CONF_CLIMATE_MAX_TEMP,
    CONF_CLIMATE_MIN_TEMP,
    CONF_DEFAULT_AWAY_TEMP,
    CONF_DEFAULT_COMFORT_TEMP,
    CONF_DEFAULT_ECO_TEMP,
    CONF_DEFAULT_TEMP,
    CONF_DEFAULT_WATER_HEATER_TEMP,
    CONF_LOG_LEVEL,
    DEFAULT_AWAY_TEMP,
    DEFAULT_CLIMATE_MAX_TEMP,
    DEFAULT_CLIMATE_MIN_TEMP,
    DEFAULT_COMFORT_TEMP,
    DEFAULT_ECO_TEMP,
    DEFAULT_LOG_LEVEL,
    DEFAULT_TEMP,
    DEFAULT_WATER_HEATER_TEMP,
    DOMAIN,
    VOLTALIS_API_BASE_URL,
    LogLevelEnum,
)
from custom_components.voltalis.lib.domain.shared.exceptions import VoltalisAuthenticationException
from custom_components.voltalis.lib.domain.shared.providers.http_client import HttpClientException
from custom_components.voltalis.lib.infrastructure.providers.voltalis_client_aiohttp import VoltalisClientAiohttp


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

    def __init__(
        self,
        *,
        client: VoltalisClientAiohttp | None = None,
    ) -> None:
        self.__client = client

    def __get_username_input(self, input: dict | None) -> str | None:
        """Extract username from config entry data."""
        if input is None:
            return None
        username = input.get("username")
        if isinstance(username, str):
            return username
        return None

    def __get_password_input(self, input: dict | None) -> SecretStr | None:
        """Extract password from config entry data."""
        if input is None:
            return None

        password = input.get("password")
        if isinstance(password, SecretStr):
            return password
        elif isinstance(password, str):
            return SecretStr(password)
        return None

    def __get_schema(self, username: str | None = None) -> vol.Schema:
        """Get the schema for the user input form."""

        return vol.Schema(
            {
                vol.Required("username", default=username or vol.UNDEFINED): str,
                vol.Required("password"): str,
            }
        )

    async def __get_client(self) -> VoltalisClientAiohttp:
        """Get or create the Voltalis client."""

        if self.__client is not None:
            return self.__client
        # Client can't be provided if the config flow is instantiated by Home Assistant so we create a new one here
        return VoltalisClientAiohttp(
            session=async_get_clientsession(self.hass),
            base_url=VOLTALIS_API_BASE_URL,
        )

    async def __validate_input(self, *, username: str | None, password: SecretStr | None) -> None:
        """Validate provided user input."""

        if not username or not password:
            raise self.ConfigFlowError("missing_fields")

        client = await self.__get_client()

        try:
            await client.get_access_token(
                username=username,
                password=password,
            )
        except VoltalisAuthenticationException as err:
            raise self.AuthError("invalid_auth") from err
        except (HttpClientException, RuntimeError, TimeoutError, asyncio.TimeoutError) as err:
            raise self.ConnectionError("cannot_connect") from err
        except Exception as err:
            raise self.ConfigFlowError("unknown") from err

    async def async_step_user(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        """Handle the initial step of the config flow."""
        errors: dict[str, str] = {}

        username = self.__get_username_input(user_input)
        password = self.__get_password_input(user_input)

        if user_input is not None:
            try:
                await self.__validate_input(username=username, password=password)
            except self.AuthError:
                errors["base"] = "invalid_auth"
            except self.ConnectionError:
                errors["base"] = "cannot_connect"
            except self.ConfigFlowError as err:
                errors["base"] = str(err)
            except Exception:
                errors["base"] = "unknown"

            if not errors:
                await self.async_set_unique_id(username)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=cast(str, username),
                    data={"username": username, "password": cast(SecretStr, password).get_secret_value()},
                )

        return self.async_show_form(step_id="user", data_schema=self.__get_schema(), errors=errors)

    async def async_step_reconfigure(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        """Handle reconfiguration of an existing entry."""
        errors: dict[str, str] = {}

        username = self.__get_username_input(user_input)
        password = self.__get_password_input(user_input)

        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        assert entry is not None

        if user_input is not None:
            try:
                await self.__validate_input(username=username, password=password)
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
                    title=entry.title,
                    data={"username": username, "password": cast(SecretStr, password).get_secret_value()},
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reconfigure_successful")

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.__get_schema(username=entry.data["username"]),
            errors=errors,
        )

    async def async_step_reauth(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:  # noqa: D401
        """Handle a reauthentication flow.

        Triggered automatically when the existing credentials become invalid.
        If successful, update the existing entry and abort with a success reason.
        """
        errors: dict[str, str] = {}

        username = self.__get_username_input(user_input)
        password = self.__get_password_input(user_input)

        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])  # type: ignore[index]
        assert entry is not None

        if user_input is not None:
            try:
                await self.__validate_input(username=username, password=password)
            except self.AuthError:
                errors["base"] = "invalid_auth"
            except self.ConnectionError:
                errors["base"] = "cannot_connect"
            except self.ConfigFlowError as err:
                errors["base"] = str(err)
            except Exception:
                errors["base"] = "unknown"

            if not errors:
                # Update existing entry with new credentials
                self.hass.config_entries.async_update_entry(
                    entry,
                    title=entry.title,
                    data={"username": username, "password": cast(SecretStr, password).get_secret_value()},
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth", data_schema=self.__get_schema(username=entry.data["username"]), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return VoltalisOptionsFlowHandler(config_entry)


class VoltalisOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for Voltalis."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title=f"{self.config_entry.title} config", data=user_input)

        data_schema = vol.Schema(
            {
                # Log level option
                vol.Optional(
                    CONF_LOG_LEVEL,
                    default=self._config_entry.options.get(CONF_LOG_LEVEL, DEFAULT_LOG_LEVEL),
                ): vol.In([option.value for option in LogLevelEnum]),
                # Climate control options
                vol.Optional(
                    CONF_CLIMATE_MIN_TEMP,
                    default=self._config_entry.options.get(CONF_CLIMATE_MIN_TEMP, DEFAULT_CLIMATE_MIN_TEMP),
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_CLIMATE_MAX_TEMP,
                    default=self._config_entry.options.get(CONF_CLIMATE_MAX_TEMP, DEFAULT_CLIMATE_MAX_TEMP),
                ): vol.Coerce(float),
                # Default temperature options
                vol.Optional(
                    CONF_DEFAULT_TEMP,
                    default=self._config_entry.options.get(CONF_DEFAULT_TEMP, DEFAULT_TEMP),
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_DEFAULT_AWAY_TEMP,
                    default=self._config_entry.options.get(CONF_DEFAULT_AWAY_TEMP, DEFAULT_AWAY_TEMP),
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_DEFAULT_ECO_TEMP,
                    default=self._config_entry.options.get(CONF_DEFAULT_ECO_TEMP, DEFAULT_ECO_TEMP),
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_DEFAULT_COMFORT_TEMP,
                    default=self._config_entry.options.get(CONF_DEFAULT_COMFORT_TEMP, DEFAULT_COMFORT_TEMP),
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_DEFAULT_WATER_HEATER_TEMP,
                    default=self._config_entry.options.get(CONF_DEFAULT_WATER_HEATER_TEMP, DEFAULT_WATER_HEATER_TEMP),
                ): vol.Coerce(float),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
