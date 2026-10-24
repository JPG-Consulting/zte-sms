# Research log

This document preserves the chronological history of research and testing for the ZTE SMS integration.

Earlier entries describe what was known at the time. Later findings may resolve questions raised in previous entries.

Technical API details belong in [MF833U1 HTTP API findings](api/mf833u1.md). Current feature support belongs in [Compatibility](compatibility.md).

## 2026-10-24 — MF833U1 on MikroTik / Home Assistant OS

### Environment

- ZTE MF833U1 with Movistar SIM, web UI at `192.168.0.1`.
- MikroTik hEX S, RouterOS 7.20.8 long-term (ARM), modem recognized as running `lte1`.
- LTE Internet fallback successfully tested when fiber physical link failed; recovery also confirmed after correcting an ONT cable-port mistake.
- Home Assistant OS is the intended automation platform; connectivity from HA OS to modem was **not yet tested at this stage**.

### RouterOS SMS limitations

- `/tool sms print` showed `port: none` and `status: off`.
- `/port print` showed no serial ports.
- `/interface lte at-chat lte1 input="AT"` returned `failure: Modem unsupported!`.
- `/interface lte sms` is not a valid command on this RouterOS setup.
- **Conclusion:** Native RouterOS SMS via a serial/AT interface is not available in the observed modem mode. Avoid changing working USB mode/firmware to pursue this.

### HTTP discovery

1. ZTE UI displayed an SMS page with New, Delete, Refresh, Settings.
2. A test SMS sent from another phone arrived and appeared in the UI.
3. Chrome Network inspection revealed `goform_get_cmd_process` and the actual SMS list request.
4. The SMS list response contained `messages`, metadata, and UTF-16-hex content.
5. Simple `cmd=sms_data_total` queries returned an empty string; the full pagination/filter query was needed.
6. In browser console, the full query returned one SMS (`messages.length === 1`).
7. Postman Desktop initially returned `{ "sms_data_total": "" }` for the same URL.
8. Adding `Referer: http://192.168.0.1/index.html` to Postman changed the result to `{"messages":[...]}`.
9. Browser tests showed `X-Requested-With` was **not necessary** for the successful full-query request.
10. A multi-field modem-status query required `multi_data=1` to split command names into separate response fields.

### Questions open at this stage

- Can Home Assistant OS reach and query the modem directly?
- How does the UI send SMS (request method, payload, encoding, authorization)?
- How can new messages be detected reliably without duplicates or missed messages?
- Does the modem paginate, reorder, or expire stored messages?
- How do other ZTE firmware variants behave?

Some of these questions were answered by later experiments documented below.

### Privacy note

Original captures contained a real sender number; this repository deliberately stores only synthetic/redacted examples.

## 2026-10-24 — Outbound SMS API and Home Assistant integration

### Sending SMS through the modem HTTP API

**Status: Verified on the tested MF833U1.**

The modem's web interface was used to identify the outbound SMS operation:

- Endpoint: `POST /goform/goform_set_cmd_process`.
- Form operation: `goformId=SEND_SMS`.
- Destination: `Number`.
- Message text: `MessageBody`, encoded as UTF-16BE hexadecimal data.
- Encoding selector: `encode_type`.
- Additional observed parameters: `isTest`, `notCallback`, `sms_time`, and `ID`.

The request was reproduced in Postman.

The modem returned:

```json
{"result":"success"}
```

The destination phone also received the test message.

This verifies successful sending in the tested environment. It does not establish that every successful API response guarantees delivery.

See [MF833U1 HTTP API findings](api/mf833u1.md) for the recorded request details.

### Unicode encoding experiment

**Status: Verified for the tested characters.**

The following text was tested:

```text
Prueba áéíóú ñ
```

With `encode_type=GSM7_default`, several accented characters arrived incorrectly.

With `encode_type=UNICODE`, the received message preserved the tested characters.

**Conclusion:** The integration should use UTF-16BE hexadecimal message content with `encode_type=UNICODE` for the tested MF833U1.

Emoji support, long-message handling, and multipart behavior remain unverified.

### Home Assistant configuration

**Status: Verified in the tested Home Assistant installation.**

The custom integration was recognized by Home Assistant and successfully configured through its UI.

The configuration supports:

- Modem host, using `192.168.0.1` as the default.
- Multiple default SMS recipients.
- Editing recipients through the options flow.

The recipients interface uses Home Assistant's native telephone text selector with multiple values.

Configuration of multiple recipients was tested. Sending real messages to several distinct recipients has not yet been fully verified.

### Home Assistant SMS action

**Status: Verified through actual SMS reception.**

The `zte_sms.send_sms` action was invoked from Home Assistant.

The action accepts one explicit destination number and a message.

