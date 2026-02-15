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
from custom_components.voltalis.lib.domain.devices_management.devices.device import DeviceProgramming
from custom_components.voltalis.lib.domain.devices_management.devices.device_builder import DeviceBuilder
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.water_heaters.water_heater_current_operations_enum import (  # noqa: E501
    WaterHeaterCurrentOperationEnum,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum


@pytest.mark.unit
async def test_set_water_heater_operation_on(
    fixture: DeviceManagementFixture,
) -> None:
    """Test water heater ON operation sets manual mode."""

    # Given
    device = (
        DeviceBuilder()
        .with_id(1)
        .with_programming(
            DeviceProgramming(
                prog_type=ProgramTypeEnum.DEFAULT,
                mode=DeviceModeEnum.OFF,
                temperature_target=None,
                default_temperature=None,
            )
        )
        .build()
    )
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings({manual_setting.id: manual_setting})

    # When
    await fixture.set_water_heater_operation_handler.handle(
        SetWaterHeaterOperationCommand(
            device=DeviceDto(**device.model_dump(), manual_setting=manual_setting),
            operation_mode=WaterHeaterCurrentOperationEnum.ON,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_enabled(True)
        .with_until_further_notice(True)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.NORMAL)
        .with_end_date(None)
        .with_temperature_target(fixture.default_water_heater_temp)
        .build()
    )
    await fixture.then_manual_settings_should_be({expected.id: expected})


@pytest.mark.unit
async def test_set_water_heater_operation_off(
    fixture: DeviceManagementFixture,
) -> None:
    """Test water heater OFF operation updates manual setting."""

    # Given
    device = (
        DeviceBuilder()
        .with_id(1)
        .with_programming(
            DeviceProgramming(
                prog_type=ProgramTypeEnum.DEFAULT,
                mode=DeviceModeEnum.OFF,
                temperature_target=None,
                default_temperature=None,
            )
        )
        .build()
    )
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings({manual_setting.id: manual_setting})

    # When
    await fixture.set_water_heater_operation_handler.handle(
        SetWaterHeaterOperationCommand(
            device=DeviceDto(**device.model_dump(), manual_setting=manual_setting),
            operation_mode=WaterHeaterCurrentOperationEnum.OFF,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_enabled(True)
        .with_until_further_notice(True)
        .with_is_on(False)
        .with_mode(DeviceModeEnum.NORMAL)
        .with_end_date(None)
        .with_temperature_target(fixture.default_water_heater_temp)
        .build()
    )
    await fixture.then_manual_settings_should_be({expected.id: expected})


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()


@pytest.mark.unit
async def test_set_water_heater_operation_auto(
    fixture: DeviceManagementFixture,
) -> None:
    """Test water heater AUTO operation disables manual mode."""

    # Given
    now = datetime(2024, 1, 4, 7, 0, 0)
    fixture.given_now(now)
    device = (
        DeviceBuilder()
        .with_id(1)
        .with_programming(
            DeviceProgramming(
                prog_type=ProgramTypeEnum.DEFAULT,
                mode=DeviceModeEnum.ECO,
                temperature_target=53.0,
                default_temperature=None,
            )
        )
        .build()
    )
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings({manual_setting.id: manual_setting})

    # When
    await fixture.set_water_heater_operation_handler.handle(
        SetWaterHeaterOperationCommand(
            device=DeviceDto(**device.model_dump(), manual_setting=manual_setting),
            operation_mode=WaterHeaterCurrentOperationEnum.AUTO,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_until_further_notice(False)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.ECO)
        .with_end_date(now)
        .with_temperature_target(53.0)
        .build()
    )
    await fixture.then_manual_settings_should_be({expected.id: expected})
