"""Unit tests for DeviceConsumptionBuilder."""

from datetime import datetime

import pytest

from custom_components.voltalis.lib.domain.devices_management.consumptions.device_consumption import ConsumptionRecord
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
    consumption = DeviceConsumptionBuilder().with_daily_consumption_records([]).build()

    # Assert
    assert consumption.daily_consumption_records == []


@pytest.mark.unit
def test_device_consumption_builder_with_zero_consumption() -> None:
    """Test DeviceConsumptionBuilder with zero consumption."""

    # Act
    consumption = (
        DeviceConsumptionBuilder()
        .with_daily_consumption_records(
            [ConsumptionRecord(timestamp=datetime(2026, 1, 1, 0, 0, 0), total_consumption_in_wh=0.0)]
        )
        .build()
    )

    # Assert
    assert consumption.daily_consumption_records == [
        ConsumptionRecord(timestamp=datetime(2026, 1, 1, 0, 0, 0), total_consumption_in_wh=0.0)
    ]
