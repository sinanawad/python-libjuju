# Data Model: Juju 4 Adaptation

## Entities

### 1. Secret
Represents a Juju Secret.

**Attributes**:
- `id` (str): The secret URI (e.g., `secret:12345`).
- `label` (str): User-friendly label.
- `owner` (str): The application or unit that owns the secret.
- `revision` (int): Current revision.
- `content` (dict): The secret data (only available if authorized/owner).

**Relationships**:
- Belongs to a `Model`.
- Can be granted to `Application` or `Unit`.

### 2. Base
Represents an OS base.

**Attributes**:
- `name` (str): e.g., `ubuntu`.
- `channel` (str): e.g., `22.04`.
- `architecture` (str): e.g., `amd64`.

**Usage**:
- Replaces `series` string in `deploy` and `add_machine`.

## State Management (Internal)

### 1. Model State
- **Current**: `self.state` is a `ModelState` object updated by `AllWatcher` deltas.
- **New**: `self.state` will be updated by a `StateUpdater`.
    - **Juju 3**: `AllWatcherUpdater` (feeds deltas).
    - **Juju 4**: `PollingUpdater` (fetches full entities and generates "synthetic" deltas or updates state directly).

**Rationale**: Keeps the `Model` public API largely unchanged (`model.applications['app']` still works), but changes the engine under the hood.
