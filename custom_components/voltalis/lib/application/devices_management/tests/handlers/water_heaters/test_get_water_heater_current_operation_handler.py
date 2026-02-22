import pytest

from custom_components.voltalis.lib.application.devices_management.queries.get_water_heater_current_operation_query import (  # noqa: E501
    GetWaterHeaterCurrentOperationQuery,
)
from custom_components.voltalis.lib.application.devices_management.tests.device_management_fixture import (
    DeviceManagementFixture,
)
from custom_components.voltalis.lib.domain.devices_management.water_heaters.water_heater_current_operations_enum import (  # noqa: E501
    WaterHeaterCurrentOperationEnum,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum


@pytest.mark.unit
def test_get_water_heater_current_operation_off(
    fixture: DeviceManagementFixture,
) -> None:
    """Test water heater current operation returns OFF when device is off."""

    result = fixture.get_water_heater_current_operation_handler.handle(
        GetWaterHeaterCurrentOperationQuery(is_on=False, prog_type=ProgramTypeEnum.DEFAULT)
    )

    assert result == WaterHeaterCurrentOperationEnum.OFF


@pytest.mark.unit
def test_get_water_heater_current_operation_manual(
    fixture: DeviceManagementFixture,
) -> None:
    """Test water heater current operation returns ON in manual program."""

    result = fixture.get_water_heater_current_operation_handler.handle(
        GetWaterHeaterCurrentOperationQuery(is_on=True, prog_type=ProgramTypeEnum.MANUAL)
    )

    assert result == WaterHeaterCurrentOperationEnum.ON


@pytest.mark.unit
def test_get_water_heater_current_operation_auto(
    fixture: DeviceManagementFixture,
) -> None:
    """Test water heater current operation returns AUTO in default program."""

    result = fixture.get_water_heater_current_operation_handler.handle(
        GetWaterHeaterCurrentOperationQuery(is_on=True, prog_type=ProgramTypeEnum.DEFAULT)
    )

    assert result == WaterHeaterCurrentOperationEnum.AUTO


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
