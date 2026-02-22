from datetime import datetime

import pytest
from homeassistant.components.climate.const import HVACAction

from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto
from custom_components.voltalis.lib.application.devices_management.queries.set_climate_action_command import (
    SetClimateActionCommand,
)
from custom_components.voltalis.lib.application.devices_management.tests.device_management_fixture import (
    DeviceManagementFixture,
)
from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting_builder import (
    ManualSettingBuilder,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device import DeviceProgramming
from custom_components.voltalis.lib.domain.devices_management.devices.device_builder import DeviceBuilder
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum


@pytest.mark.unit
async def test_set_climate_action_turns_off_device(
    fixture: DeviceManagementFixture,
) -> None:
    """Test set climate action OFF updates manual setting."""

    # Given
    device = (
        DeviceBuilder()
        .with_id(1)
        .with_programming(
            DeviceProgramming(
                prog_type=ProgramTypeEnum.DEFAULT,
                mode=DeviceModeEnum.COMFORT,
                temperature_target=21.0,
                default_temperature=17.0,
            )
        )
        .build()
    )
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings([manual_setting])

    # When
    await fixture.set_climate_action_handler.handle(
        SetClimateActionCommand(
            device=DeviceDto.from_device(device, manual_setting),
            action=HVACAction.OFF,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_enabled(True)
        .with_until_further_notice(True)
        .with_is_on(False)
        .with_mode(DeviceModeEnum.COMFORT)
        .with_end_date(None)
        .with_temperature_target(21.0)
        .build()
    )
    fixture.then_manual_settings_should_be({expected.id: expected})


@pytest.mark.unit
async def test_set_climate_action_turns_on_device(
    fixture: DeviceManagementFixture,
) -> None:
    """Test set climate action HEAT updates manual setting."""

    # Given
    device = (
        DeviceBuilder()
        .with_id(1)
        .with_programming(
            DeviceProgramming(
                prog_type=ProgramTypeEnum.DEFAULT,
                mode=DeviceModeEnum.ECO,
                temperature_target=20.0,
                default_temperature=17.0,
            )
        )
        .build()
    )
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings([manual_setting])

    # When
    await fixture.set_climate_action_handler.handle(
        SetClimateActionCommand(
            device=DeviceDto.from_device(device, manual_setting),
            action=HVACAction.HEATING,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_enabled(True)
        .with_until_further_notice(True)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.ECO)
        .with_end_date(None)
        .with_temperature_target(20.0)
        .build()
    )
    fixture.then_manual_settings_should_be({expected.id: expected})


@pytest.mark.unit
async def test_set_climate_action_auto_disables_manual_mode(
    fixture: DeviceManagementFixture,
) -> None:
    """Test set climate action AUTO disables manual mode."""

    # Given
    now = datetime(2024, 1, 1, 9, 0, 0)
    fixture.given_now(now)
    device = (
        DeviceBuilder()
        .with_id(1)
        .with_programming(
            DeviceProgramming(
                prog_type=ProgramTypeEnum.DEFAULT,
                mode=DeviceModeEnum.ECO,
                temperature_target=19.0,
                default_temperature=17.0,
            )
        )
        .build()
    )
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings([manual_setting])

    # When
    await fixture.set_climate_action_handler.handle(
        SetClimateActionCommand(
            device=DeviceDto.from_device(device, manual_setting),
            action=HVACAction.IDLE,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_until_further_notice(False)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.ECO)
        .with_end_date(now)
        .with_temperature_target(19.0)
        .build()
    )
    fixture.then_manual_settings_should_be({expected.id: expected})


@pytest.mark.unit
async def test_set_climate_action_without_manual_settings(
    fixture: DeviceManagementFixture,
) -> None:
    """Test setting water heater operation without manual settings raises error."""

    device = DeviceBuilder().with_id(1).build()

    with pytest.raises(ValueError, match="does not support manual settings") as exc_info:
        await fixture.set_climate_action_handler.handle(
            SetClimateActionCommand(
                device=DeviceDto.from_device(device, None),
                action=HVACAction.IDLE,
            )
        )

    assert str(exc_info.value) == f"Device {device.id} does not support manual settings"


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
