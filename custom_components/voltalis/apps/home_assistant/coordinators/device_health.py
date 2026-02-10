import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.devices_management.health.device_health import VoltalisDeviceHealth
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceHealthCoordinator(BaseVoltalisCoordinator[dict[int, VoltalisDeviceHealth]]):
    """Coordinator to fetch devices health from Voltalis API."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        voltalis_provider: VoltalisProvider,
        entry: ConfigEntry,  # ConfigEntry reference used for reauth triggering
    ) -> None:
        super().__init__(
            "Voltalis Device Health",
            hass=hass,
            logger=_LOGGER,
            voltalis_provider=voltalis_provider,
            entry=entry,
            update_interval=timedelta(minutes=1),
        )

    async def _get_data(self) -> dict[int, VoltalisDeviceHealth]:
        """Fetch updated data from the Voltalis API."""

        result = await self._voltalis_provider.get_devices_health()
        return result
