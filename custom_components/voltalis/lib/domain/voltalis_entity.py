from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.domain.device import (
    VoltalisDevice,
    VoltalisDeviceModulatorTypeEnum,
    VoltalisDeviceTypeEnum,
)


class VoltalisEntity(CoordinatorEntity):
    """Base class for Voltalis entities."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: VoltalisDevice,
    ) -> None:
        """Initialize the device."""
        super().__init__(coordinator)

        self._device = device
        unique_id = str(device.id)

        # Unique id for Home Assistant
        self._attr_unique_id = unique_id
        self._attr_has_entity_name = True
        self._attr_device_info: DeviceInfo = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=self.__get_device_name(),
            manufacturer="Voltalis",
            model=self.__get_device_model_key(),  # key for translation
        )

    @property
    def device_info(self) -> DeviceInfo:
        return self._attr_device_info

    def __get_device_name(self) -> str:
        return self._device.name.capitalize()

    def __get_device_model_key(self) -> str:
        """Return the translation key for the device model."""

        model_keys = {
            VoltalisDeviceTypeEnum.WATER_HEATER: "water_heater",
            VoltalisDeviceTypeEnum.HEATER: "heater",
        }
        type_keys = {
            VoltalisDeviceModulatorTypeEnum.VX_WIRE: "wire",
            VoltalisDeviceModulatorTypeEnum.VX_RELAY: "relay",
        }

        model = model_keys.get(self._device.type, "unknown")
        model_type = type_keys.get(self._device.modulator_type, "unknown")

        return f"device_model.{model}.{model_type}"
