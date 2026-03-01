from datetime import datetime, time

import pytest

from custom_components.voltalis.lib.application.energy_contracts.queries.get_energy_contract_current_mode_query import (
    GetEnergyContractCurrentModeQuery,
)
from custom_components.voltalis.lib.application.energy_contracts.tests.energy_contracts_fixture import (
    EnergyContractsFixture,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_current_mode_enum import (
    EnergyContractCurrentModeEnum,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_enum import EnergyContractTypeEnum
from custom_components.voltalis.lib.domain.shared.range_model import RangeModel


@pytest.mark.unit
async def test_get_energy_contract_current_mode_base(
    fixture: EnergyContractsFixture,
) -> None:
    """Test base contracts always return BASE mode."""

    fixture.given_now(datetime(2024, 1, 2, 9, 0, 0))

    result = await fixture.get_energy_contract_current_mode_handler.handle(
        GetEnergyContractCurrentModeQuery(type=EnergyContractTypeEnum.BASE, offpeak_hours=[])
    )

    assert result == EnergyContractCurrentModeEnum.BASE


@pytest.mark.unit
async def test_get_energy_contract_current_mode_offpeak(
    fixture: EnergyContractsFixture,
) -> None:
    """Test peak/offpeak contracts return OFFPEAK during offpeak range."""

    fixture.given_now(datetime(2024, 1, 2, 2, 0, 0))

    result = await fixture.get_energy_contract_current_mode_handler.handle(
        GetEnergyContractCurrentModeQuery(
            type=EnergyContractTypeEnum.PEAK_OFFPEAK,
            offpeak_hours=[RangeModel[time](start=time(1, 0), end=time(6, 0))],
        )
    )

    assert result == EnergyContractCurrentModeEnum.OFFPEAK


@pytest.mark.unit
async def test_get_energy_contract_current_mode_peak(
    fixture: EnergyContractsFixture,
) -> None:
    """Test peak/offpeak contracts return PEAK outside offpeak range."""

    fixture.given_now(datetime(2024, 1, 2, 12, 0, 0))

    result = await fixture.get_energy_contract_current_mode_handler.handle(
        GetEnergyContractCurrentModeQuery(
            type=EnergyContractTypeEnum.PEAK_OFFPEAK,
            offpeak_hours=[RangeModel[time](start=time(1, 0), end=time(6, 0))],
        )
    )

    assert result == EnergyContractCurrentModeEnum.PEAK


@pytest.fixture
def fixture() -> EnergyContractsFixture:
    return EnergyContractsFixture()
