# Feature Specification: Juju 4 Adaptation

**Feature Branch**: `001-juju4-adaptation`
**Created**: 2025-12-08
**Status**: Draft
**Input**: User description: "Implement the feature specification based on the updated constitution. The spec should currently focus on the minimal changes to support the constitution, and see if this is a good iteration to adapt this library to juju4."

## User Scenarios & Testing

### User Story 1 - Connect to Juju 4 Controller (Priority: P1)

As a developer, I want to connect `python-libjuju` to a Juju 4 controller so that I can interact with Juju 4 models.

**Why this priority**: This is the fundamental entry point. Without connection, no other operations are possible.

**Independent Test**: Can be tested by running a script that connects to a bootstrapped Juju 4 controller and retrieves basic model info.

**Acceptance Scenarios**:

1.  **Given** a running Juju 4 controller, **When** I call `Model.connect()`, **Then** the connection is established successfully without errors related to handshake or version mismatch.
2.  **Given** a Juju 4 connection, **When** I inspect the connection object, **Then** it reflects the correct Juju version and capabilities.

---

### User Story 2 - Deploy Charm with Base (Priority: P1)

As a developer, I want to deploy a charm using the `base` argument (e.g., `ubuntu@22.04`) instead of `series` so that I comply with Juju 4 standards.

**Why this priority**: `series` is deprecated/removed in Juju 4. Deployment is a core function.

**Independent Test**: Deploy a simple charm (e.g., `ubuntu`) using `base` and verify it deploys.

**Acceptance Scenarios**:

1.  **Given** a connected Juju 4 model, **When** I call `model.deploy('ubuntu', base='ubuntu@22.04')`, **Then** the application is added to the model.
2.  **Given** a connected Juju 4 model, **When** I call `model.deploy('ubuntu', series='jammy')`, **Then** the library raises a `DeprecationWarning` or `ValueError` (depending on strictness) or automatically maps it to a base if possible (but preference is to enforce base). *Decision: Enforce base for Juju 4.*

---

### User Story 3 - Wait for Idle without AllWatcher (Priority: P1)

As a developer, I want `model.wait_for_idle()` to work reliably without the `AllWatcher` so that I can write stable integration tests.

**Why this priority**: `AllWatcher` is removed. `wait_for_idle` is critical for CI/CD and testing.

**Independent Test**: Deploy an app, call `wait_for_idle`, and verify it returns only when the app is ready.

**Acceptance Scenarios**:

1.  **Given** a deploying application, **When** I call `model.wait_for_idle(status='active')`, **Then** the call blocks until the application reaches 'active' state.
2.  **Given** a model with multiple apps, **When** I call `wait_for_idle`, **Then** it correctly tracks the status of specified apps using targeted watchers or polling, not `AllWatcher`.

---

### User Story 4 - Manage Secrets (Priority: P2)

As a developer, I want to create and manage secrets using the Juju Secrets API so that I can configure applications securely.

**Why this priority**: Config-based secrets are legacy. Juju 4 enforces the Secrets API.

**Independent Test**: Create a secret, grant it to an application, and verify the application can access it.

**Acceptance Scenarios**:

1.  **Given** a connected model, **When** I call `model.add_secret(name='my-secret', data={'key': 'value'})`, **Then** a secret object is returned with a valid URI.
2.  **Given** a secret, **When** I call `secret.grant(application='my-app')`, **Then** the application is granted access to the secret.

## Requirements

### Functional Requirements

-   **FR-001**: The library MUST successfully handshake with Juju 4 controllers.
-   **FR-002**: The library MUST NOT use the global event watcher mechanism (AllWatcher).
-   **FR-003**: The library MUST implement a state tracking mechanism (polling or targeted watchers) to replace the global watcher for `wait_for_idle` and entity caching.
-   **FR-004**: Deployment operations MUST accept a `base` argument (string, e.g., "ubuntu@22.04").
-   **FR-005**: Deployment operations MUST raise an error if `series` is provided when connected to Juju 4.
-   **FR-006**: The library MUST provide a `Secret` entity wrapping the Juju Secrets API.
-   **FR-007**: The library MUST provide methods to add, update, grant, revoke, and remove secrets.

### Key Entities

-   **Secret**: Represents a Juju Secret. Attributes: `uri`, `label`, `data` (write-only/hidden), `owner`.
-   **Base**: Represents a simplified OS base (replacing Series). Format: `name@version`.

## Success Criteria

### Measurable Outcomes

-   **SC-001**: Integration tests pass against a Juju 4 controller for basic deploy/remove scenarios.
-   **SC-002**: `wait_for_idle` returns within 5 seconds of actual state change (verifying efficient polling/watching).
-   **SC-003**: Zero calls to the global watcher mechanism observed in debug logs during a standard deployment lifecycle.
-   **SC-004**: 100% of new code is type-hinted and passes configured linting standards.

## Assumptions

-   Juju 4 controller is available for testing.
-   Juju 4 API exposes necessary targeted watchers or allows efficient polling of entity status.
-   Existing Juju 3 compatibility can be maintained via feature flags or separate logic paths if needed, but Juju 4 is the priority for this iteration.
