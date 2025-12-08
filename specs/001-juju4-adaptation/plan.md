# Implementation Plan: Juju 4 Adaptation

**Branch**: `001-juju4-adaptation` | **Date**: 2025-12-08 | **Spec**: [specs/001-juju4-adaptation/spec.md](specs/001-juju4-adaptation/spec.md)
**Input**: Feature specification from `/specs/001-juju4-adaptation/spec.md`

## Summary

This plan covers the adaptation of `python-libjuju` to support Juju 4. The primary focus is removing the dependency on the global `AllWatcher` for event tracking, enforcing the use of `base` over `series` for deployments, and ensuring robust connection handling with Juju 4 controllers. This is a foundational refactor to align with Juju 4's architectural changes while maintaining backward compatibility where possible (though Juju 4 is the priority).

## Technical Context

**Language/Version**: Python 3.8 - 3.13
**Primary Dependencies**: `websockets`, `juju` (internal generated clients), `macaroonbakery`
**Storage**: N/A (Client library)
**Testing**: `tox`, `pytest` (Integration tests against Juju 4 controller)
**Target Platform**: Linux, macOS, Windows (Client)
**Project Type**: Python Library
**Performance Goals**: `wait_for_idle` must return within 5s of state change.
**Constraints**: Must not use `AllWatcher` on Juju 4. Must support `base` argument.
**Schema Generation**: Requires adding `schemas-juju-4.x.x.json` and updating `facade_versions.py`.

## Constitution Check

*GATE: Passed.*
- **No AllWatcher Dependency**: Plan explicitly replaces `AllWatcher` with polling/targeted watchers for Juju 4.
- **Robust Integration Testing**: Plan includes updates to `wait_for_idle` to ensure stability.
- **Code Hygiene**: New code will be type-hinted.
- **Modern Juju Concepts**: `base` is enforced, `series` deprecated.

## Project Structure

### Documentation (this feature)

```text
specs/001-juju4-adaptation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output (API signatures)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
juju/
├── client/
│   ├── connection.py    # Handshake updates
│   └── ...
├── model/
│   ├── __init__.py      # Model class updates (deploy, watch)
│   └── ...
└── ...
```

**Structure Decision**: Modifying existing library structure. No new top-level directories.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Dual Watcher Logic | Need to support Juju 4 (No AllWatcher) while potentially keeping Juju 3 support (AllWatcher) or just for architectural cleanliness. | Dropping Juju 3 support entirely might be too aggressive for a single PR, but we are prioritizing Juju 4. |
