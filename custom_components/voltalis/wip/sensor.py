# from homeassistant.components.sensor import SensorEntity
# from homeassistant.helpers.entity import DeviceInfo

# from custom_components.voltalisconst import DOMAIN


# async def async_setup_platform(hass, config, add_entities, discovery_info=None):
#     coordinator = hass.data[DOMAIN]["coordinator"]
#     devices = coordinator.data
#     entities = [VoltalisConsumption(d, coordinator) for d in devices]
#     add_entities(entities)


# class VoltalisConsumption(SensorEntity):
#     """Class that handle voltalis consumption entity"""

#     def __init__(self, device, coordinator):
#         self._device = device
#         self._coordinator = coordinator
#         self._attr_name = f"{device.name} Consommation"
#         self._attr_unique_id = f"{device.id}_consumption"
#         self._attr_native_unit_of_measurement = "kWh"

#     @property
#     def native_value(self):
#         for d in self._coordinator.data:
#             if d.id == self._device.id:
#                 return d.consumption

#     @property
#     def device_info(self) -> DeviceInfo:
#         model = "Radiateur" if self._device.is_heater() else "Chauffe-eau"
#         return DeviceInfo(
#             identifiers={("voltalis", self._device.id)},
#             name=self._device.name,
#             manufacturer="Voltalis",
#             model=model,
#         )
