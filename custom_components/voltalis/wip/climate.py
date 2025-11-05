# import logging

# from homeassistant.components.climate import ClimateEntity
# from homeassistant.helpers.entity import DeviceInfo

# from custom_components.voltalisconst import (
#     DEFAULT_MAX_TEMP,
#     DEFAULT_MIN_TEMP,
#     DOMAIN,
#     HA_PRESET_MODES,
#     TEMP_UNITS,
#     VOLTALIS_PRESET_MODES,
# )

# _LOGGER = logging.getLogger(__name__)


# async def async_setup_platform(hass, config, add_entities, discovery_info=None):
#     """Setup des radiateurs Voltalis."""
#     coordinator = hass.data[DOMAIN]["coordinator"]
#     devices = coordinator.data
#     entities = [VoltalisHeater(d, coordinator) for d in devices if d.is_heater()]
#     add_entities(entities)


# class VoltalisHeater(ClimateEntity):
#     """Class that handle voltalis heater entity"""

#     _attr_temperature_unit = TEMP_UNITS["CELSIUS"]
#     _attr_preset_modes = list(VOLTALIS_PRESET_MODES.keys())
#     _attr_min_temp = DEFAULT_MIN_TEMP
#     _attr_max_temp = DEFAULT_MAX_TEMP
#     _attr_hvac_modes = ["off", "heat"]

#     def __init__(self, device, coordinator):
#         self._device = device
#         self._coordinator = coordinator
#         self._attr_name = device.name
#         self._attr_unique_id = f"{device.id}_climate"

#     @property
#     def current_temperature(self):
#         return self._device.temperature

#     @property
#     def preset_mode(self):
#         """Convert Voltalis mode -> HA preset"""
#         return HA_PRESET_MODES.get(self._device.mode, None)

#     async def async_set_preset_mode(self, preset_mode):
#         """Convert HA preset -> Voltalis mode et envoie la commande"""
#         voltalis_mode = VOLTALIS_PRESET_MODES.get(preset_mode)
#         if voltalis_mode:
#             service = self._coordinator.hass.data[DOMAIN]["service"]
#             await service.set_device_mode(self._device.id, voltalis_mode)
#             await self._coordinator.async_request_refresh()

#     @property
#     def device_info(self) -> DeviceInfo:
#         """Regroupe le climate et le capteur consommation sous le même device"""
#         return DeviceInfo(
#             identifiers={("voltalis", self._device.id)},
#             name=self._device.name,
#             manufacturer="Voltalis",
#             model="Radiateur",
#         )
