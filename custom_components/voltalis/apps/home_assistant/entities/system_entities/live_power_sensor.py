from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfPower
from homeassistant.core import callback
from propcache.api import cached_property

from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_system_entity import (
    VoltalisSystemEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry


class VoltalisSystemLivePowerSensor(VoltalisSystemEntity, SensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """Sensor entity to represent near real-time consumption for a Voltalis system."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_translation_key = "system_live_power"

    def __init__(self, entry: VoltalisConfigEntry) -> None:
        """Initialize the sensor entity."""
        super().__init__(
            entry, "energy_contract", entry.runtime_data.voltalis_home_assistant_module.live_power_coordinator
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        data = self._voltalis_module.live_power_coordinator.data.get(0, None)
        if data is None:
            self._voltalis_module.logger.warning("Live consumption data is None")
            return

        new_value = data.power
        if self.native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    @cached_property
    def available(self) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Return if the entity is available."""
        data = self.coordinator.data.get(0)
        if data is None:
            return False
        return self.coordinator.last_update_success and self._is_available_from_data(data)

    def _is_available_from_data(self, data: float) -> bool:
        return True
