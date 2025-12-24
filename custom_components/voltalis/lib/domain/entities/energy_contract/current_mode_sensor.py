import logging
from datetime import datetime
from enum import StrEnum
from typing import Callable

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_time_change

from custom_components.voltalis.lib.application.providers.date_provider import DateProvider
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_energy_contract_entity import (
    VoltalisEnergyContractEntity,
)
from custom_components.voltalis.lib.domain.helpers.is_in_time_range import is_in_time_range
from custom_components.voltalis.lib.domain.models.energy_contract import (
    VoltalisEnergyContract,
    VoltalisEnergyContractTypeEnum,
)

_LOGGER = logging.getLogger(__name__)


class EnergyContractCurrentModeEnum(StrEnum):
    """Voltalis energy contract current mode options."""

    BASE = "base"
    PEAK = "peak"
    OFFPEAK = "offpeak"


class VoltalisEnergyContractCurrentModeSensor(VoltalisEnergyContractEntity, SensorEntity):
    """Sensor entity for Voltalis energy contract current mode."""

    _attr_translation_key = "energy_contract_current_mode"
    _unique_id_suffix = "energy_contract_current_mode"

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        energy_contract: VoltalisEnergyContract,
        date_provider: DateProvider,
    ) -> None:
        """Initialize the energy contract current mode sensor."""
        super().__init__(entry, energy_contract, entry.runtime_data.coordinators.energy_contract)
        self.__date_provider = date_provider
        self.__unsub: Callable | None = None

    @property
    def icon(self) -> str:
        """Return the icon to use for this entity."""
        if self.native_value is None:
            return "mdi:calendar-minus"
        if self.native_value == EnergyContractCurrentModeEnum.BASE:
            return "mdi:sort-calendar-today"
        if self.native_value == EnergyContractCurrentModeEnum.PEAK:
            return "mdi:sort-calendar-descending"
        if self.native_value == EnergyContractCurrentModeEnum.OFFPEAK:
            return "mdi:sort-calendar-ascending"
        return "mdi:calendar-blank-outline"

    async def __update(self, _: datetime) -> None:
        energy_contract = self._coordinators.energy_contract.data.get(self._energy_contract.id)
        if energy_contract is None:
            _LOGGER.warning("Energy contract with id %s is None", self._energy_contract.id)
            return

        new_value: EnergyContractCurrentModeEnum | None = None
        if energy_contract.type == VoltalisEnergyContractTypeEnum.BASE:
            new_value = EnergyContractCurrentModeEnum.BASE
        else:
            now = self.__date_provider.get_now().time()
            in_off_peak = any(is_in_time_range(time_range, now) for time_range in energy_contract.offpeak_hours)
            new_value = EnergyContractCurrentModeEnum.OFFPEAK if in_off_peak else EnergyContractCurrentModeEnum.PEAK

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
    def _is_available_from_data(self, data: VoltalisEnergyContract) -> bool:
        return data.subscribed_power is not None
