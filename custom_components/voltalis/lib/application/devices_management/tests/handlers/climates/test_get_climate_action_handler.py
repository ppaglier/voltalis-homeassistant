import pytest
from homeassistant.components.climate.const import HVACAction

from custom_components.voltalis.lib.application.devices_management.queries.get_climate_action_query import (
    GetClimateActionQuery,
)
from custom_components.voltalis.lib.application.devices_management.tests.device_management_fixture import (
    DeviceManagementFixture,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum


@pytest.mark.unit
def test_get_climate_action_off_when_device_off(
    fixture: DeviceManagementFixture,
) -> None:
    """Test climate action handler returns OFF when device is off."""

    result = fixture.get_climate_action_handler.handle(GetClimateActionQuery(is_on=False, mode=DeviceModeEnum.ECO))

    assert result == HVACAction.OFF


@pytest.mark.unit
def test_get_climate_action_maps_modes(
    fixture: DeviceManagementFixture,
) -> None:
    """Test climate action handler maps modes to actions."""

    idle = fixture.get_climate_action_handler.handle(GetClimateActionQuery(is_on=True, mode=DeviceModeEnum.HORS_GEL))
    heating = fixture.get_climate_action_handler.handle(GetClimateActionQuery(is_on=True, mode=DeviceModeEnum.ECO))

    assert idle == HVACAction.IDLE
    assert heating == HVACAction.HEATING


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
