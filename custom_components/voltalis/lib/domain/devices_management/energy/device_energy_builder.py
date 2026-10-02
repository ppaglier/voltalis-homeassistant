from typing import Self

from custom_components.voltalis.lib.domain.devices_management.energy.device_energy import DeviceEnergy, EnergyRecord
from custom_components.voltalis.lib.domain.shared.generic_builder import GenericBuilder


class DeviceEnergyBuilder(GenericBuilder[DeviceEnergy]):
    """Builder for DeviceEnergy model."""

    DEFAULT_VALUES = DeviceEnergy(
        daily_energy_records=[],
    )

    def build(self) -> DeviceEnergy:
        return DeviceEnergy(**self.props)

    def with_daily_energy_records(self, records: list[EnergyRecord]) -> Self:
        """Set the energy records of the device."""
        return self._set_value("daily_energy_records", records)
