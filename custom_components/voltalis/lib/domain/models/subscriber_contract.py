from pydantic import ConfigDict

from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisTimeRange(CustomModel):
    """Class to represent time ranges for peak/offpeak hours"""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=None,
    )

    from_time: str  # Format: "HH:MM"
    to_time: str  # Format: "HH:MM"


class VoltalisSubscriberContract(CustomModel):
    """Class to represent a Voltalis subscriber contract"""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=None,
    )

    id: int
    site_id: int
    subscriber_id: int
    name: str
    is_default: bool
    subscribed_power: int
    is_peak_offpeak_contract: bool
    subscription_base_price: float | None = None
    subscription_peak_offpeak_base_price: float | None = None
    kwh_base_price: float | None = None
    kwh_peak_hour_price: float | None = None
    kwh_offpeak_hour_price: float | None = None
    creation_date_time: str
    start_date: str | None = None
    end_date: str | None = None
    company_name: str
    api_contract_id: int
    company_id: int
    peak_hours: list[VoltalisTimeRange]
    offpeak_hours: list[VoltalisTimeRange]
