import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.voltalis.lib.application.providers.date_provider import DateProvider
from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceConsumptionCoordinator(BaseVoltalisCoordinator[dict[int, float]]):
    """Coordinator to fetch devices consumptions from Voltalis API."""

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
            update_interval=timedelta(hours=1),
        )
        self.__date_provider = date_provider

    async def _async_update_data(self) -> dict[int, float]:
        """Fetch updated data from the Voltalis API."""

        try:
            self.logger.debug("Fetching Voltalis devices data...")

            # We remove 1 hour because we can't fetch data from the current our
            target_datetime = self.__date_provider.get_now() - timedelta(hours=1)
            result = await self._voltalis_repository.get_devices_consumptions(target_datetime)

            self._handle_after_update()
            return result

        except Exception as err:
            raise self._handle_update_error(err) from err
