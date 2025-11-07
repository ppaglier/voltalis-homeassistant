import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.voltalis.lib.application.voltalis_client import VoltalisClient

_LOGGER = logging.getLogger(__name__)


class VoltalisConsumptionCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch consumption data from Voltalis API."""

    def __init__(self, hass: HomeAssistant, client: VoltalisClient) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Voltalis",
            update_interval=timedelta(hours=1),
        )
        self.__client = client

        self.data: dict[int, float] = {}
