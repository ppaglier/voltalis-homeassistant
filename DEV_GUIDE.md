# Developer Guide

This guide provides technical information for developers contributing to the Voltalis Home Assistant integration.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Setting Up Development Environment](#setting-up-development-environment)
- [Running and Debugging](#running-and-debugging)
- [Key Concepts](#key-concepts)
- [Troubleshooting](#troubleshooting)

## Architecture Overview

The integration follows **Domain-Driven Design (DDD)** with three main layers:

### 1. Domain Layer (`lib/domain/`)

Pure business logic with no external dependencies. Contains:
- **Models**: Device, EnergyContract, Program, ManualSetting
- **Enums**: DeviceTypeEnum, DeviceModeEnum, HVACModeEnum
- **Builders**: DeviceBuilder, EnergyContractBuilder, etc.
- **Exceptions**: VoltalisException, VoltalisAuthenticationException, etc.

### 2. Application Layer (`lib/application/`)

Use-case handlers that orchestrate domain logic and coordinate with providers:
- **Handlers**: GetDevicesHandler, SetDevicePresetHandler, GetLiveConsumptionHandler
- **Commands**: Action requests (e.g., SetDeviceTemperatureCommand)
- **Queries**: Data retrieval (e.g., GetDevicesQuery)
- **DTOs**: Data transfer objects for API responses

### 3. Infrastructure Layer (`lib/infrastructure/`)

External integrations (API clients, database, providers):
- **Providers**: VoltalisClientAiohttp, VoltalisProviderVoltalisApi, DateProviderReal
- **DTOs**: API request/response models
- **Tests**: Mock implementations (stubs) for testing

### Home Assistant Integration Layer (`apps/home_assistant/`)

Home Assistant specific code:
- **Coordinators**: DataUpdateCoordinator subclasses for polling and error recovery
- **Entities**: Climate, Sensor, Switch, Select, WaterHeater
- **Config Flow**: User configuration and authentication
- **Module**: Dependency injection and setup

## Setting Up Development Environment

### 1. Clone and Install

```bash
git clone https://github.com/ppaglier/voltalis-homeassistant.git
cd voltalis-homeassistant
poetry install
```

### 2. Verify Installation

```bash
poetry run task lint
poetry run task typecheck
poetry run task test:all
```

### 3. Start Home Assistant with Docker

```bash
docker compose up
```

This starts:
- Home Assistant on `http://localhost:8123`
- The integration is automatically mounted as a custom component

### 4. IDE Setup

**VSCode** (recommended):
- Install Python extension
- Install Pylance extension
- Install MyPy extension
- Project will auto-configure from pyproject.toml

**PyCharm**:
- Open the project folder
- PyCharm auto-detects the Poetry environment
- Configure run configuration for `poetry run task ...`

## Running and Debugging

### Run Tests

```bash
# All tests with coverage
poetry run task test:cov:check

# Specific test category
poetry run task test:unit
poetry run task test:integration
poetry run task test:e2e

# Single test
pytest custom_components/voltalis/lib/application/devices_management/tests/handlers/devices/test_get_devices_handler.py -v

# With debug output
pytest custom_components/voltalis/tests/test_climate.py -v -s
```

### Type Checking

```bash
# Check all types
poetry run task typecheck

# Check specific file
mypy custom_components/voltalis/lib/domain/devices_management/devices/device.py
```

### Linting

```bash
# Check all issues
poetry run task lint

# Fix issues automatically
poetry run task lint:fix

# Check specific file
ruff check custom_components/voltalis/climate.py --fix
```

### Format Code

```bash
# Check formatting
poetry run task format

# Fix formatting
poetry run task format:fix
```

### Docker Compose

```bash
# Start Home Assistant (detached)
docker compose up -d

# View logs
docker compose logs -f home-assistant

# Stop
docker compose down

# Clean volume
docker compose down -v
```

### Debug Home Assistant

Home Assistant is run in the container with the integration mounted. To debug:

1. Check logs: `docker compose logs -f home-assistant`
2. Access UI: `http://localhost:9123`
3. Add the Voltalis integration via Settings > Devices & Services
4. Check integration logs in Home Assistant logs

### Print Debugging

Add this to print debug output in tests:

```python
@pytest.mark.unit
def test_something(fixture: DeviceManagementFixture, capsys) -> None:
    """Test with print debugging."""
    print("Debug info here")
    # Test code
    captured = capsys.readouterr()
    print(captured.out)
```

## Key Concepts

### Coordinators

Coordinators in `apps/home_assistant/coordinators/` manage API polling and error recovery:

```python
class VoltalisDeviceCoordinator(BaseVoltalisCoordinator[dict[int, DeviceDto]]):
    async def _get_data(self) -> dict[int, DeviceDto]:
        result = await self._voltalis_module.get_devices_handler.handle()
        return result
```

**Key features**:
- Automatic retry with exponential backoff
- Handles 401 errors with reauth flow
- Logs errors once (not spammy)
- Updates all subscribed entities

### Handlers

Handlers in `lib/application/` implement business logic:

```python
class GetDevicesHandler:
    async def handle(self) -> dict[int, Device]:
        """Fetch and return devices."""
```

Handlers are tested with **unit + integration tests**.

### Entities

Entities in `apps/home_assistant/entities/` connect to Home Assistant:

```python
class VoltalisClimate(ClimateEntity):
    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode via coordinator."""
```

Entities are tested with **E2E tests** using HomeAssistantFixture.

### Fixtures

Test fixtures provide DRY, readable test setup:

```python
@pytest.mark.unit
def test_get_devices(fixture: DeviceManagementFixture) -> None:
    # given
    fixture.given_devices([device1, device2])

    # when
    result = await fixture.get_devices_handler.handle()

    # then
    fixture.then_devices_should_be({1: device1, 2: device2})
```

## Troubleshooting

### Poetry Lock Issues

```bash
# Remove lock and reinstall
rm poetry.lock
poetry install
```

### Type Check Fails but Tests Pass

This usually means:
- Missing type hints on a function
- Incorrect import path
- Environment mismatch

Run:

```bash
mypy custom_components --show-error-codes
```

### Docker Compose Issues

```bash
# Ensure containers are stopped
docker compose down

# Rebuild images
docker compose build --no-cache

# Start fresh
docker compose up
```

### Test Isolation Issues

If tests fail in CI but pass locally:

```bash
# Run tests in isolation
pytest --forked custom_components/voltalis/tests/

# Clear pytest cache
pytest --cache-clear
```

### Home Assistant Not Loading Integration

1. Check container logs: `docker compose logs home-assistant`
2. Ensure manifest.json is valid JSON
3. Check config_flow.py syntax
4. Restart Home Assistant: `docker compose restart home-assistant`

## Further Reading

- [Domain-Driven Design basics](https://www.domainlanguage.com/ddd/)
- [Home Assistant integration documentation](https://developers.home-assistant.io/docs/creating_integrations_intro/)
- [Pydantic validation](https://docs.pydantic.dev/latest/)
- [Pytest best practices](https://docs.pytest.org/en/stable/goodpractices.html)

## Security & Observability Checklist

When adding features, ensure:

### Security
- ✅ Credentials stored in Home Assistant config entries (encrypted at rest)
- ✅ Passwords/tokens use `Pydantic.SecretStr` (auto-masked in logs)
- ✅ All API responses validated with Pydantic (reject unexpected fields)
- ✅ No credentials or tokens logged (even with `%s`)
- ✅ HTTPS enforced for all API calls

### Observability
- ✅ Coordinators use `_was_unavailable` flag to prevent log spam
- ✅ Errors logged with appropriate levels (not all INFO)
- ✅ User-facing errors are actionable (not internal details)
- ✅ No full payload logging (only status codes or error messages)

### Error Handling
- ✅ Use Voltalis exceptions (VoltalisAuthenticationException, VoltalisConnectionException, etc.)
- ✅ Handle 401 errors with automatic reauth flow
- ✅ Graceful degradation (entities become `unavailable` not crashed)
- ✅ Clear error types mapped in coordinators

See the code for live examples:
- Secure client: [voltalis_client_aiohttp.py](custom_components/voltalis/lib/infrastructure/providers/voltalis_client_aiohttp.py)
- Error handling: [coordinators/base.py](custom_components/voltalis/apps/home_assistant/coordinators/base.py)
- Validation: [voltalis_provider_voltalis_api.py](custom_components/voltalis/lib/infrastructure/providers/voltalis_provider_voltalis_api.py)
