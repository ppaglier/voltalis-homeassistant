import pytest

from custom_components.voltalis.lib.application.programs_management.tests.programs_management_fixture import (
    ProgramsManagementFixture,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program_builder import ProgramBuilder
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum


@pytest.mark.unit
async def test_get_programs_returns_provider_data(
    fixture: ProgramsManagementFixture,
) -> None:
    """Test get programs handler returns provider data."""

    # Given
    programs = [
        ProgramBuilder().with_id(1).with_type(ProgramTypeEnum.MANUAL).build(),
        ProgramBuilder().with_id(2).with_type(ProgramTypeEnum.QUICK).build(),
        ProgramBuilder().with_id(3).with_type(ProgramTypeEnum.USER).build(),
    ]
    fixture.given_programs(programs)

    # When
    result = await fixture.get_programs_handler.handle()

    # Then
    expected_result = {
        2: programs[1],
        3: programs[2],
    }
    fixture.compare_dicts(result, expected_result)


@pytest.fixture
def fixture() -> ProgramsManagementFixture:
    return ProgramsManagementFixture()
