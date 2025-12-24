from typing import Any

from homeassistant.helpers.entity import DeviceInfo

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.coordinators.device import VoltalisDeviceCoordinatorData
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_base_entity import VoltalisBaseEntity
from custom_components.voltalis.lib.domain.models.device import VoltalisDeviceModulatorTypeEnum, VoltalisDeviceTypeEnum


class VoltalisDeviceEntity(VoltalisBaseEntity):
    """Base class for Voltalis device entities tied to a specific device."""

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        device: VoltalisDeviceCoordinatorData,
        coordinator: BaseVoltalisCoordinator[dict[int, Any]],
    ) -> None:
        """Initialize the device entity."""
        super().__init__(entry, coordinator)

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
    def unique_internal_name(self) -> str:
        """Return a unique internal name for the entity."""
        return f"{self._device.name.lower()}_{self._attr_unique_id}"

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
        if data is None:
            return False
        return self.coordinator.last_update_success and self._is_available_from_data(data)
