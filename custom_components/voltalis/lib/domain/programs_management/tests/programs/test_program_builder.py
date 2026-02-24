"""Unit tests for ProgramBuilder."""

import pytest

from custom_components.voltalis.lib.domain.programs_management.programs.program_builder import ProgramBuilder
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum


@pytest.mark.unit
def test_program_builder_default_values() -> None:
    """Test that ProgramBuilder creates a program with default values."""

    assert ProgramBuilder().build() == ProgramBuilder.DEFAULT_VALUES


@pytest.mark.unit
def test_program_builder_creates_valid_program() -> None:
    """Test that ProgramBuilder creates a valid program."""

    # Act
    program = ProgramBuilder().with_id(1).with_name("Manual Program").with_type(ProgramTypeEnum.MANUAL).build()

    # Assert
    assert program.id == 1
    assert program.name == "Manual Program"
    assert program.type == ProgramTypeEnum.MANUAL
