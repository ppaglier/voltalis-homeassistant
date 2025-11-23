"""Service handlers for Voltalis integration."""

import logging

from homeassistant.core import HomeAssistant, ServiceCall

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator

_LOGGER = logging.getLogger(__name__)


class VoltalisServiceHandler:
    """Handle service calls for Voltalis integration."""

    def __init__(self, hass: HomeAssistant, coordinator: VoltalisCoordinator) -> None:
        """Initialize the service handler."""
        self._hass = hass
        self._coordinator = coordinator

    def register_services(self) -> None:
        """Register all integration services."""
        self._hass.services.async_register(
            DOMAIN,
            "refresh_subscriber_contracts",
            self.async_handle_refresh_subscriber_contracts,
        )

    def unregister_services(self) -> None:
        """Unregister all integration services."""
        self._hass.services.async_remove(DOMAIN, "refresh_subscriber_contracts")

    async def async_handle_refresh_subscriber_contracts(self, call: ServiceCall) -> None:
        """Handle the service call to refresh subscriber contracts."""
        _LOGGER.info("Refreshing subscriber contracts...")
        try:
            await self._coordinator.async_fetch_contracts()
            self._hass.bus.async_fire(f"{DOMAIN}_contracts_updated")
            _LOGGER.info("Subscriber contracts refreshed successfully")
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Failed to refresh subscriber contracts: %s", err)
            raise
