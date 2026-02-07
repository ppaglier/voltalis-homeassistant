import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.voltalis.lib.application.providers.date_provider import DateProvider
from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.models.energy_contract import VoltalisEnergyContract

_LOGGER = logging.getLogger(__name__)


class VoltalisEnergyContractCoordinator(BaseVoltalisCoordinator[dict[int, VoltalisEnergyContract]]):
    """Coordinator to fetch energy contracts from Voltalis API."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        voltalis_repository: VoltalisRepository,
        entry: ConfigEntry,  # ConfigEntry reference used for reauth triggering
        date_provider: DateProvider,
    ) -> None:
        super().__init__(
            "Voltalis Energy Contract",
            hass=hass,
            logger=_LOGGER,
            voltalis_repository=voltalis_repository,
            entry=entry,
            update_interval=timedelta(days=1),
        )
        self.__date_provider = date_provider

    async def _get_data(self) -> dict[int, VoltalisEnergyContract]:
        """Fetch updated data from the Voltalis API."""

        # Fetch energy contracts
        result = await self._voltalis_repository.get_energy_contracts()

        return result

    def get_current_energy_contract(self) -> VoltalisEnergyContract | None:
        """Get the currently active energy contract, if any."""
        if self.data is None:
            return None

        now = self.__date_provider.get_now().date()
        for energy_contract in self.data.values():
            if energy_contract.end_date is None or now <= energy_contract.end_date:
                return energy_contract

        return None
