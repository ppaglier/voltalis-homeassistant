from logging import Logger

from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class VoltalisModule:
    """Module to initialize the voltalis lib."""

    def __init__(
        self,
        *,
        # Providers
        date_provider: DateProvider,
        logger: Logger,
        voltalis_provider: VoltalisProvider,
    ) -> None:
        """Initialize the the voltalis module."""

        # Providers
        self._date_provider = date_provider
        self._logger = logger
        self._voltalis_provider = voltalis_provider

    def setup_handlers(self) -> None:
        """Setup the handlers."""
