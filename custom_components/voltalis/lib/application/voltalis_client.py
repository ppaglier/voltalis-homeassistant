from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from custom_components.voltalis.lib.domain.device import VoltalisDevice


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
    async def get_me(self) -> None:
        """Get the account of the current user"""
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
    async def get_consumptions(self, target_datetime: datetime) -> dict[int, float]:
        """Get devices consumptions from the Voltalis servers"""
        ...
