import logging
from datetime import datetime
from typing import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change

from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceRealtimeConsumptionCoordinator(BaseVoltalisCoordinator[dict[int, float]]):
    """Coordinator to manage real-time device consumption data from Voltalis API."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        voltalis_repository: VoltalisRepository,
        entry: ConfigEntry,
        seconds: bool,
    ) -> None:
        # No automatic update_interval - updates only triggered by time tracker
        super().__init__(
            "Voltalis Device Realtime Consumption",
            hass=hass,
            logger=_LOGGER,
            voltalis_repository=voltalis_repository,
            entry=entry,
        )

        self.__seconds = seconds
        self.__stop_time_tracking: Callable[[], None] | None = None

    def start_time_tracking(self) -> None:
        """Start tracking time to trigger updates at specific minutes."""
        if self.__stop_time_tracking:
            return

        self.__stop_time_tracking = async_track_time_change(
            self.hass,
            self.__scheduled_update,
            # Update every 10 minutes (HH:00, HH:10, HH:20, HH:30, HH:40, HH:50)
            minute=[0, 10, 20, 30, 40, 50] if not self.__seconds else None,
            # Update every 10 seconds (0, 10, 20, 30, 40, 50)
            second=[0, 10, 20, 30, 40, 50] if self.__seconds else None,
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

    async def _get_data(self) -> dict[int, float]:
        """Fetch updated data from the Voltalis API."""

        # result = await self._voltalis_repository.get_realtime_consumption()
        return {0: 0.0}  # Placeholder for actual consumption value
