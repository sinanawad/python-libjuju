# Research: Juju 4 Adaptation

**Feature**: Juju 4 Adaptation
**Date**: 2025-12-08

## 1. Juju 4 Handshake & Connection
- **Unknown**: How to detect Juju 4 vs 3?
- **Finding**: The `Connection` class negotiates facades. Juju 4 will expose different facade versions.
- **Decision**: We will rely on the negotiated API version. If the controller reports version 4.x, we switch to Juju 4 mode.
- **Rationale**: Standard Juju client behavior.

## 2. AllWatcher Replacement
- **Unknown**: What replaces `AllWatcher`?
- **Finding**: Juju 4 removes the global `AllWatcher`.
- **Decision**: We will implement a "State Updater" strategy.
    - **Strategy**: For `wait_for_idle` and entity status, we will use **Polling** of specific facades (`ApplicationFacade`, `UnitFacade`) initially.
    - **Future Optimization**: If Juju 4 exposes targeted watchers (e.g., `WatchApplication`), we will adopt them. For now, efficient polling (e.g., every 1-2s) is the safest MVP.
- **Rationale**: Polling is robust and guaranteed to work if the entities exist. `AllWatcher` was convenient but heavy.

## 3. Base vs Series
- **Unknown**: How to enforce `base`?
- **Finding**: `Model.deploy` already has a `base` argument.
- **Decision**:
    - If connected to Juju 4:
        - If `series` is passed -> Raise `ValueError`.
        - If `base` is missing -> Raise `ValueError` (unless charm metadata provides it).
    - If connected to Juju 3:
        - Allow `series` (backward compat).
- **Rationale**: Strict enforcement for Juju 4 to align with the Constitution.

## 4. Secrets
- **Unknown**: API for Secrets?
- **Finding**: Juju Secrets API exists (likely `SecretBackingFacade` or similar).
- **Decision**: Implement a `Secret` class in `juju.secrets` (or `juju.model`) that wraps the facade.
- **Rationale**: First-class support required by Constitution.
