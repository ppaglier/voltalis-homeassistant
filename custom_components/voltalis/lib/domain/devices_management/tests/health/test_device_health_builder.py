"""Unit tests for DeviceHealthBuilder."""

import pytest

from custom_components.voltalis.lib.domain.devices_management.health.device_health import DeviceHealthStatusEnum
from custom_components.voltalis.lib.domain.devices_management.health.device_health_builder import DeviceHealthBuilder


@pytest.mark.unit
def test_device_health_builder_default_values() -> None:
    """Test that DeviceHealthBuilder creates a health with default values."""

    assert DeviceHealthBuilder().build() == DeviceHealthBuilder.DEFAULT_VALUES


@pytest.mark.unit
def test_device_health_builder_creates_valid_health() -> None:
    """Test that DeviceHealthBuilder creates a valid device health."""

    # Act
    health = DeviceHealthBuilder().with_device_id(5).with_status(DeviceHealthStatusEnum.OK).build()

    # Assert
    assert health.device_id == 5
    assert health.status == DeviceHealthStatusEnum.OK


@pytest.mark.unit
def test_device_health_builder_with_different_statuses() -> None:
    """Test DeviceHealthBuilder with different health statuses."""

    # Test with NOT_OK status
    health = DeviceHealthBuilder().with_device_id(10).with_status(DeviceHealthStatusEnum.NOT_OK).build()

    assert health.status == DeviceHealthStatusEnum.NOT_OK

    # Test with COMM_ERROR status
    health = DeviceHealthBuilder().with_device_id(11).with_status(DeviceHealthStatusEnum.COMM_ERROR).build()

    assert health.status == DeviceHealthStatusEnum.COMM_ERROR
