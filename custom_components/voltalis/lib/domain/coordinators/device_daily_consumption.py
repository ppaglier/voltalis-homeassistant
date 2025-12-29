import logging
from datetime import datetime, timedelta
from typing import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change

from custom_components.voltalis.lib.application.providers.date_provider import DateProvider
from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceDailyConsumptionCoordinator(BaseVoltalisCoordinator[dict[int, float]]):
    """Coordinator to manage daily device consumption data from Voltalis API."""

    # Minutes offset after the hour to launch the update (e.g., 5 = HH:05)
    MINUTE_OFFSET = 5

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        voltalis_repository: VoltalisRepository,
        date_provider: DateProvider,
        entry: ConfigEntry,
    ) -> None:
        # No automatic update_interval - updates only triggered by time tracker
        super().__init__(
            "Voltalis Device Consumption",
            hass=hass,
            logger=_LOGGER,
            voltalis_repository=voltalis_repository,
            entry=entry,
        )

        self.__date_provider = date_provider
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

    async def _get_data(self) -> dict[int, float]:
        """Fetch updated data from the Voltalis API."""

        # We remove 1 hour because we can't fetch data from the current hour
        target_datetime = self.__date_provider.get_now() - timedelta(hours=1)
        result = await self._voltalis_repository.get_devices_daily_consumptions(target_datetime)
        return result
