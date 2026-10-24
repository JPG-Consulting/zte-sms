# Proposed architecture (not yet implemented)

Home Assistant custom integration -> async HTTP client -> local ZTE modem HTTP API.

1. Config flow asks for modem host/IP, validates read-only connectivity, and stores only necessary configuration.
2. Client uses a configurable timeout and a Referer derived from the configured modem base URL; no hard-coded `192.168.0.1` in production logic.
3. Polling coordinator fetches SMS pages and parses records.
4. Decoder transforms UTF-16-hex content to Unicode text, preserving errors for diagnostics without leaking sensitive message bodies.
5. New-message detection uses stable message identifiers plus modem identity, with persisted checkpoint state and restart-safe deduplication.
6. Integration exposes useful status entities and a documented event or equivalent Home Assistant automation trigger; never expose sensitive SMS text in logs by default.
7. Outbound send action remains out of scope until the exact API and safety behavior are verified.

## Risks

- Device HTTP API is undocumented and firmware-specific.
- The modem may not authenticate API calls consistently; limit access to trusted local networks.
- Message bodies and sender numbers are personal data; make retention and event exposure explicit.
- Polling could miss messages if the device's message store overflows; pagination and polling strategy need tests.
- Internet fallback must continue functioning even if SMS integration fails.
