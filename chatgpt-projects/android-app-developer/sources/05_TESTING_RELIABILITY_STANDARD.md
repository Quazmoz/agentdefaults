# Testing and Reliability Standard

## Reliability model

Assume:

- networks fail
- vendors throttle
- requests time out after remote success
- callbacks/events duplicate
- events arrive out of order
- processes restart
- devices go offline
- permissions change
- cached state becomes stale

Design and test accordingly.

## Test pyramid

Use the smallest layer that proves the behavior.

### Unit tests

Use for:

- reducers/state machines
- entitlement logic
- parsing/validation
- date/time logic
- retry decisions
- merge/deduplication
- ViewModel/domain behavior with fake dependencies

### Integration tests

Use for:

- Room migrations
- repositories
- WorkManager contracts
- billing wrapper behavior with fakes/test doubles
- Data Layer serialization/reconciliation
- persistence + state restoration

### Instrumentation/emulator/device

Use for:

- Android lifecycle behavior
- permissions
- navigation
- foreground services
- notifications
- Wear screen shape/font scale
- real database migration
- cross-device flows
- screenshots
- system integrations

## Bug-fix workflow

For a reported defect:

1. reproduce or trace the actual failing path
2. identify root cause
3. add a regression test when practical
4. make the smallest coherent fix
5. test the failure path
6. test adjacent state transitions
7. run applicable build/lint/tests
8. report anything not reproduced or not verified

Do not close a race-condition bug merely because the happy-path unit test passes.

## Adversarial cases

For stateful/background/mobile flows, consider:

- duplicate event
- stale event
- out-of-order event
- retry after remote success
- cancellation mid-operation
- process death
- app upgrade
- device reboot
- offline startup
- reconnect
- time/clock boundary
- user changes system settings
- permission denied/revoked
- old app version communicating with new version
- slow or unavailable vendor API

## Observability

Where the app has telemetry, prefer actionable events over noisy logging.

Useful metadata may include:

- app version
- build/versionCode
- operation name
- sanitized error category
- retry count
- duration
- state transition
- device/form factor where appropriate

Never log:

- purchase tokens
- auth tokens
- secrets
- sensitive user content unless explicitly justified and protected

## ANR and crash work

For crashes/ANRs:

- inspect current stack traces when available
- map to current source, not remembered source
- distinguish main-thread blocking from deadlock/livelock
- inspect strict-mode/lifecycle/IPC/network/database paths
- add targeted regression coverage
- verify on the affected device/API range where possible

Zero crashes does not imply zero ANRs, and zero ANRs does not imply a healthy UX.

## Completion

Use `TESTED` only when the stated tests actually ran successfully. Preserve `UNKNOWN` when evidence was unavailable.
