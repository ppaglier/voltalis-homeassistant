import logging
from datetime import timedelta

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.voltalis.lib.application.date_provider import DateProvider
from custom_components.voltalis.lib.application.voltalis_client import VoltalisClient
from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.device import (
    VoltalisApplianceDiagnostic,
    VoltalisConsumptionObjective,
    VoltalisContract,
    VoltalisDevice,
    VoltalisManagedAppliance,
    VoltalisProgram,
    VoltalisRealTimeConsumption,
    VoltalisSiteInfo,
)
from custom_components.voltalis.lib.domain.exceptions import VoltalisAuthenticationException, VoltalisException

_LOGGER = logging.getLogger(__name__)


class VoltalisCoordinatorData(CustomModel):
    """Class that represent the data of the coordinator"""

    device: VoltalisDevice
    consumption: float | None = None
    status: bool | None = None
    consumption_objective: VoltalisConsumptionObjective | None = None
    realtime_consumption: list[VoltalisRealTimeConsumption] | None = None
    current_power: float | None = None  # Current power in Watts from latest realtime data
    programs: list[VoltalisProgram] | None = None

    # Per-appliance detailed data
    managed_appliance: VoltalisManagedAppliance | None = None
    diagnostic: VoltalisApplianceDiagnostic | None = None

    # Site-wide data (cached, same for all devices)
    site_info: VoltalisSiteInfo | None = None
    contracts: list[VoltalisContract] | None = None


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

        # Cache for rarely changing data with timestamps
        self.__cache: dict[str, tuple[any, float]] = {}
        self.__update_counter = 0  # Counter to track update cycles

    async def _async_update_data(self) -> dict[int, VoltalisCoordinatorData]:
        """Fetch updated data from the Voltalis API with intelligent caching."""
        try:
            _LOGGER.debug("Fetching Voltalis data (update #%d)...", self.__update_counter)
            self.__update_counter += 1

            # ALWAYS FETCH (every minute): Real-time and frequently changing data
            devices = await self.__client.get_devices()
            devices_health = await self.__client.get_devices_health()
            realtime_consumptions = await self.__client.get_realtime_consumption(num_points=10)
            managed_appliances = await self.__client.get_managed_appliances()
            diagnostics = await self.__client.get_appliance_diagnostics()

            # We remove 1 hour because we can't fetch data from the current hour
            target_datetime = self.__date_provider.get_now() - timedelta(hours=1)
            consumptions = await self.__client.get_devices_consumptions(target_datetime)

            # HOURLY FETCH: Data that changes occasionally
            # Fetch every 60 updates (60 minutes)
            if self.__update_counter % 60 == 1:
                _LOGGER.debug("Fetching hourly data...")
                consumption_objective = await self.__client.get_consumption_objective()
                programs = await self.__client.get_programs()
                self.__cache["consumption_objective"] = consumption_objective
                self.__cache["programs"] = programs
            else:
                consumption_objective = self.__cache.get("consumption_objective")
                programs = self.__cache.get("programs")

            # DAILY FETCH: Data that rarely changes
            # Fetch every 1440 updates (24 hours)
            if self.__update_counter % 1440 == 1:
                _LOGGER.debug("Fetching daily data...")
                site_info = await self.__client.get_site_info()
                contracts = await self.__client.get_subscriber_contracts()
                self.__cache["site_info"] = site_info
                self.__cache["contracts"] = contracts
            else:
                site_info = self.__cache.get("site_info")
                contracts = self.__cache.get("contracts")

            # Calculate current power from latest realtime consumption
            current_power = None
            if realtime_consumptions:
                # Convert Wh to W by multiplying by 6 (10 minute intervals = 1/6 hour)
                latest = realtime_consumptions[-1]
                current_power = latest.total_consumption_in_wh * 6

            result: dict[int, VoltalisCoordinatorData] = {}

            for device_id, device in devices.items():
                result[device_id] = VoltalisCoordinatorData(
                    device=device,
                    consumption=consumptions.get(device_id, None),
                    status=devices_health.get(device_id, None),
                    consumption_objective=consumption_objective,
                    realtime_consumption=realtime_consumptions,
                    current_power=current_power,
                    programs=programs,
                    managed_appliance=managed_appliances.get(device_id),
                    diagnostic=diagnostics.get(device_id),
                    site_info=site_info,
                    contracts=contracts,
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
