from datetime import datetime

from custom_components.voltalis.lib.application.voltalis_client import VoltalisClient
from custom_components.voltalis.lib.domain.device import VoltalisDevice
from custom_components.voltalis.lib.domain.exceptions import VoltalisAuthenticationException, VoltalisException


class VoltalisClientStub(VoltalisClient):
    """Voltalis client integration using stub implementation for tests"""

    class Storage:
        """Class that represent the storage of the client"""

        devices: dict[int, VoltalisDevice] = {}
        devices_health: dict[int, bool] = {}
        devices_consumptions: dict[int, list[tuple[datetime, float]]] = {}

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

    async def get_access_token(
        self,
        *,
        username: str,
        password: str,
    ) -> str:
        if self.__should_fail_auth:
            raise VoltalisAuthenticationException("Invalid credentials")
        if self.__should_fail_connection:
            raise VoltalisException("Connection failed")
        if self.__should_fail_unexpected:
            raise RuntimeError("Unexpected error")
        return ""

    async def login(self) -> None:
        pass

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
