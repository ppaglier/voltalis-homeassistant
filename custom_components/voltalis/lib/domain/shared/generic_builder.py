from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Generic, Self, TypeVar

from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel

T = TypeVar("T", bound=CustomModel)


class GenericBuilder(ABC, Generic[T]):
    """Generic builder for model."""

    DEFAULT_VALUES: T

    props: dict = {}

    def __init__(self, props: dict = {}):
        self.props = {**self.DEFAULT_VALUES.model_dump(exclude_unset=True), **props}

    def _get_value(self, key: str) -> Any:
        """Get the value of a key in the props."""
        return deepcopy(self.props.get(key))

    def _set_values(self, props: dict) -> Self:
        """Set the values of the props."""
        _c = deepcopy(self)
        for key, value in props.items():
            _c.props[key] = value
        return _c

    def _set_value(self, key: str, value: Any) -> Self:
        """Set the value of a key in the props."""
        return self._set_values({key: value})

    @abstractmethod
    def build(self) -> T:
        """Build the model."""
        ...
