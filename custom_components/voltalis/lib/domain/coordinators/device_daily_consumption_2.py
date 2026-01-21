import asyncio
import logging
from typing import cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.voltalis.lib.application.providers.date_provider import DateProvider
from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceDailyConsumptionCoordinator2(BaseVoltalisCoordinator[dict[int, float]]):
    """Coordinator to manage daily device consumption data from Voltalis API."""

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
            "Voltalis Device Daily Consumption 2",
            hass=hass,
            logger=_LOGGER,
            voltalis_repository=voltalis_repository,
            entry=entry,
        )

        self.__date_provider = date_provider

    async def _get_data(self) -> dict[int, float]:
        """Fetch updated data from the Voltalis API."""

        target_datetime = self.__date_provider.get_now()
        devices = cast(dict[int, VoltalisDevice] | None, self._entry.runtime_data.coordinators.device.data)
        # Retry once after a short delay if devices are not yet available
        if devices is None:
            await asyncio.sleep(5)
            return await self._get_data()
        result = await self._voltalis_repository.get_devices_daily_consumptions_2(target_datetime, devices)
        return result
