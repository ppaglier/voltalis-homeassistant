import logging
from datetime import timedelta
from typing import TypeVar

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.voltalis.lib.application.providers.date_provider import DateProvider
from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.exceptions import (
    VoltalisAuthenticationException,
    VoltalisException,
    VoltalisValidationException,
)

TData = TypeVar("TData")


class BaseVoltalisCoordinator(DataUpdateCoordinator[TData]):
    """Mixin supplying shared Voltalis error handling & recovery logging."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        logger: logging.Logger,
        voltalis_repository: VoltalisRepository,
        date_provider: DateProvider,
        update_interval: timedelta,
        entry: ConfigEntry,  # ConfigEntry reference used for reauth triggering
    ) -> None:
        super().__init__(
            hass,
            logger=logger,
            name="Voltalis",
            update_interval=update_interval,
        )
        self._voltalis_repository = voltalis_repository
        self._date_provider = date_provider
        self._entry = entry
        self._was_unavailable = False  # Track previous availability state for one-shot logging

    def _handle_update_error(self, err: Exception) -> Exception:
        if self._was_unavailable:
            return UpdateFailed("Voltalis API unavailable")

        was_unavailable = self._was_unavailable

        self._was_unavailable = True

        if isinstance(err, VoltalisAuthenticationException):
            if not was_unavailable:
                self.logger.error("Voltalis authentication failed: %s", err)
                self.hass.async_create_task(
                    self.hass.config_entries.flow.async_init(
                        self._entry.domain,
                        context={
                            "source": config_entries.SOURCE_REAUTH,
                            "entry_id": self._entry.entry_id,
                        },
                        data=self._entry.data,
                    )
                )

            return UpdateFailed("Authentication failed")

        if isinstance(err, VoltalisValidationException):
            if not was_unavailable:
                self.logger.error("Voltalis data validation error: %s", err)
            return UpdateFailed("Voltalis data validation error")

        if isinstance(err, VoltalisException):
            if not was_unavailable:
                self.logger.error("Voltalis API error: %s", err)
            return UpdateFailed("Voltalis API error")

        if not was_unavailable:
            self.logger.exception("Unexpected error while updating Voltalis data")
        return UpdateFailed(f"Unexpected error: {err}")

    def _handle_after_update(self) -> None:
        if not self._was_unavailable:
            return

        self.logger.info("Voltalis API back online for %s", self.name)
        self._was_unavailable = False
