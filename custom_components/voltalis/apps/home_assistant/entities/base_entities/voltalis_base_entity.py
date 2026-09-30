from typing import Any, Callable, cast

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from propcache.api import cached_property

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry


class VoltalisBaseEntity(CoordinatorEntity[BaseVoltalisCoordinator[dict[int, Any]]]):
    """Base class for all Voltalis entities."""

    _unique_id_suffix: str = ""

    _statistic_id: str = ""
    __remove_statistics_listener: Callable[[], None] | None = None

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        coordinator: BaseVoltalisCoordinator[dict[int, Any]],
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._voltalis_module = entry.runtime_data.voltalis_home_assistant_module
        self._entry = entry

        if len(self._unique_id_suffix) == 0:
            raise ValueError("Unique ID suffix must be defined in subclass.")

    @property
    def unique_internal_name(self) -> str:
        """Return a unique internal name for the entity."""
        raise NotImplementedError()

    # ------------------------------------------------------------------
    # Availability handling
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: Any) -> bool:
        """Check if entity is available based on entity data.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError()

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        # Invalidate cached properties to ensure they are recalculated on the next access
        cls = self.__class__
        for attr_name in dir(cls):
            if isinstance(getattr(cls, attr_name, None), cached_property):
                self.__dict__.pop(attr_name, None)  # pyright: ignore[reportAttributeAccessIssue]

        super()._handle_coordinator_update()

    def _register_statistics_updates(self) -> None:
        """Register an entity to a Voltalis external statistic."""

        publisher = self._voltalis_module.energy_statistics_publisher

        if self._statistic_id == "":
            raise ValueError("Statistic ID must be defined in subclass.")

        @callback
        def handle_update(updated_statistic_id: str, value: Any) -> None:
            if updated_statistic_id != self._statistic_id or getattr(self, "native_value", None) == value:
                return

            self._attr_native_value = value
            self.async_write_ha_state()

        self.__remove_statistics_listener = publisher.add_statistic_listener(handle_update)
        latest_value = publisher.get_latest_value(self._statistic_id)
        if latest_value is not None:
            # The cast is necessary because we don't want to override the type of _attr_native_value,
            # which is defined in subclasses.
            self._attr_native_value = cast(Any, latest_value)
            self.async_write_ha_state()

    def _unregister_statistics_updates(self) -> None:
        """Disconnect an entity from a Voltalis external statistic."""

        if self.__remove_statistics_listener is None:
            return

        self.__remove_statistics_listener()
        self.__remove_statistics_listener = None
