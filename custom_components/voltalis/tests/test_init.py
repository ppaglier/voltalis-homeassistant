"""E2E tests for the Voltalis integration initialization."""

from collections.abc import AsyncGenerator

import pytest
from homeassistant.core import HomeAssistant

from custom_components.voltalis.apps.home_assistant.tests.home_assistant_fixture import HomeAssistantFixture
from custom_components.voltalis.const import DOMAIN


@pytest.mark.e2e
async def test_integration_setup(fixture: HomeAssistantFixture) -> None:
    """Test that the integration is set up correctly."""

    # Verify the config entry exists
    entries = fixture.hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    # Verify the entry is loaded
    entry = entries[0]
    assert entry.state.name == "LOADED"


@pytest.mark.e2e
async def test_platforms_loaded(fixture: HomeAssistantFixture) -> None:
    """Test that all platforms are loaded."""

    # Check that entities from each platform are created
    all_states = fixture.hass.states.async_all()

    # Check for climate entities
    climate_entities = [state for state in all_states if state.entity_id.startswith("climate.")]
    assert len(climate_entities) > 0

    # Check for sensor entities
    sensor_entities = [state for state in all_states if state.entity_id.startswith("sensor.")]
    assert len(sensor_entities) > 0

    # Check for switch entities
    switch_entities = [state for state in all_states if state.entity_id.startswith("switch.")]
    assert len(switch_entities) > 0

    # Check for select entities
    select_entities = [state for state in all_states if state.entity_id.startswith("select.")]
    assert len(select_entities) > 0

    # Check for water_heater entities
    water_heater_entities = [state for state in all_states if state.entity_id.startswith("water_heater.")]
    assert len(water_heater_entities) > 0


@pytest.mark.e2e
async def test_integration_unload(fixture: HomeAssistantFixture) -> None:
    """Test that the integration can be unloaded."""

    # Get the config entry
    entries = fixture.hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    entry = entries[0]

    # Unload the integration
    result = await fixture.hass.config_entries.async_unload(entry.entry_id)
    assert result is True

    # Verify entry is now unloaded
    assert entry.state.name == "NOT_LOADED"


@pytest.mark.e2e
async def test_config_entry_update_listener(fixture: HomeAssistantFixture) -> None:
    """Test that the config entry update listener works."""

    # Get the config entry
    entries = fixture.hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    entry = entries[0]

    # Verify entry is loaded
    assert entry.state.name == "LOADED"

    # Update the entry options (this triggers the update listener)
    fixture.hass.config_entries.async_update_entry(entry, options={"test_option": "test_value"})

    # Trigger the update listener by reloading
    result = await fixture.hass.config_entries.async_reload(entry.entry_id)
    assert result is True

    # Verify entry is still loaded after reload
    assert entry.state.name == "LOADED"


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
    fixture_all.init_provider_with_data()
    await fixture_all.configure_entry()
    yield fixture_all
