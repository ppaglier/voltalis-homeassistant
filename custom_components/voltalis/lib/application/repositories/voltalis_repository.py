from abc import ABC, abstractmethod
from datetime import datetime

from custom_components.voltalis.lib.domain.models.device import VoltalisDevice
from custom_components.voltalis.lib.domain.models.device_health import VoltalisDeviceHealth
from custom_components.voltalis.lib.domain.models.energy_contract import VoltalisEnergyContract
from custom_components.voltalis.lib.domain.models.manual_setting import (
    VoltalisManualSetting,
    VoltalisManualSettingUpdate,
)


class VoltalisRepository(ABC):
    """Repository for Voltalis data access."""

    @abstractmethod
    async def get_devices(self) -> dict[int, VoltalisDevice]:
        """Get devices from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_devices_health(self) -> dict[int, VoltalisDeviceHealth]:
        """Get devices health from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_devices_consumptions(self, target_datetime: datetime) -> dict[int, float]:
        """Get devices consumptions from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_manual_settings(self) -> dict[int, VoltalisManualSetting]:
        """Get manual settings for all devices from the Voltalis servers"""
        ...

    @abstractmethod
    async def set_manual_setting(self, manual_setting_id: int, setting: VoltalisManualSettingUpdate) -> None:
        """Set manual setting for a device on the Voltalis servers

        Args:
            manual_setting_id: The ID of the manual setting (not the appliance ID)
            setting: The manual setting update to apply
        """
        ...

    @abstractmethod
    async def get_current_energy_contract(self) -> VoltalisEnergyContract:
        """Get the current energy contract from the Voltalis servers"""
        ...
