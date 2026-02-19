import pytest

from custom_components.voltalis.lib.application.devices_management.handlers.devices.get_device_mode_handler import (
    DeviceCurrentModeEnum,
)
from custom_components.voltalis.lib.application.devices_management.queries.get_device_mode_query import (
    GetDeviceModeQuery,
)
from custom_components.voltalis.lib.application.devices_management.tests.device_management_fixture import (
    DeviceManagementFixture,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum


@pytest.mark.unit
def test_get_device_mode_returns_off_when_device_is_off(
    fixture: DeviceManagementFixture,
) -> None:
    """Test device mode handler returns OFF when device is off."""

    result = fixture.get_device_mode_handler.handle(GetDeviceModeQuery(is_on=False, mode=DeviceModeEnum.ECO))

    assert result == DeviceCurrentModeEnum.OFF


@pytest.mark.unit
def test_get_device_mode_maps_on(
    fixture: DeviceManagementFixture,
) -> None:
    """Test device mode handler maps modes to current modes."""

    result = fixture.get_device_mode_handler.handle(GetDeviceModeQuery(is_on=True, mode=DeviceModeEnum.ON))

    assert result == DeviceCurrentModeEnum.ON


@pytest.mark.unit
def test_get_device_mode_maps_comfort(
    fixture: DeviceManagementFixture,
) -> None:
    """Test device mode handler defaults to OFF for unrecognized modes."""

    result = fixture.get_device_mode_handler.handle(GetDeviceModeQuery(is_on=True, mode=DeviceModeEnum.COMFORT))

    assert result == DeviceCurrentModeEnum.COMFORT


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
