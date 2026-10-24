# Research log

## 2026-10-24 — MF833U1 on MikroTik / Home Assistant OS

### Environment

- ZTE MF833U1 with Movistar SIM, web UI at `192.168.0.1`.
- MikroTik hEX S, RouterOS 7.20.8 long-term (ARM), modem recognized as running `lte1`.
- LTE Internet fallback successfully tested when fiber physical link failed; recovery also confirmed after correcting an ONT cable-port mistake.
- Home Assistant OS is the intended automation platform; connectivity from HA OS to modem is **not yet tested**.

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

### Remaining questions

- Can Home Assistant OS reach and query the modem directly?
- How does the UI send SMS (request method, payload, encoding, authorization)?
- How can new messages be detected reliably without duplicates or missed messages?
- Does the modem paginate, reorder, or expire stored messages?
- How do other ZTE firmware variants behave?

### Privacy note

Original captures contained a real sender number; this repository deliberately stores only synthetic/redacted examples.
