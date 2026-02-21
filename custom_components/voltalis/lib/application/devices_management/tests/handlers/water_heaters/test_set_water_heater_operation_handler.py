from datetime import datetime

import pytest

from custom_components.voltalis.lib.application.devices_management.commands.set_water_heater_operation_command import (
    SetWaterHeaterOperationCommand,
)
from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto
from custom_components.voltalis.lib.application.devices_management.tests.device_management_fixture import (
    DeviceManagementFixture,
)
from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting_builder import (
    ManualSettingBuilder,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_builder import DeviceBuilder
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.water_heaters.water_heater_current_operations_enum import (  # noqa: E501
    WaterHeaterCurrentOperationEnum,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum


@pytest.mark.unit
async def test_set_water_heater_operation_from_off_to_on(
    fixture: DeviceManagementFixture,
) -> None:
    """Test water heater ON operation sets manual mode."""

    # Given
    device = (
        DeviceBuilder()
        .with_id(1)
        .with_programming_is_on(False)
        .with_programming_type(ProgramTypeEnum.MANUAL)
        .with_programming_mode(DeviceModeEnum.ON)
        .with_programming_temperature_target(fixture.default_water_heater_temp)
        .build()
    )
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id).with_enabled(False)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings([manual_setting])

    # When
    await fixture.set_water_heater_operation_handler.handle(
        SetWaterHeaterOperationCommand(
            device=DeviceDto.from_device(device, manual_setting),
            operation_mode=WaterHeaterCurrentOperationEnum.ON,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_enabled(True)
        .with_until_further_notice(True)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.ON)
        .with_end_date(None)
        .with_temperature_target(fixture.default_water_heater_temp)
        .build()
    )
    fixture.then_manual_settings_should_be({expected.id: expected})


@pytest.mark.unit
async def test_set_water_heater_operation_from_auto_to_off(
    fixture: DeviceManagementFixture,
) -> None:
    """Test water heater OFF operation updates manual setting."""

    # Given
    device = (
        DeviceBuilder()
        .with_id(1)
        .with_programming_is_on(False)
        .with_programming_type(ProgramTypeEnum.MANUAL)
        .with_programming_mode(DeviceModeEnum.ON)
        .with_programming_temperature_target(fixture.default_water_heater_temp)
        .build()
    )
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings([manual_setting])

    # When
    await fixture.set_water_heater_operation_handler.handle(
        SetWaterHeaterOperationCommand(
            device=DeviceDto.from_device(device, manual_setting),
            operation_mode=WaterHeaterCurrentOperationEnum.OFF,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_enabled(True)
        .with_until_further_notice(True)
        .with_is_on(False)
        .with_mode(DeviceModeEnum.ON)
        .with_end_date(None)
        .with_temperature_target(fixture.default_water_heater_temp)
        .build()
    )
    fixture.then_manual_settings_should_be({expected.id: expected})


@pytest.mark.unit
async def test_set_water_heater_operation_from_on_to_auto(
    fixture: DeviceManagementFixture,
) -> None:
    """Test water heater AUTO operation disables manual mode."""

    # Given
    now = datetime(2024, 1, 4, 7, 0, 0)
    fixture.given_now(now)
    device = (
        DeviceBuilder()
        .with_id(1)
        .with_programming_is_on(True)
        .with_programming_type(ProgramTypeEnum.MANUAL)
        .with_programming_mode(DeviceModeEnum.ON)
        .with_programming_temperature_target(fixture.default_water_heater_temp)
        .build()
    )
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings([manual_setting])

    # When
    await fixture.set_water_heater_operation_handler.handle(
        SetWaterHeaterOperationCommand(
            device=DeviceDto.from_device(device, manual_setting),
            operation_mode=WaterHeaterCurrentOperationEnum.AUTO,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_until_further_notice(False)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.ON)
        .with_end_date(now)
        .with_temperature_target(fixture.default_water_heater_temp)
        .build()
    )
    fixture.then_manual_settings_should_be({expected.id: expected})


@pytest.mark.unit
async def test_set_water_heater_operation_from_off_to_auto(
    fixture: DeviceManagementFixture,
) -> None:
    """Test water heater AUTO operation disables manual mode."""

    # Given
    now = datetime(2024, 1, 4, 7, 0, 0)
    fixture.given_now(now)
    device = (
        DeviceBuilder()
        .with_id(1)
        .with_programming_is_on(False)
        .with_programming_type(ProgramTypeEnum.MANUAL)
        .with_programming_mode(DeviceModeEnum.ON)
        .with_programming_temperature_target(fixture.default_water_heater_temp)
        .build()
    )
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings([manual_setting])

    # When
    await fixture.set_water_heater_operation_handler.handle(
        SetWaterHeaterOperationCommand(
            device=DeviceDto.from_device(device, manual_setting),
            operation_mode=WaterHeaterCurrentOperationEnum.AUTO,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_until_further_notice(False)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.ON)
        .with_end_date(now)
        .with_temperature_target(fixture.default_water_heater_temp)
        .build()
    )
    fixture.then_manual_settings_should_be({expected.id: expected})


@pytest.mark.unit
async def test_set_water_heater_operation_without_manual_settings(
    fixture: DeviceManagementFixture,
) -> None:
    """Test setting water heater operation without manual settings raises error."""

    device = DeviceBuilder().with_id(1).build()

    with pytest.raises(ValueError, match="does not support manual settings") as exc_info:
        await fixture.set_water_heater_operation_handler.handle(
            SetWaterHeaterOperationCommand(
                device=DeviceDto.from_device(device, None),
                operation_mode=WaterHeaterCurrentOperationEnum.AUTO,
            )
        )

    assert str(exc_info.value) == f"Device {device.id} does not support manual settings"


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
