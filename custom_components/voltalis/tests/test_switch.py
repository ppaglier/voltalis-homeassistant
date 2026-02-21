"""E2E tests for the Voltalis switch platform."""

from collections.abc import AsyncGenerator

import pytest
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import SERVICE_TURN_OFF, SERVICE_TURN_ON, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant

from custom_components.voltalis.apps.home_assistant.tests.home_assistant_fixture import HomeAssistantFixture


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,expected_state",
    [
        ("switch.heater_1_device_switch", STATE_ON),
        ("switch.heater_2_device_switch", STATE_OFF),
        ("switch.water_heater_1_device_switch", STATE_ON),
        ("switch.water_heater_2_device_switch", STATE_OFF),
    ],
)
async def test_switch_entity_setup(
    fixture: HomeAssistantFixture,
    entity_id: str,
    expected_state: str,
) -> None:
    """Test that switch entities are created for all devices."""

    switch_entity = fixture.get_entity_state(entity_id)
    fixture.compare_data(switch_entity.state, expected_state)


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,service,expected_state",
    [
        ("switch.heater_1_device_switch", SERVICE_TURN_OFF, STATE_OFF),  # ON -> OFF
        ("switch.heater_2_device_switch", SERVICE_TURN_ON, STATE_ON),  # OFF -> ON
        ("switch.heater_1_device_switch", SERVICE_TURN_ON, STATE_ON),  # ON -> ON
        ("switch.heater_2_device_switch", SERVICE_TURN_OFF, STATE_OFF),  # OFF -> OFF
    ],
)
async def test_switch_turn_on(
    fixture: HomeAssistantFixture,
    entity_id: str,
    service: str,
    expected_state: str,
) -> None:
    """Test turning on a switch entity."""

    # Turn on the switch
    await fixture.async_call_service(SWITCH_DOMAIN, service, entity_id)

    # Trigger coordinator refresh to update HA state
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_coordinator)

    # Verify state changed in HA
    state = fixture.get_entity_state(entity_id)
    fixture.compare_data(state.state, expected_state)


@pytest.mark.e2e
async def test_switch_coordinator_update_reflects_state(fixture: HomeAssistantFixture) -> None:
    """Test that coordinator updates reflect in switch state."""

    entity_id = "switch.heater_1_device_switch"
    state = fixture.get_entity_state(entity_id)
    state.state = STATE_OFF  # Simulate external change to OFF

    # Trigger coordinator refresh to update HA state
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_coordinator)

    # Verify state is consistent
    state = fixture.get_entity_state(entity_id)
    fixture.compare_data(state.state, STATE_ON)


@pytest.mark.e2e
async def test_switch_entity_handles_missing_device_data(fixture: HomeAssistantFixture) -> None:
    """Test that switch entity handles missing device data gracefully."""

    entity_id = "switch.heater_1_device_switch"

    # Verify entity is available initially
    initial_state = fixture.get_entity_state(entity_id)
    assert initial_state.state != "unavailable"

    # Remove the device from coordinator data
    coordinator = fixture.get_home_assistant_voltalis_module().device_coordinator
    device_id = 1
    if device_id in coordinator.data:
        del coordinator.data[device_id]

    # Manually trigger listeners to notify entities of data change
    coordinator.async_set_updated_data(coordinator.data)
    await fixture.hass.async_block_till_done(True)

    # Verify entity either becomes unavailable or retains state
    # (Entity should not crash when data is missing)
    state = fixture.get_entity_state(entity_id)
    assert state is not None


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
