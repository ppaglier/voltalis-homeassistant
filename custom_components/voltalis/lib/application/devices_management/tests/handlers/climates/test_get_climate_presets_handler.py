import pytest

from custom_components.voltalis.lib.application.devices_management.dtos.get_climate_presets_dto import (
    GetClimatePresetsDto,
)
from custom_components.voltalis.lib.application.devices_management.queries.get_climate_presets_query import (
    GetClimatePresetsQuery,
)
from custom_components.voltalis.lib.application.devices_management.tests.device_management_fixture import (
    DeviceManagementFixture,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.presets.device_current_preset_enum import (
    DeviceCurrentPresetEnum,
)


@pytest.mark.unit
def test_get_climate_presets_handler_returns_available_presets(
    fixture: DeviceManagementFixture,
) -> None:
    """Test climate presets handler with ECOV and other modes."""

    result = fixture.get_climate_presets_handler.handle(
        GetClimatePresetsQuery(
            available_modes=[
                DeviceModeEnum.CONFORT,
                DeviceModeEnum.ECOV,
                DeviceModeEnum.HORS_GEL,
                DeviceModeEnum.NORMAL,
            ]
        )
    )

    expected = GetClimatePresetsDto(
        presets=[
            DeviceCurrentPresetEnum.COMFORT,
            DeviceCurrentPresetEnum.ECO,
            DeviceCurrentPresetEnum.AWAY,
            DeviceCurrentPresetEnum.OFF,
        ],
        has_ecov_mode=True,
    )

    fixture.compare_data(result, expected)


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
