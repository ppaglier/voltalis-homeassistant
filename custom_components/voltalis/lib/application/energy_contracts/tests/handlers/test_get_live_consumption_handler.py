import pytest

from custom_components.voltalis.lib.application.energy_contracts.tests.energy_contracts_fixture import (
    EnergyContractsFixture,
)
from custom_components.voltalis.lib.domain.energy_contracts.live_consumption import LiveConsumption


@pytest.mark.unit
async def test_get_live_consumption_returns_provider_data(
    fixture: EnergyContractsFixture,
) -> None:
    """Test live consumption handler returns provider data."""

    # Given
    live_consumption = LiveConsumption(consumption=42.0)
    fixture.given_live_consumption(live_consumption)

    # When
    result = await fixture.get_live_consumption_handler.handle()

    # Then
    fixture.compare_data(result, live_consumption)


@pytest.fixture
def fixture() -> EnergyContractsFixture:
    return EnergyContractsFixture()
