from datetime import timedelta

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto
from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting import (
    ManualSettingUpdate,
)


class VoltalisDeviceCoordinator(BaseVoltalisCoordinator[dict[int, DeviceDto]]):
    """Coordinator to fetch devices from Voltalis API."""

    def __init__(
        self,
        *,
        entry: VoltalisConfigEntry,
    ) -> None:
        super().__init__(
            "Voltalis Device",
            entry=entry,
            update_interval=timedelta(minutes=1),
        )

    async def set_manual_setting(self, manual_setting_id: int, settings: ManualSettingUpdate) -> None:
        """Set manual setting for a device."""
        await self._voltalis_module.voltalis_provider.set_manual_setting(manual_setting_id, settings)

    async def _get_data(self) -> dict[int, DeviceDto]:
        """Fetch updated data from the Voltalis API."""

        result = await self._voltalis_module.get_devices_handler.handle()
        return result
