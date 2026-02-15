from datetime import UTC, datetime

from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider


class DateProviderStub(DateProvider):
    """Stub date provider."""

    DEFAULT_NOW = datetime.now().replace(microsecond=0)
    DEFAULT_NOW_UTC = datetime.now(UTC).replace(microsecond=0)

    now: datetime = DEFAULT_NOW
    now_utc: datetime = DEFAULT_NOW_UTC

    def get_now(self) -> datetime:
        """Get the current date and time."""
        return self.now

    def get_now_utc(self) -> datetime:
        """Get the current date and time in UTC."""
        return self.now_utc
