from datetime import datetime

import pytest

from custom_components.voltalis.lib.application.devices_management.commands.disable_manual_mode_command import (
    DisableManualModeCommand,
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


@pytest.mark.unit
async def test_disable_manual_mode(fixture: DeviceManagementFixture) -> None:
    """Test the disable manual mode handler."""

    # Given
    now = datetime(2024, 1, 4, 7, 0, 0)
    fixture.given_now(now)
    device = DeviceBuilder().with_id(1).build()
    fixture.given_devices({device.id: device})
    manual_setting_builder = (
        ManualSettingBuilder()
        .with_id(1)
        .with_id_appliance(device.id)
        .with_until_further_notice(True)
        .with_is_on(False)
        .with_mode(DeviceModeEnum.ECO)
        .with_end_date(None)
        .with_temperature_target(0.0)
    )
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings([manual_setting])

    # When
    await fixture.disable_manual_mode_handler.handle(
        DisableManualModeCommand(
            device=DeviceDto(**device.model_dump(), manual_setting=manual_setting),
        )
    )

    # Then
    expected_manual_setting = (
        manual_setting_builder.with_until_further_notice(False).with_is_on(True).with_end_date(now).build()
    )
    fixture.then_devices_should_be({device.id: device})
    fixture.then_manual_settings_should_be({expected_manual_setting.id: expected_manual_setting})


@pytest.mark.unit
async def test_disable_manual_mode_with_no_manual_setting(fixture: DeviceManagementFixture) -> None:
    """Test the disable manual mode handler when there is no manual setting."""

    # Given
    device = DeviceBuilder().with_id(1).build()
    fixture.given_devices({device.id: device})
    fixture.given_manual_settings([])

    # When / Then
    with pytest.raises(ValueError, match="does not support manual settings") as exc_info:
        await fixture.disable_manual_mode_handler.handle(
            DisableManualModeCommand(
                device=DeviceDto(**device.model_dump(), manual_setting=None),
            )
        )

    assert str(exc_info.value) == f"Device {device.id} does not support manual settings"


@pytest.mark.unit
async def test_disable_manual_mode_with_already_disabled_manual_setting(fixture: DeviceManagementFixture) -> None:
    """Test the disable manual mode handler when the manual setting is already disabled."""

    # Given
    now = datetime(2024, 1, 4, 7, 0, 0)
    fixture.given_now(now)
    device = DeviceBuilder().with_id(1).build()
    fixture.given_devices({device.id: device})
    manual_setting_builder = (
        ManualSettingBuilder()
        .with_id(1)
        .with_id_appliance(device.id)
        .with_until_further_notice(False)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.ECO)
        .with_end_date(now)
        .with_temperature_target(0.0)
    )
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings([manual_setting])

    # When
    await fixture.disable_manual_mode_handler.handle(
        DisableManualModeCommand(
            device=DeviceDto(**device.model_dump(), manual_setting=manual_setting),
        )
    )

    # Then
    fixture.then_devices_should_be({device.id: device})
    fixture.then_manual_settings_should_be({manual_setting.id: manual_setting})


@pytest.mark.unit
async def test_disable_manual_mode_with_fallback_mode(fixture: DeviceManagementFixture) -> None:
    """Test the disable manual mode handler when the device is in fallback mode."""

    # Given
    now = datetime(2024, 1, 4, 7, 0, 0)
    fixture.given_now(now)
    device = DeviceBuilder().with_id(1).build()
    fixture.given_devices({device.id: device})
    manual_setting_builder = (
        ManualSettingBuilder()
        .with_id(1)
        .with_id_appliance(device.id)
        .with_until_further_notice(True)
        .with_is_on(False)
        .with_mode(DeviceModeEnum.ECO)
        .with_end_date(None)
        .with_temperature_target(0.0)
    )
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings([manual_setting])

    # When
    await fixture.disable_manual_mode_handler.handle(
        DisableManualModeCommand(
            device=DeviceDto(**device.model_dump(), manual_setting=manual_setting),
            fallback_mode=DeviceModeEnum.ECO,
        )
    )

    # Then
    expected_manual_setting = (
        manual_setting_builder.with_until_further_notice(False)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.ECO)
        .with_end_date(now)
        .build()
    )
    fixture.then_devices_should_be({device.id: device})
    fixture.then_manual_settings_should_be({expected_manual_setting.id: expected_manual_setting})


@pytest.mark.unit
async def test_disable_manual_mode_with_fallback_temperature(fixture: DeviceManagementFixture) -> None:
    """Test the disable manual mode handler when a fallback temperature is provided."""

    # Given
    now = datetime(2024, 1, 4, 7, 0, 0)
    fixture.given_now(now)
    device = DeviceBuilder().with_id(1).build()
    fixture.given_devices({device.id: device})
    manual_setting_builder = (
        ManualSettingBuilder()
        .with_id(1)
        .with_id_appliance(device.id)
        .with_until_further_notice(True)
        .with_is_on(False)
        .with_mode(DeviceModeEnum.ECO)
        .with_end_date(None)
        .with_temperature_target(0.0)
    )
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings([manual_setting])

    # When
    await fixture.disable_manual_mode_handler.handle(
        DisableManualModeCommand(
            device=DeviceDto(**device.model_dump(), manual_setting=manual_setting),
            fallback_temperature=22.0,
        )
    )

    # Then
    expected_manual_setting = (
        manual_setting_builder.with_until_further_notice(False)
        .with_is_on(True)
        .with_temperature_target(22.0)
        .with_end_date(now)
        .build()
    )
    fixture.then_devices_should_be({device.id: device})
    fixture.then_manual_settings_should_be({expected_manual_setting.id: expected_manual_setting})


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
