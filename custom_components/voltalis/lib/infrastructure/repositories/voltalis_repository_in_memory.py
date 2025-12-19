from datetime import datetime

from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice
from custom_components.voltalis.lib.domain.models.device_health import VoltalisDeviceHealth
from custom_components.voltalis.lib.domain.models.manual_setting import (
    VoltalisManualSetting,
    VoltalisManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.models.program import VoltalisProgram


class VoltalisRepositoryInMemory(VoltalisRepository):
    """In-memory implementation of the VoltalisRepository for testing purposes."""

    def __init__(self) -> None:
        self.__devices: dict[int, VoltalisDevice] = {}
        self.__devices_health: dict[int, VoltalisDeviceHealth] = {}
        self.__devices_consumptions: dict[int, list[tuple[datetime, float]]] = {}
        self.__manual_settings: dict[int, VoltalisManualSetting] = {}
        self.__programs: dict[int, VoltalisProgram] = {}

    def set_devices(self, devices: dict[int, VoltalisDevice]) -> None:
        self.__devices = devices

    def set_devices_health(self, devices_health: dict[int, VoltalisDeviceHealth]) -> None:
        self.__devices_health = devices_health

    def set_devices_consumptions(self, devices_consumptions: dict[int, list[tuple[datetime, float]]]) -> None:
        self.__devices_consumptions = devices_consumptions

    def set_manual_settings(self, manual_settings: dict[int, VoltalisManualSetting]) -> None:
        self.__manual_settings = manual_settings

    def set_programs(self, programs: dict[int, VoltalisProgram]) -> None:
        self.__programs = programs

    # ------------------------------------------------------------
    # Implementation of VoltalisRepository methods
    # ------------------------------------------------------------

    async def get_devices(self) -> dict[int, VoltalisDevice]:
        return self.__devices

    async def get_devices_health(self) -> dict[int, VoltalisDeviceHealth]:
        return self.__devices_health

    async def get_devices_consumptions(self, target_datetime: datetime) -> dict[int, float]:
        consumptions: dict[int, float] = {}
        for device_id, consumption_records in self.__devices_consumptions.items():
            for record_datetime, consumption in consumption_records:
                if record_datetime == target_datetime:
                    consumptions[device_id] = consumption
                    break

        return consumptions

    async def get_manual_settings(self) -> dict[int, VoltalisManualSetting]:
        return self.__manual_settings

    async def set_manual_setting(self, manual_setting_id: int, setting: VoltalisManualSettingUpdate) -> None:
        existing_setting = self.__manual_settings[manual_setting_id]
        updated_setting = existing_setting.model_copy(update=setting.model_dump(exclude_unset=True))
        self.__manual_settings[manual_setting_id] = updated_setting

    # ------------------------------------------------------------
    # Programs
    # ------------------------------------------------------------

    async def get_programs(self) -> dict[int, VoltalisProgram]:
        return self.__programs

    async def get_user_program(self, program_id: int) -> VoltalisProgram:
        return self.__programs[program_id]

    async def get_default_programs(self) -> dict[int, VoltalisProgram]:
        from custom_components.voltalis.lib.domain.models.program import VoltalisProgramTypeEnum

        return {
            program_id: program
            for program_id, program in self.__programs.items()
            if program.program_type == VoltalisProgramTypeEnum.DEFAULT
        }

    async def set_user_program_state(self, program_id: int, name: str, enabled: bool) -> None:
        program = self.__programs[program_id]
        self.__programs[program_id] = program.model_copy(update={"enabled": enabled, "name": name})

    async def set_default_program_state(self, program_id: int, enabled: bool) -> None:
        program = self.__programs[program_id]
        self.__programs[program_id] = program.model_copy(update={"enabled": enabled})
