import pytest

from custom_components.voltalis.lib.application.energy_contracts.tests.energy_contracts_fixture import (
    EnergyContractsFixture,
)
from custom_components.voltalis.lib.domain.energy_contracts.live_power import LivePower


@pytest.mark.unit
async def test_get_live_power_returns_provider_data(
    fixture: EnergyContractsFixture,
) -> None:
    """Test live consumption handler returns provider data."""

    # Given
    live_power = LivePower(consumption=42.0)
    fixture.given_live_power(live_power)

    # When
    result = await fixture.get_live_power_handler.handle()

    # Then
    fixture.compare_data(result, live_power)


@pytest.fixture
def fixture() -> EnergyContractsFixture:
    return EnergyContractsFixture()
