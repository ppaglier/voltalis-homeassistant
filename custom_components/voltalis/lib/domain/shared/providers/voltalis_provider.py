from abc import ABC, abstractmethod
from datetime import datetime

from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting import (
    ManualSetting,
    ManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.devices_management.consumptions.device_consumption import (
    DeviceConsumption,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device import Device
from custom_components.voltalis.lib.domain.devices_management.health.device_health import DeviceHealth
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract
from custom_components.voltalis.lib.domain.energy_contracts.live_consumption import LiveConsumption
from custom_components.voltalis.lib.domain.voltalis_programs_management.programs.program import Program


class VoltalisProvider(ABC):
    """Provider for Voltalis data access."""

    @abstractmethod
    async def get_devices(self) -> dict[int, Device]:
        """Get devices from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_devices_health(self) -> dict[int, DeviceHealth]:
        """Get devices health from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_live_consumption(self) -> LiveConsumption:
        """Get real-time consumption from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_devices_daily_consumptions(self, target_datetime: datetime) -> dict[int, DeviceConsumption]:
        """Get devices daily consumptions from the Voltalis servers for a specific datetime"""
        ...

    @abstractmethod
    async def get_manual_settings(self) -> dict[int, ManualSetting]:
        """Get manual settings for all devices from the Voltalis servers"""
        ...

    @abstractmethod
    async def set_manual_setting(self, manual_setting_id: int, setting: ManualSettingUpdate) -> None:
        """Set manual setting for a device on the Voltalis servers

        Args:
            manual_setting_id: The ID of the manual setting (not the appliance ID)
            setting: The manual setting update to apply
        """
        ...

    @abstractmethod
    async def get_energy_contracts(self) -> dict[int, EnergyContract]:
        """Get energy contracts from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_programs(self) -> dict[int, Program]:
        """Get programs from the Voltalis servers"""
        ...

    @abstractmethod
    async def toggle_program(self, program: Program) -> None:
        """Enable or disable a program on the Voltalis servers
        Args:
            program: The program to enable or disable
        """
        ...
