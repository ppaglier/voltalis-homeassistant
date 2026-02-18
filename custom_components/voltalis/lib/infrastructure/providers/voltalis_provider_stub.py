from datetime import date, datetime

from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting import (
    ManualSetting,
    ManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device import Device
from custom_components.voltalis.lib.domain.devices_management.health.device_health import DeviceHealth
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract
from custom_components.voltalis.lib.domain.energy_contracts.live_consumption import LiveConsumption
from custom_components.voltalis.lib.domain.programs_management.programs.program import Program
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class VoltalisProviderStub(VoltalisProvider):
    """Stub implementation of the VoltalisProvider for testing purposes."""

    def __init__(self) -> None:
        self._devices: dict[int, Device] = {}
        self._devices_health: dict[int, DeviceHealth] = {}
        self._live_consumption = LiveConsumption(consumption=0.0)
        self._devices_consumptions: dict[int, list[tuple[datetime, float]]] = {}
        self._manual_settings: dict[int, ManualSetting] = {}
        self._energy_contracts: dict[int, EnergyContract] = {}
        self._programs: dict[int, Program] = {}

    def set_devices(self, devices: dict[int, Device]) -> None:
        self._devices = devices

    def set_devices_health(self, devices_health: dict[int, DeviceHealth]) -> None:
        self._devices_health = devices_health

    def set_live_consumption(self, consumption: LiveConsumption) -> None:
        self._live_consumption = consumption

    def set_devices_consumptions(self, devices_consumptions: dict[int, list[tuple[datetime, float]]]) -> None:
        self._devices_consumptions = devices_consumptions

    def set_manual_settings(self, manual_settings: list[ManualSetting]) -> None:
        self._manual_settings = {manual_setting.id: manual_setting for manual_setting in manual_settings}

    def set_energy_contracts(self, energy_contracts: dict[int, EnergyContract]) -> None:
        self._energy_contracts = energy_contracts

    def set_programs(self, programs: dict[int, Program]) -> None:
        self._programs = programs

    # ------------------------------------------------------------
    # Implementation of VoltalisProvider methods
    # ------------------------------------------------------------

    async def get_devices(self) -> dict[int, Device]:
        return self._devices

    async def get_devices_health(self) -> dict[int, DeviceHealth]:
        return self._devices_health

    async def get_live_consumption(self) -> LiveConsumption:
        return self._live_consumption

    async def get_devices_daily_consumptions(self, target_date: date) -> dict[int, list[tuple[datetime, float]]]:
        devices_consumptions = {
            device_id: [
                (consumption_date, consumption_value)
                for (consumption_date, consumption_value) in consumption_records
                if consumption_date.date() == target_date
            ]
            for device_id, consumption_records in self._devices_consumptions.items()
        }
        return devices_consumptions

    async def get_manual_settings(self) -> dict[int, ManualSetting]:
        return {manual_setting.id_appliance: manual_setting for manual_setting in self._manual_settings.values()}

    async def set_manual_setting(self, manual_setting_id: int, setting: ManualSettingUpdate) -> None:
        existing_setting = self._manual_settings[manual_setting_id]
        updated_setting = existing_setting.model_copy(update=setting.model_dump(exclude_unset=True))
        self._manual_settings[manual_setting_id] = updated_setting

    async def get_energy_contracts(self) -> dict[int, EnergyContract]:
        return self._energy_contracts

    async def get_programs(self) -> dict[int, Program]:
        return {
            program_id: program
            for program_id, program in self._programs.items()
            if program.type in [ProgramTypeEnum.USER, ProgramTypeEnum.QUICK]
        }

    async def toggle_program(self, program: Program) -> None:
        self._programs[program.id].enabled = program.enabled
