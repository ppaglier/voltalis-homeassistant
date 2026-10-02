"""Unit tests for DeviceEnergyBuilder."""

from datetime import datetime

import pytest

from custom_components.voltalis.lib.domain.devices_management.energy.device_energy import EnergyRecord
from custom_components.voltalis.lib.domain.devices_management.energy.device_energy_builder import DeviceEnergyBuilder


@pytest.mark.unit
def test_device_energy_builder_default_values() -> None:
    """Test that DeviceEnergyBuilder creates a energy with default values."""

    assert DeviceEnergyBuilder().build() == DeviceEnergyBuilder.DEFAULT_VALUES


@pytest.mark.unit
def test_device_energy_builder_creates_valid_energy() -> None:
    """Test that DeviceEnergyBuilder creates a valid device energy."""

    # Act
    energy = DeviceEnergyBuilder().with_daily_energy_records([]).build()

    # Assert
    assert energy.daily_energy_records == []


@pytest.mark.unit
def test_device_energy_builder_with_zero_energy() -> None:
    """Test DeviceEnergyBuilder with zero energy."""

    # Act
    energy = (
        DeviceEnergyBuilder()
        .with_daily_energy_records([EnergyRecord(timestamp=datetime(2026, 1, 1, 0, 0, 0), total=0.0)])
        .build()
    )

    # Assert
    assert energy.daily_energy_records == [EnergyRecord(timestamp=datetime(2026, 1, 1, 0, 0, 0), total=0.0)]
