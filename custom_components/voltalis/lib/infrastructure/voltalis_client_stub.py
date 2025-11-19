from datetime import datetime

from custom_components.voltalis.lib.application.voltalis_client import VoltalisClient
from custom_components.voltalis.lib.domain.device import (
    VoltalisDevice,
    VoltalisManualSetting,
    VoltalisManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.exceptions import VoltalisAuthenticationException, VoltalisException


class VoltalisClientStub(VoltalisClient):
    """Voltalis client integration using stub implementation for tests"""

    class Storage:
        """Class that represent the storage of the client"""

        devices: dict[int, VoltalisDevice] = {}
        devices_health: dict[int, bool] = {}
        devices_consumptions: dict[int, list[tuple[datetime, float]]] = {}
        manual_settings: dict[int, VoltalisManualSetting] = {}

    def __init__(self) -> None:
        self.__storage = self.Storage()
        self.__should_fail_auth = False
        self.__should_fail_connection = False
        self.__should_fail_unexpected = False

    def set_auth_failure(self, should_fail: bool = True) -> None:
        """Configure the client to fail authentication."""
        self.__should_fail_auth = should_fail

    def set_connection_failure(self, should_fail: bool = True) -> None:
        """Configure the client to fail connection."""
        self.__should_fail_connection = should_fail

    def set_unexpected_failure(self, should_fail: bool = True) -> None:
        """Configure the client to fail with unexpected error."""
        self.__should_fail_unexpected = should_fail

    async def login(self) -> None:
        if self.__should_fail_auth:
            raise VoltalisAuthenticationException("Invalid credentials")
        if self.__should_fail_connection:
            raise VoltalisException("Connection failed")
        if self.__should_fail_unexpected:
            raise RuntimeError("Unexpected error")

    async def logout(self) -> None:
        pass

    async def get_devices(self) -> dict[int, VoltalisDevice]:
        return self.__storage.devices

    async def get_devices_health(self) -> dict[int, bool]:
        return self.__storage.devices_health

    async def get_devices_consumptions(self, target_datetime: datetime) -> dict[int, float]:
        return {
            device_id: consumption_value
            for device_id, consumptions_list in self.__storage.devices_consumptions.items()
            for consumption_datetime, consumption_value in consumptions_list
            if consumption_datetime == target_datetime
        }

    async def get_manual_settings(self) -> dict[int, VoltalisManualSetting]:
        """Get manual settings for all devices."""
        return self.__storage.manual_settings

    async def set_manual_setting(self, manual_setting_id: int, setting: VoltalisManualSettingUpdate) -> None:
        """Set manual setting for a device."""
        # Find the manual setting by its ID (not appliance ID)
        for appliance_id, manual_setting in self.__storage.manual_settings.items():
            if manual_setting.id == manual_setting_id:
                # Update existing manual setting
                self.__storage.manual_settings[appliance_id] = VoltalisManualSetting(
                    id=manual_setting.id,
                    enabled=setting.enabled,
                    id_appliance=setting.id_appliance,
                    appliance_name=manual_setting.appliance_name,
                    appliance_type=manual_setting.appliance_type,
                    until_further_notice=setting.until_further_notice,
                    is_on=setting.is_on,
                    mode=setting.mode,
                    heating_level=manual_setting.heating_level,
                    end_date=setting.end_date,
                    temperature_target=setting.temperature_target,
                )
                break
