import logging
from abc import abstractmethod
from datetime import timedelta
from typing import TypeVar

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.exceptions import (
    VoltalisAuthenticationException,
    VoltalisConnectionException,
    VoltalisException,
    VoltalisValidationException,
)

TData = TypeVar("TData")


class BaseVoltalisCoordinator(DataUpdateCoordinator[TData]):
    """Mixin supplying shared Voltalis error handling & recovery logging."""

    def __init__(
        self,
        name: str,
        *,
        hass: HomeAssistant,
        logger: logging.Logger,
        voltalis_repository: VoltalisRepository,
        entry: ConfigEntry,  # ConfigEntry reference used for reauth triggering
        update_interval: timedelta,
        retry_interval_on_error: timedelta = timedelta(seconds=30),
    ) -> None:
        super().__init__(
            hass,
            logger=logger,
            name=name,
            update_interval=update_interval,
        )
        self._voltalis_repository = voltalis_repository
        self._entry = entry
        self._was_unavailable = False  # Track previous availability state for one-shot logging

        # Enforce type for subclasses
        self.__retry_interval_on_error = retry_interval_on_error

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

        if isinstance(err, VoltalisConnectionException):
            if not was_unavailable:
                self.logger.error("Voltalis connection error: %s", err)
            return UpdateFailed("Voltalis connection error")

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

    def _calculate_next_update_interval(self) -> timedelta | None:
        """Calculate time until next update.

        This is a placeholder method and should be overridden by subclasses
        if they require custom update interval calculations.
        """
        return self.update_interval

    @abstractmethod
    async def _get_data(self) -> TData:
        """Fetch updated data from the Voltalis API."""
        raise NotImplementedError()

    def __update_interval(self) -> None:
        """Recalculate and update the update interval if needed."""

        new_update_interval = self._calculate_next_update_interval()
        if new_update_interval == self.update_interval:
            return

        self.logger.debug(
            "Updating %s update interval: %s -> %s",
            self.name,
            self.update_interval,
            new_update_interval,
        )
        self.update_interval = new_update_interval

    async def _async_update_data(self) -> TData:
        """Fetch updated data from the Voltalis API."""

        try:
            result = await self._get_data()

            if self._was_unavailable:
                self.logger.info("Voltalis API back online for %s", self.name)
                self._was_unavailable = False

            self.__update_interval()

            return result
        except Exception as err:
            self.update_interval = self.__retry_interval_on_error
            raise self._handle_update_error(err) from err
