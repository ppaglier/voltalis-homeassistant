"""Initialization of the Voltalis integration in Home Assistant."""

from homeassistant.core import HomeAssistant

from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import (
    VoltalisConfigEntry,
)
from custom_components.voltalis.apps.home_assistant.home_assistant_module import VoltalisHomeAssistantModule
from custom_components.voltalis.const import CONFIG_SCHEMA

PLATFORMS = VoltalisHomeAssistantModule.PLATFORMS

__all__ = ["CONFIG_SCHEMA"]


async def async_setup(hass: HomeAssistant, entry: VoltalisConfigEntry) -> bool:
    """Set up the Voltalis component."""

    return True


async def async_setup_entry(hass: HomeAssistant, entry: VoltalisConfigEntry) -> bool:
    """Set up Voltalis from a config entry."""

    home_assistant_module = VoltalisHomeAssistantModule()
    setup_ok = await home_assistant_module.async_setup_entry(hass=hass, entry=entry)

    if setup_ok:
        entry.async_on_unload(entry.add_update_listener(_update_listener))

    return setup_ok


async def async_unload_entry(hass: HomeAssistant, entry: VoltalisConfigEntry) -> bool:
    """Unload a config entry."""

    return await entry.runtime_data.voltalis_home_assistant_module.async_unload_entry()


async def _update_listener(hass: HomeAssistant, entry: VoltalisConfigEntry) -> None:
    """Handle options updates by reloading the config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
