import pytest

from custom_components.voltalis.lib.application.devices_management.dtos.get_device_presets_dto import (
    GetDevicePresetsDto,
)
from custom_components.voltalis.lib.application.devices_management.queries.get_device_presets_query import (
    GetDevicePresetsQuery,
)
from custom_components.voltalis.lib.application.devices_management.tests.device_management_fixture import (
    DeviceManagementFixture,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.presets.preset_enum import DeviceCurrentPresetEnum


@pytest.mark.unit
def test_get_device_presets_includes_auto_on_and_off(
    fixture: DeviceManagementFixture,
) -> None:
    """Test device presets handler builds presets list with AUTO/ON/OFF."""

    result = fixture.get_device_presets_handler.handle(
        GetDevicePresetsQuery(
            available_modes=[
                DeviceModeEnum.COMFORT,
                DeviceModeEnum.ECO,
                DeviceModeEnum.AWAY,
                DeviceModeEnum.ON,
                DeviceModeEnum.TEMPERATURE,
            ]
        )
    )

    expected = GetDevicePresetsDto(
        presets=[
            DeviceCurrentPresetEnum.AUTO,
            DeviceCurrentPresetEnum.ON,
            DeviceCurrentPresetEnum.COMFORT,
            DeviceCurrentPresetEnum.ECO,
            DeviceCurrentPresetEnum.AWAY,
            DeviceCurrentPresetEnum.TEMPERATURE,
            DeviceCurrentPresetEnum.OFF,
        ],
        has_on_mode=True,
    )

    fixture.compare_data(result, expected)


@pytest.mark.unit
def test_get_device_presets_climate_mode(
    fixture: DeviceManagementFixture,
) -> None:
    """Test device presets handler excludes AUTO/ON/OFF for climate devices."""

    result = fixture.get_device_presets_handler.handle(
        GetDevicePresetsQuery(
            available_modes=[
                DeviceModeEnum.COMFORT,
                DeviceModeEnum.ECO,
                DeviceModeEnum.AWAY,
                DeviceModeEnum.ON,
                DeviceModeEnum.TEMPERATURE,
            ],
            climate_mode=True,
        )
    )

    expected = GetDevicePresetsDto(
        presets=[
            DeviceCurrentPresetEnum.COMFORT,
            DeviceCurrentPresetEnum.ECO,
            DeviceCurrentPresetEnum.AWAY,
            DeviceCurrentPresetEnum.OFF,
        ],
        has_on_mode=True,
    )

    fixture.compare_data(result, expected)


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
