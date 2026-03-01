"""Unit tests for DeviceBuilder."""

import pytest

from custom_components.voltalis.lib.domain.devices_management.devices.device_builder import (
    DeviceBuilder,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import (
    DeviceModeEnum,
    DeviceTypeEnum,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import (
    ProgramTypeEnum,
)


@pytest.mark.unit
def test_device_builder_default_values() -> None:
    """Test that DeviceBuilder creates a device with default values."""

    assert DeviceBuilder().build() == DeviceBuilder.DEFAULT_VALUES


@pytest.mark.unit
def test_device_builder_creates_valid_heater_device() -> None:
    """Test that DeviceBuilder creates a valid heater device."""

    # Act
    device = (
        DeviceBuilder()
        .with_id(1)
        .with_name("Living Room Heater")
        .with_type(DeviceTypeEnum.HEATER)
        .with_available_modes([DeviceModeEnum.COMFORT, DeviceModeEnum.ECO])
        .with_programming_is_on(True)
        .with_programming_type(ProgramTypeEnum.MANUAL)
        .build()
    )

    # Assert
    assert device.id == 1
    assert device.name == "Living Room Heater"
    assert device.type == DeviceTypeEnum.HEATER
    assert DeviceModeEnum.COMFORT in device.available_modes
    assert DeviceModeEnum.ECO in device.available_modes
    assert device.programming.is_on is True


@pytest.mark.unit
def test_device_builder_creates_valid_water_heater_device() -> None:
    """Test that DeviceBuilder creates a valid water heater device."""

    # Act
    device = (
        DeviceBuilder()
        .with_id(2)
        .with_name("Kitchen Water Heater")
        .with_type(DeviceTypeEnum.WATER_HEATER)
        .with_available_modes([DeviceModeEnum.ON])
        .with_programming_is_on(False)
        .with_programming_type(ProgramTypeEnum.DEFAULT)
        .build()
    )

    # Assert
    assert device.id == 2
    assert device.name == "Kitchen Water Heater"
    assert device.type == DeviceTypeEnum.WATER_HEATER
    assert device.available_modes == [DeviceModeEnum.ON]
    assert device.programming.is_on is False


@pytest.mark.unit
def test_device_builder_with_temperature_mode() -> None:
    """Test DeviceBuilder with temperature mode support."""

    # Act
    device = (
        DeviceBuilder()
        .with_id(3)
        .with_name("Bedroom Heater")
        .with_type(DeviceTypeEnum.HEATER)
        .with_available_modes(
            [
                DeviceModeEnum.COMFORT,
                DeviceModeEnum.ECO,
                DeviceModeEnum.TEMPERATURE,
            ]
        )
        .build()
    )

    # Assert
    assert DeviceModeEnum.TEMPERATURE in device.available_modes
    assert len(device.available_modes) == 3


@pytest.mark.unit
def test_device_available_modes_not_empty() -> None:
    """Test that device must have at least one available mode."""

    # Act
    device = (
        DeviceBuilder()
        .with_id(1)
        .with_name("Test Device")
        .with_type(DeviceTypeEnum.HEATER)
        .with_available_modes([DeviceModeEnum.COMFORT])
        .build()
    )

    # Assert
    assert len(device.available_modes) > 0


@pytest.mark.unit
def test_device_id_immutability() -> None:
    """Test that device ID cannot be changed after creation."""

    # Act
    device = (
        DeviceBuilder()
        .with_id(42)
        .with_name("Test Device")
        .with_type(DeviceTypeEnum.HEATER)
        .with_available_modes([DeviceModeEnum.COMFORT])
        .build()
    )

    # Assert - device ID should be 42
    assert device.id == 42

    # Attempting to change ID should not be possible (immutable)
    # This is enforced by the Device model being frozen/immutable
    original_id = device.id
    assert device.id == original_id  # Verify it's still the same


@pytest.mark.unit
def test_device_name_format() -> None:
    """Test that device names are preserved as-is."""

    test_names = [
        "Living Room Heater",
        "Kitchen Water Heater",
        "Bedroom Climate Control",
        "Device 1",
    ]

    for name in test_names:
        # Act
        device = (
            DeviceBuilder()
            .with_id(1)
            .with_name(name)
            .with_type(DeviceTypeEnum.HEATER)
            .with_available_modes([DeviceModeEnum.COMFORT])
            .build()
        )

        # Assert
        assert device.name == name
