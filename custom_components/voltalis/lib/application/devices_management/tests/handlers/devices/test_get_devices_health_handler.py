import pytest

from custom_components.voltalis.lib.application.devices_management.tests.device_management_fixture import (
    DeviceManagementFixture,
)
from custom_components.voltalis.lib.domain.devices_management.health.device_health import DeviceHealthStatusEnum
from custom_components.voltalis.lib.domain.devices_management.health.device_health_builder import DeviceHealthBuilder


@pytest.mark.unit
async def test_get_devices_health_returns_provider_data(
    fixture: DeviceManagementFixture,
) -> None:
    """Test get devices health handler returns provider data."""

    # Given
    device_health = DeviceHealthBuilder().with_status(DeviceHealthStatusEnum.OK).build()
    fixture.given_devices_health([device_health])

    # When
    result = await fixture.get_devices_health_handler.handle()

    # Then
    fixture.compare_dicts(result, {device_health.device_id: device_health})


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
