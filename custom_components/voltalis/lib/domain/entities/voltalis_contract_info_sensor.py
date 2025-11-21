import logging

from homeassistant.components.sensor import SensorEntity

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.models.subscriber_contract import VoltalisSubscriberContract
from custom_components.voltalis.lib.domain.voltalis_contract_entity import VoltalisContractEntity

_LOGGER = logging.getLogger(__name__)


class VoltalisContractInfoSensor(VoltalisContractEntity, SensorEntity):
    """Sensor entity for Voltalis subscriber contract information."""

    _attr_translation_key = "contract_info"
    _unique_id_suffix = "contract_info"
    _attr_icon = "mdi:file-document-outline"

    def __init__(self, entry: VoltalisConfigEntry, contract: VoltalisSubscriberContract) -> None:
        """Initialize the contract info sensor."""
        super().__init__(entry, contract)
        self._update_state()

    def _update_state(self) -> None:
        """Update the state of the sensor."""
        # The native value is the contract name
        self._attr_native_value = self._contract.name

        # Extra state attributes contain all the contract details
        self._attr_extra_state_attributes = {
            "contract_id": self._contract.id,
            "company_name": self._contract.company_name,
            "subscribed_power": self._contract.subscribed_power,
            "is_peak_offpeak_contract": self._contract.is_peak_offpeak_contract,
            "is_default": self._contract.is_default,
            "start_date": self._contract.start_date,
            "end_date": self._contract.end_date,
            "subscription_base_price": self._contract.subscription_base_price,
            "subscription_peak_and_offpeak_hour_base_price":
            self._contract.subscription_peak_and_offpeak_hour_base_price,
            "kwh_base_price": self._contract.kwh_base_price,
            "kwh_peak_hour_price": self._contract.kwh_peak_hour_price,
            "kwh_offpeak_hour_price": self._contract.kwh_offpeak_hour_price,
            "peak_hours": [{"from": hour.from_time, "to": hour.to_time} for hour in self._contract.peak_hours],
            "offpeak_hours": [{"from": hour.from_time, "to": hour.to_time} for hour in self._contract.offpeak_hours],
        }
