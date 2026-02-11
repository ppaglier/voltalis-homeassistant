from datetime import date, time

from pydantic import Field

from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import (
    EnergyContract,
    EnergyContractPrices,
    EnergyContractTypeEnum,
)
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel
from custom_components.voltalis.lib.domain.shared.range_model import RangeModel


class VoltalisTimeRange(CustomModel):
    """Class to represent time ranges for peak/offpeak hours"""

    from_time: time = Field(alias="from")
    to_time: time = Field(alias="to")


class VoltalisSubscriberContractDto(CustomModel):
    """Class to represent a Voltalis subscriber contract DTO"""

    id: int
    api_contract_id: int = Field(alias="apiContractId")
    company_name: str = Field(alias="companyName")
    name: str
    subscribed_power: int = Field(alias="subscribedPower")
    is_peak_off_peak_contract: bool = Field(alias="isPeakOffPeakContract")
    end_date: date | None = Field(None, alias="endDate")

    subscription_base_price: float | None = Field(None, alias="subscriptionBasePrice")
    subscription_peak_off_peak_base_price: float | None = Field(None, alias="subscriptionPeakOffPeakBasePrice")
    kwh_base_price: float | None = Field(None, alias="kwhBasePrice")
    kwh_peak_hour_price: float | None = Field(None, alias="kwhPeakHourPrice")
    kwh_offpeak_hour_price: float | None = Field(None, alias="kwhOffpeakHourPrice")

    peak_hours: list[VoltalisTimeRange] = Field(alias="peakHours")
    offpeak_hours: list[VoltalisTimeRange] = Field(alias="offpeakHours")

    def to_energy_contract(self) -> EnergyContract:
        return EnergyContract(
            id=self.id,
            contract_id=self.api_contract_id,
            company_name=self.company_name,
            name=self.name,
            subscribed_power=self.subscribed_power,
            end_date=self.end_date,
            type=(
                EnergyContractTypeEnum.BASE
                if not self.is_peak_off_peak_contract
                else EnergyContractTypeEnum.PEAK_OFFPEAK
            ),
            prices=EnergyContractPrices(
                subscription=(
                    (self.subscription_base_price or 0.0)
                    if not self.is_peak_off_peak_contract
                    else (self.subscription_peak_off_peak_base_price or 0.0)
                ),
                kwh_base=self.kwh_base_price,
                kwh_peak=self.kwh_peak_hour_price,
                kwh_offpeak=self.kwh_offpeak_hour_price,
            ),
            peak_hours=[
                RangeModel(start=time_range.from_time, end=time_range.to_time) for time_range in self.peak_hours
            ],
            offpeak_hours=[
                RangeModel(start=time_range.from_time, end=time_range.to_time) for time_range in self.offpeak_hours
            ],
        )
