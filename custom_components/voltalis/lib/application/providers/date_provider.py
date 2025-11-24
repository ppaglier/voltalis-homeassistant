from abc import ABC, abstractmethod
from datetime import datetime


class DateProvider(ABC):
    """Interface for date provider."""

    @abstractmethod
    def get_now(self) -> datetime:
        """Get the current date and time."""
        ...

    @abstractmethod
    def get_now_utc(self) -> datetime:
        """Get the current date and time in UTC."""
        ...
