from abc import ABC, abstractmethod
from datetime import datetime

from custom_components.voltalis.lib.domain.models.device import VoltalisDevice
from custom_components.voltalis.lib.domain.models.device_health import VoltalisDeviceHealth
from custom_components.voltalis.lib.domain.models.manual_setting import (
    VoltalisManualSetting,
    VoltalisManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.models.program import VoltalisProgram


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

    # -------------------------------------------------------------------------
    # Programs
    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_programs(self) -> dict[int, VoltalisProgram]:
        """Get all programs (USER + DEFAULT) from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_user_program(self, program_id: int) -> VoltalisProgram:
        """Get a single user program by ID"""
        ...

    @abstractmethod
    async def get_default_programs(self) -> dict[int, VoltalisProgram]:
        """Get all default programs (quicksettings) from the Voltalis servers"""
        ...

    @abstractmethod
    async def set_user_program_state(self, program_id: int, name: str, enabled: bool) -> None:
        """Set the enabled state of a user program

        Args:
            program_id: The ID of the program
            name: The name of the program (required for user programs)
            enabled: The new enabled state
        """
        ...

    @abstractmethod
    async def set_default_program_state(self, program_id: int, enabled: bool) -> None:
        """Set the enabled state of a default program

        Args:
            program_id: The ID of the program
            enabled: The new enabled state
        """
        ...
