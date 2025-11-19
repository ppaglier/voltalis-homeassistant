from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from custom_components.voltalis.lib.domain.device import (
    VoltalisDevice,
    VoltalisManualSetting,
    VoltalisManualSettingUpdate,
)


class VoltalisClient(ABC):
    """Create a Voltalis client that will be used to communicate with Voltalis servers."""

    async def __aenter__(self) -> "VoltalisClient":
        """Async enter."""

        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        """Logout after async exit."""
        await self.logout()


    @abstractmethod
    async def login(self) -> None:
        """Login to the Voltalis servers"""
        ...

    @abstractmethod
    async def logout(self) -> None:
        """Logout from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_devices(self) -> dict[int, VoltalisDevice]:
        """Get devices from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_devices_health(self) -> dict[int, bool]:
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
