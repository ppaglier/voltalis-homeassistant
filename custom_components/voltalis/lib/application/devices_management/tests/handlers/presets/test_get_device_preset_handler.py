import pytest

from custom_components.voltalis.lib.application.devices_management.queries.get_device_preset_query import (
    GetDevicePresetQuery,
)
from custom_components.voltalis.lib.application.devices_management.tests.device_management_fixture import (
    DeviceManagementFixture,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.presets.preset_enum import DeviceCurrentPresetEnum


@pytest.mark.unit
def test_get_device_preset_returns_off_when_device_is_off(
    fixture: DeviceManagementFixture,
) -> None:
    """Test device preset handler returns OFF when device is off."""

    result = fixture.get_device_preset_handler.handle(
        GetDevicePresetQuery(
            is_on=False,
            id_manual_setting=1,
            mode=DeviceModeEnum.COMFORT,
        )
    )

    assert result == DeviceCurrentPresetEnum.OFF


@pytest.mark.unit
def test_get_device_preset_returns_auto_when_no_manual_setting(
    fixture: DeviceManagementFixture,
) -> None:
    """Test device preset handler returns AUTO without manual setting."""

    result = fixture.get_device_preset_handler.handle(
        GetDevicePresetQuery(
            is_on=True,
            id_manual_setting=None,
            mode=DeviceModeEnum.COMFORT,
        )
    )

    assert result == DeviceCurrentPresetEnum.AUTO


@pytest.mark.unit
def test_get_device_preset_returns_off_for_climate_temperature_mode(
    fixture: DeviceManagementFixture,
) -> None:
    """Test device preset handler returns OFF for climate TEMPERATURE mode."""

    result = fixture.get_device_preset_handler.handle(
        GetDevicePresetQuery(
            is_on=True,
            id_manual_setting=1,
            mode=DeviceModeEnum.TEMPERATURE,
            climate_mode=True,
        )
    )

    assert result == DeviceCurrentPresetEnum.OFF


@pytest.mark.unit
def test_get_device_preset_maps_modes(
    fixture: DeviceManagementFixture,
) -> None:
    """Test device preset handler maps modes to presets."""

    result = fixture.get_device_preset_handler.handle(
        GetDevicePresetQuery(
            is_on=True,
            id_manual_setting=1,
            mode=DeviceModeEnum.COMFORT,
        )
    )

    assert result == DeviceCurrentPresetEnum.COMFORT


@pytest.mark.unit
def test_get_device_preset_non_climate_device_with_unrecognized_mode_returns_off(
    fixture: DeviceManagementFixture,
) -> None:
    """Test device preset handler returns OFF for non-climate devices with unrecognized modes."""

    result = fixture.get_device_preset_handler.handle(
        GetDevicePresetQuery(
            is_on=True,
            id_manual_setting=1,
            mode=None,
            climate_mode=True,
        )
    )

    assert result is None


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
