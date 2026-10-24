# ZTE SMS — Home Assistant Integration Component

This directory contains the implementation of the ZTE SMS custom integration for Home Assistant.

**Status:** Functional, early-development integration.

The integration has been tested with a ZTE MF833U1 modem and a Home Assistant installation. It supports outbound SMS sending through the modem's local HTTP API.

## Implemented functionality

- Configuration flow for the modem host.
- Configuration and options for default SMS recipients.
- `zte_sms.send_sms` action for sending an SMS to one explicit recipient.
- `notify.zte_sms` notification entity for sending SMS individually to configured default recipients.
- UTF-16BE hexadecimal message encoding using `encode_type=UNICODE`.
- On-demand SMS reading functionality in the HTTP client, not currently exposed as an incoming-message feature in Home Assistant.

## Current limitations

- No incoming SMS entities, events, or automation triggers.
- No automatic SMS inbox polling.
- No cellular signal or network registration monitoring.
- No automatic SMS storage management or deletion.
- No independently verified delivery confirmation.
- Limited automated coverage of Home Assistant runtime behavior.

The integration does not modify the modem's network configuration or the MikroTik router's LTE failover settings.

## Installation

This directory must be installed at:

```text
/config/custom_components/zte_sms/
```

Copy the complete integration directory, restart Home Assistant, and add **ZTE SMS** through the Home Assistant integrations interface.

For full installation instructions, configuration examples, supported capabilities, and known limitations, see the [project README](../../README.md).

## Development documentation

- [Agent guidance](../../AGENTS.md)
- [Current tasks](../../TODO.md)
- [Contributing workflow](../../CONTRIBUTING.md)
- [Architecture](../../docs/architecture.md)
- [Compatibility](../../docs/compatibility.md)
- [MF833U1 HTTP API findings](../../docs/api/mf833u1.md)

Do not introduce unsolicited periodic polling, automatic deletion of unidentified SMS, or changes to the working LTE Internet fallback configuration.

Real-device SMS tests require explicit authorization.