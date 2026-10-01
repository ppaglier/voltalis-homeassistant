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
        GetEnergyContractCurrentTariffQuery(type=EnergyContractTypeEnum.BASE, off_peak_hours=[])
    )

    assert result == EnergyContractCurrentTariffEnum.BASE


@pytest.mark.unit
async def test_get_energy_contract_current_tariff_off_peak(
    fixture: EnergyContractsFixture,
) -> None:
    """Test peak/off-peak contracts return OFF_PEAK during off-peak range."""

    fixture.given_now(datetime(2024, 1, 2, 2, 0, 0))

    result = await fixture.get_energy_contract_current_tariff_handler.handle(
        GetEnergyContractCurrentTariffQuery(
            type=EnergyContractTypeEnum.PEAK_OFF_PEAK,
            off_peak_hours=[RangeModel[time](start=time(1, 0), end=time(6, 0))],
        )
    )

    assert result == EnergyContractCurrentTariffEnum.OFF_PEAK


@pytest.mark.unit
async def test_get_energy_contract_current_tariff_peak(
    fixture: EnergyContractsFixture,
) -> None:
    """Test peak/off-peak contracts return PEAK outside off-peak range."""

    fixture.given_now(datetime(2024, 1, 2, 12, 0, 0))

    result = await fixture.get_energy_contract_current_tariff_handler.handle(
        GetEnergyContractCurrentTariffQuery(
            type=EnergyContractTypeEnum.PEAK_OFF_PEAK,
            off_peak_hours=[RangeModel[time](start=time(1, 0), end=time(6, 0))],
        )
    )

    assert result == EnergyContractCurrentTariffEnum.PEAK


@pytest.fixture
def fixture() -> EnergyContractsFixture:
    return EnergyContractsFixture()
