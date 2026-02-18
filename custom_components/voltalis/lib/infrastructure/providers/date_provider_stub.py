from datetime import datetime, tzinfo

from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider


class DateProviderStub(DateProvider):
    """Stub date provider."""

    DEFAULT_NOW = datetime.now().replace(microsecond=0)

    now: datetime = DEFAULT_NOW

    def get_now(self, tz: tzinfo | None = None) -> datetime:
        """Get the current date and time."""
        return self.now.astimezone(tz) if tz else self.now
