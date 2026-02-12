from datetime import datetime
from typing import Callable

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.event import async_track_time_change

from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_energy_contract_entity import (
    VoltalisEnergyContractEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.application.energy_contracts.handlers.get_energy_contract_current_mode_handler import (  # noqa: E501
    EnergyContractCurrentModeEnum,
)
from custom_components.voltalis.lib.application.energy_contracts.queries.get_energy_contract_current_mode_query import (
    GetEnergyContractCurrentModeQuery,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract


class VoltalisEnergyContractCurrentModeSensor(VoltalisEnergyContractEntity, SensorEntity):
    """Sensor entity for Voltalis energy contract current mode."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = "energy_contract_current_mode"
    _attr_options = [option for option in EnergyContractCurrentModeEnum]
    _unique_id_suffix = "energy_contract_current_mode"

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        energy_contract: EnergyContract,
    ) -> None:
        """Initialize the energy contract current mode sensor."""
        super().__init__(
            entry, energy_contract, entry.runtime_data.voltalis_home_assistant_module.energy_contract_coordinator
        )
        self.__date_provider = self._voltalis_module.date_provider
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
        energy_contract = self._voltalis_module.energy_contract_coordinator.data.get(self._energy_contract.id)
        if energy_contract is None:
            self._voltalis_module.logger.warning("Energy contract with id %s is None", self._energy_contract.id)
            return

        new_value = await self._voltalis_module.get_energy_contract_current_mode_handler.handle(
            GetEnergyContractCurrentModeQuery(type=energy_contract.type, offpeak_hours=energy_contract.offpeak_hours)
        )

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
        return data.subscribed_power is not None
