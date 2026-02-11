from datetime import datetime
from typing import Callable

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy
from homeassistant.helpers.event import async_track_time_change

from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_energy_contract_entity import (
    VoltalisEnergyContractEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.apps.home_assistant.entities.energy_contract.current_mode_sensor import (
    EnergyContractCurrentModeEnum,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import (
    EnergyContract,
    EnergyContractTypeEnum,
)
from custom_components.voltalis.lib.domain.energy_contracts.helpers.is_in_time_range import is_in_time_range


class VoltalisEnergyContractKwhCurrentCostSensor(VoltalisEnergyContractEntity, SensorEntity):
    """Sensor entity for Voltalis energy contract kWh current cost."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"
    _attr_translation_key = "energy_contract_kwh_current_cost"
    _attr_icon = "mdi:currency-eur"
    _unique_id_suffix = "energy_contract_kwh_current_cost"

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        energy_contract: EnergyContract,
    ) -> None:
        """Initialize the energy contract kWh current cost sensor."""
        super().__init__(
            entry, energy_contract, entry.runtime_data.voltalis_home_assistant_module.energy_contract_coordinator
        )
        self.__date_provider = self._voltalis_module.date_provider
        self.__current_mode: EnergyContractCurrentModeEnum | None = None
        self.__unsub: Callable | None = None

    @property
    def icon(self) -> str:
        """Return the icon to use for this entity."""
        if self.__current_mode is None:
            return "mdi:gauge-empty"
        if self.__current_mode == EnergyContractCurrentModeEnum.PEAK:
            return "mdi:gauge-full"
        if self.__current_mode == EnergyContractCurrentModeEnum.OFFPEAK:
            return "mdi:gauge-low"
        return "mdi:gauge"

    async def __update(self, _: datetime) -> None:
        energy_contract = self._voltalis_module.energy_contract_coordinator.data.get(self._energy_contract.id)
        if energy_contract is None:
            self._voltalis_module.logger.warning("Energy contract with id %s is None", self._energy_contract.id)
            return

        current_mode: EnergyContractCurrentModeEnum | None = None
        if energy_contract.type == EnergyContractTypeEnum.BASE:
            current_mode = EnergyContractCurrentModeEnum.BASE
        else:
            now = self.__date_provider.get_now().time()
            in_off_peak = any(is_in_time_range(time_range, now) for time_range in energy_contract.offpeak_hours)
            current_mode = EnergyContractCurrentModeEnum.OFFPEAK if in_off_peak else EnergyContractCurrentModeEnum.PEAK

        new_value: float | None = None
        if current_mode == EnergyContractCurrentModeEnum.BASE:
            new_value = energy_contract.prices.kwh_base
        elif current_mode == EnergyContractCurrentModeEnum.PEAK:
            new_value = energy_contract.prices.kwh_peak
        elif current_mode == EnergyContractCurrentModeEnum.OFFPEAK:
            new_value = energy_contract.prices.kwh_offpeak

        self.__current_mode = current_mode

        if new_value is None or self._attr_native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        # Start periodic updates every minute
        self.__unsub = async_track_time_change(
            self.hass,
            self.__update,
            second=0,  # Start every minute at second 0
        )

        await self.__update(self.__date_provider.get_now())

    async def async_will_remove_from_hass(self) -> None:
        if self.__unsub:
            self.__unsub()
            self.__unsub = None

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: EnergyContract) -> bool:
        if data.type == EnergyContractTypeEnum.BASE:
            return data.prices.kwh_base is not None
        return data.prices.kwh_peak is not None or data.prices.kwh_offpeak is not None
