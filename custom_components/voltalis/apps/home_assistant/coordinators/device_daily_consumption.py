from datetime import datetime
from typing import Callable

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_change

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.apps.home_assistant.home_assistant_module import VoltalisHomeAssistantModule
from custom_components.voltalis.lib.domain.devices_management.consumption.device_consumption import (
    VoltalisDeviceConsumption,
)


class VoltalisDeviceDailyConsumptionCoordinator(BaseVoltalisCoordinator[dict[int, VoltalisDeviceConsumption]]):
    """Coordinator to manage daily device consumption data from Voltalis API."""

    # Minutes offset after the hour to launch the update (e.g., 5 = HH:05)
    MINUTE_OFFSET = 5

    def __init__(
        self,
        *,
        voltalis_module: VoltalisHomeAssistantModule,
    ) -> None:
        # No automatic update_interval - updates only triggered by time tracker
        super().__init__(
            "Voltalis Device Daily Consumption",
            voltalis_module=voltalis_module,
        )

        self.__stop_time_tracking: Callable[[], None] | None = None

    def start_time_tracking(self) -> None:
        """Start tracking time to trigger updates at specific minutes."""
        if self.__stop_time_tracking:
            return
        # Schedule updates every hour at MINUTE_OFFSET minutes (e.g., HH:05)
        self.__stop_time_tracking = async_track_time_change(
            self.hass,
            self.__scheduled_update,
            minute=VoltalisDeviceDailyConsumptionCoordinator.MINUTE_OFFSET,
            second=0,
        )

    def stop_time_tracking(self) -> None:
        """Stop the time tracking."""
        if not self.__stop_time_tracking:
            return

        self.__stop_time_tracking()
        self.__stop_time_tracking = None

    @callback
    def __scheduled_update(self, scheduled_at: datetime) -> None:
        """Triggered by time tracker at the scheduled time."""
        # Request a refresh (will call _async_update_data)
        self.hass.async_create_task(self.async_request_refresh())

    async def _get_data(self) -> dict[int, VoltalisDeviceConsumption]:
        """Fetch updated data from the Voltalis API."""

        data = await self._voltalis_module.get_devices_daily_consumption_handler.handle()
        return data
