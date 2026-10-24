# ADR 0001 — Home Assistant custom integration rather than add-on

**Status:** Accepted

**Date:** 2026-10-24

## Context

The ZTE MF833U1 exposes a local HTTP API for SMS operations.

The initial investigation verified that stored SMS could be retrieved using an HTTP GET request. Subsequent experiments also verified SMS sending through an HTTP POST request.

The target environment uses Home Assistant OS, with the ZTE modem providing LTE Internet fallback through a MikroTik hEX S router.

The project aims to provide a maintainable, reinstallable, and shareable Home Assistant integration through GitHub, with potential future HACS distribution.

SMS functionality must not interfere with the existing LTE failover configuration.

## Decision

Implement ZTE SMS as a native Home Assistant custom integration under:

```text
custom_components/zte_sms
```

Do not introduce a separate Home Assistant add-on or background container for the currently supported functionality.

Use a dedicated HTTP client to communicate with the modem and expose functionality through supported Home Assistant interfaces.

The current implementation provides:

- Configuration and options flows.
- A modem HTTP client.
- The `zte_sms.send_sms` action.
- The `notify.zte_sms` notification entity.

Additional functionality, such as incoming SMS detection or cellular monitoring, may be considered later without changing this architectural decision.

## Rationale

### Native Home Assistant integration

A custom integration supports Home Assistant's existing configuration, automation, action, entity, and notification mechanisms.

It avoids requiring users to install and manage a separate service for the currently implemented functionality.

### HTTP-based modem communication

The verified SMS operations use the modem's local HTTP API.

They do not require a serial interface, an external daemon, or a dedicated container.

The modem's observed RouterOS interface does not expose usable native SMS functionality through the tested serial or AT-command mechanisms.

Changing the modem's USB mode or firmware to obtain serial access would introduce unnecessary risk to the working LTE Internet fallback.

### Simpler deployment

The integration can be installed under Home Assistant's `custom_components` directory.

This fits the project's goal of distributing the integration through a version-controlled repository and potentially HACS in the future.

HACS compatibility and distribution should be validated separately rather than assumed from the existence of a custom integration.

### Limited operational scope

The current implementation performs outbound SMS operations when explicitly invoked.

It does not require periodic inbox polling, a persistent process, or automatic SMS deletion.

Any future monitoring must be optional and disabled by default.

## Consequences

### Positive

- Native Home Assistant configuration and automation support.
- No separate add-on installation or container lifecycle.
- Direct reuse of the modem's verified local HTTP API.
- Reduced operational complexity.
- Separation between modem communication and Home Assistant interfaces.
- No required changes to MikroTik routing or LTE failover.

### Limitations and trade-offs

- The integration depends on an undocumented, potentially firmware-specific ZTE HTTP API.
- Compatibility must be verified for each supported modem model and firmware version.
- Home Assistant runtime compatibility requires testing beyond isolated HTTP client unit tests.
- SMS sending responses do not independently confirm delivery.
- More advanced monitoring or message processing may require additional Home Assistant components and lifecycle management.

These limitations do not currently justify a separate add-on.

## Revisit this decision if

Reconsider the architecture if reliable evidence shows that required functionality cannot reasonably operate within the Home Assistant integration runtime.

Examples include:

- A mandatory persistent proprietary process.
- Required serial-device access unavailable to the integration.
- Processing requirements incompatible with Home Assistant's supported APIs.
- Isolation or resource requirements that make a separate service demonstrably necessary.

Do not introduce an add-on merely because a future feature is more complex.

Any proposed architectural change must preserve the existing LTE Internet fallback and include a documented justification.

## Implementation status

**Implemented and verified in the tested environment:**

- Home Assistant configuration and options.
- SMS sending through `zte_sms.send_sms`.
- SMS sending through `notify.zte_sms`.
- Unicode encoding for the tested accented characters.

**Not currently implemented:**

- Incoming SMS entities or automation triggers.
- Periodic SMS inbox polling.
- Cellular signal monitoring.
- SMS storage monitoring or automatic deletion.

For the current implementation, see [Architecture](../architecture.md).

For tested compatibility and API evidence, see [Compatibility](../compatibility.md) and [MF833U1 HTTP API findings](../api/mf833u1.md).

## Decision history

- **2026-10-24:** Initially proposed a custom integration instead of an add-on, based on successful HTTP inbox retrieval.
- **2026-10-24:** Decision accepted and confirmed by the working Home Assistant SMS action and notification entity.