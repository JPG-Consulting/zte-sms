# TODO — ZTE SMS

This document tracks the project's current milestones and outstanding work.

For implemented functionality, see [README.md](README.md). For architectural constraints, see [docs/architecture.md](docs/architecture.md). For contribution rules, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Current status

- [x] Establish the initial Home Assistant custom integration.
- [x] Configure the modem host through the Home Assistant UI.
- [x] Support multiple configurable default SMS recipients.
- [x] Implement the `zte_sms.send_sms` action.
- [x] Implement the `notify.zte_sms` notification entity.
- [x] Add configurable sequential notification batches (1–5 SMS; default 5), with safe fallback for invalid stored batch sizes.
- [x] Implement notification-level accepted/rejected/unknown outcome counts and aggregate partial/complete failure reporting.
- [x] Continue notification processing after individual SMS failures and between-batch maintenance-hook failures.
- [x] Add privacy-safe notification WARNING/ERROR logging and mocked batch-processing tests.
- [x] Verify basic outbound SMS on the tested ZTE MF833U1.
- [x] Verify Unicode SMS containing Spanish accented characters and `ñ`.
- [x] Add initial automated tests and GitHub Actions.
- [x] Align repository documentation with the current implementation.
- [x] Add `TODO.md` and `CONTRIBUTING.md`.
- [x] Create and publish the `develop` branch.
- [x] Configure active GitHub rulesets for `main` and `develop`.
- [x] Require the `unit` GitHub Actions check for both protected branches.
- [x] Complete an independent cold-start repository audit.
- [x] Verify the protected-branch workflow through a real pull request.

The project is currently in early development. Successful SMS tests and passing CI do not yet establish production readiness.

## Milestone 1 — Reliable outbound SMS and safe sent-message storage

**Priority: highest.**

The first stable release must prioritize fast, reliable SMS submission and safe handling of modem storage occupied by integration-generated sent messages.

The SMS submission path must not wait for inbox synchronization, LTE status queries, local archive writes, or sent-message cleanup.

### P0 — Correctness and error handling

- [ ] Resolve the service lifecycle and modem-selection problem when multiple configuration entries exist.
  - [ ] Decide whether the initial integration supports one modem or multiple modems.
  - [ ] Ensure the `zte_sms.send_sms` action cannot silently use the wrong modem.
  - [ ] Cover setup, unload, reload, and relevant configuration-entry scenarios with automated tests.
- [ ] Distinguish confirmed submission failures from uncertain outcomes.
  - [ ] Handle modem rejections separately from transport failures.
  - [ ] Treat timeouts and lost responses conservatively.
  - [ ] Preserve actionable errors for Home Assistant callers.
  - [ ] Never automatically retry a submission when doing so could duplicate an SMS.
- [x] Improve notification handling for multiple recipients.
  - [x] Account for partial success when a later recipient fails.
  - [x] Avoid leaking full phone numbers or message contents in notification diagnostics.
  - [x] Add mocked tests for failures at different points in the recipient list.
- [ ] Investigate concurrent SMS submissions.
  - [ ] Determine whether the tested modem safely supports overlapping requests.
  - [ ] Define appropriate per-modem concurrency behavior.
  - [ ] Ensure synchronization does not introduce unnecessary submission delays.
  - [ ] Add concurrency tests using simulated modem responses.
- [ ] Improve modem host validation and request safety.
  - [ ] Reject malformed hosts, unexpected URL schemes, embedded credentials, and arbitrary paths.
  - [ ] Investigate and prevent unsafe HTTP redirection of SMS requests.
  - [ ] Preserve support for the verified local modem configuration.

### Future feature — Priority-aware SMS scheduling (separate PR)

