import pytest
from homeassistant.components.climate.const import HVACMode

from custom_components.voltalis.lib.application.devices_management.queries.get_climate_mode_query import (
    GetClimateModeQuery,
)
from custom_components.voltalis.lib.application.devices_management.tests.device_management_fixture import (
    DeviceManagementFixture,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum


@pytest.mark.unit
def test_get_climate_mode_off_when_device_off(
    fixture: DeviceManagementFixture,
) -> None:
    """Test climate mode handler returns OFF when device is off."""

    result = fixture.get_climate_mode_handler.handle(
        GetClimateModeQuery(is_on=False, prog_type=ProgramTypeEnum.DEFAULT)
    )

    assert result == HVACMode.OFF


@pytest.mark.unit
def test_get_climate_mode_manual_and_auto(
    fixture: DeviceManagementFixture,
) -> None:
    """Test climate mode handler maps program types to modes."""

    manual = fixture.get_climate_mode_handler.handle(GetClimateModeQuery(is_on=True, prog_type=ProgramTypeEnum.MANUAL))
    auto = fixture.get_climate_mode_handler.handle(GetClimateModeQuery(is_on=True, prog_type=ProgramTypeEnum.DEFAULT))

    assert manual == HVACMode.HEAT
    assert auto == HVACMode.AUTO


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
