"""Tests for the Voltalis config flow."""

from collections.abc import AsyncGenerator

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.voltalis.apps.home_assistant.tests.home_assistant_fixture import HomeAssistantFixture
from custom_components.voltalis.const import DOMAIN


@pytest.mark.e2e
async def test_form_user_input_none(fixture: HomeAssistantFixture) -> None:
    """Test that the form is shown when user_input is None."""

    # Start the flow via Home Assistant to ensure proper context handling
    init_result = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"
    assert init_result["data_schema"] is not None

    # Check that the schema contains the required fields
    schema_keys = [key.schema for key in init_result["data_schema"].schema.keys()]
    assert "username" in schema_keys
    assert "password" in schema_keys

    # Submit user input to complete the flow
    result = await fixture.hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=None,
    )
    assert result["type"] == FlowResultType.FORM


@pytest.mark.e2e
async def test_config_flow_creates_entry(fixture: HomeAssistantFixture) -> None:
    """Test that the config flow creates an entry successfully using the flow manager."""

    # Reset and configure the mock server
    fixture.voltalis_server.given_login_ok()

    # Start the flow via Home Assistant to ensure proper context handling
    init_result = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"
    assert init_result["data_schema"] is not None

    # Submit user input to complete the flow
    result = await fixture.hass.config_entries.flow.async_configure(
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
    fixture: HomeAssistantFixture,
    exception_type: str,
) -> None:
    """Test that errors are handled correctly in the config flow."""

    # Configure the server based on the error type being tested
    fixture.voltalis_server.given_login_failure(exception_type)

    # Start the flow via Home Assistant to ensure proper context handling
    init_result = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"

    # Submit user input to complete the flow
    result = await fixture.hass.config_entries.flow.async_configure(
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
async def test_already_configured(fixture: HomeAssistantFixture) -> None:
    """Test that we abort if already configured."""

    fixture.voltalis_server.given_login_ok()

    credentials = {
        "username": "test@example.com",
        "password": "secret",
    }

    # Start the first flow and create an entry
    init_result = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"
    assert init_result["data_schema"] is not None

    # Submit user input to complete the first flow
    result = await fixture.hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=credentials,
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Start a second flow with the same credentials
    init_result2 = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert init_result2["type"] == FlowResultType.FORM
    assert init_result2["step_id"] == "user"

    # Submit the same credentials - should abort because already configured
    result2 = await fixture.hass.config_entries.flow.async_configure(
        init_result2["flow_id"],
        user_input=credentials,
    )
    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


@pytest.mark.e2e
async def test_step_reconfigure_success(fixture: HomeAssistantFixture) -> None:
    """Test reconfigure flow updates existing entry."""

    fixture.voltalis_server.given_login_ok()

    credentials = {
        "username": "test@example.com",
        "password": "secret",
    }

    # Start the first flow and create an entry
    init_result = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"
    assert init_result["data_schema"] is not None

    # Submit user input to complete the first flow
    result = await fixture.hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=credentials,
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Start a second flow with the same credentials
    init_result2 = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_RECONFIGURE, "entry_id": result["result"].entry_id}
    )
    assert init_result2["type"] == FlowResultType.FORM
    assert init_result2["step_id"] == "reconfigure"

    # Submit new credentials - should abort because reconfiguration successful
    new_credentials = credentials.copy()
    new_credentials.update({"password": "newsecret"})
    result2 = await fixture.hass.config_entries.flow.async_configure(
        init_result2["flow_id"],
        user_input=new_credentials,
    )
    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "reconfigure_successful"

    # Verify the entry was updated
    updated_entry = fixture.hass.config_entries.async_get_entry(result["result"].entry_id)
    assert updated_entry is not None
    assert updated_entry.data["username"] == new_credentials["username"]
    assert updated_entry.data["password"] == new_credentials["password"]