- [ ] Design and implement one per-modem priority scheduler shared by `notify.send_message` (targeting the ZTE SMS notification entity) and `zte_sms.send_sms`.
- [ ] Accept an optional `priority` parameter in both supported sending paths; omission must preserve backward compatibility and default to `normal`.
- [ ] Initially support `normal`, `high`, and `critical`, in increasing priority order.
- [ ] **Permanent invariant: `critical` is always the absolute highest priority.** Any priority levels introduced later must rank below `critical`; no level may supersede it.
- [ ] Re-evaluate pending priorities between individual SMS submissions, including within a configurable notification batch, rather than waiting for an entire batch to finish.
- [ ] Never cancel or preempt an SMS request already in progress with the modem; uncertain submission outcomes must not be retried automatically.
- [ ] Preserve FIFO order for pending SMS of equal priority and resume interrupted lower-priority notification batches without losing recipient progress.
- [ ] Define fair scheduling and failure/cancellation behavior so lower-priority work is not silently discarded or indefinitely starved.
- [ ] Add mocked concurrency, ordering, batch-resumption, default-priority, and backwards-compatibility tests. Include a regression test that adding future levels cannot outrank `critical`.
- [ ] Validate both sending paths in running Home Assistant and obtain explicit authorization before any real-modem SMS tests.

**Scope:** design and implementation are deferred to a dedicated future PR. The current feature branch only serializes modem access; it does not implement priority scheduling. A priority scheduler must not claim instantaneous transmission while the modem is already processing a request.

### P0 — Safe sent-message storage management

- [ ] Establish whether SMS generated by the integration occupy persistent modem storage.
- [ ] Determine when outbound SMS records appear in modem storage and whether they remain after submission.
- [ ] Investigate whether the modem exposes a reliable identifier for each integration-generated message.
- [ ] Verify whether the exact stored record can be attributed unambiguously to the integration.
- [ ] Investigate the modem's deletion API and its safety properties using explicitly authorized tests.
- [ ] Determine whether deleting an eligible sent record can interfere with transmission or delivery.
- [ ] Implement automatic post-submission cleanup **only if all ownership and deletion safety requirements are proven**.
- [ ] Provide an option to retain integration-generated sent messages in modem storage if cleanup is implemented.
- [ ] Keep cleanup separate from the critical SMS submission path.
- [ ] Handle cleanup failures without automatically resending SMS.
- [ ] Document any unresolved storage limitation that prevents a stable release.

**Deletion safety rule:** never automatically delete received SMS, manually sent SMS, or messages of uncertain origin. Matching a recipient, body, timestamp, or sent-folder location is not sufficient evidence of ownership.

No automatic deletion is currently implemented.

### P1 — Diagnostics and test coverage

- [ ] Extend privacy-safe diagnostic logging across the integration (basic notification WARNING/ERROR logs are implemented).
  - [x] Add privacy-safe WARNING/ERROR logging for notification submission failures.
  - [ ] Review appropriate DEBUG, INFO, WARNING, and ERROR levels across all components.
  - [ ] Audit all components for SMS bodies, full phone numbers, credentials, cookies, or tokens in logs.
  - [ ] Verify error propagation remains independent of logging configuration throughout the integration.
  - [ ] Review use of Home Assistant's native logging controls.
- [ ] Add automated coverage for Home Assistant integration behavior (mocked notification batch tests are implemented).
  - [ ] Configuration and options flows.
  - [ ] Setup, unload, and reload.
  - [ ] Action registration and execution.
  - [ ] Notification entity setup and sending.
  - [ ] Default-recipient updates and invalid inputs.
  - [x] Mocked notification batch processing, individual failure continuation, partial/complete outcomes, invalid stored batch size fallback, and privacy-safe warning/error logs.
  - [ ] End-to-end Home Assistant runtime verification of notification failures and option validation.
- [ ] Add simulated HTTP transport failure tests.
  - [ ] Connection failures.
  - [ ] HTTP errors.
  - [ ] Timeouts and uncertain outcomes.
  - [ ] Invalid or unexpected modem responses.
  - [ ] Redirect handling.
