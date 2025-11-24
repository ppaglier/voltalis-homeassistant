from datetime import UTC, datetime

from custom_components.voltalis.lib.application.providers.date_provider import DateProvider


class DateProviderReal(DateProvider):
    """Real date provider."""

    def get_now(self) -> datetime:
        """Get the current date and time."""
        return datetime.now().replace(microsecond=0)

    def get_now_utc(self) -> datetime:
        """Get the current date and time in UTC."""
        return datetime.now(UTC).replace(microsecond=0)
