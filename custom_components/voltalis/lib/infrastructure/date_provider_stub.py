from datetime import UTC, datetime

from custom_components.voltalis.lib.application.date_provider import DateProvider


class DateProviderStub(DateProvider):
    """Stub date provider."""

    now: datetime = datetime.now().replace(microsecond=0)
    now_utc: datetime = datetime.now(UTC).replace(microsecond=0)

    def get_now(self) -> datetime:
        """Get the current date and time."""
        return self.now

    def get_now_utc(self) -> datetime:
        """Get the current date and time in UTC."""
        return self.now_utc
