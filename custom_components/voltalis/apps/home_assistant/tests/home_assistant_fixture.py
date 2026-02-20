"""Base fixture class for Home Assistant E2E tests."""

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest import MonkeyPatch

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.tests.utils.base_fixture import BaseFixture
from custom_components.voltalis.tests.utils.mock_voltalis_server import MockVoltalisServer


class HomeAssistantFixture(BaseFixture[None]):
    """Base fixture class for Home Assistant E2E tests."""

    def __init__(self) -> None:
        """Initialize the fixture.

        Args:
            hass: Home Assistant instance
            monkeypatch: pytest MonkeyPatch instance
        """
        super().__init__()
        self.voltalis_server = MockVoltalisServer()

    async def async_before_all(self) -> None:
        """Set up before all tests - called once at the start."""
        await self.voltalis_server.start_server()

    async def async_after_all(self) -> None:
        """Clean up after all tests - called once at the end."""
        await self.voltalis_server.stop_server()

    async def async_before_each(self) -> None:
        """Set up before each test - called before each test function.

        Resets the server and initializes default devices/settings.
        """
        await super().async_before_each()

        # Reset and configure the mock server
        self.voltalis_server.reset_storage()

    def setup_before_test(
        self,
        *,
        hass: HomeAssistant,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Set up the Home Assistant fixture.

        Args:
            hass: Home Assistant instance
            monkeypatch: pytest MonkeyPatch instance
        """
        self.hass = hass

        monkeypatch.setattr(
            "custom_components.voltalis.config_flow.VoltalisClientAiohttp",
            lambda session, **kwargs: self.voltalis_server.get_client(),
        )

        monkeypatch.setattr(
            "custom_components.voltalis.apps.home_assistant.home_assistant_module.VoltalisClientAiohttp",
            lambda session, **kwargs: self.voltalis_server.get_client(),
        )

    async def configure_entry(
        self,
        username: str = "test@example.com",
        password: str = "secret",
    ) -> None:
        """Configure the integration entry via config flow.

        Args:
            username: Username for the config flow
            password: Password for the config flow
        """
        # Start the flow
        init_result = await self.hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert init_result["type"] == FlowResultType.FORM

        # Submit credentials
        result = await self.hass.config_entries.flow.async_configure(
            init_result["flow_id"],
            user_input={
                "username": username,
                "password": password,
            },
        )
        assert result["type"] == FlowResultType.CREATE_ENTRY

        # Wait for setup to complete
        await self.hass.async_block_till_done()
