import pytest

from custom_components.voltalis.lib.application.programs_management.tests.programs_management_fixture import (
    ProgramsManagementFixture,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program import Program
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum


@pytest.mark.unit
async def test_get_programs_returns_provider_data(
    fixture: ProgramsManagementFixture,
) -> None:
    """Test get programs handler returns provider data."""

    # Given
    programs = {
        1: Program(id=1, type=ProgramTypeEnum.DEFAULT, name="Default", enabled=True),
        2: Program(id=2, type=ProgramTypeEnum.USER, name="User", enabled=False),
    }
    fixture.given_programs(programs)

    # When
    result = await fixture.get_programs_handler.handle()

    # Then
    fixture.compare_dicts(result, programs)


@pytest.fixture
def fixture() -> ProgramsManagementFixture:
    return ProgramsManagementFixture()
