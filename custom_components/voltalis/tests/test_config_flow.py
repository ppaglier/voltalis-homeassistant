"""Tests for the Voltalis config flow."""

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.application.voltalis_client import VoltalisClient
from custom_components.voltalis.lib.infrastructure.voltalis_client_stub import VoltalisClientStub


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_form_user_input_none(hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch) -> None:
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
@pytest.mark.asyncio
async def test_config_flow_creates_entry(hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that the config flow creates an entry successfully using the flow manager."""

    # Ensure the config flow uses the stub client instead of performing real I/O
    monkeypatch.setattr(
        "custom_components.voltalis.config_flow.VoltalisClientAiohttp",
        lambda session: VoltalisClientStub(),
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
@pytest.mark.asyncio
@pytest.mark.parametrize("exception_type", ["invalid_auth", "cannot_connect", "unknown"])
async def test_form_errors(hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch, exception_type: str) -> None:
    """Test that errors are handled correctly in the config flow."""

    # Ensure the config flow uses the stub client instead of performing real I/O
    def get_client() -> VoltalisClient:
        client = VoltalisClientStub()
        client.set_auth_failure(exception_type == "invalid_auth")
        client.set_connection_failure(exception_type == "cannot_connect")
        client.set_unexpected_failure(exception_type == "unknown")
        return client

    monkeypatch.setattr(
        "custom_components.voltalis.config_flow.VoltalisClientAiohttp",
        lambda session: get_client(),
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
    assert result["errors"]["base"] == exception_type


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_already_configured(hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that we abort if already configured."""

    # Ensure the config flow uses the stub client instead of performing real I/O
    monkeypatch.setattr(
        "custom_components.voltalis.config_flow.VoltalisClientAiohttp", lambda session: VoltalisClientStub()
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
@pytest.mark.asyncio
async def test_step_reconfigure_success(
    hass: HomeAssistant,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test reconfigure flow updates existing entry."""

    # Ensure the config flow uses the stub client instead of performing real I/O
    monkeypatch.setattr(
        "custom_components.voltalis.config_flow.VoltalisClientAiohttp", lambda session: VoltalisClientStub()
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
@pytest.mark.asyncio
async def test_step_reconfigure_shows_form(
    hass: HomeAssistant,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test reconfigure flow updates existing entry."""

    # Ensure the config flow uses the stub client instead of performing real I/O
    monkeypatch.setattr(
        "custom_components.voltalis.config_flow.VoltalisClientAiohttp", lambda session: VoltalisClientStub()
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
@pytest.mark.asyncio
async def test_step_reconfigure_invalid_auth(
    hass: HomeAssistant,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test reconfigure flow shows error when authentication fails."""

    # Track whether we're in the initial setup or reconfigure step
    is_reconfiguring = False

    # Ensure the config flow uses the stub client instead of performing real I/O
    def get_client() -> VoltalisClient:
        client = VoltalisClientStub()
        # Only fail auth during reconfiguration, not during initial setup
        if is_reconfiguring:
            client.set_auth_failure(True)
        return client

    monkeypatch.setattr(
        "custom_components.voltalis.config_flow.VoltalisClientAiohttp",
        lambda session: get_client(),
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

    # Now we're in reconfiguration mode
    is_reconfiguring = True

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
