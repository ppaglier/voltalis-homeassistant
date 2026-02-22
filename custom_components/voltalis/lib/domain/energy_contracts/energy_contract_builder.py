from datetime import date, time
from typing import Self

from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import (
    EnergyContract,
    EnergyContractPrices,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_enum import EnergyContractTypeEnum
from custom_components.voltalis.lib.domain.shared.generic_builder import GenericBuilder
from custom_components.voltalis.lib.domain.shared.range_model import RangeModel


class EnergyContractBuilder(GenericBuilder[EnergyContract]):
    """Builder for EnergyContract model."""

    DEFAULT_VALUES = EnergyContract(
        id=1,
        contract_id=1,
        company_name="ACME",
        name="Contract 1",
        subscribed_power=3,
        type=EnergyContractTypeEnum.BASE,
        end_date=None,
        prices=EnergyContractPrices(
            subscription=10.0,
            kwh_base=0.2,
            kwh_peak=0.3,
            kwh_offpeak=0.1,
        ),
        peak_hours=[RangeModel[time](start=time(8, 0), end=time(20, 0))],
        offpeak_hours=[RangeModel[time](start=time(20, 0), end=time(6, 0))],
    )

    def build(self) -> EnergyContract:
        return EnergyContract(**self.props)

    def with_id(self, id: int) -> Self:
        """Set the id."""
        return self._set_value("id", id)

    def with_contract_id(self, contract_id: int) -> Self:
        """Set the contract id."""
        return self._set_value("contract_id", contract_id)

    def with_type(self, _type: EnergyContractTypeEnum) -> Self:
        """Set the contract type."""
        return self._set_value("type", _type)

    def with_end_date(self, end_date: date | None) -> Self:
        """Set the end date."""
        return self._set_value("end_date", end_date)
