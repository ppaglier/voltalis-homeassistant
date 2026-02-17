from datetime import datetime, timedelta

import pytest

from custom_components.voltalis.lib.application.devices_management.commands.set_device_temperature_command import (
    SetDeviceTemperatureCommand,
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
async def test_set_device_temperature_sets_manual_mode_with_duration(
    fixture: DeviceManagementFixture,
) -> None:
    """Test set device temperature sets duration and target temperature."""

    # Given
    now = datetime(2024, 1, 2, 10, 0, 0)
    fixture.given_now(now)
    device = DeviceBuilder().with_id(1).build()
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings({manual_setting.id: manual_setting})

    # When
    await fixture.set_device_temperature_handler.handle(
        SetDeviceTemperatureCommand(
            device=DeviceDto(**device.model_dump(), manual_setting=manual_setting),
            temperature=22.5,
            mode=DeviceModeEnum.TEMPERATURE,
            duration_hours=2,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_enabled(True)
        .with_until_further_notice(False)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.TEMPERATURE)
        .with_end_date(now + timedelta(hours=2))
        .with_temperature_target(22.5)
        .build()
    )
    fixture.then_manual_settings_should_be({expected.id: expected})


@pytest.mark.unit
async def test_set_device_temperature_requires_manual_setting(
    fixture: DeviceManagementFixture,
) -> None:
    """Test set device temperature raises when device has no manual setting."""

    device = DeviceBuilder().with_id(1).build()

    with pytest.raises(ValueError, match="does not support manual settings"):
        await fixture.set_device_temperature_handler.handle(
            SetDeviceTemperatureCommand(
                device=DeviceDto(**device.model_dump(), manual_setting=None),
                temperature=22.0,
            )
        )


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
