import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

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
    ) -> None:
        super().__init__(
            "Voltalis Energy Contract",
            hass=hass,
            logger=_LOGGER,
            voltalis_repository=voltalis_repository,
            entry=entry,
            update_interval=timedelta(days=1),
        )

    async def _get_data(self) -> dict[int, VoltalisEnergyContract]:
        """Fetch updated data from the Voltalis API."""

        # Fetch energy contracts
        result = await self._voltalis_repository.get_energy_contracts()

        return result
