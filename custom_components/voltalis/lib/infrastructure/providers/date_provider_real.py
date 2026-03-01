from datetime import datetime, tzinfo

from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider


class DateProviderReal(DateProvider):
    """Real date provider."""

    def get_now(self, tz: tzinfo | None = None) -> datetime:
        """Get the current date and time."""
        return datetime.now(tz).replace(microsecond=0)
