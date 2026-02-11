from datetime import datetime
from typing import Callable

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_change

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.apps.home_assistant.home_assistant_module import VoltalisHomeAssistantModule
from custom_components.voltalis.lib.domain.energy_contracts.live_consumption import VoltalisLiveConsumption


class VoltalisLiveConsumptionCoordinator(BaseVoltalisCoordinator[dict[int, VoltalisLiveConsumption]]):
    """Coordinator to manage real-time consumption data for a Voltalis."""

    def __init__(
        self,
        *,
        voltalis_module: VoltalisHomeAssistantModule,
    ) -> None:
        # No automatic update_interval - updates only triggered by time tracker
        super().__init__(
            "Voltalis Live Consumption",
            voltalis_module=voltalis_module,
        )
        self.__stop_time_tracking: Callable[[], None] | None = None

    def start_time_tracking(self) -> None:
        """Start tracking time to trigger updates at specific minutes."""
        if self.__stop_time_tracking:
            return

        self.__stop_time_tracking = async_track_time_change(
            self.hass,
            self.__scheduled_update,
            # Update every 10 minutes (HH:00, HH:10, HH:20, HH:30, HH:40, HH:50)
            minute=[0, 10, 20, 30, 40, 50],
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

    async def _get_data(self) -> dict[int, VoltalisLiveConsumption]:
        """Fetch updated data from the Voltalis API."""

        result = await self._voltalis_module.voltalis_provider.get_live_consumption()
        return {0: result}
