from datetime import datetime

from custom_components.voltalis.lib.application.voltalis_client import VoltalisClient
from custom_components.voltalis.lib.domain.device import VoltalisDevice


class VoltalisClientStub(VoltalisClient):
    """Voltalis client integration using stub implementation for tests"""

    class Storage:
        """Class that represent the storage of the client"""

        devices: dict[int, VoltalisDevice] = {}
        devices_health: dict[int, bool] = {}
        devices_consumptions: dict[int, list[tuple[datetime, float]]] = {}

    def __init__(self) -> None:
        self.__storage = self.Storage()

    async def get_access_token(
        self,
        *,
        username: str,
        password: str,
    ) -> str:
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