@pytest.mark.e2e
async def test_step_reconfigure_shows_form(fixture: HomeAssistantFixture) -> None:
    """Test reconfigure flow updates existing entry."""

    fixture.voltalis_server.given_login_ok()

    credentials = {
        "username": "test@example.com",
        "password": "secret",
    }

    # Start the first flow and create an entry
    init_result = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"
    assert init_result["data_schema"] is not None

    # Submit user input to complete the first flow
    result = await fixture.hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=credentials,
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Start a second flow with the same credentials
    init_result2 = await fixture.hass.config_entries.flow.async_init(
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
    result = await fixture.hass.config_entries.flow.async_configure(
        init_result2["flow_id"],
        user_input=None,
    )
    assert result["type"] == FlowResultType.FORM


@pytest.mark.e2e
async def test_step_reconfigure_invalid_auth(fixture: HomeAssistantFixture) -> None:
    """Test reconfigure flow shows error when authentication fails."""

    fixture.voltalis_server.given_login_ok()

    credentials = {
        "username": "test@example.com",
        "password": "secret",
    }

    # Start the first flow and create an entry
    init_result = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"
    assert init_result["data_schema"] is not None

    # Submit user input to complete the first flow
    result = await fixture.hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=credentials,
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Now configure the server to fail auth for reconfiguration
    fixture.voltalis_server.given_login_failure("invalid_auth")

    # Start a second flow with the same credentials
    init_result2 = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_RECONFIGURE, "entry_id": result["result"].entry_id}
    )
    assert init_result2["type"] == FlowResultType.FORM
    assert init_result2["step_id"] == "reconfigure"

    # Submit new credentials - should show form with error because authentication failed
    new_credentials = credentials.copy()
    new_credentials.update({"password": "newsecret"})

    result2 = await fixture.hass.config_entries.flow.async_configure(
        init_result2["flow_id"],
        user_input=new_credentials,
    )
    assert result2["type"] == FlowResultType.FORM
    assert isinstance(result2["errors"], dict), result2["errors"]
    assert result2["errors"]["base"] == "invalid_auth"

    # Verify the entry was NOT updated (since auth failed)
    updated_entry = fixture.hass.config_entries.async_get_entry(result["result"].entry_id)
    assert updated_entry is not None
    assert updated_entry.data["username"] == credentials["username"]
    assert updated_entry.data["password"] == credentials["password"]


@pytest.mark.e2e
async def test_step_reauth_shows_form(fixture: HomeAssistantFixture) -> None:
    """Test reauth flow shows form when user_input is None."""

    fixture.voltalis_server.given_login_ok()

    credentials = {
        "username": "test@example.com",
        "password": "secret",
    }

    # Start the first flow and create an entry
    init_result = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"

    # Submit user input to complete the first flow
    result = await fixture.hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=credentials,
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Start a reauth flow
    init_result2 = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_REAUTH, "entry_id": result["result"].entry_id}
    )
    assert init_result2["type"] == FlowResultType.FORM
    assert init_result2["step_id"] == "reauth"
    assert init_result2["data_schema"] is not None

    # Check that the schema contains the required fields
    schema_keys = [key.schema for key in init_result2["data_schema"].schema.keys()]
    assert "username" in schema_keys
    assert "password" in schema_keys

    # Submit user input to complete the flow
    result2 = await fixture.hass.config_entries.flow.async_configure(
        init_result2["flow_id"],
        user_input=None,
    )
    assert result2["type"] == FlowResultType.FORM


@pytest.mark.e2e
async def test_step_reauth_success(fixture: HomeAssistantFixture) -> None:
    """Test reauth flow updates existing entry."""

    fixture.voltalis_server.given_login_ok()

    credentials = {
        "username": "test@example.com",
        "password": "secret",
    }

    # Start the first flow and create an entry
    init_result = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"

    # Submit user input to complete the first flow
    result = await fixture.hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=credentials,
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Start a reauth flow
    init_result2 = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_REAUTH, "entry_id": result["result"].entry_id}
    )
    assert init_result2["type"] == FlowResultType.FORM
    assert init_result2["step_id"] == "reauth"

    # Submit new credentials - should abort because reauth successful
    new_credentials = credentials.copy()
    new_credentials.update({"password": "newsecret"})
    result2 = await fixture.hass.config_entries.flow.async_configure(
        init_result2["flow_id"],
        user_input=new_credentials,
    )
    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "reauth_successful"

    # Verify the entry was updated
    updated_entry = fixture.hass.config_entries.async_get_entry(result["result"].entry_id)
    assert updated_entry is not None
    assert updated_entry.data["username"] == new_credentials["username"]
    assert updated_entry.data["password"] == new_credentials["password"]


