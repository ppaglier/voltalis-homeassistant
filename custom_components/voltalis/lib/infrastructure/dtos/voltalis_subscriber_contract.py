from datetime import datetime

from pydantic import Field

from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.models.energy_contract import (
    VoltalisEnergyContract,
    VoltalisEnergyContractPrices,
    VoltalisEnergyContractTypeEnum,
)
from custom_components.voltalis.lib.domain.range_model import RangeModel


class VoltalisTimeRange(CustomModel):
    """Class to represent time ranges for peak/offpeak hours"""

    from_time: str = Field(alias="from")
    to_time: str = Field(alias="to")


class VoltalisSubscriberContractDto(CustomModel):
    """Class to represent a Voltalis subscriber contract DTO"""

    id: int
    company_name: str = Field(alias="companyName")
    name: str
    subscribed_power: int = Field(alias="subscribedPower")
    is_peak_off_peak_contract: bool = Field(alias="isPeakOffPeakContract")

    subscription_base_price: float | None = Field(None, alias="subscriptionBasePrice")
    subscription_peak_off_peak_base_price: float | None = Field(None, alias="subscriptionPeakOffPeakBasePrice")
    kwh_base_price: float | None = Field(None, alias="kwhBasePrice")
    kwh_peak_hour_price: float | None = Field(None, alias="kwhPeakHourPrice")
    kwh_offpeak_hour_price: float | None = Field(None, alias="kwhOffpeakHourPrice")

    peak_hours: list[VoltalisTimeRange] = Field(alias="peakHours")
    offpeak_hours: list[VoltalisTimeRange] = Field(alias="offpeakHours")

    def to_voltalis_energy_contract(self) -> VoltalisEnergyContract:
        return VoltalisEnergyContract(
            id=self.id,
            company_name=self.company_name,
            name=self.name,
            subscribed_power=self.subscribed_power,
            type=(
                VoltalisEnergyContractTypeEnum.BASE
                if not self.is_peak_off_peak_contract
                else VoltalisEnergyContractTypeEnum.PEAK_OFFPEAK
            ),
            prices=VoltalisEnergyContractPrices(
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
                RangeModel(
                    start=datetime.strptime(time_range.from_time, "%H:%M").time(),
                    end=datetime.strptime(time_range.to_time, "%H:%M").time(),
                )
                for time_range in self.peak_hours
            ],
            offpeak_hours=[
                RangeModel(
                    start=datetime.strptime(time_range.from_time, "%H:%M").time(),
                    end=datetime.strptime(time_range.to_time, "%H:%M").time(),
                )
                for time_range in self.offpeak_hours
            ],
        )
