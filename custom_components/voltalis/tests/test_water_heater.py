"""E2E tests for the Voltalis water heater platform."""

from collections.abc import AsyncGenerator

import pytest
from homeassistant.components.water_heater import (
    ATTR_AWAY_MODE,
    ATTR_OPERATION_MODE,
    SERVICE_SET_AWAY_MODE,
    SERVICE_SET_OPERATION_MODE,
)
from homeassistant.components.water_heater import DOMAIN as WATER_HEATER_DOMAIN
from homeassistant.const import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant

from custom_components.voltalis.apps.home_assistant.tests.home_assistant_fixture import HomeAssistantFixture
from custom_components.voltalis.lib.domain.devices_management.water_heaters.water_heater_current_operations_enum import (  # noqa: E501
    WaterHeaterCurrentOperationEnum,
)


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,expected_state",
    [
        ("water_heater.water_heater_1", WaterHeaterCurrentOperationEnum.ON),
        ("water_heater.water_heater_2", WaterHeaterCurrentOperationEnum.OFF),
    ],
)
async def test_water_heater_entity_setup(
    fixture: HomeAssistantFixture,
    entity_id: str,
    expected_state: WaterHeaterCurrentOperationEnum,
) -> None:
    """Test that water heater entities are created for all water heater devices."""

    water_heater_entity = fixture.get_entity_state(entity_id)
    fixture.compare_data(water_heater_entity.state, expected_state.value)


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,service,expected_state",
    [
        ("water_heater.water_heater_1", SERVICE_TURN_OFF, WaterHeaterCurrentOperationEnum.OFF),  # ON -> OFF
        ("water_heater.water_heater_2", SERVICE_TURN_ON, WaterHeaterCurrentOperationEnum.ON),  # OFF -> ON
    ],
)
async def test_water_heater_turn_on_off(
    fixture: HomeAssistantFixture,
    entity_id: str,
    service: str,
    expected_state: WaterHeaterCurrentOperationEnum,
) -> None:
    """Test turning on/off a water heater entity."""

    # Turn on/off the water heater
    await fixture.async_call_service(WATER_HEATER_DOMAIN, service, entity_id)

    # Trigger coordinator refresh to update HA state
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_coordinator)

    # Verify operation mode changed in HA
    state = fixture.get_entity_state(entity_id)
    fixture.compare_data(state.state, expected_state.value)


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,expected_state",
    [
        ("water_heater.water_heater_1", WaterHeaterCurrentOperationEnum.AUTO),
        ("water_heater.water_heater_1", WaterHeaterCurrentOperationEnum.OFF),
        ("water_heater.water_heater_1", WaterHeaterCurrentOperationEnum.ON),
    ],
)
async def test_water_heater_set_operation_mode(
    fixture: HomeAssistantFixture,
    entity_id: str,
    expected_state: WaterHeaterCurrentOperationEnum,
) -> None:
    """Test setting operation mode for a water heater entity."""

    # Set operation mode
    await fixture.async_call_service(
        WATER_HEATER_DOMAIN, SERVICE_SET_OPERATION_MODE, entity_id, {ATTR_OPERATION_MODE: expected_state.value}
    )

    # Trigger coordinator refresh to update HA state
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_coordinator)

    # Verify operation mode changed in HA
    state = fixture.get_entity_state(entity_id)
    print(state.attributes.get("operation_mode"), expected_state.value)
    fixture.compare_data(state.attributes.get("operation_mode"), expected_state.value)


@pytest.mark.e2e
async def test_water_heater_away_mode(fixture: HomeAssistantFixture) -> None:
    """Test away mode functionality for water heater."""

    entity_id = "water_heater.water_heater_1"

    # Enable away mode
    await fixture.async_call_service(WATER_HEATER_DOMAIN, SERVICE_SET_AWAY_MODE, entity_id, {ATTR_AWAY_MODE: True})

    # Trigger coordinator refresh to update HA state
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_coordinator)

    # Verify away mode is ON and operation is OFF
    state = fixture.get_entity_state(entity_id)
    fixture.compare_data(state.attributes.get("away_mode"), "on")
    fixture.compare_data(state.state, WaterHeaterCurrentOperationEnum.OFF.value)

    # Disable away mode
    await fixture.async_call_service(WATER_HEATER_DOMAIN, SERVICE_SET_AWAY_MODE, entity_id, {ATTR_AWAY_MODE: False})

    # Trigger coordinator refresh to update HA state
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_coordinator)

    # Verify away mode is OFF
    state = fixture.get_entity_state(entity_id)
    fixture.compare_data(state.attributes.get("away_mode"), "off")


@pytest.mark.e2e
async def test_water_heater_coordinator_update_reflects_state(fixture: HomeAssistantFixture) -> None:
    """Test that coordinator updates reflect in water heater state."""

    entity_id = "water_heater.water_heater_1"

    # Get initial state
    initial_state = fixture.get_entity_state(entity_id)
    initial_operation = initial_state.state

    # Trigger coordinator refresh to update HA state
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_coordinator)

    # Verify state is consistent
    state = fixture.get_entity_state(entity_id)
    fixture.compare_data(state.state, initial_operation)


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
