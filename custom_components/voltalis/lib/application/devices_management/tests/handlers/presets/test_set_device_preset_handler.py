import pytest

from custom_components.voltalis.lib.application.devices_management.commands.set_device_preset_command import (
    SetDevicePresetCommand,
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
from custom_components.voltalis.lib.domain.devices_management.presets.device_current_preset_enum import (
    DeviceCurrentPresetEnum,
)


@pytest.mark.unit
async def test_set_device_preset_auto_disables_manual_mode(
    fixture: DeviceManagementFixture,
) -> None:
    """Test setting AUTO preset disables manual mode."""

    # Given
    now = fixture.date_provider.get_now()
    device = DeviceBuilder().with_id(1).build()
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings({manual_setting.id: manual_setting})

    # When
    await fixture.set_device_preset_handler.handle(
        SetDevicePresetCommand(
            device=DeviceDto(**device.model_dump(), manual_setting=manual_setting),
            preset=DeviceCurrentPresetEnum.AUTO,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_until_further_notice(False)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.ECO)
        .with_end_date(now)
        .with_temperature_target(16.0)
        .build()
    )
    fixture.then_manual_settings_should_be({expected.id: expected})


@pytest.mark.unit
async def test_set_device_preset_off_in_climate_mode_sets_temperature(
    fixture: DeviceManagementFixture,
) -> None:
    """Test OFF preset in climate mode maps to TEMPERATURE manual mode."""

    # Given
    device = DeviceBuilder().with_id(1).build()
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings({manual_setting.id: manual_setting})

    # When
    await fixture.set_device_preset_handler.handle(
        SetDevicePresetCommand(
            device=DeviceDto(**device.model_dump(), manual_setting=manual_setting),
            preset=DeviceCurrentPresetEnum.OFF,
            climate_mode=True,
            temperature=19.0,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_enabled(True)
        .with_until_further_notice(True)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.TEMPERATURE)
        .with_end_date(None)
        .with_temperature_target(19.0)
        .build()
    )
    fixture.then_manual_settings_should_be({expected.id: expected})


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()


@pytest.mark.unit
async def test_set_device_preset_eco_maps_to_ecov(
    fixture: DeviceManagementFixture,
) -> None:
    """Test ECO preset maps to ECOV when available."""

    # Given
    device = DeviceBuilder().with_id(1).build()
    manual_setting_builder = ManualSettingBuilder().with_id(1).with_id_appliance(device.id)
    manual_setting = manual_setting_builder.build()
    fixture.given_manual_settings({manual_setting.id: manual_setting})

    # When
    await fixture.set_device_preset_handler.handle(
        SetDevicePresetCommand(
            device=DeviceDto(**device.model_dump(), manual_setting=manual_setting),
            preset=DeviceCurrentPresetEnum.ECO,
            has_ecov_mode=True,
            temperature=18.0,
        )
    )

    # Then
    expected = (
        manual_setting_builder.with_enabled(True)
        .with_until_further_notice(True)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.ECOV)
        .with_end_date(None)
        .with_temperature_target(18.0)
        .build()
    )
    fixture.then_manual_settings_should_be({expected.id: expected})
