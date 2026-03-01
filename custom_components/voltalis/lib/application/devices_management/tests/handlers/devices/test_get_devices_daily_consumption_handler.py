from datetime import datetime

import pytest

from custom_components.voltalis.lib.application.devices_management.tests.device_management_fixture import (
    DeviceManagementFixture,
)
from custom_components.voltalis.lib.domain.devices_management.consumptions.device_consumption import (
    DeviceConsumption,
)


@pytest.mark.unit
async def test_get_devices_daily_consumption_uses_previous_hour(
    fixture: DeviceManagementFixture,
) -> None:
    """Test daily consumption handler uses previous hour to aggregate."""

    # Given
    now = datetime(2024, 1, 1, 10, 30, 0)
    fixture.given_now(now)
    fixture.given_devices_consumptions(
        {
            1: [
                (datetime(2024, 1, 1, 8, 15, 0), 1.2),
                (datetime(2024, 1, 1, 9, 45, 0), 2.3),
                (datetime(2024, 1, 1, 10, 15, 0), 3.0),
            ]
        }
    )

    # When
    result = await fixture.get_devices_daily_consumption_handler.handle()

    # Then
    expected = {1: DeviceConsumption(daily_consumption=1.2 + 2.3)}
    fixture.compare_dicts(result, expected)


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
