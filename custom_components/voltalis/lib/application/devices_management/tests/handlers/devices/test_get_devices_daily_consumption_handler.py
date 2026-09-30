from datetime import datetime

import pytest

from custom_components.voltalis.lib.application.devices_management.tests.device_management_fixture import (
    DeviceManagementFixture,
)
from custom_components.voltalis.lib.domain.devices_management.consumptions.device_consumption import (
    ConsumptionRecord,
    DeviceConsumption,
)


@pytest.mark.unit
async def test_get_devices_daily_consumption_uses_previous_hour(
    fixture: DeviceManagementFixture,
) -> None:
    """Test daily consumption handler uses previous hour to aggregate."""

    # Given
    now = datetime(2024, 1, 1, 9, 15, 0)
    fixture.given_now(now)
    fixture.given_devices_consumptions(
        {
            1: [
                ConsumptionRecord(timestamp=datetime(2024, 1, 1, 8, 15, 0), total_consumption_in_wh=1.2),
                ConsumptionRecord(timestamp=datetime(2024, 1, 1, 9, 45, 0), total_consumption_in_wh=2.3),
                ConsumptionRecord(timestamp=datetime(2024, 1, 1, 10, 15, 0), total_consumption_in_wh=3.0),
            ]
        }
    )

    # When
    result = await fixture.get_devices_daily_consumption_handler.handle(
        target_date=now.date(),
        target_time=now.time(),
    )

    # Then
    expected = {
        1: DeviceConsumption(
            daily_consumption_records=[
                ConsumptionRecord(timestamp=datetime(2024, 1, 1, 8, 15, 0), total_consumption_in_wh=1.2),
            ],
        )
    }
    fixture.compare_dicts(result, expected)


@pytest.fixture
def fixture() -> DeviceManagementFixture:
    return DeviceManagementFixture()
