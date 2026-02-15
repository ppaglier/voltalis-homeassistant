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

    props: dict = {}

    def __init__(self, props: dict | None = None):
        self.props = {**EnergyContractBuilder.DEFAULT_VALUES.model_dump(), **(props or {})}

    def build(self) -> EnergyContract:
        return EnergyContract(**self.props)

    def with_id(self, id: int) -> Self:
        """Set the id."""
        self.props["id"] = id
        self.props["contract_id"] = id
        return self

    def with_contract_id(self, contract_id: int) -> Self:
        """Set the contract_id."""
        return self._set_value("contract_id", contract_id)

    def with_company_name(self, company_name: str) -> Self:
        """Set the company name."""
        return self._set_value("company_name", company_name)

    def with_name(self, name: str) -> Self:
        """Set the name."""
        return self._set_value("name", name)

    def with_subscribed_power(self, subscribed_power: int) -> Self:
        """Set the subscribed power."""
        return self._set_value("subscribed_power", subscribed_power)

    def with_type(self, type: EnergyContractTypeEnum) -> Self:
        """Set the type."""
        return self._set_value("type", type)

    def with_end_date(self, end_date: date | None) -> Self:
        """Set the end date."""
        return self._set_value("end_date", end_date)

    def with_prices_kwh_base(self, kwh_base: float) -> Self:
        """Set the base kWh price."""

        prices = self._get_value("prices")
        prices["kwh_base"] = kwh_base
        return self._set_value("prices", prices)

    def with_prices_kwh_peak(self, kwh_peak: float) -> Self:
        """Set the peak kWh price."""

        prices = self._get_value("prices")
        prices["kwh_peak"] = kwh_peak
        return self._set_value("prices", prices)

    def with_prices_kwh_offpeak(self, kwh_offpeak: float) -> Self:
        """Set the offpeak kWh price."""

        prices = self._get_value("prices")
        prices["kwh_offpeak"] = kwh_offpeak
        return self._set_value("prices", prices)

    def with_peak_hours(self, peak_hours: list[RangeModel[time]]) -> Self:
        """Set the peak hours."""
        return self._set_value("peak_hours", peak_hours)

    def with_offpeak_hours(self, offpeak_hours: list[RangeModel[time]]) -> Self:
        """Set the offpeak hours."""
        return self._set_value("offpeak_hours", offpeak_hours)
