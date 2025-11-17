from datetime import datetime

from custom_components.voltalis.lib.application.voltalis_client import VoltalisClient
from custom_components.voltalis.lib.domain.device import (
    VoltalisApplianceDiagnostic,
    VoltalisConsumptionObjective,
    VoltalisContract,
    VoltalisDevice,
    VoltalisManagedAppliance,
    VoltalisProgram,
    VoltalisRealTimeConsumption,
    VoltalisSiteInfo,
)
from custom_components.voltalis.lib.domain.exceptions import VoltalisAuthenticationException, VoltalisException


class VoltalisClientStub(VoltalisClient):
    """Voltalis client integration using stub implementation for tests"""

    class Storage:
        """Class that represent the storage of the client"""

        devices: dict[int, VoltalisDevice] = {}
        devices_health: dict[int, bool] = {}
        devices_consumptions: dict[int, list[tuple[datetime, float]]] = {}
        consumption_objective: VoltalisConsumptionObjective | None = None
        realtime_consumptions: list[VoltalisRealTimeConsumption] = []
        programs: list[VoltalisProgram] = []
        site_info: VoltalisSiteInfo | None = None
        contracts: list[VoltalisContract] = []
        managed_appliances: dict[int, VoltalisManagedAppliance] = {}
        diagnostics: dict[int, VoltalisApplianceDiagnostic] = {}

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

    async def get_consumption_objective(self) -> VoltalisConsumptionObjective | None:
        return self.__storage.consumption_objective

    async def get_realtime_consumption(self, num_points: int = 10) -> list[VoltalisRealTimeConsumption]:
        return self.__storage.realtime_consumptions[:num_points]

    async def get_programs(self) -> list[VoltalisProgram]:
        return self.__storage.programs

    async def get_site_info(self) -> VoltalisSiteInfo | None:
        return self.__storage.site_info

    async def get_subscriber_contracts(self) -> list[VoltalisContract]:
        return self.__storage.contracts

    async def get_managed_appliances(self) -> dict[int, VoltalisManagedAppliance]:
        return self.__storage.managed_appliances

    async def get_appliance_diagnostics(self) -> dict[int, VoltalisApplianceDiagnostic]:
        return self.__storage.diagnostics
