import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice, VoltalisDeviceTypeEnum

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceCoordinator(BaseVoltalisCoordinator[dict[int, VoltalisDevice]]):
    """Coordinator to fetch devices from Voltalis API."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        voltalis_repository: VoltalisRepository,
        entry: ConfigEntry,  # ConfigEntry reference used for reauth triggering
    ) -> None:
        super().__init__(
            "Voltalis Device",
            hass=hass,
            logger=_LOGGER,
            voltalis_repository=voltalis_repository,
            entry=entry,
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self) -> dict[int, VoltalisDevice]:
        """Fetch updated data from the Voltalis API."""

        try:
            self.logger.debug("Fetching Voltalis devices data...")

            # Fetch devices, health, consumptions, and manual settings
            devices = await self._voltalis_repository.get_devices()

            result: dict[int, VoltalisDevice] = {}

            for device_id, device in devices.items():
                if device.type not in [VoltalisDeviceTypeEnum.HEATER, VoltalisDeviceTypeEnum.WATER_HEATER]:
                    self.logger.debug(f"Skipping unsupported device type: {device.type}")
                    continue

                result[device_id] = device

            self.logger.debug("Fetched %d devices from Voltalis", len(result))

            self._handle_after_update()
            return result

        except Exception as err:
            raise self._handle_update_error(err) from err
