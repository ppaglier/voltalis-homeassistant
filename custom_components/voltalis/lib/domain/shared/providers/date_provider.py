from abc import ABC, abstractmethod
from datetime import datetime, tzinfo


class DateProvider(ABC):
    """Interface for date provider."""

    @abstractmethod
    def get_now(self, tz: tzinfo | None = None) -> datetime:
        """Get the current date and time."""
        ...
