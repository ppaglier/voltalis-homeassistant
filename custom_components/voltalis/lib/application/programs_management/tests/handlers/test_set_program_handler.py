import pytest

from custom_components.voltalis.lib.application.programs_management.tests.programs_management_fixture import (
    ProgramsManagementFixture,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program_builder import (
    ProgramBuilder,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum


@pytest.mark.unit
async def test_set_program_disables_old_and_enables_new(
    fixture: ProgramsManagementFixture,
) -> None:
    """Test set program handler toggles old and new programs."""

    # Given
    old_program = (
        ProgramBuilder().with_id(1).with_type(ProgramTypeEnum.DEFAULT).with_name("Default").with_enabled(True).build()
    )
    new_program = (
        ProgramBuilder().with_id(2).with_type(ProgramTypeEnum.USER).with_name("User").with_enabled(False).build()
    )
    fixture.given_programs([old_program, new_program])

    # When
    await fixture.set_program_handler.handle(new_program=new_program, old_program=old_program)

    # Then
    fixture.then_programs_should_be(
        {
            1: ProgramBuilder()
            .with_id(1)
            .with_type(ProgramTypeEnum.DEFAULT)
            .with_name("Default")
            .with_enabled(False)
            .build(),
            2: ProgramBuilder().with_id(2).with_type(ProgramTypeEnum.USER).with_name("User").with_enabled(True).build(),
        }
    )


@pytest.mark.unit
async def test_set_program_allows_new_only(
    fixture: ProgramsManagementFixture,
) -> None:
    """Test set program handler enables new program when old is None."""

    # Given
    new_program = (
        ProgramBuilder().with_id(2).with_type(ProgramTypeEnum.USER).with_name("User").with_enabled(False).build()
    )
    fixture.given_programs([new_program])

    # When
    await fixture.set_program_handler.handle(new_program=new_program, old_program=None)

    # Then
    fixture.then_programs_should_be(
        {
            2: ProgramBuilder().with_id(2).with_type(ProgramTypeEnum.USER).with_name("User").with_enabled(True).build(),
        }
    )


@pytest.fixture
def fixture() -> ProgramsManagementFixture:
    return ProgramsManagementFixture()
