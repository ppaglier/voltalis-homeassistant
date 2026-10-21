from typing import Any

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from propcache.api import cached_property

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_base_entity import (
    VoltalisBaseEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.const import DOMAIN


class VoltalisSystemEntity(VoltalisBaseEntity):
    """Base class for Voltalis system entities."""

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        name: str,
        coordinator: BaseVoltalisCoordinator[dict[int, Any]],
    ) -> None:
        """Initialize the system entity."""
        super().__init__(entry, coordinator)

        self._name = name

        # Unique id for Home Assistant
        unique_id = f"{entry.runtime_data.site_id}"
        self._attr_unique_id = f"{unique_id}_{self._attr_translation_key}"

        self._attr_device_info: DeviceInfo = DeviceInfo(  # pyright: ignore[reportIncompatibleVariableOverride]
            identifiers={(DOMAIN, f"{unique_id}_system")},
            name="Voltalis",
            manufacturer="Voltalis",
            configuration_url="https://myvoltalis.com",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def unique_internal_name(self) -> str:
        """Return a unique internal name for the entity."""
        return f"system_{self._attr_unique_id}"

    @cached_property
    def has_entity_name(self) -> bool:
        return True

    @cached_property
    def device_info(self) -> DeviceInfo:
        return self._attr_device_info

    # ------------------------------------------------------------------
    # Availability handling
    # ------------------------------------------------------------------
    @cached_property
    def available(self) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Return if entity is available."""
        data = self.coordinator.data
        return data is not None and self.coordinator.last_update_success
