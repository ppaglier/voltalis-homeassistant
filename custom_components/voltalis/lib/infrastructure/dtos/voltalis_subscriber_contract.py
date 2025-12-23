from pydantic import Field

from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisTimeRange(CustomModel):
    """Class to represent time ranges for peak/offpeak hours"""

    from_time: str = Field(alias="from")
    to_time: str = Field(alias="to")


class VoltalisSubscriberContractDto(CustomModel):
    """Class to represent a Voltalis subscriber contract DTO"""

    id: int
    company_name: str
    name: str
    subscribed_power: int
    is_peak_off_peak_contract: bool

    subscription_base_price: float | None = None
    subscription_peak_off_peak_base_price: float | None = None
    kwh_base_price: float | None = None
    kwh_peak_hour_price: float | None = None
    kwh_offpeak_hour_price: float | None = None

    peak_hours: list[VoltalisTimeRange]
    offpeak_hours: list[VoltalisTimeRange]
