import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.devices_management.climate.manual_setting import (
    VoltalisManualSetting,
    VoltalisManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.devices_management.device.device import VoltalisDevice
from custom_components.voltalis.lib.domain.devices_management.device.device_enum import VoltalisDeviceTypeEnum
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceCoordinatorData(VoltalisDevice):
    """Data class to hold device information."""

    manual_setting: VoltalisManualSetting | None = None


class VoltalisDeviceCoordinator(BaseVoltalisCoordinator[dict[int, VoltalisDeviceCoordinatorData]]):
    """Coordinator to fetch devices from Voltalis API."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        voltalis_provider: VoltalisProvider,
        entry: ConfigEntry,  # ConfigEntry reference used for reauth triggering
    ) -> None:
        super().__init__(
            "Voltalis Device",
            hass=hass,
            logger=_LOGGER,
            voltalis_provider=voltalis_provider,
            entry=entry,
            update_interval=timedelta(minutes=1),
        )

    async def set_manual_setting(self, manual_setting_id: int, settings: VoltalisManualSettingUpdate) -> None:
        """Set manual setting for a device."""
        await self._voltalis_provider.set_manual_setting(manual_setting_id, settings)

    async def _get_data(self) -> dict[int, VoltalisDeviceCoordinatorData]:
        """Fetch updated data from the Voltalis API."""

        # Fetch devices and manual settings
        devices = await self._voltalis_provider.get_devices()
        devices_manual_settings = await self._voltalis_provider.get_manual_settings()

        result: dict[int, VoltalisDeviceCoordinatorData] = {}
        for device_id, device in devices.items():
            if device.type not in [VoltalisDeviceTypeEnum.HEATER, VoltalisDeviceTypeEnum.WATER_HEATER]:
                self.logger.debug(f"Skipping unsupported device type: {device.type}")
                continue

            result[device_id] = VoltalisDeviceCoordinatorData(
                **device.model_dump(),
                manual_setting=devices_manual_settings.get(device_id),
            )

        return result
