import pytest

from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto
from custom_components.voltalis.lib.application.devices_management.tests.device_management_fixture import (
    DeviceManagementFixture,
)
from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting_builder import (
    ManualSettingBuilder,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_builder import DeviceBuilder
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import (
    DeviceTypeEnum,
)


@pytest.mark.unit
async def test_get_devices_filters_supported_types_and_attaches_manual_settings(
    fixture: DeviceManagementFixture,
) -> None:
    """Test get devices handler with manual settings and supported types."""

    # Given
    heater = DeviceBuilder().with_id(1).build()
    water_heater = DeviceBuilder().with_id(2).with_type(DeviceTypeEnum.WATER_HEATER).build()
    other = DeviceBuilder().with_id(3).with_type(DeviceTypeEnum.OTHER).build()
    manual_setting = ManualSettingBuilder().with_id(10).with_id_appliance(heater.id).build()
    fixture.given_devices([heater, water_heater, other])
    fixture.given_manual_settings([manual_setting])

    # When
    result = await fixture.get_devices_handler.handle()

    # Then
    expected = {
        heater.id: DeviceDto.from_device(heater, manual_setting),
        water_heater.id: DeviceDto.from_device(water_heater, None),
    }
    fixture.compare_dicts(result, expected)


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
