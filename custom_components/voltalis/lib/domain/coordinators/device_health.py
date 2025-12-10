import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.models.device_health import VoltalisDeviceHealth

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceHealthCoordinator(BaseVoltalisCoordinator[dict[int, VoltalisDeviceHealth]]):
    """Coordinator to fetch devices health from Voltalis API."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        voltalis_repository: VoltalisRepository,
        entry: ConfigEntry,  # ConfigEntry reference used for reauth triggering
    ) -> None:
        super().__init__(
            "Voltalis Device Health",
            hass=hass,
            logger=_LOGGER,
            voltalis_repository=voltalis_repository,
            entry=entry,
            update_interval=timedelta(minutes=1),
        )

    async def _get_data(self) -> dict[int, VoltalisDeviceHealth]:
        """Fetch updated data from the Voltalis API."""

        result = await self._voltalis_repository.get_devices_health()
        return result
