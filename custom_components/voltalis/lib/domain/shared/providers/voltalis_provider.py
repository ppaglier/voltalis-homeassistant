from abc import ABC, abstractmethod
from datetime import datetime

from custom_components.voltalis.lib.domain.devices_management.climate.manual_setting import (
    VoltalisManualSetting,
    VoltalisManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.devices_management.consumption.device_consumption import (
    VoltalisDeviceConsumption,
)
from custom_components.voltalis.lib.domain.devices_management.device.device import VoltalisDevice
from custom_components.voltalis.lib.domain.devices_management.health.device_health import VoltalisDeviceHealth
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import VoltalisEnergyContract
from custom_components.voltalis.lib.domain.energy_contracts.live_consumption import VoltalisLiveConsumption
from custom_components.voltalis.lib.domain.voltalis_programs_management.programs.voltalis_program import VoltalisProgram


class VoltalisProvider(ABC):
    """Provider for Voltalis data access."""

    @abstractmethod
    async def get_devices(self) -> dict[int, VoltalisDevice]:
        """Get devices from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_devices_health(self) -> dict[int, VoltalisDeviceHealth]:
        """Get devices health from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_live_consumption(self) -> VoltalisLiveConsumption:
        """Get real-time consumption from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_devices_daily_consumptions(self, target_datetime: datetime) -> dict[int, VoltalisDeviceConsumption]:
        """Get devices daily consumptions from the Voltalis servers for a specific datetime"""
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
    async def get_energy_contracts(self) -> dict[int, VoltalisEnergyContract]:
        """Get energy contracts from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_programs(self) -> dict[int, VoltalisProgram]:
        """Get programs from the Voltalis servers"""
        ...

    @abstractmethod
    async def toggle_program(self, program: VoltalisProgram) -> None:
        """Enable or disable a program on the Voltalis servers
        Args:
            program: The program to enable or disable
        """
        ...
