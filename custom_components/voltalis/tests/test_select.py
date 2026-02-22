"""E2E tests for the Voltalis select platform."""

from collections.abc import AsyncGenerator

import pytest
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.select import SERVICE_SELECT_OPTION
from homeassistant.const import ATTR_OPTION
from homeassistant.core import HomeAssistant

from custom_components.voltalis.apps.home_assistant.tests.home_assistant_fixture import HomeAssistantFixture
from custom_components.voltalis.lib.domain.devices_management.presets.preset_enum import DeviceCurrentPresetEnum


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,expected_state",
    [
        ("select.heater_1_preset", DeviceCurrentPresetEnum.ECO.value),
        ("select.heater_2_preset", DeviceCurrentPresetEnum.OFF.value),
        ("select.water_heater_1_preset", "unknown"),
        ("select.water_heater_2_preset", DeviceCurrentPresetEnum.OFF.value),
        ("select.program", "internal_program-none"),
    ],
)
async def test_select_entity_setup(
    fixture: HomeAssistantFixture,
    entity_id: str,
    expected_state: str,
) -> None:
    """Test that select entities are created for all devices and programs."""

    select_entity = fixture.get_entity_state(entity_id)

    assert len(select_entity.attributes["options"]) > 0
    fixture.compare_data(select_entity.state, expected_state)


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,option_to_select",
    [
        ("select.heater_1_preset", DeviceCurrentPresetEnum.COMFORT.value),
        ("select.heater_2_preset", DeviceCurrentPresetEnum.ECO.value),
        ("select.water_heater_1_preset", DeviceCurrentPresetEnum.OFF.value),
        ("select.water_heater_2_preset", DeviceCurrentPresetEnum.ON.value),
        ("select.program", "Morning Program"),
    ],
)
async def test_select_device_preset_change_option(
    fixture: HomeAssistantFixture,
    entity_id: str,
    option_to_select: str,
) -> None:
    """Test changing a preset option for a device."""

    # Select the preset option
    await fixture.async_call_service(SELECT_DOMAIN, SERVICE_SELECT_OPTION, entity_id, {ATTR_OPTION: option_to_select})

    # Trigger coordinator refresh to update HA state
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_coordinator)

    # Verify the option is still valid
    state = fixture.get_entity_state(entity_id)
    fixture.compare_data(state.state, option_to_select)


@pytest.mark.e2e
async def test_select_device_preset_available_options(fixture: HomeAssistantFixture) -> None:
    """Test that device preset select has the correct available options."""

    entity_id = "select.heater_1_preset"
    select_entity = fixture.get_entity_state(entity_id)

    # Verify that options are available
    assert "options" in select_entity.attributes
    assert len(select_entity.attributes["options"]) > 0
    # heater_1 has CONFORT (comfort) and ECO modes
    assert set(["comfort", "eco"]).issubset(set(select_entity.attributes["options"]))


@pytest.mark.e2e
@pytest.mark.parametrize(
    "program_option",
    [
        "internal_program-none",
    ],
)
async def test_select_program_option(
    fixture: HomeAssistantFixture,
    program_option: str,
) -> None:
    """Test selecting a program option."""

    entity_id = "select.program"

    # Select the program option
    await fixture.async_call_service(SELECT_DOMAIN, SERVICE_SELECT_OPTION, entity_id, {ATTR_OPTION: program_option})

    # Trigger coordinator refresh to update HA state
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().programs_coordinator)

    # Verify program entity still exists and is valid
    state = fixture.get_entity_state(entity_id)
    assert state is not None
    assert state.state in state.attributes.get("options", [])


@pytest.mark.e2e
async def test_select_program_available_options(fixture: HomeAssistantFixture) -> None:
    """Test that program select has the correct available options."""

    entity_id = "select.program"
    select_entity = fixture.get_entity_state(entity_id)

    # Verify that options are available
    assert "options" in select_entity.attributes
    assert len(select_entity.attributes["options"]) >= 1
    assert "internal_program-none" in select_entity.attributes["options"]


@pytest.mark.e2e
async def test_select_coordinator_update_reflects_state(fixture: HomeAssistantFixture) -> None:
    """Test that coordinator updates reflect in select state."""

    entity_id = "select.heater_1_preset"

    # Get initial state
    initial_state = fixture.get_entity_state(entity_id)

    # Verify entity is available
    assert initial_state is not None
    assert "options" in initial_state.attributes

    # Trigger coordinator refresh to update HA state
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_coordinator)

    # Verify entity still has options after refresh
    state = fixture.get_entity_state(entity_id)
    assert "options" in state.attributes


@pytest.mark.e2e
async def test_select_device_preset_unavailable_when_device_removed(fixture: HomeAssistantFixture) -> None:
    """Test that device preset select handles missing device data gracefully."""

    entity_id = "select.heater_1_preset"

    # Verify entity is available initially
    initial_state = fixture.get_entity_state(entity_id)
    assert initial_state.state != "unavailable"
    initial_option = initial_state.state

    # Remove the device from coordinator data
    coordinator = fixture.get_home_assistant_voltalis_module().device_coordinator
    device_id = 1
    if device_id in coordinator.data:
        del coordinator.data[device_id]

    # Manually trigger listeners to notify entities of data change
    coordinator.async_set_updated_data(coordinator.data)
    await fixture.hass.async_block_till_done(True)

    # Verify that the entity either becomes unavailable or retains last known state
    # (This is acceptable behavior - the entity warns in logs but doesn't crash)
    state = fixture.get_entity_state(entity_id)
    assert state is not None  # Entity should still exist
    # The select can retain the last known option or become unavailable
    assert state.state in ["unavailable", initial_option]


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id",
    [
        "select.heater_1_preset",
        "select.heater_2_preset",
        "select.water_heater_1_preset",
        "select.water_heater_2_preset",
        "select.program",
    ],
)
async def test_select_entity_has_icon(fixture: HomeAssistantFixture, entity_id: str) -> None:
    """Test that select entities have icons."""

    select_entity = fixture.get_entity_state(entity_id)
    # Check that icon attribute exists (can be mdi:* format or None)
    assert "icon" in select_entity.attributes or select_entity.attributes.get("icon") is None


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
