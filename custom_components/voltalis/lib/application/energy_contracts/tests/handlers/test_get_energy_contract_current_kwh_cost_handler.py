import pytest

from custom_components.voltalis.lib.application.energy_contracts.queries.get_energy_contract_current_kwh_cost_query import (  # noqa: E501
    GetEnergyContractCurrentKwCostQuery,
)
from custom_components.voltalis.lib.application.energy_contracts.tests.energy_contracts_fixture import (
    EnergyContractsFixture,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_current_mode_enum import (
    EnergyContractCurrentModeEnum,
)


@pytest.mark.unit
async def test_get_energy_contract_current_kwh_cost_base(
    fixture: EnergyContractsFixture,
) -> None:
    """Test kWh cost handler returns base price."""

    result = await fixture.get_energy_contract_current_kwh_cost_handler.handle(
        GetEnergyContractCurrentKwCostQuery(
            current_mode=EnergyContractCurrentModeEnum.BASE,
            base_kwh_cost=0.2,
            peak_kwh_cost=0.3,
            offpeak_kwh_cost=0.1,
        )
    )

    assert result == 0.2


@pytest.mark.unit
async def test_get_energy_contract_current_kwh_cost_peak(
    fixture: EnergyContractsFixture,
) -> None:
    """Test kWh cost handler returns peak price."""

    result = await fixture.get_energy_contract_current_kwh_cost_handler.handle(
        GetEnergyContractCurrentKwCostQuery(
            current_mode=EnergyContractCurrentModeEnum.PEAK,
            base_kwh_cost=0.2,
            peak_kwh_cost=0.3,
            offpeak_kwh_cost=0.1,
        )
    )

    assert result == 0.3


@pytest.mark.unit
async def test_get_energy_contract_current_kwh_cost_offpeak(
    fixture: EnergyContractsFixture,
) -> None:
    """Test kWh cost handler returns offpeak price."""

    result = await fixture.get_energy_contract_current_kwh_cost_handler.handle(
        GetEnergyContractCurrentKwCostQuery(
            current_mode=EnergyContractCurrentModeEnum.OFFPEAK,
            base_kwh_cost=0.2,
            peak_kwh_cost=0.3,
            offpeak_kwh_cost=0.1,
        )
    )

    assert result == 0.1


@pytest.fixture
def fixture() -> EnergyContractsFixture:
    return EnergyContractsFixture()
