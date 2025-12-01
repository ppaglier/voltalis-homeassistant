import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.models.manual_setting import VoltalisManualSetting

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceSettingsCoordinator(BaseVoltalisCoordinator[dict[int, VoltalisManualSetting]]):
    """Coordinator to fetch devices settings from Voltalis API."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        voltalis_repository: VoltalisRepository,
        entry: ConfigEntry,  # ConfigEntry reference used for reauth triggering
    ) -> None:
        super().__init__(
            "Voltalis Device Settings",
            hass=hass,
            logger=_LOGGER,
            voltalis_repository=voltalis_repository,
            entry=entry,
            update_interval=timedelta(minutes=1),
        )

    @property
    def voltalis_repository(self) -> VoltalisRepository:
        """Get the Voltalis repository."""
        return self._voltalis_repository

    async def _async_update_data(self) -> dict[int, VoltalisManualSetting]:
        """Fetch updated data from the Voltalis API."""

        try:
            self.logger.debug("Fetching Voltalis devices data...")

            result = await self._voltalis_repository.get_manual_settings()

            self._handle_after_update()
            return result

        except Exception as err:
            raise self._handle_update_error(err) from err