@pytest.mark.e2e
@pytest.mark.parametrize("exception_type", ["invalid_auth", "cannot_connect", "unknown"])
async def test_step_reauth_errors(
    fixture: HomeAssistantFixture,
    exception_type: str,
) -> None:
    """Test that errors are handled correctly in the reauth flow."""

    fixture.voltalis_server.given_login_ok()

    credentials = {
        "username": "test@example.com",
        "password": "secret",
    }

    # Start the first flow and create an entry
    init_result = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "user"

    # Submit user input to complete the first flow
    result = await fixture.hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=credentials,
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Now configure the server to fail auth for reauth
    fixture.voltalis_server.given_login_failure(exception_type)

    # Start a reauth flow
    init_result2 = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_REAUTH, "entry_id": result["result"].entry_id}
    )
    assert init_result2["type"] == FlowResultType.FORM
    assert init_result2["step_id"] == "reauth"

    # Submit new credentials - should show form with error because authentication failed
    new_credentials = credentials.copy()
    new_credentials.update({"password": "newsecret"})

    result2 = await fixture.hass.config_entries.flow.async_configure(
        init_result2["flow_id"],
        user_input=new_credentials,
    )
    assert result2["type"] == FlowResultType.FORM
    assert isinstance(result2["errors"], dict), result2["errors"]
    # Note: "unknown" error type in this test will also result in "cannot_connect" error
    # because HTTP 500 errors from a real server become HttpClientException which maps to "cannot_connect"
    expected_error = "cannot_connect" if exception_type == "unknown" else exception_type
    assert result2["errors"]["base"] == expected_error

    # Verify the entry was NOT updated (since auth failed)
    updated_entry = fixture.hass.config_entries.async_get_entry(result["result"].entry_id)
    assert updated_entry is not None
    assert updated_entry.data["username"] == credentials["username"]
    assert updated_entry.data["password"] == credentials["password"]


@pytest.mark.e2e
async def test_options_flow_init_shows_form(fixture: HomeAssistantFixture) -> None:
    """Test options flow shows form when user_input is None."""

    fixture.voltalis_server.given_login_ok()

    credentials = {
        "username": "test@example.com",
        "password": "secret",
    }

    # Start the config flow and create an entry
    init_result = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await fixture.hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=credentials,
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Start the options flow
    entry = result["result"]
    options_result = await fixture.hass.config_entries.options.async_init(entry.entry_id)
    assert options_result["type"] == FlowResultType.FORM
    assert options_result["step_id"] == "init"
    assert options_result["data_schema"] is not None

    # Check that the schema contains the expected fields
    schema_keys = [key.schema for key in options_result["data_schema"].schema.keys()]
    assert "log_level" in schema_keys
    assert "climate_min_temp" in schema_keys
    assert "climate_max_temp" in schema_keys
    assert "default_temp" in schema_keys
    assert "default_away_temp" in schema_keys
    assert "default_eco_temp" in schema_keys
    assert "default_comfort_temp" in schema_keys
    assert "default_water_heater_temp" in schema_keys

    # Submit None to keep the form displayed
    result2 = await fixture.hass.config_entries.options.async_configure(
        options_result["flow_id"],
        user_input=None,
    )
    assert result2["type"] == FlowResultType.FORM


