import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.voltalis.lib.application.date_provider import DateProvider
from custom_components.voltalis.lib.application.voltalis_client import VoltalisClient
from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.device import VoltalisDevice
from custom_components.voltalis.lib.domain.exceptions import VoltalisAuthenticationException, VoltalisException

_LOGGER = logging.getLogger(__name__)


class VoltalisCoordinatorData(CustomModel):
    """Class that represent the data of the coordinator"""

    device: VoltalisDevice
    consumption: float | None = None
    status: bool | None = None


class VoltalisCoordinator(DataUpdateCoordinator[dict[int, VoltalisCoordinatorData]]):
    """Coordinator to fetch data from Voltalis API."""

    def __init__(self, hass: HomeAssistant, client: VoltalisClient, date_provider: DateProvider) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Voltalis",
            # update_interval=timedelta(hours=1),  # Refresh every hour
            update_interval=timedelta(seconds=30),  # Refresh every hour
        )
        self.__client = client
        self.__date_provider = date_provider

    async def _async_update_data(self) -> dict[int, VoltalisCoordinatorData]:
        """Fetch updated data from the Voltalis API."""
        try:
            _LOGGER.debug("Fetching Voltalis data...")

            # Fetch devices and consumptions
            devices = await self.__client.get_devices()
            devices_health = await self.__client.get_devices_health()

            # We remove 1 hour because we can't fetch data from the current our
            target_datetime = self.__date_provider.get_now() - timedelta(hours=1)
            consumptions = await self.__client.get_devices_consumptions(target_datetime)

            result: dict[int, VoltalisCoordinatorData] = {}

            for device_id, device in devices.items():
                result[device_id] = VoltalisCoordinatorData(
                    device=device,
                    consumption=consumptions.get(device_id, None),
                    status=devices_health.get(device_id, None),
                )

            _LOGGER.debug("Fetched %d devices from Voltalis", len(result))
            return result

        except VoltalisAuthenticationException as err:
            _LOGGER.error("Voltalis authentication failed: %s", err)
            raise UpdateFailed("Authentication failed") from err

        except VoltalisException as err:
            _LOGGER.error("Voltalis API error: %s", err)
            raise UpdateFailed("Voltalis API error") from err

        except Exception as err:  # noqa: BLE001
            _LOGGER.exception("Unexpected error while updating Voltalis data")
            raise UpdateFailed(f"Unexpected error: {err}") from err
