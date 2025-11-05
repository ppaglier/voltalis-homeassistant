""""""

import logging
from typing import Any

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Async setup for home assistant"""
    print("-----async_setup-------")
    print(hass)
    print("------------")
    print(config)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: Any) -> bool:
    """Setup via Config Flow UI."""

    print("-----async_setup_entry-------")
    print(hass)
    print("------------")
    print(entry)
    # username = entry.data[CONF_USERNAME]
    # password = entry.data[CONF_PASSWORD]

    # gateway = HttpVoltalisGateway(username, password)
    # service = DeviceService(gateway)

    # await _setup_hass(hass, service)
    return True


# async def _setup_hass(hass: HomeAssistant, service: DeviceService):
#     async def update_data():
#         return await service.get_all_devices()

#     coordinator = DataUpdateCoordinator(
#         hass,
#         _LOGGER,
#         name="Voltalis Coordinator",
#         update_method=update_data,
#         update_interval=timedelta(seconds=30),
#     )

#     await coordinator.async_config_entry_first_refresh()

#     hass.data[DOMAIN] = {"service": service, "coordinator": coordinator}

#     hass.helpers.discovery.load_platform("climate", DOMAIN, {}, {})
#     hass.helpers.discovery.load_platform("sensor", DOMAIN, {}, {})
#     hass.helpers.discovery.load_platform("water_heater", DOMAIN, {}, {})