@pytest.mark.e2e
async def test_options_flow_creates_entry(fixture: HomeAssistantFixture) -> None:
    """Test options flow creates entry successfully."""

    fixture.voltalis_server.given_login_ok()

    credentials = {
        "username": "test@example.com",
        "password": "secret",
    }

    # Start the config flow and create an entry
    init_result = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await fixture.hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=credentials,
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Start the options flow
    entry = result["result"]
    options_result = await fixture.hass.config_entries.options.async_init(entry.entry_id)
    assert options_result["type"] == FlowResultType.FORM
    assert options_result["step_id"] == "init"

    # Submit options data
    options_data = {
        "log_level": "info",
        "climate_min_temp": 7.0,
        "climate_max_temp": 30.0,
        "default_temp": 19.0,
        "default_away_temp": 16.0,
        "default_eco_temp": 17.0,
        "default_comfort_temp": 20.0,
        "default_water_heater_temp": 55.0,
    }
    result2 = await fixture.hass.config_entries.options.async_configure(
        options_result["flow_id"],
        user_input=options_data,
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"] == options_data


@pytest.mark.e2e
async def test_options_flow_with_existing_options(fixture: HomeAssistantFixture) -> None:
    """Test options flow loads existing options as defaults."""

    fixture.voltalis_server.given_login_ok()

    credentials = {
        "username": "test@example.com",
        "password": "secret",
    }

    # Start the config flow and create an entry
    init_result = await fixture.hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await fixture.hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input=credentials,
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Start the first options flow and set some options
    entry = result["result"]
    options_result = await fixture.hass.config_entries.options.async_init(entry.entry_id)
    assert options_result["type"] == FlowResultType.FORM

    # Submit options data
    options_data = {
        "log_level": "debug",
        "climate_min_temp": 10.0,
        "climate_max_temp": 25.0,
        "default_temp": 18.0,
        "default_away_temp": 15.0,
        "default_eco_temp": 16.0,
        "default_comfort_temp": 21.0,
        "default_water_heater_temp": 60.0,
    }
    result2 = await fixture.hass.config_entries.options.async_configure(
        options_result["flow_id"],
        user_input=options_data,
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY

    # Start the options flow again to verify defaults are loaded from existing options
    options_result2 = await fixture.hass.config_entries.options.async_init(entry.entry_id)
    assert options_result2["type"] == FlowResultType.FORM
    assert options_result2["step_id"] == "init"

    # Verify that the defaults match our previously saved options
    # We need to check the default values in the schema
    assert options_result2["data_schema"] is not None
    schema = options_result2["data_schema"].schema
    schema_dict = {}
    for key in schema:
        if hasattr(key, "default"):
            schema_dict[key.schema] = key.default()

    assert schema_dict["log_level"] == "debug"
    assert schema_dict["climate_min_temp"] == 10.0
    assert schema_dict["climate_max_temp"] == 25.0
    assert schema_dict["default_temp"] == 18.0
    assert schema_dict["default_away_temp"] == 15.0
    assert schema_dict["default_eco_temp"] == 16.0
    assert schema_dict["default_comfort_temp"] == 21.0
    assert schema_dict["default_water_heater_temp"] == 60.0


# We can't use the module-level because of the hass fixture scope
pytestmark = [pytest.mark.asyncio(loop_scope="function"), pytest.mark.enable_socket]


# We can't use the module-level because of the hass fixture scope
@pytest.fixture(scope="function")
async def fixture_all() -> AsyncGenerator[HomeAssistantFixture, None]:
    """
    Before all tests, start the server.
    Then after all tests, stop the server.
    """
    fixture = HomeAssistantFixture()
    await fixture.async_before_all()
    yield fixture
    await fixture.async_after_all()


@pytest.fixture(scope="function")
async def fixture(
    fixture_all: HomeAssistantFixture,
    hass: HomeAssistant,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[HomeAssistantFixture, None]:
    """Before each test, initialize the collection."""
    await fixture_all.async_before_each()
    fixture_all.setup_before_test(hass=hass, monkeypatch=monkeypatch)
    yield fixture_all
