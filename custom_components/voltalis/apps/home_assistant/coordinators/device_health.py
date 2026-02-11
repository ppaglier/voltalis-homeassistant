from datetime import timedelta

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.apps.home_assistant.home_assistant_module import VoltalisHomeAssistantModule
from custom_components.voltalis.lib.domain.devices_management.health.device_health import VoltalisDeviceHealth


class VoltalisDeviceHealthCoordinator(BaseVoltalisCoordinator[dict[int, VoltalisDeviceHealth]]):
    """Coordinator to fetch devices health from Voltalis API."""

    def __init__(
        self,
        *,
        voltalis_module: VoltalisHomeAssistantModule,
    ) -> None:
        super().__init__(
            "Voltalis Device Health",
            voltalis_module=voltalis_module,
            update_interval=timedelta(minutes=1),
        )

    async def _get_data(self) -> dict[int, VoltalisDeviceHealth]:
        """Fetch updated data from the Voltalis API."""

        result = await self._voltalis_module.voltalis_provider.get_devices_health()
        return result
