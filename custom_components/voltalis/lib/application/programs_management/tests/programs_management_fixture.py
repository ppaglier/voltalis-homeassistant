import logging

from custom_components.voltalis.lib.application.programs_management.handlers.get_programs_handler import (
    GetProgramsHandler,
)
from custom_components.voltalis.lib.application.programs_management.handlers.set_program_handler import (
    SetProgramHandler,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program import Program
from custom_components.voltalis.lib.infrastructure.providers.voltalis_provider_stub import VoltalisProviderStub
from custom_components.voltalis.tests.base_fixture import BaseFixture


class ProgramsManagementFixture(BaseFixture):
    """Fixture for programs management tests."""

    def __init__(self) -> None:
        self.logger = logging.getLogger("voltalis-home_assistant-tests programs-management-fixture")

        self.voltalis_provider = VoltalisProviderStub()

        self.get_programs_handler = GetProgramsHandler(
            voltalis_provider=self.voltalis_provider,
        )
        self.set_program_handler = SetProgramHandler(
            voltalis_provider=self.voltalis_provider,
        )

    # ------------------------------------------------------------
    # Given
    # ------------------------------------------------------------

    def given_programs(self, programs: dict[int, Program]) -> None:
        """Set programs returned by the provider."""

        self.voltalis_provider.set_programs(programs)

    # ------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------

    async def then_programs_should_be(self, expected_programs: dict[int, Program]) -> None:
        """Assert programs returned by the provider are as expected."""

        programs = await self.voltalis_provider.get_programs()
        self.compare_dicts(programs, expected_programs)
