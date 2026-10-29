# Quality bar

Pick the items that apply to the ticket and rewrite each one as a concrete requirement for that change. A generic line ("handle errors") gives the reader nothing; a specific one does ("a failed delete sets the pending-sync flag and is retried on `online`"). Items marked **always** go in every build ticket.

## Correctness

- **Edge values (always):** zero, empty, negative, the maximum, missing fields and old data shapes. Example: use `??` instead of `||` when 0 is a valid value.
- **Units and ranges:** state the unit and the valid range for every number, and clamp or reject outside it.
- **Time and order:** timers, retries and async calls that can overlap or race. Name what cancels what.

## Durability (survives failure and restarts)

- **No silent failures (always):** never catch-and-ignore. Errors are logged, shown to the user when it matters, and never swallowed to pass a test.
- **Persistence:** what is saved, where, and under which key. What happens after a reload, a crash, or the app going to the background.
- **Offline and flaky networks:** timeouts on every network call, retries with a limit, a pending flag for unsent changes, and a user-visible status.
- **Idempotency:** a retried or duplicated request does no harm.
- **Data migration:** old stored data still loads; say how it's upgraded or clamped.

## Safety and security

- **Input validation:** anything from URLs, storage, the network or other apps is validated before use.
- **Secrets and tokens:** never in URLs after load, logs, telemetry or test fixtures. Only allow-listed hosts receive credentials.
- **Hardware and physical safety:** a universal stop always works, and nothing can start motion the user didn't ask for.
- **Least privilege:** tokens scoped to the app, routes checked for permission.

## Scalability and performance

- **Bounded resources:** caps on list sizes, queues, payloads and logs, and what happens at the cap.
- **Batching:** no request per event when a batch works (telemetry, sync).
- **Startup path:** nothing slow or remote blocks first render or core controls.

## Extensibility and flexibility

- **Single source of truth (always):** one implementation of each rule or protocol. No copies that can drift.
- **Configuration over constants:** environment-specific values (hosts, ids, limits) come from one config point, not scattered literals.
- **Seams:** new cases (another shot type, another app, another hub) are added by extending a table or adding a function, not by editing branches throughout the code.
- **Stable contracts:** public names, routes, storage keys and payload shapes stay unchanged unless the ticket says otherwise, and any change is versioned.

## Observability

- **Diagnosable in the field:** key actions and failures are recorded (in this squad, the in-app flight recorder for `qa` builds), with no secrets.
- **Clear status:** the user can see connection, sync and error state.

## Testability and maintainability

- **Tests at the right level (always):**
  - unit tests for logic
  - vault regression tests for behaviour that must not break
  - one end-to-end check of the real flow
- **Deterministic tests:** no real network, fake timers for timing, and fixed random seeds or masked random bytes.
- **Readable change:** match the surrounding style, keep the diff focused, and update `AGENTS.md` when commands, pitfalls or env vars change.

## Compatibility and rollout

- **Other clients:** apps or devices on the old version still work during the rollout.
- **Coordinated deploys:** name any ticket that must ship in the same window.
- **Rollback:** how to undo, and whether stored data survives the undo.

## Accessibility and mobile (UI tickets)

- Keyboard and screen-reader labels on new controls.
- The repo's mobile invariants: deep sleep when hidden, no background DOM churn, limited wake lock.
