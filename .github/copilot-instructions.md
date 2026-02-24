# Voltalis Home Assistant - AI Agent Instructions

## Project Overview

Voltalis Home Assistant is a custom integration that connects Voltalis devices to Home Assistant. It exposes entities
for climate, water heater, sensors, switches, and selects, backed by a layered domain/application/infrastructure
library and Home Assistant specific coordinators and entities.

## Architecture

### Home Assistant integration layer

- **Entry point**: `custom_components/voltalis/__init__.py`
- **Config flow and options**: `custom_components/voltalis/config_flow.py`
- **Platforms**: climate, sensor, select, switch, water_heater
- **Coordinators**: centralize polling and error handling under `custom_components/voltalis/apps/home_assistant/coordinators`

### Library layer (DDD-style)

- **Domain models, enums, builders, exceptions**: `custom_components/voltalis/lib/domain`
- **Application handlers and commands**: `custom_components/voltalis/lib/application`
- **Infrastructure providers and DTOs**: `custom_components/voltalis/lib/infrastructure`

## Key Patterns

- Keep Home Assistant logic thin. Put domain rules in lib handlers.
- Prefer DataUpdateCoordinator for polling logic and error recovery.
- Use pydantic DTOs to validate API responses; raise VoltalisValidationException on invalid payloads.
- Use type hints everywhere. Mypy is strict in this repo.
- Keep line length <= 120.
- Default to ASCII in files unless the file already uses non-ASCII characters.

## Development Workflow

### Commands (Poetry + Taskipy)

```bash
# Setup
poetry install                    # Install dependencies
poetry run task lint              # Lint checks
poetry run task format            # Format checks
poetry run task typecheck         # Type checks
poetry run task test:unit         # Unit tests
poetry run task test:integration  # Integration tests
poetry run task test:e2e          # End-to-end tests
poetry run task test:cov:check    # Test coverage

# Docker Compose
docker compose up        # Start Home Assistant
```

### Critical Conventions

1. **User docs focus** - README.md and README.fr.md are for Home Assistant users only.
2. **Tech docs separation** - Developer guidance goes in a separate file (e.g., DEV_GUIDE.md).
3. **Tests markers** - Tests are separated by pytest markers: `unit`, `integration`, `e2e`. Every test must have at least one of these tags.
4. **Error handling** - Use Voltalis exceptions and surface actionable errors in coordinators.
5. **Types everywhere** - No untyped defs; keep mypy strict.

## Security and Privacy

- Never log credentials or tokens.
- Store secrets only in Home Assistant config entries.
- Handle API failures gracefully with actionable errors.

## Testing Strategy

- **Unit**: lib layer handlers and domain behavior
- **Integration**: providers and API client behavior
- **E2E**: Home Assistant flows and entities

## Review Checklist

- Changes are minimal and scoped.
- Tests cover new behavior or rationale is documented.
- User docs updated only when behavior changes are user-visible.
