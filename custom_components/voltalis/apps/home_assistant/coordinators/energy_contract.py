from datetime import timedelta

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract


class VoltalisEnergyContractCoordinator(BaseVoltalisCoordinator[dict[int, EnergyContract]]):
    """Coordinator to fetch energy contracts from Voltalis API."""

    def __init__(
        self,
        *,
        entry: VoltalisConfigEntry,
    ) -> None:
        super().__init__(
            "Voltalis Energy Contract",
            entry=entry,
            update_interval=timedelta(days=1),
        )

    async def _get_data(self) -> dict[int, EnergyContract]:
        """Fetch updated data from the Voltalis API."""

        # Fetch energy contracts
        energy_contract = await self._voltalis_module.get_current_energy_contract_handler.handle()
        if energy_contract is None:
            return {}

        return {energy_contract.id: energy_contract}
