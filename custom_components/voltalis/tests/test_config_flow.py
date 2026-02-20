"""Tests for the Voltalis config flow."""

from collections.abc import AsyncGenerator

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.tests.utils.mock_voltalis_server import MockVoltalisServer


@pytest.mark.e2e
async def test_form_user_input_none(
    hass: HomeAssistant,
    voltalis_server: MockVoltalisServer,
) -> None:
    """Test that the form is shown when user_input is None."""

    # Start the flow via Home Assistant to ensure proper context handling
    init_result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"
    assert init_result["data_schema"] is not None

    # Check that the schema contains the required fields
    schema_keys = [key.schema for key in init_result["data_schema"].schema.keys()]
    assert "username" in schema_keys
    assert "password" in schema_keys

    # Submit user input to complete the flow
    result = await hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=None,
    )
    assert result["type"] == FlowResultType.FORM


@pytest.mark.e2e
async def test_config_flow_creates_entry(
    hass: HomeAssistant,
    voltalis_server: MockVoltalisServer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that the config flow creates an entry successfully using the flow manager."""

    # Reset and configure the mock server
    voltalis_server.reset_storage()
    voltalis_server.given_login_ok()

    # Mock VoltalisClientAiohttp to use the mock server's client
    monkeypatch.setattr(
        "custom_components.voltalis.config_flow.VoltalisClientAiohttp",
        lambda session, **kwargs: voltalis_server.get_client(),
    )

    # Start the flow via Home Assistant to ensure proper context handling
    init_result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"
    assert init_result["data_schema"] is not None

    # Submit user input to complete the flow
    result = await hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input={
            "username": "test@example.com",
            "password": "secret",
        },
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "test@example.com"
    assert result["data"]["username"] == "test@example.com"
    assert result["data"]["password"] == "secret"


@pytest.mark.e2e
@pytest.mark.parametrize("exception_type", ["invalid_auth", "cannot_connect", "unknown"])
async def test_form_errors(
    hass: HomeAssistant,
    voltalis_server: MockVoltalisServer,
    monkeypatch: pytest.MonkeyPatch,
    exception_type: str,
) -> None:
    """Test that errors are handled correctly in the config flow."""

    # Reset the mock server
    voltalis_server.reset_storage()

    # Configure the server based on the error type being tested
    voltalis_server.given_login_failure(exception_type)

    # Mock VoltalisClientAiohttp to use the mock server's client
    monkeypatch.setattr(
        "custom_components.voltalis.config_flow.VoltalisClientAiohttp",
        lambda session, **kwargs: voltalis_server.get_client(),
    )

    # Start the flow via Home Assistant to ensure proper context handling
    init_result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"

    # Submit user input to complete the flow
    result = await hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input={
            "username": "test@example.com",
            "password": "secret",
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert isinstance(result["errors"], dict), result["errors"]
    # Note: "unknown" error type in this test will also result in "cannot_connect" error
    # because HTTP 500 errors from a real server become HttpClientException which maps to "cannot_connect"
    expected_error = "cannot_connect" if exception_type == "unknown" else exception_type
    assert result["errors"]["base"] == expected_error


@pytest.mark.e2e
async def test_already_configured(
    hass: HomeAssistant,
    voltalis_server: MockVoltalisServer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that we abort if already configured."""

    # Reset and configure the mock server
    voltalis_server.reset_storage()
    voltalis_server.given_login_ok()

    # Mock VoltalisClientAiohttp to use the mock server's client
    monkeypatch.setattr(
        "custom_components.voltalis.config_flow.VoltalisClientAiohttp",
        lambda session, **kwargs: voltalis_server.get_client(),
    )

    credentials = {
        "username": "test@example.com",
        "password": "secret",
    }

    # Start the first flow and create an entry
    init_result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"
    assert init_result["data_schema"] is not None

    # Submit user input to complete the first flow
    result = await hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=credentials,
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Start a second flow with the same credentials
    init_result2 = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert init_result2["type"] == FlowResultType.FORM
    assert init_result2["step_id"] == "user"

    # Submit the same credentials - should abort because already configured
    result2 = await hass.config_entries.flow.async_configure(
        init_result2["flow_id"],
        user_input=credentials,
    )
    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


@pytest.mark.e2e
async def test_step_reconfigure_success(
    hass: HomeAssistant,
    voltalis_server: MockVoltalisServer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test reconfigure flow updates existing entry."""

    # Reset and configure the mock server
    voltalis_server.reset_storage()
    voltalis_server.given_login_ok()

    # Mock VoltalisClientAiohttp to use the mock server's client
    monkeypatch.setattr(
        "custom_components.voltalis.config_flow.VoltalisClientAiohttp",
        lambda session, **kwargs: voltalis_server.get_client(),
    )

    credentials = {
        "username": "test@example.com",
        "password": "secret",
    }

    # Start the first flow and create an entry
    init_result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"
    assert init_result["data_schema"] is not None

    # Submit user input to complete the first flow
    result = await hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=credentials,
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Start a second flow with the same credentials
    init_result2 = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_RECONFIGURE, "entry_id": result["result"].entry_id}
    )
    assert init_result2["type"] == FlowResultType.FORM
    assert init_result2["step_id"] == "reconfigure"

    # Submit new credentials - should abort because reconfiguration successful
    new_credentials = credentials.copy()
    new_credentials.update({"password": "newsecret"})
    result2 = await hass.config_entries.flow.async_configure(
        init_result2["flow_id"],
        user_input=new_credentials,
    )
    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "reconfigure_successful"

    # Verify the entry was updated
    updated_entry = hass.config_entries.async_get_entry(result["result"].entry_id)
    assert updated_entry is not None
    assert updated_entry.data["username"] == new_credentials["username"]
    assert updated_entry.data["password"] == new_credentials["password"]


@pytest.mark.e2e
async def test_step_reconfigure_shows_form(
    hass: HomeAssistant,
    voltalis_server: MockVoltalisServer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test reconfigure flow updates existing entry."""

    # Reset and configure the mock server
    voltalis_server.reset_storage()
    voltalis_server.given_login_ok()

    # Mock VoltalisClientAiohttp to use the mock server's client
    monkeypatch.setattr(
        "custom_components.voltalis.config_flow.VoltalisClientAiohttp",
        lambda session, **kwargs: voltalis_server.get_client(),
    )

    credentials = {
        "username": "test@example.com",
        "password": "secret",
    }

    # Start the first flow and create an entry
    init_result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"
    assert init_result["data_schema"] is not None

    # Submit user input to complete the first flow
    result = await hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=credentials,
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Start a second flow with the same credentials
    init_result2 = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_RECONFIGURE, "entry_id": result["result"].entry_id}
    )
    assert init_result2["type"] == FlowResultType.FORM
    assert init_result2["step_id"] == "reconfigure"
    assert init_result2["data_schema"] is not None

    # Check that the schema contains the required fields
    schema_keys = [key.schema for key in init_result2["data_schema"].schema.keys()]
    assert "username" in schema_keys
    assert "password" in schema_keys

    # Submit user input to complete the flow
    result = await hass.config_entries.flow.async_configure(
        init_result2["flow_id"],
        user_input=None,
    )
    assert result["type"] == FlowResultType.FORM