- [ ] Review SMS timestamp behavior and the hard-coded `Europe/Madrid` timezone.
- [ ] Consolidate duplicated UTF-16BE decoding helpers.
- [ ] Review `iot_class` in `manifest.json` against the current non-polling implementation and supported Home Assistant conventions.
- [ ] Validate the integration against an explicitly identified Home Assistant version.
- [ ] Record the tested modem firmware version where available.
- [ ] Investigate Unicode edge cases, message-length limits, and multipart SMS behavior.

### Home Assistant validation for this feature branch

- [x] Install `feat/configurable-sms-batches` in a running Home Assistant instance and restart Home Assistant.
- [x] Verify that the integration loads and its ZTE SMS notification entity is present.
- [x] Verify that the options form opens without an HTTP 500 error after replacing the non-serializable custom field validator.
- [x] Verify that the batch-size selector supports values 1–5, initially displays the default 5, and retains a saved value of 3 after reopening.
- [x] With explicit maintainer authorization, send one real SMS using `notify.send_message` targeting `notify.zte_sms` with batch size 3 and one configured recipient. Home Assistant reported no error and the recipient confirmed receipt.
- [x] Verify sequential batch boundaries, ordering, continuation, and outcome handling using mocked modem tests in GitHub Actions.
- [x] Verify integration reload in Home Assistant: reload completed without errors, `notify.zte_sms` remained available, and batch size 3 and the configured recipient were preserved.
- [x] Verify invalid recipient input feedback: an invalid phone number without `+` was rejected with the expected international-format error; closing without saving preserved the original recipient and batch size 3.
- [x] After introducing the shared per-modem asynchronous SMS lock, copy the updated `client.py`, `notify.py`, and `__init__.py` into Home Assistant and restart; the integration loaded without errors, its notification entity remained available, and integration reload succeeded.
- [x] With explicit maintainer authorization, send one additional real SMS through `notify.send_message` targeting `notify.zte_sms` after the lock change; the recipient confirmed receipt and Home Assistant displayed no error.
- [x] With separate explicit maintainer authorization, send one additional real SMS through `zte_sms.send_sms` after the lock change; the recipient confirmed receipt and Home Assistant displayed no error.
- [x] Verify that mocked concurrency tests enforce serialization of overlapping notification requests and that GitHub Actions passes after updating mocked clients with asynchronous locks.
- [ ] Verify overlapping requests from both sending paths in a running Home Assistant instance if safe, explicitly authorized conditions become available; concurrent modem use has been exercised only with mocks, not simultaneous real SMS.
- [ ] Verify successful recipient updates (changing and saving the recipient list) in Home Assistant; this was not exercised to avoid altering the live destination.
- [ ] Verify notification failure/error display and privacy-safe logs in a running Home Assistant instance; no live modem failure was intentionally induced.
- [x] Verify the existing single-recipient `zte_sms.send_sms` action with one explicitly authorized real SMS to the maintainer's own number. Home Assistant reported no error and the recipient confirmed receipt.
- [ ] Verify multiple consecutive batches and failure scenarios against the real modem if sufficient explicitly authorized test recipients and safe test conditions become available. Only one real recipient was available during this validation, so multi-recipient and multi-batch real-device behavior remains unverified.
- [ ] Do not declare this branch ready for a PR until applicable Home Assistant runtime and authorized real-SMS tests pass. If tests cannot be completed, keep validation explicitly pending and document the limitation.
- [x] Record completed tests and remaining limitations in this TODO after the initial Home Assistant test session.

### Milestone 1 release criteria

Do not declare the first stable release complete until:

