import pytest

from custom_components.voltalis.lib.application.devices_management.tests.device_management_fixture import (
    DeviceManagementFixture,
)
from custom_components.voltalis.lib.domain.devices_management.health.device_health import (
    DeviceHealth,
    DeviceHealthStatusEnum,
)


@pytest.mark.unit
async def test_get_devices_health_returns_provider_data(
    fixture: DeviceManagementFixture,
) -> None:
    """Test get devices health handler returns provider data."""

    # Given
    devices_health = {1: DeviceHealth(status=DeviceHealthStatusEnum.OK)}
    fixture.given_devices_health(devices_health)

    # When
    result = await fixture.get_devices_health_handler.handle()

    # Then
    fixture.compare_dicts(result, devices_health)


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
