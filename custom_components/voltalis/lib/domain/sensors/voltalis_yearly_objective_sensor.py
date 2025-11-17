"""Voltalis yearly objective sensor."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfEnergy

from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity


class VoltalisYearlyObjectiveSensor(VoltalisEntity, SensorEntity):
    """Representation of a Voltalis yearly objective sensor."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_icon = "mdi:target"
    _attr_translation_key = "yearly_objective"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        data = self.coordinator.data.get(self.device_id)
        if data is None or data.consumption_objective is None:
            return None
        return data.consumption_objective.yearly_objective_in_wh

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return additional state attributes."""
        data = self.coordinator.data.get(self.device_id)
        if data is None or data.consumption_objective is None:
            return {}

        return {
            "yearly_objective_currency": data.consumption_objective.yearly_objective_in_currency,
        }