@pytest.mark.e2e
async def test_step_reconfigure_invalid_auth(
    hass: HomeAssistant,
    voltalis_server: MockVoltalisServer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test reconfigure flow shows error when authentication fails."""

    # Reset and configure the mock server
    voltalis_server.reset_storage()
    voltalis_server.given_login_ok()

    # Mock VoltalisClientAiohttp to use the mock server's client
    # We'll set up the server to fail auth only after the first entry is created
    monkeypatch.setattr(
        "custom_components.voltalis.config_flow.VoltalisClientAiohttp",
        lambda session, **kwargs: voltalis_server.get_client(),
    )

    credentials = {
        "username": "test@example.com",
        "password": "secret",
    }

    # Start the first flow and create an entry
    init_result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"
    assert init_result["data_schema"] is not None

    # Submit user input to complete the first flow
    result = await hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=credentials,
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Now configure the server to fail auth for reconfiguration
    voltalis_server.given_login_failure("invalid_auth")

    # Start a second flow with the same credentials
    init_result2 = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_RECONFIGURE, "entry_id": result["result"].entry_id}
    )
    assert init_result2["type"] == FlowResultType.FORM
    assert init_result2["step_id"] == "reconfigure"

    # Submit new credentials - should show form with error because authentication failed
    new_credentials = credentials.copy()
    new_credentials.update({"password": "newsecret"})

    result2 = await hass.config_entries.flow.async_configure(
        init_result2["flow_id"],
        user_input=new_credentials,
    )
    assert result2["type"] == FlowResultType.FORM
    assert isinstance(result2["errors"], dict), result2["errors"]
    assert result2["errors"]["base"] == "invalid_auth"

    # Verify the entry was NOT updated (since auth failed)
    updated_entry = hass.config_entries.async_get_entry(result["result"].entry_id)
    assert updated_entry is not None
    assert updated_entry.data["username"] == credentials["username"]
    assert updated_entry.data["password"] == credentials["password"]


pytestmark = [pytest.mark.asyncio(loop_scope="function"), pytest.mark.enable_socket]


@pytest.fixture(scope="module")
async def fixture_all() -> AsyncGenerator[MockVoltalisServer, None]:
    """
    Before all tests, start the server.
    Then after all tests, stop the server.
    """
    server = MockVoltalisServer()
    await server.start_server()
    yield server
    await server.stop_server()


@pytest.fixture(scope="function")
async def fixture(fixture_all: MockVoltalisServer) -> AsyncGenerator[MockVoltalisServer, None]:
    """Before each test, initialize the collection."""
    fixture_all.reset_storage()
    yield fixture_all
