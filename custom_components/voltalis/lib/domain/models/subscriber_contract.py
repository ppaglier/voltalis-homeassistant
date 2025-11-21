from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisTimeRange(CustomModel):
    """Class to represent time ranges for peak/offpeak hours"""

    from_time: str  # Format: "HH:MM"
    to_time: str  # Format: "HH:MM"

    class Config:
        """Pydantic config"""

        fields = {
            "from_time": "from",
            "to_time": "to",
        }


class VoltalisSubscriberContract(CustomModel):
    """Class to represent a Voltalis subscriber contract"""

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

    class Config:
        """Pydantic config"""

        fields = {
            "site_id": "siteId",
            "subscriber_id": "subscriberId",
            "is_default": "isDefault",
            "subscribed_power": "subscribedPower",
            "is_peak_offpeak_contract": "isPeakOffPeakContract",
            "subscription_base_price": "subscriptionBasePrice",
            "subscription_peak_offpeak_base_price": "subscriptionPeakAndOffPeakHourBasePrice",
            "kwh_base_price": "kwhBasePrice",
            "kwh_peak_hour_price": "kwhPeakHourPrice",
            "kwh_offpeak_hour_price": "kwhOffpeakHourPrice",
            "creation_date_time": "creationDateTime",
            "start_date": "startDate",
            "end_date": "endDate",
            "company_name": "companyName",
            "api_contract_id": "apiContractId",
            "company_id": "companyId",
            "peak_hours": "peakHours",
            "offpeak_hours": "offpeakHours",
        }
