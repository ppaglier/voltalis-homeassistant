from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator
from custom_components.voltalis.lib.domain.device import (
    VoltalisDevice,
    VoltalisDeviceModulatorTypeEnum,
    VoltalisDeviceTypeEnum,
)


class VoltalisEntity(CoordinatorEntity[VoltalisCoordinator]):
    """Base class for Voltalis entities."""

    _unique_id_suffix: str = ""

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        device: VoltalisDevice,
    ) -> None:
        """Initialize the device."""
        super().__init__(entry.runtime_data.coordinator)
        self._entry = entry

        if len(self._unique_id_suffix) == 0:
            raise ValueError("Unique ID suffix must be defined in subclass.")

        self._device = device

        unique_id = str(device.id)
        device_name = self.__get_device_name()

        # Unique id for Home Assistant
        self._attr_unique_id = f"{unique_id}_{self._unique_id_suffix}"

        self._attr_device_info: DeviceInfo = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=device_name,
            manufacturer="Voltalis",
            model=self.__get_device_model(),
        )

    @property
    def has_entity_name(self) -> bool:
        return True

    @property
    def device_info(self) -> DeviceInfo:
        return self._attr_device_info

    def __get_device_name(self) -> str:
        return self._device.name.capitalize()

    def __get_device_model(self) -> str:
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

        return f"{model}.{model_type}"

    # ------------------------------------------------------------------
    # Availability handling
    # ------------------------------------------------------------------
    @property
    def available(self) -> bool:
        """Return True if entity is available.

        We consider an entity available only if:
        - The last coordinator update succeeded AND
        - Device data exists for this entity AND
        - Subclass-specific data (consumption/status) is present.
        """
        data = self.coordinator.data.get(self._device.id)
        return self.coordinator.last_update_success and self._is_available_from_data(data)

    def _is_available_from_data(self, data: object) -> bool:
        """Base availability check, overridden by subclasses."""
        return data is not None
