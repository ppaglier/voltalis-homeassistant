import logging
from datetime import timedelta
from typing import cast

from homeassistant.core import HomeAssistant

from custom_components.voltalis.lib.application.providers.date_provider import DateProvider
from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
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
        entry: "VoltalisConfigEntry",
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

        # We remove 1 hour because we can't fetch data from the current hour
        target_datetime = self.__date_provider.get_now() - timedelta(hours=1)
        devices = cast(dict[int, VoltalisDevice], self._entry.runtime_data.coordinators.device.data)
        result = await self._voltalis_repository.get_devices_daily_consumptions_2(target_datetime, devices)
        return result
