from abc import ABC, abstractmethod


class VoltalisClient(ABC):
    """Create a Voltalis client that will be used to communicate with Voltalis servers."""

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
