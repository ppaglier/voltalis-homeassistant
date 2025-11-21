import logging
from datetime import timedelta

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.voltalis.lib.application.date_provider import DateProvider
from custom_components.voltalis.lib.application.voltalis_client import VoltalisClient
from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.exceptions import (
    VoltalisAuthenticationException,
    VoltalisException,
    VoltalisValidationException,
)
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice, VoltalisDeviceTypeEnum
from custom_components.voltalis.lib.domain.models.device_health import VoltalisDeviceHealth
from custom_components.voltalis.lib.domain.models.manual_setting import VoltalisManualSetting
from custom_components.voltalis.lib.domain.models.subscriber_contract import VoltalisSubscriberContract

_LOGGER = logging.getLogger(__name__)


class VoltalisCoordinatorData(CustomModel):
    """Class that represent the data of the coordinator"""

    device: VoltalisDevice
    consumption: float | None = None
    health: VoltalisDeviceHealth | None = None
    manual_setting: VoltalisManualSetting | None = None


class VoltalisCoordinator(DataUpdateCoordinator[dict[int, VoltalisCoordinatorData]]):
    """Coordinator to fetch data from Voltalis API.

    Handles transition logging (down/up) and triggers a reauthentication flow
    on authentication failures.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        client: VoltalisClient,
        date_provider: DateProvider,
        *,
        entry: ConfigEntry,  # ConfigEntry reference used for reauth triggering
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Voltalis",
            update_interval=timedelta(minutes=1),
        )
        self.__client = client
        self.__date_provider = date_provider
        self.__entry = entry
        self._was_unavailable = False  # Track previous availability state for one-shot logging
        self.__contracts: list[VoltalisSubscriberContract] | None = None  # Store contracts separately

    @property
    def client(self) -> VoltalisClient:
        """Expose the client for service calls."""
        return self.__client

    @property
    def contracts(self) -> list[VoltalisSubscriberContract]:
        """Get cached subscriber contracts."""
        return self.__contracts or []

    async def async_fetch_contracts(self) -> None:
        """Fetch subscriber contracts (called once at setup or manually via service)."""
        try:
            _LOGGER.debug("Fetching Voltalis subscriber contracts...")
            self.__contracts = await self.__client.get_subscriber_contracts()
            _LOGGER.info("Fetched %d subscriber contracts from Voltalis", len(self.__contracts))
        except VoltalisAuthenticationException as err:
            _LOGGER.error("Voltalis authentication failed while fetching contracts: %s", err)
            raise
        except VoltalisValidationException as err:
            _LOGGER.error("Voltalis contract data validation error: %s", err)
            raise
        except VoltalisException as err:
            _LOGGER.error("Voltalis API error while fetching contracts: %s", err)
            raise
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Unexpected error while fetching Voltalis contracts")
            raise

    async def _async_update_data(self) -> dict[int, VoltalisCoordinatorData]:
        """Fetch updated data from the Voltalis API."""
        try:
            _LOGGER.debug("Fetching Voltalis data...")

            # Fetch devices, health, consumptions, and manual settings
            devices = await self.__client.get_devices()
            devices_health = await self.__client.get_devices_health()
            manual_settings = await self.__client.get_manual_settings()

            # We remove 1 hour because we can't fetch data from the current our
            target_datetime = self.__date_provider.get_now() - timedelta(hours=1)
            consumptions = await self.__client.get_devices_consumptions(target_datetime)

            result: dict[int, VoltalisCoordinatorData] = {}

            for device_id, device in devices.items():
                if device.type not in [VoltalisDeviceTypeEnum.HEATER, VoltalisDeviceTypeEnum.WATER_HEATER]:
                    _LOGGER.debug(f"Skipping unsupported device type: {device.type}")
                    continue

                result[device_id] = VoltalisCoordinatorData(
                    device=device,
                    consumption=consumptions.get(device_id, None),
                    health=devices_health.get(device_id, None),
                    manual_setting=manual_settings.get(device_id, None),
                )

            _LOGGER.debug("Fetched %d devices from Voltalis", len(result))

            # Log recovery once if we were previously unavailable
            if self._was_unavailable:
                _LOGGER.info("Voltalis API back online")
                self._was_unavailable = False
            return result

        except VoltalisAuthenticationException as err:
            if not self._was_unavailable:
                _LOGGER.error("Voltalis authentication failed: %s", err)
                self._was_unavailable = True
                # Trigger reauth flow
                # Manually start a reauthentication flow
                self.hass.async_create_task(
                    self.hass.config_entries.flow.async_init(
                        self.__entry.domain,
                        context={
                            "source": config_entries.SOURCE_REAUTH,
                            "entry_id": self.__entry.entry_id,
                        },
                        data=self.__entry.data,
                    )
                )
            raise UpdateFailed("Authentication failed") from err

        except VoltalisValidationException as err:
            if not self._was_unavailable:
                _LOGGER.error("Voltalis data validation error: %s", err)
                self._was_unavailable = True
            raise UpdateFailed("Voltalis data validation error") from err

        except VoltalisException as err:
            if not self._was_unavailable:
                _LOGGER.error("Voltalis API error: %s", err)
                self._was_unavailable = True
            raise UpdateFailed("Voltalis API error") from err

        except Exception as err:  # noqa: BLE001
            if not self._was_unavailable:
                _LOGGER.exception("Unexpected error while updating Voltalis data")
                self._was_unavailable = True
            raise UpdateFailed(f"Unexpected error: {err}") from err
