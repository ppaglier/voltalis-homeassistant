"""Unit tests for DeviceConsumptionBuilder."""

import pytest

from custom_components.voltalis.lib.domain.devices_management.consumptions.device_consumption_builder import (
    DeviceConsumptionBuilder,
)


@pytest.mark.unit
def test_device_consumption_builder_default_values() -> None:
    """Test that DeviceConsumptionBuilder creates a consumption with default values."""

    assert DeviceConsumptionBuilder().build() == DeviceConsumptionBuilder.DEFAULT_VALUES


@pytest.mark.unit
def test_device_consumption_builder_creates_valid_consumption() -> None:
    """Test that DeviceConsumptionBuilder creates a valid device consumption."""

    # Act
    consumption = DeviceConsumptionBuilder().with_daily_consumption(25.5).build()

    # Assert
    assert consumption.daily_consumption == 25.5


@pytest.mark.unit
def test_device_consumption_builder_with_zero_consumption() -> None:
    """Test DeviceConsumptionBuilder with zero consumption."""

    # Act
    consumption = DeviceConsumptionBuilder().with_daily_consumption(0.0).build()

    # Assert
    assert consumption.daily_consumption == 0.0


@pytest.mark.unit
def test_device_consumption_builder_with_large_consumption() -> None:
    """Test DeviceConsumptionBuilder with large consumption values."""

    # Act
    consumption = DeviceConsumptionBuilder().with_daily_consumption(999.99).build()

    # Assert
    assert consumption.daily_consumption == 999.99
