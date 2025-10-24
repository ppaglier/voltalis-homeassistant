"""Initializing the HACS integration package"""

import logging

from const import DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.debug("async_setup_entry entry_id='%s'", entry.entry_id)

    hass.data.setdefault(DOMAIN, {})

    return True
