import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.voltalis.lib.application.providers.date_provider import DateProvider
from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice, VoltalisDeviceTypeEnum
from custom_components.voltalis.lib.domain.models.device_health import VoltalisDeviceHealth
from custom_components.voltalis.lib.domain.models.manual_setting import VoltalisManualSetting


class VoltalisCoordinatorData(CustomModel):
    """Class that represent the data of the coordinator"""

    device: VoltalisDevice
    consumption: float | None = None
    health: VoltalisDeviceHealth | None = None
    manual_setting: VoltalisManualSetting | None = None


_LOGGER = logging.getLogger(__name__)


class VoltalisCoordinator(BaseVoltalisCoordinator[dict[int, VoltalisCoordinatorData]]):
    """Coordinator fetching manual settings every minute."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        voltalis_repository: VoltalisRepository,
        date_provider: DateProvider,
        entry: ConfigEntry,  # ConfigEntry reference used for reauth triggering
    ) -> None:
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            voltalis_repository=voltalis_repository,
            date_provider=date_provider,
            entry=entry,
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self) -> dict[int, VoltalisCoordinatorData]:
        """Fetch updated data from the Voltalis API."""
        try:
            self.logger.debug("Fetching Voltalis data...")

            # Fetch devices, health, consumptions, and manual settings
            devices = await self._voltalis_repository.get_devices()
            devices_health = await self._voltalis_repository.get_devices_health()
            manual_settings = await self._voltalis_repository.get_manual_settings()

            # We remove 1 hour because we can't fetch data from the current our
            target_datetime = self._date_provider.get_now() - timedelta(hours=1)
            consumptions = await self._voltalis_repository.get_devices_consumptions(target_datetime)

            result: dict[int, VoltalisCoordinatorData] = {}

            for device_id, device in devices.items():
                if device.type not in [VoltalisDeviceTypeEnum.HEATER, VoltalisDeviceTypeEnum.WATER_HEATER]:
                    self.logger.debug(f"Skipping unsupported device type: {device.type}")
                    continue

                result[device_id] = VoltalisCoordinatorData(
                    device=device,
                    consumption=consumptions.get(device_id, None),
                    health=devices_health.get(device_id, None),
                    manual_setting=manual_settings.get(device_id, None),
                )

            self.logger.debug("Fetched %d devices from Voltalis", len(result))

            self._handle_after_update()
            return result

        except Exception as err:
            raise self._handle_update_error(err) from err
