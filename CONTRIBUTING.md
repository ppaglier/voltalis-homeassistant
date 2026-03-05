# Contributing

We would love for you to contribute and help make it even better than it is today! As a contributor, here are the guidelines we would like you to follow.

## Table of Contents

- [Getting Started](#getting-started)
- [Contributing via Fork](#contributing-via-fork)
- [Development Workflow](#development-workflow)
- [Code Quality](#code-quality)
- [Testing](#testing)
- [Commits and Pull Requests](#commits-and-pull-requests)
- [Release Process](#release-process)

## Getting Started

### Prerequisites

- Python 3.13+
- Poetry (for dependency management)
- A Home Assistant instance for testing (optional but recommended)

### Local Setup

1. Clone the repository:

```bash
git clone https://github.com/ppaglier/voltalis-homeassistant.git
cd voltalis-homeassistant
```

2. Install dependencies:

```bash
poetry install
```

3. Verify the setup:

```bash
poetry run task lint
poetry run task typecheck
poetry run task test:all
```

## Contributing via Fork

If you don't have direct access to the repository, you can contribute by forking and submitting a pull request:

### 1. Fork the Repository

Click the "Fork" button on GitHub to create your own copy of the repository.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/voltalis-homeassistant.git
cd voltalis-homeassistant
```

### 3. Add Upstream Remote

To keep your fork in sync with the original repository:

```bash
git remote add upstream https://github.com/ppaglier/voltalis-homeassistant.git
```

### 4. Create a Feature Branch

```bash
git checkout -b feature/my-feature
```

### 5. Keep Your Fork Updated

Before starting work, sync with upstream:

```bash
git fetch upstream
git checkout dev
git merge upstream/dev
```

### 6. Make Your Changes

Follow the [Development Workflow](#development-workflow) section below.

### 7. Push and Create a Pull Request

```bash
git push origin feature/my-feature
```

Then go to your fork on GitHub and click "Create Pull Request". Target the `dev` branch.

## Development Workflow

### Run Tests

```bash
# Unit tests only
poetry run task test:unit

# Integration tests only
poetry run task test:integration

# E2E tests only
poetry run task test:e2e

# All tests (with coverage)
poetry run task test:cov:check

# Check for tests without markers
poetry run task test:miss
```

### Code Quality

Before committing, ensure your code passes all checks:

```bash
# Linting
poetry run task lint

# Fix linting issues automatically
poetry run task lint:fix

# Format check
poetry run task format

# Fix formatting automatically
poetry run task format:fix

# Type checking
poetry run task typecheck
```

### Recommended Workflow

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Format and fix issues:
   ```bash
   poetry run task format:fix
   poetry run task lint:fix
   ```
4. Run tests:
   ```bash
   poetry run task test:all
   ```
5. Type check:
   ```bash
   poetry run task typecheck
   ```
6. Commit your changes with a clear message
7. Push and create a Pull Request

## Code Quality

### Type Safety

- **All code must have type hints.** Mypy is configured in strict mode.
- Use Python 3.14+ syntax where applicable.

### Line Length

- Keep lines under 120 characters.

### Docstrings

- Add docstrings to public functions, classes, and modules.
- Follow standard Python docstring conventions.

### Imports

- Keep imports organized: stdlib → third-party → local
- Use absolute imports (no relative imports from custom_components)

## Testing

### Test Markers

All tests **must** be marked with one of these pytest markers:
- `@pytest.mark.unit` - Unit tests for lib layer (domain, application, helpers)
- `@pytest.mark.integration` - Integration tests for infrastructure providers
- `@pytest.mark.e2e` - End-to-end tests for Home Assistant integration

Example:

```python
@pytest.mark.unit
def test_device_builder_creates_valid_device() -> None:
    """Test that DeviceBuilder creates a valid Device."""
    # ...

@pytest.mark.integration
async def test_voltalis_provider_fetches_devices() -> None:
    """Test that VoltalisProvider can fetch devices from API."""
    # ...

@pytest.mark.e2e
async def test_climate_entity_setup() -> None:
    """Test that climate entities are created for heater devices."""
    # ...
```

### Coverage Requirements

- **Minimum 95%** test coverage required.
- Use `poetry run task test:cov:check` to verify.

### Writing Tests

1. **Unit tests**: Focus on lib layer handlers, domain models, and business logic. Use stubs for dependencies.
2. **Integration tests**: Test providers against real HTTP mocks (MockHttpServer).
3. **E2E tests**: Test full Home Assistant flows using HomeAssistantFixture.

See [custom_components/voltalis/lib/application/devices_management/tests](custom_components/voltalis/lib/application/devices_management/tests) for examples of good fixtures.

## Commits and Pull Requests

### Commit Messages

- Use clear, descriptive messages: `"feat: add preset mode support for climate entities"`
- Reference issues when applicable: `"fix: resolve 401 retry logic (#42)"`

### Pull Request Guidelines

1. **Keep PRs focused and reviewable.** Break large changes into smaller PRs.
2. **Add a description** explaining what changed and why.
3. **Reference related issues** if applicable.
4. **Ensure all CI checks pass** (tests, lint, type check).

## Release Process

### Versioning

We follow **Semantic Versioning** (MAJOR.MINOR.PATCH):
- `MAJOR`: Breaking changes to Home Assistant compatibility or API
- `MINOR`: New features (backwards compatible)
- `PATCH`: Bug fixes

### Release Workflow

#### Pre-release Flow

1. **Create a pre-release branch** (e.g., `release/0.X.Y-beta`):
   - Update version in `pyproject.toml` (top of file) and `manifest.json`

2. **Create and merge PR**:
   - Open a PR into `dev`
   - Get reviewed and merge it

3. **Create the GitHub Release**:
   - Go to [Releases](https://github.com/ppaglier/voltalis-homeassistant/releases)
   - Click "Create a new release"
   - Tag: `0.X.Y-beta` (matching the version you updated)
   - Title: `0.X.Y-beta`
   - Description: Use the [Release Template](.github/RELEASE_TEMPLATE.md)
   - **Target**: Select `dev` branch
   - **Check**: "Set as a pre-release"
   - Publish the release

4. **GitHub Actions** will automatically build and publish the pre-release

#### Stable Release Flow

1. **Create a release branch** (e.g., `release/0.X.Y`):
   - Update version in `pyproject.toml` (top of file) and `manifest.json`

2. **Create and merge PR**:
   - Open a PR into `dev`
   - Get reviewed and merge it

3. **Merge to main**:
   - Create a PR from `dev` → `main`
   - Review and merge it

4. **Create the GitHub Release**:
   - Go to [Releases](https://github.com/ppaglier/voltalis-homeassistant/releases)
   - Click "Create a new release"
   - Tag: `0.X.Y` (matching the version you updated)
   - Title: `0.X.Y`
   - Description: Use the [Release Template](.github/RELEASE_TEMPLATE.md)
   - **Target**: Select `main` branch
   - Publish the release

5. **GitHub Actions** will automatically build and publish the release

### Release Notes

All release notes are managed in [GitHub Releases](https://github.com/ppaglier/voltalis-homeassistant/releases).

Use the [Release Template](.github/RELEASE_TEMPLATE.md) when creating a new release.

## Questions?

If you have questions or need help, open an issue or a discussion on GitHub.

Thank you for contributing! 🎉