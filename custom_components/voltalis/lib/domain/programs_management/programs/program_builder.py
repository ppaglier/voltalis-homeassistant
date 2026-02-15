from typing import Self

from custom_components.voltalis.lib.domain.programs_management.programs.program import Program
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum
from custom_components.voltalis.lib.domain.shared.generic_builder import GenericBuilder


class ProgramBuilder(GenericBuilder[Program]):
    """Builder for Program model."""

    DEFAULT_VALUES = Program(
        id=1,
        type=ProgramTypeEnum.DEFAULT,
        name="Default Program",
        enabled=True,
    )

    props: dict = {}

    def __init__(self, props: dict | None = None):
        self.props = {**ProgramBuilder.DEFAULT_VALUES.model_dump(), **(props or {})}

    def build(self) -> Program:
        return Program(**self.props)

    def with_id(self, id: int) -> Self:
        """Set the id."""
        return self._set_value("id", id)

    def with_type(self, type: ProgramTypeEnum) -> Self:
        """Set the type."""
        return self._set_value("type", type)

    def with_name(self, name: str) -> Self:
        """Set the name."""
        return self._set_value("name", name)

    def with_enabled(self, enabled: bool) -> Self:
        """Set the enabled status."""
        return self._set_value("enabled", enabled)