- [ ] Outbound SMS behavior is predictable under supported configuration scenarios.
- [ ] Confirmed failures and uncertain outcomes are distinguished.
- [ ] No unsafe automatic retry behavior exists.
- [ ] Notification failures and partial results are handled appropriately.
- [ ] The modem-storage behavior of integration-generated SMS is understood.
- [ ] Any automatic deletion is supported by verified ownership and safe deletion semantics.
- [ ] Storage limitations are explicitly resolved or documented as release blockers where appropriate.
- [ ] Automated tests cover the relevant critical paths.
- [ ] Required real-device tests have been explicitly authorized and completed.
- [ ] Documentation and compatibility claims match verified behavior.
- [ ] Validated release changes have been merged from `develop` into `main`.

## Milestone 2 — Optional local SMS archive and viewer

**Deferred until Milestone 1 is complete.**

- [ ] Design optional local storage for integration-generated outbound SMS.
- [ ] Define a Home Assistant-compatible persistence mechanism.
- [ ] Require explicit user consent for storing SMS contents locally.
- [ ] Define retention, access-control, privacy, and backup behavior.
- [ ] Store submission outcomes without misrepresenting uncertain results as confirmed delivery.
- [ ] Provide a usable Home Assistant UI for viewing archived messages.
- [ ] Clearly distinguish local archive records from modem-stored records.
- [ ] Ensure archive operations do not delay urgent SMS submission.
- [ ] Consider received-message archiving separately after outbound archiving is validated.

Local archiving must not be considered a complete user-facing feature without a usable message viewer.

## Milestone 3 — SMS synchronization and incoming messages

**Deferred until Milestone 1 is complete.**

- [ ] Design an on-demand **Sync now** operation.
- [ ] Investigate stable message identifiers, pagination, ordering, and deduplication.
- [ ] Support reading messages from modem storage without changing their read or deletion state.
- [ ] Consider optional synchronization of received SMS.
- [ ] Consider optional polling, disabled by default.
- [ ] Define configurable polling intervals if polling is implemented.
- [ ] Consider incoming SMS entities, events, or automation triggers.
- [ ] Ensure synchronization never blocks or delays outbound SMS submission.

Manual synchronization must remain possible without enabling periodic polling.

## Milestone 4 — Optional LTE status and monitoring

**Deferred until Milestone 1 is complete.**

- [ ] Investigate on-demand modem reachability and LTE status queries.
- [ ] Investigate cellular registration and signal measurements.
- [ ] Consider Home Assistant entities for verified read-only status information.
- [ ] Consider optional periodic monitoring, disabled by default.
- [ ] Define a configurable refresh interval.
- [ ] Investigate automation-controlled monitoring without conflicting with explicit user preferences.
- [ ] Keep monitoring independent of MikroTik routing and LTE failover.
- [ ] Avoid interpreting signal loss alone as evidence of deliberate interference.

On-demand queries and periodic monitoring are separate capabilities.

## Repository maintenance and workflow

### Completed

- [x] Establish English as the primary repository language.
- [x] Document the `main` / `develop` branching strategy.
- [x] Publish `develop`.
- [x] Configure branch rulesets for `main` and `develop`.
- [x] Require pull requests and the `unit` status check.
- [x] Complete the first independent cold-start audit.
- [x] Validate the rulesets through the first real pull request.

### Pending

- [ ] Update the public repository description to reflect outbound SMS functionality accurately.
- [ ] Review GitHub Actions warnings and action versions.
- [ ] Consider Home Assistant-specific validation in CI.
- [ ] Review HACS distribution requirements when approaching a stable release.
- [ ] Prepare release notes and a tagged release only after Milestone 1 criteria are satisfied.

## Non-goals and permanent constraints

The integration must not:

- Modify MikroTik routing or failover configuration.
- Change modem firmware, USB mode, APN, or cellular network settings.
- Delete received, manually sent, or unidentifiable SMS automatically.
- Send real SMS during automated tests.
- Retry uncertain SMS submissions automatically.
- Expose sensitive message data through logs or test fixtures.
- Introduce unsolicited polling.
- Claim successful delivery based only on modem submission acceptance.

See [AGENTS.md](AGENTS.md) for the complete safety rules and [docs/architecture.md](docs/architecture.md) for architectural boundaries.