A real SMS arrived successfully, including the tested accented characters.

This confirms that Home Assistant can communicate with the modem for outbound SMS in the tested environment.

It does not independently verify that the existing on-demand inbox-reading code has been exercised from Home Assistant.

### Home Assistant notification entity

**Status: Verified through actual SMS reception.**

The integration implements a modern Home Assistant notification entity:

```text
notify.zte_sms
```

The entity was invoked using the `notify.send_message` action, and the SMS arrived successfully.

The implementation submits an individual SMS request for each configured default recipient.

The entity may display an unknown state in Home Assistant; this does not by itself indicate that notification sending has failed.

### Automated validation

**Status: Passing in GitHub Actions for the tested revision.**

Automated tests cover selected client and encoding behavior.

The GitHub Actions workflow passed after the notification entity was introduced.

However, the existing test coverage does not fully exercise Home Assistant runtime imports, configuration, notification platform behavior, or real modem error conditions.

A successful CI run must not be interpreted as complete compatibility validation.

### Current operational boundaries

The integration currently:

- Sends SMS only when explicitly invoked.
- Does not schedule periodic SMS inbox polling.
- Does not automatically delete stored messages.
- Does not modify the MikroTik router or LTE failover settings.
- Does not provide incoming SMS automation triggers.
- Does not provide cellular signal monitoring.

The modem's web interface remains available for manually sending and reading SMS.

## 2026-10-24 — SMS storage and operational safety observations

### Device SMS capacity

The modem web interface displayed:

```text
Device SMS (10/100)
```

This was interpreted as an indication that 10 of 100 available SMS storage slots were occupied.

**Status: Observed, with incomplete interpretation.**

It has not yet been established whether integration-generated outbound messages occupy these slots, whether concatenated messages consume multiple slots, or how storage behavior varies by firmware.

### Web interface composition limits

The SMS composition interface displayed:

```text
You can choose 5 contacts at most
```

It also displayed counters resembling:

```text
(0/765) (1/5)
```

These are observations about the modem's web interface, not verified limits of the HTTP API.

The five-contact limit may apply only to the browser interface's recipient selection. The integration sends messages individually, so that UI restriction should not automatically be treated as an integration limit.

The length and segment counters require further investigation, particularly when using Unicode.

### Deletion safety

The modem's SMS storage contains messages that may have been received or sent manually.

No reliable method has been verified for identifying the exact stored message created by an integration send operation.

**Decision:** Do not automatically delete any SMS unless its origin can be established unambiguously and the exact modem message identifier can be verified.

Recipient, content, timestamp, or folder membership alone are insufficient.

If reliable identification proves impossible, prefer storage monitoring and warnings over automatic deletion.

## Outstanding research

### SMS reliability

- Classify confirmed sending failures and uncertain outcomes.
- Investigate modem error responses without exposing private information.
- Determine whether delivery receipts are available.
- Verify long messages, multipart SMS, and emojis.
- Avoid automatic retries that could produce duplicate SMS.

### SMS storage

- Determine whether outbound SMS sent through the integration occupy device storage.
- Investigate reliable storage-capacity reporting.
- Determine whether the API exposes an unambiguous identifier for integration-generated sent messages.
- Investigate deletion only if strict ownership guarantees can be established.

### Incoming SMS

- Verify on-demand inbox retrieval from Home Assistant.
- Investigate stable message identifiers, pagination, and deduplication.
- Determine whether inbox reads affect read/unread state.
- Investigate optional incoming-message detection, disabled by default.

### Cellular monitoring

- Investigate modem reachability, network registration, and signal measurements.
- Keep monitoring optional and disabled by default.
- Use a configurable refresh interval if periodic monitoring is introduced.
- Do not modify MikroTik routing, failover, or modem network configuration.
- Do not treat loss of signal as proof of deliberate interference.

### Compatibility and testing

- Record the exact tested modem firmware and Home Assistant versions.
- Expand mocked error-condition tests.
- Improve Home Assistant-specific automated validation.
- Test multiple distinct recipients when practical and explicitly authorized.
- Investigate other modem models only with reproducible evidence.

### Diagnostics

- Add privacy-safe diagnostic logging at appropriate levels.
- Support disabling diagnostic logging through Home Assistant's logging configuration.
- Preserve actionable failures for callers even when logging is disabled.
- Never log SMS contents, complete phone numbers, credentials, cookies, or tokens.

## Research principles

- Preserve historical observations even when later experiments resolve them.
- Clearly distinguish verified results from hypotheses.
- Never run live SMS operations without explicit authorization.
- Use synthetic or redacted data in repository documentation and tests.
- Protect the working LTE Internet fallback configuration.
- Update the API documentation, compatibility matrix, and architecture when new evidence changes supported behavior.