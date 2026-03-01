from datetime import timedelta

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.devices_management.health.device_health import DeviceHealth


class VoltalisDeviceHealthCoordinator(BaseVoltalisCoordinator[dict[int, DeviceHealth]]):
    """Coordinator to fetch devices health from Voltalis API."""

    def __init__(
        self,
        *,
        entry: VoltalisConfigEntry,
    ) -> None:
        super().__init__(
            "Voltalis Device Health",
            entry=entry,
            update_interval=timedelta(minutes=1),
        )

    async def _get_data(self) -> dict[int, DeviceHealth]:
        """Fetch updated data from the Voltalis API."""

        result = await self._voltalis_module.get_devices_health_handler.handle()
        return result
