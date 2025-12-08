<!--
Sync Impact Report:
- Version change: 0.2.0 -> 0.3.0
- List of modified principles: Mission & Scope (compatibility clause), Modern Juju Concepts (Base over Series scoped to Juju 4), No AllWatcher Dependency (scoped to Juju 4)
- Added sections: N/A (textual refinements only)
- Removed sections: N/A
- Templates requiring updates: N/A
- Follow-up TODOs: None
-->
# python-libjuju Constitution

> **Version:** 0.3.0
> **Ratified:** 2025-12-08
> **Last Amended:** 2025-12-08

## 1. Mission & Scope

**Mission:**
To provide a robust, Pythonic interface for interacting with Juju 4, adapting to architectural changes such as the removal of `AllWatcher` capabilities and the shift from `series` to `base`, while ensuring reliability for charm integration testing and maintaining compatibility with supported pre-4 Juju controllers where feasible.

**Scope:**
This constitution governs the development and maintenance of the `python-libjuju` library, specifically focusing on its adaptation for Juju 4 compatibility. It covers architectural decisions, coding standards, and testing requirements.

## 2. Core Principles

### Modern Juju Concepts
The library MUST align with Juju 4's architectural shifts:
- **Base over Series:** The concept of `series` (e.g., "focal") is deprecated. For connections to Juju 4 controllers, the library MUST use `base` (e.g., `ubuntu@22.04`) for all operations involving machine provisioning or charm deployment, and MUST reject `series` arguments. For older supported controllers, `series` MAY be accepted but SHOULD be treated as deprecated and, where possible, mapped to an appropriate `base`.
- **Secrets Management:** The library MUST support Juju's first-class Secrets API. Configuration-based secrets are considered legacy; the library MUST provide robust methods to create, grant, revoke, and remove secrets.

### No AllWatcher Dependency
For connections to Juju 4 controllers, the library MUST NOT rely on the `AllWatcher` facade or global event streams, as these are removed in Juju 4. It MUST implement targeted event listening or efficient polling mechanisms to track specific entity states (e.g., Applications, Units, Machines). For older supported controllers, existing `AllWatcher`-based paths MAY remain but SHOULD be minimized, treated as legacy, and gradually replaced by more targeted mechanisms where feasible.

### Robust Integration Testing Support
The library MUST be designed to support rigorous integration testing of charms (e.g., PostgreSQL, K8s charms). This implies:
- **Stability:** Connections MUST be resilient to network flakes and controller restarts.
- **Wait States:** Reliable `wait_for_idle` mechanisms MUST be provided to ensure charms have settled before assertions.
- **Cleanup:** Robust teardown of models and applications to prevent resource leaks in CI.
- **Debuggability:** Logs MUST be verbose enough to diagnose CI failures but structured enough to be parseable.

### Code Hygiene & Standards
The codebase MUST adhere to strict hygiene standards to ensure maintainability:
- **Type Hinting:** All new code MUST be fully type-hinted.
- **Linting:** Code MUST pass `flake8` and other configured linters (via `pre-commit`).
- **Documentation:** Public APIs MUST have docstrings.
- **Schema Management:** Updates to Juju schemas MUST follow the established process in `CONTRIBUTING.md` (generating clients via `make client`).

### Asynchronous Design
The library MUST maintain its asynchronous nature using Python's `asyncio`. Blocking operations MUST be avoided in the main event loop to ensure high concurrency performance, especially when managing multiple models or heavy integration suites.

## 3. Governance & Compliance

**Amendment Process:**
Amendments to this constitution require a Pull Request with a clear rationale and consensus from the maintainers.

**Versioning Policy:**
The library follows Semantic Versioning.
- **MAJOR:** Breaking changes (e.g., Juju 4 support dropping Juju 2/3 compatibility if necessary).
- **MINOR:** New features or backward-compatible API additions.
- **PATCH:** Bug fixes and internal improvements.

**Compliance Review:**
All Pull Requests MUST be reviewed against these principles. CI pipelines MUST enforce linting and testing standards.
