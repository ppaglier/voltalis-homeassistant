from typing import Generic, TypeVar

from custom_components.voltalis.lib.domain.custom_model import CustomModel

T = TypeVar("T")


class RangeModel(CustomModel, Generic[T]):
    """Range model"""

    start: T
    end: T
