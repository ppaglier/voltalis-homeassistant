from datetime import datetime

from custom_components.voltalis.lib.domain.devices_management.climate.manual_setting import (
    ManualSetting,
    ManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.devices_management.consumption.device_consumption import (
    DeviceConsumption,
)
from custom_components.voltalis.lib.domain.devices_management.device.device import Device
from custom_components.voltalis.lib.domain.devices_management.health.device_health import DeviceHealth
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract
from custom_components.voltalis.lib.domain.energy_contracts.live_consumption import LiveConsumption
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider
from custom_components.voltalis.lib.domain.voltalis_programs_management.programs.program import Program
from custom_components.voltalis.lib.infrastructure.helpers.get_consumption_for_hour import get_consumption_for_hour


class VoltalisProviderStub(VoltalisProvider):
    """Stub implementation of the VoltalisProvider for testing purposes."""

    def __init__(self) -> None:
        self.__devices: dict[int, Device] = {}
        self.__devices_health: dict[int, DeviceHealth] = {}
        self.__live_consumption = LiveConsumption(consumption=0.0)
        self.__devices_consumptions: dict[int, list[tuple[datetime, float]]] = {}
        self.__manual_settings: dict[int, ManualSetting] = {}
        self.__energy_contracts: dict[int, EnergyContract] = {}
        self.__programs: dict[int, Program] = {}

    def set_devices(self, devices: dict[int, Device]) -> None:
        self.__devices = devices

    def set_devices_health(self, devices_health: dict[int, DeviceHealth]) -> None:
        self.__devices_health = devices_health

    def set_live_consumption(self, consumption: LiveConsumption) -> None:
        self.__live_consumption = consumption

    def set_devices_consumptions(self, devices_consumptions: dict[int, list[tuple[datetime, float]]]) -> None:
        self.__devices_consumptions = devices_consumptions

    def set_manual_settings(self, manual_settings: dict[int, ManualSetting]) -> None:
        self.__manual_settings = manual_settings

    def set_current_energy_contract(self, energy_contracts: dict[int, EnergyContract]) -> None:
        self.__energy_contracts = energy_contracts

    def set_programs(self, programs: dict[int, Program]) -> None:
        self.__programs = programs

    # ------------------------------------------------------------
    # Implementation of VoltalisProvider methods
    # ------------------------------------------------------------

    async def get_devices(self) -> dict[int, Device]:
        return self.__devices

    async def get_devices_health(self) -> dict[int, DeviceHealth]:
        return self.__devices_health

    async def get_live_consumption(self) -> LiveConsumption:
        return self.__live_consumption

    async def get_devices_daily_consumptions(self, target_datetime: datetime) -> dict[int, DeviceConsumption]:
        consumptions = {
            device_id: DeviceConsumption(
                daily_consumption=get_consumption_for_hour(
                    consumptions=consumption_records, target_datetime=target_datetime
                )
            )
            for device_id, consumption_records in self.__devices_consumptions.items()
        }
        return consumptions

    async def get_manual_settings(self) -> dict[int, ManualSetting]:
        return self.__manual_settings

    async def set_manual_setting(self, manual_setting_id: int, setting: ManualSettingUpdate) -> None:
        existing_setting = self.__manual_settings[manual_setting_id]
        updated_setting = existing_setting.model_copy(update=setting.model_dump(exclude_unset=True))
        self.__manual_settings[manual_setting_id] = updated_setting

    async def get_energy_contracts(self) -> dict[int, EnergyContract]:
        return self.__energy_contracts

    async def get_programs(self) -> dict[int, Program]:
        return self.__programs

    async def toggle_program(self, program: Program) -> None:
        self.__programs[program.id].enabled = program.enabled
