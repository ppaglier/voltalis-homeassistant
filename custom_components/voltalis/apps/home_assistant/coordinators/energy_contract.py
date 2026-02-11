from datetime import timedelta

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.apps.home_assistant.home_assistant_module import VoltalisHomeAssistantModule
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import VoltalisEnergyContract


class VoltalisEnergyContractCoordinator(BaseVoltalisCoordinator[dict[int, VoltalisEnergyContract]]):
    """Coordinator to fetch energy contracts from Voltalis API."""

    def __init__(
        self,
        *,
        voltalis_module: VoltalisHomeAssistantModule,
    ) -> None:
        super().__init__(
            "Voltalis Energy Contract",
            voltalis_module=voltalis_module,
            update_interval=timedelta(days=1),
        )

    async def _get_data(self) -> dict[int, VoltalisEnergyContract]:
        """Fetch updated data from the Voltalis API."""

        # Fetch energy contracts
        result = await self._voltalis_module.voltalis_provider.get_energy_contracts()

        return result

    def get_current_energy_contract(self) -> VoltalisEnergyContract | None:
        """Get the currently active energy contract, if any."""
        if self.data is None:
            return None

        now = self._voltalis_module.date_provider.get_now().date()
        for energy_contract in self.data.values():
            if energy_contract.end_date is None or now <= energy_contract.end_date:
                return energy_contract

        return None
