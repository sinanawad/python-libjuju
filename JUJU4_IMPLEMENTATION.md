# Juju 4.0 Support Implementation Guide

This document outlines the design decisions and implementation details regarding the support for Juju 4.0 in `python-libjuju`.

## Overview

Juju 4.0 introduces several breaking changes to the API and internal behavior, specifically regarding schema definitions, API parameter signatures, and the mechanism for watching model changes. This implementation aims to provide seamless support for Juju 4.0 while maintaining backward compatibility with Juju 2.x and 3.x.

## Key Challenges & Design Decisions

### 1. Schema Structure Changes
**Challenge:** The Juju 4.0 API schema (JSON) differs slightly from previous versions. Specifically, some object definitions in the schema omit the `properties` key when the object has no properties, whereas previous versions included an empty `properties` object. This caused the existing code generator (`facade.py`) to crash with `KeyError`.

**Decision:** Update the code generator to be more robust.
**Implementation:** Modified `juju/client/facade.py` to use `.get("properties", {})` instead of direct access. This ensures the generator handles both old and new schema formats gracefully.

### 2. API Signature Changes (Model Creation)
**Challenge:** The `ModelManager` facade in Juju 4 (v11) changed the signature for `CreateModel`.
- **Removed:** `owner_tag` parameter.
- **Added/Changed:** `qualifier` parameter is now strictly enforced and used to specify the model owner/qualifier.

**Decision:** Abstract this difference in the high-level `Controller.add_model` method.
**Implementation:**
- Added version detection (`is_juju4`) in `juju/controller.py`.
- Conditionally construct the arguments for `CreateModel`:
  - **Juju < 4:** Pass `owner_tag`.
  - **Juju >= 4:** Pass `qualifier` (set to the owner's username).

### 3. Model State Updates (The Watcher Problem)
**Challenge:** In Juju 4.0, the `AllWatcher` facade—traditionally used by `python-libjuju` to receive real-time delta updates for the model—is restricted or behaves differently for standard users. Relying solely on `AllWatcher` caused connection issues or lack of updates in Juju 4 environments.

**Decision:** Implement a strategy pattern for model state updates.
- **Strategy A (Legacy):** Use `AllWatcher` for Juju < 4.
- **Strategy B (Juju 4):** Use a polling-based approach via `ClientFacade.FullStatus()`.

**Implementation:**
- Refactored the monolithic watcher logic out of `juju/model/__init__.py`.
- Created `juju/model/state_updater.py` containing:
  - `StateUpdater` (Abstract Base Class)
  - `AllWatcherUpdater` (Original logic)
  - `PollingUpdater` (New logic that polls `FullStatus` and calculates deltas)
- The `Model` class selects the appropriate updater based on the connected controller version.

### 4. Type Definition Conflicts
**Challenge:** The `Binary` type definition was removed or changed in the Juju 4 schema, causing the `juju/client/overrides.py` file (which inherited from the generated `_definitions.Binary`) to fail.

**Decision:** Decouple the override from the generated definition.
**Implementation:** Updated `juju/client/overrides.py` to make `Binary` inherit directly from the base `Type` class, ensuring it remains functional regardless of the generated schema content.

## File Modifications Summary

| File | Purpose |
|------|---------|
| `juju/client/schemas-juju-4.0.0.json` | **New.** The raw API schema for Juju 4.0. |
| `juju/client/facade.py` | **Modified.** Fixed codegen to handle missing `properties` key. |
| `juju/client/facade_versions.py` | **Modified.** Mapped Juju 4 facade versions (e.g., Controller v13). |
| `juju/client/_client*.py` | **Regenerated.** Client code generated from the new schema. |
| `juju/controller.py` | **Modified.** Logic for `add_model` parameter compatibility. |
| `juju/model/__init__.py` | **Modified.** Integrated `StateUpdater` for version-specific watching. |
| `juju/model/state_updater.py` | **New.** Implements `AllWatcherUpdater` and `PollingUpdater`. |
| `juju/client/overrides.py` | **Modified.** Fixed `Binary` class inheritance. |

## Verification

A new integration test `tests/integration/test_juju4_connection.py` was added to verify:
1. Connection to a Juju 4 controller.
2. Creation of a model (verifying the `qualifier` fix).
3. Basic interaction with the model.

To run the verification:
```bash
pytest tests/integration/test_juju4_connection.py
```
