from pydantic import Field

from custom_components.voltalis.lib.domain.custom_model import CustomModel


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
