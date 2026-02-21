from datetime import date, datetime

import pytest

from custom_components.voltalis.lib.application.energy_contracts.tests.energy_contracts_fixture import (
    EnergyContractsFixture,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_builder import (
    EnergyContractBuilder,
)


@pytest.mark.unit
async def test_get_current_energy_contract_returns_active_contract(
    fixture: EnergyContractsFixture,
) -> None:
    """Test current energy contract handler returns the active contract."""

    # Given
    fixture.given_now(datetime(2024, 1, 10, 10, 0, 0))
    expired = EnergyContractBuilder().with_id(1).with_end_date(date(2024, 1, 1)).build()
    current = EnergyContractBuilder().with_id(2).with_end_date(None).build()
    fixture.given_energy_contracts([expired, current])

    # When
    result = await fixture.get_current_energy_contract_handler.handle()

    # Then
    fixture.compare_data(result, current)


@pytest.mark.unit
async def test_get_current_energy_contract_returns_none_when_all_expired(
    fixture: EnergyContractsFixture,
) -> None:
    """Test current energy contract handler returns None when no contract is active."""

    # Given
    fixture.given_now(datetime(2024, 1, 10, 10, 0, 0))
    expired = EnergyContractBuilder().with_id(1).with_end_date(date(2024, 1, 1)).build()
    fixture.given_energy_contracts([expired])

    # When
    result = await fixture.get_current_energy_contract_handler.handle()

    # Then
    assert result is None


@pytest.fixture
def fixture() -> EnergyContractsFixture:
    return EnergyContractsFixture()
