from datetime import datetime, time

import pytest

from custom_components.voltalis.lib.application.energy_contracts.queries.get_energy_contract_current_tariff_query import (  # noqa: E501
    GetEnergyContractCurrentTariffQuery,
)
from custom_components.voltalis.lib.application.energy_contracts.tests.energy_contracts_fixture import (
    EnergyContractsFixture,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_current_tariff_enum import (
    EnergyContractCurrentTariffEnum,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_enum import EnergyContractTypeEnum
from custom_components.voltalis.lib.domain.shared.range_model import RangeModel


@pytest.mark.unit
async def test_get_energy_contract_current_tariff_base(
    fixture: EnergyContractsFixture,
) -> None:
    """Test base contracts always return BASE mode."""

    fixture.given_now(datetime(2024, 1, 2, 9, 0, 0))

    result = await fixture.get_energy_contract_current_tariff_handler.handle(
        GetEnergyContractCurrentTariffQuery(type=EnergyContractTypeEnum.BASE, offpeak_hours=[])
    )

    assert result == EnergyContractCurrentTariffEnum.BASE


@pytest.mark.unit
async def test_get_energy_contract_current_tariff_offpeak(
    fixture: EnergyContractsFixture,
) -> None:
    """Test peak/offpeak contracts return OFFPEAK during offpeak range."""

    fixture.given_now(datetime(2024, 1, 2, 2, 0, 0))

    result = await fixture.get_energy_contract_current_tariff_handler.handle(
        GetEnergyContractCurrentTariffQuery(
            type=EnergyContractTypeEnum.PEAK_OFFPEAK,
            offpeak_hours=[RangeModel[time](start=time(1, 0), end=time(6, 0))],
        )
    )

    assert result == EnergyContractCurrentTariffEnum.OFFPEAK


@pytest.mark.unit
async def test_get_energy_contract_current_tariff_peak(
    fixture: EnergyContractsFixture,
) -> None:
    """Test peak/offpeak contracts return PEAK outside offpeak range."""

    fixture.given_now(datetime(2024, 1, 2, 12, 0, 0))

    result = await fixture.get_energy_contract_current_tariff_handler.handle(
        GetEnergyContractCurrentTariffQuery(
            type=EnergyContractTypeEnum.PEAK_OFFPEAK,
            offpeak_hours=[RangeModel[time](start=time(1, 0), end=time(6, 0))],
        )
    )

    assert result == EnergyContractCurrentTariffEnum.PEAK


@pytest.fixture
def fixture() -> EnergyContractsFixture:
    return EnergyContractsFixture()
