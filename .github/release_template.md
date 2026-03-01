# Release Template

Use this template when creating a new release on GitHub.

## Title

`v0.X.Y - YYYY-MM-DD`

## Description

```markdown
## What's New

### Added
- Feature 1
- Feature 2

### Fixed
- Bug fix 1
- Bug fix 2

### Changed
- Breaking change 1

### Deprecated
- Deprecation notice 1
```

## Instructions

1. Create a new release on GitHub: https://github.com/ppaglier/voltalis-homeassistant/releases/new
2. Set the tag to `v0.X.Y` (matching version in `pyproject.toml` and `manifest.json`)
3. Fill in the release title and description using the template above
4. Mark as "pre-release" if it's a release candidate (e.g., `0.6.0-rc.2`)
5. Publish the release
6. GitHub Actions will automatically build and publish the integration

## Changelog Format

Use **Keep a Changelog** format:
- **Added**: New features or capabilities
- **Fixed**: Bug fixes
- **Changed**: Changes to existing functionality (including breaking changes)
- **Deprecated**: Features marked for removal
- **Removed**: Features that were removed
- **Security**: Security fixes or improvements

## Example Release

```markdown
## v0.7.0 - 2026-03-15

### Added
- Support for device presets with quick mode switching
- Energy contract sensors for live consumption monitoring

### Fixed
- Resolved issue where sensor values were sometimes stale (#42)

### Changed
- **BREAKING**: Removed old `get_modes` handler (use presets instead)
```
