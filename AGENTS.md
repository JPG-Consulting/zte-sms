# AGENTS.md — guidance for AI coding agents

## Project state

This repository is an **exploratory scaffold**, not a working Home Assistant integration. Start by reading `README.md`, `docs/research-log.md`, and `docs/api/mf833u1.md`. Never present a hypothesized API behavior as tested.

## Non-negotiable constraints

1. **Protect LTE fallback.** The MF833U1 currently provides working LTE failover through a MikroTik hEX S. Do not change USB mode, firmware, APN, routing, modem configuration, or network settings as part of SMS development.
2. **No unapproved side effects.** Do not send, delete, mark-read, or otherwise mutate SMS on a live modem without explicit user permission. Default tests must use mocks/fixtures.
3. **Protect private data.** Never commit real phone numbers, SMS text, device credentials, session cookies, or tokens. Redact diagnostics. Never log full message bodies by default.
4. **Separate evidence from assumptions.** Record each finding as verified, observed-but-not-explained, or unverified. Include exact reproduction conditions.
5. **Respect Home Assistant conventions.** Before implementing, check current Home Assistant developer guidance for config flows, coordinators, entities, events/actions, translations, and HACS metadata.
6. **Keep scope modest.** Implement reliable, read-only SMS retrieval first; only then new-message detection, and later sending after API verification.

## Verified evidence to preserve

- Modem: ZTE MF833U1, UI at `http://192.168.0.1/index.html#sms`.
- The browser UI can receive and display SMS.
- GET `goform_get_cmd_process` with `cmd=sms_data_total` and additional pagination/filter parameters returns JSON `messages` in Postman **when the request has `Referer: http://192.168.0.1/index.html`**.
- The same Postman query without that Referer returned `{ "sms_data_total": "" }`.
- Message `content` is UTF-16 big-endian code units represented as hex; test using synthetic fixtures.
- For multiple state commands, `multi_data=1` was required for a correctly split response.

## Workflow for any change

1. Read relevant docs and tests.
2. State what is known versus inferred.
3. Add tests with sanitized data and no live HTTP access.
4. Implement the smallest change.
5. Run tests and update documentation, compatibility matrix, and research log when behavior changes.
6. If a real-device test is necessary, describe it and request explicit approval first.

## Suggested next milestones

- Verify HA OS can reach `192.168.0.1` and reproduce the successful GET with Referer.
- Build a minimal, read-only async API client with request timeout, structured errors, and sanitized logging.
- Implement message decoding and deduplication across restarts.
- Implement Home Assistant config flow and entities/events according to current APIs.
- Investigate SMS sending via captured browser requests, without actually sending until approved.

## Review checklist

- No sensitive data in fixtures, logs, screenshots, or docs.
- No implicit live-device requests in unit tests.
- No destructive actions.
- No unsupported compatibility claims.
- No breaking changes to LTE fallback.
