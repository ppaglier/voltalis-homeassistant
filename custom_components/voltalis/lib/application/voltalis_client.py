from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

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


class VoltalisClient(ABC):
    """Create a Voltalis client that will be used to communicate with Voltalis servers."""

    async def __aenter__(self) -> "VoltalisClient":
        """Async enter."""

        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        """Logout after async exit."""
        await self.logout()

    @abstractmethod
    async def get_access_token(
        self,
        *,
        username: str,
        password: str,
    ) -> str:
        """Get access token of the Voltalis servers"""
        ...

    @abstractmethod
    async def login(self) -> None:
        """Login to the Voltalis servers"""
        ...

    @abstractmethod
    async def logout(self) -> None:
        """Logout from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_devices(self) -> dict[int, VoltalisDevice]:
        """Get devices from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_devices_health(self) -> dict[int, bool]:
        """Get devices health from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_devices_consumptions(self, target_datetime: datetime) -> dict[int, float]:
        """Get devices consumptions from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_consumption_objective(self) -> VoltalisConsumptionObjective | None:
        """Get consumption objective from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_realtime_consumption(self, num_points: int = 10) -> list[VoltalisRealTimeConsumption]:
        """Get real-time consumption from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_programs(self) -> list[VoltalisProgram]:
        """Get programs from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_site_info(self) -> VoltalisSiteInfo | None:
        """Get site information from the Voltalis servers (cached, rarely changes)"""
        ...

    @abstractmethod
    async def get_subscriber_contracts(self) -> list[VoltalisContract]:
        """Get subscriber contracts from the Voltalis servers (cached, rarely changes)"""
        ...

    @abstractmethod
    async def get_managed_appliances(self) -> dict[int, VoltalisManagedAppliance]:
        """Get managed appliances with full details from the Voltalis servers"""
        ...

    @abstractmethod
    async def get_appliance_diagnostics(self) -> dict[int, VoltalisApplianceDiagnostic]:
        """Get appliance diagnostics from the Voltalis servers"""
        ...
