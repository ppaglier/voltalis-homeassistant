from datetime import datetime

from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice
from custom_components.voltalis.lib.domain.models.device_health import VoltalisDeviceHealth
from custom_components.voltalis.lib.domain.models.energy_contract import VoltalisEnergyContract
from custom_components.voltalis.lib.domain.models.manual_setting import (
    VoltalisManualSetting,
    VoltalisManualSettingUpdate,
)
from custom_components.voltalis.lib.infrastructure.helpers.get_consumption_for_hour import get_consumption_for_hour


class VoltalisRepositoryInMemory(VoltalisRepository):
    """In-memory implementation of the VoltalisRepository for testing purposes."""

    def __init__(self) -> None:
        self.__devices: dict[int, VoltalisDevice] = {}
        self.__devices_health: dict[int, VoltalisDeviceHealth] = {}
        self.__devices_consumptions: dict[int, list[tuple[datetime, float]]] = {}
        self.__manual_settings: dict[int, VoltalisManualSetting] = {}
        self.__energy_contracts: dict[int, VoltalisEnergyContract] = {}

    def set_devices(self, devices: dict[int, VoltalisDevice]) -> None:
        self.__devices = devices

    def set_devices_health(self, devices_health: dict[int, VoltalisDeviceHealth]) -> None:
        self.__devices_health = devices_health

    def set_devices_consumptions(self, devices_consumptions: dict[int, list[tuple[datetime, float]]]) -> None:
        self.__devices_consumptions = devices_consumptions

    def set_manual_settings(self, manual_settings: dict[int, VoltalisManualSetting]) -> None:
        self.__manual_settings = manual_settings

    def set_current_energy_contract(self, energy_contracts: dict[int, VoltalisEnergyContract]) -> None:
        self.__energy_contracts = energy_contracts

    # ------------------------------------------------------------
    # Implementation of VoltalisRepository methods
    # ------------------------------------------------------------

    async def get_devices(self) -> dict[int, VoltalisDevice]:
        return self.__devices

    async def get_devices_health(self) -> dict[int, VoltalisDeviceHealth]:
        return self.__devices_health

    async def get_devices_daily_consumptions(self, target_datetime: datetime) -> dict[int, float]:
        consumptions = {
            device_id: get_consumption_for_hour(consumptions=consumption_records, target_datetime=target_datetime)
            for device_id, consumption_records in self.__devices_consumptions.items()
        }
        return consumptions

    async def get_manual_settings(self) -> dict[int, VoltalisManualSetting]:
        return self.__manual_settings

    async def set_manual_setting(self, manual_setting_id: int, setting: VoltalisManualSettingUpdate) -> None:
        existing_setting = self.__manual_settings[manual_setting_id]
        updated_setting = existing_setting.model_copy(update=setting.model_dump(exclude_unset=True))
        self.__manual_settings[manual_setting_id] = updated_setting

    async def get_energy_contracts(self) -> dict[int, VoltalisEnergyContract]:
        return self.__energy_contracts
