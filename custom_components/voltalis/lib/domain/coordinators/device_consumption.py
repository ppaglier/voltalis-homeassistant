import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.voltalis.lib.application.providers.date_provider import DateProvider
from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceConsumptionCoordinator(BaseVoltalisCoordinator[dict[int, float]]):
    """Coordinator to fetch devices consumptions from Voltalis API at specific hours."""

    INTERVAL = timedelta(hours=1)
    # Minutes offset after the hour to launch the update (e.g., 5 = HH:05)
    MINUTE_OFFSET = 5

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        voltalis_repository: VoltalisRepository,
        date_provider: DateProvider,
        entry: ConfigEntry,  # ConfigEntry reference used for reauth triggering
    ) -> None:
        super().__init__(
            "Voltalis Device Consumption",
            hass=hass,
            logger=_LOGGER,
            voltalis_repository=voltalis_repository,
            entry=entry,
            # Start immediately at initialization
            update_interval=timedelta(seconds=30),  # Will be recalculated after first update
        )

        self.__date_provider = date_provider

    def _calculate_next_update_interval(self) -> timedelta:
        """Calculate time until next hour + minute offset."""
        now = self.__date_provider.get_now()

        # Next hour at HH:MM (e.g., 15:05)
        next_update = (now + VoltalisDeviceConsumptionCoordinator.INTERVAL).replace(
            minute=VoltalisDeviceConsumptionCoordinator.MINUTE_OFFSET,
            second=0,
            microsecond=0,
        )

        # If we're past the target minute in current hour, schedule for next hour
        if now.minute >= VoltalisDeviceConsumptionCoordinator.MINUTE_OFFSET and next_update <= now:
            next_update += VoltalisDeviceConsumptionCoordinator.INTERVAL

        delay = next_update - now
        self.logger.debug(
            "Next consumption update scheduled at %s (in %s)",
            next_update.strftime("%H:%M:%S"),
            delay,
        )
        return delay

    async def _get_data(self) -> dict[int, float]:
        """Fetch updated data from the Voltalis API."""

        # We remove 1 hour because we can't fetch data from the current hour
        target_datetime = self.__date_provider.get_now() - timedelta(hours=1)
        result = await self._voltalis_repository.get_devices_consumptions(target_datetime)

        return result
