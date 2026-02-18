from datetime import datetime, timedelta

import pytest

from custom_components.voltalis.lib.application.devices_management.commands.turn_off_device_command import (
    TurnOffDeviceCommand,
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
async def test_turn_off_device_sets_manual_mode(
    fixture: DeviceManagementFixture,
) -> None:
    """Test turning off device updates manual setting with duration."""

    # Given
    now = datetime(2024, 1, 3, 8, 0, 0)
    fixture.given_now(now)
    device = DeviceBuilder().with_id(1).build()
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings([manual_setting])

    # When
    await fixture.turn_off_device_handler.handle(
        TurnOffDeviceCommand(
            device=DeviceDto(**device.model_dump(), manual_setting=manual_setting),
            fallback_mode=DeviceModeEnum.CONFORT,
            fallback_temperature=17.0,
            duration_hours=3,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_enabled(True)
        .with_until_further_notice(False)
        .with_is_on(False)
        .with_mode(DeviceModeEnum.CONFORT)
        .with_end_date(now + timedelta(hours=3))
        .with_temperature_target(17.0)
        .build()
    )
    fixture.then_manual_settings_should_be({expected.id: expected})


@pytest.mark.unit
async def test_turn_off_device_requires_manual_setting(
    fixture: DeviceManagementFixture,
) -> None:
    """Test turn off device raises when device has no manual setting."""

    device = DeviceBuilder().with_id(1).build()

    with pytest.raises(ValueError, match="does not support manual settings"):
        await fixture.turn_off_device_handler.handle(
            TurnOffDeviceCommand(
                device=DeviceDto(**device.model_dump(), manual_setting=None),
            )
        )


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
