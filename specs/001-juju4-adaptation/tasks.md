# Tasks: Juju 4 Adaptation

**Input**: Design documents from `/specs/001-juju4-adaptation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included as requested by the Constitution (Robust Integration Testing Support).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and baseline verification

- [x] T001 Verify development environment and run existing tests to ensure baseline in `tests/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Update `Connection.connect` in `juju/client/connection.py` to detect Juju 4 version
- [ ] T002b Update client definitions/schemas for Juju 4 (Add `schemas-juju-4.x.json`, update `facade_versions.py`, run `make client`)
- [x] T003 [P] Create `StateUpdater` abstract base class in `juju/model/state_updater.py`
- [x] T004 Refactor existing `AllWatcher` logic into `AllWatcherUpdater` in `juju/model/state_updater.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Connect to Juju 4 Controller (Priority: P1) 🎯 MVP

**Goal**: Establish connection to Juju 4 controller using the correct protocol/updater.

**Independent Test**: `tests/integration/test_juju4_connection.py` passes against a Juju 4 controller.

### Tests for User Story 1

- [x] T005 [US1] Create integration test `tests/integration/test_juju4_connection.py`

### Implementation for User Story 1

- [x] T006 [US1] Update `Model.connect` in `juju/model/__init__.py` to instantiate `PollingUpdater` (placeholder) if Juju 4 detected
- [x] T007 [US1] Ensure `Model` uses `StateUpdater` interface instead of direct `AllWatcher` calls in `juju/model/__init__.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Deploy Charm with Base (Priority: P1)

**Goal**: Deploy charms using `base` argument, enforcing Juju 4 standards.

**Independent Test**: `tests/integration/test_juju4_deploy.py` passes.

### Tests for User Story 2

- [ ] T008 [US2] Create integration test `tests/integration/test_juju4_deploy.py`

### Implementation for User Story 2

- [ ] T009 [US2] Update `Model.deploy` in `juju/model/__init__.py` to accept `base` argument
- [ ] T010 [US2] Update `Model.deploy` in `juju/model/__init__.py` to validate `series` vs `base` based on Juju version
- [ ] T011 [US2] Update `Model.add_machine` in `juju/model/__init__.py` to accept `base` argument

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Wait for Idle without AllWatcher (Priority: P1)

**Goal**: Reliable `wait_for_idle` using polling/targeted watchers.

**Independent Test**: `tests/integration/test_juju4_wait.py` passes.

### Tests for User Story 3

- [ ] T012 [US3] Create integration test `tests/integration/test_juju4_wait.py`

### Implementation for User Story 3

- [ ] T013 [US3] Implement `PollingUpdater` in `juju/model/state_updater.py` using `ApplicationFacade` and `UnitFacade`
- [ ] T014 [US3] Update `Model.wait_for_idle` in `juju/model/__init__.py` to utilize `PollingUpdater` logic
- [ ] T015 [US3] Ensure `Model` entity caching works with `PollingUpdater` in `juju/model/__init__.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Manage Secrets (Priority: P2)

**Goal**: First-class support for Juju Secrets.

**Independent Test**: `tests/integration/test_secrets.py` passes.

### Tests for User Story 4

- [ ] T016 [US4] Create integration test `tests/integration/test_secrets.py`

### Implementation for User Story 4

- [ ] T017 [P] [US4] Create `Secret` class in `juju/secret.py`
- [ ] T018 [US4] Add `add_secret` method to `Model` in `juju/model/__init__.py`
- [ ] T019 [US4] Implement `grant`, `revoke`, `update`, `remove` methods in `juju/secret.py`

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T020 [P] Documentation updates in `docs/` reflecting Juju 4 changes
- [ ] T021 Code cleanup and refactoring of any remaining `AllWatcher` references
- [ ] T022 Performance optimization of `PollingUpdater`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup. BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase.
  - US1 (Connect) is effectively a prerequisite for running tests for US2, US3, US4.
  - US2, US3, US4 can be implemented in parallel but integration testing requires US1.

### Parallel Opportunities

- `StateUpdater` classes (T003, T004, T013) can be developed in parallel with `Secret` class (T017).
- Tests can be written in parallel with implementation.

---

## Implementation Strategy

### MVP First (User Story 1 & 3)

1. Complete Phase 1 & 2 (Foundational).
2. Implement US1 (Connect) and US3 (Polling/Wait) together as they are tightly coupled for a functional "Juju 4 Client".
3. Validate with `test_juju4_connection.py` and `test_juju4_wait.py`.

### Incremental Delivery

1. Foundation + Connect (US1) -> Verify connection.
2. Wait for Idle (US3) -> Verify stability.
3. Deploy (US2) -> Verify deployment.
4. Secrets (US4) -> Add new feature.
