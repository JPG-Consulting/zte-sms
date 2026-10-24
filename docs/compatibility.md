# Compatibility

## Device compatibility matrix

| Device | Firmware | SMS web UI | HTTP inbox read | HTTP send | Home Assistant integration |
|---|---|---|---|---|---|
| ZTE MF833U1 | Exact version not recorded | Verified | Verified through browser and Postman | Verified through Postman and Home Assistant | Working: configuration, SMS action, and notification entity |

**The ZTE MF833U1 is currently the only device tested with this project.**

Compatibility with other ZTE modems or firmware versions must not be inferred from similar HTTP endpoints or web interfaces.

## Verified capabilities

The following capabilities have been tested on the ZTE MF833U1.

| Capability | Status | Evidence |
|---|---|---|
| Display received SMS in modem web UI | Verified | Browser testing |
| Read stored SMS through HTTP API | Verified | Browser and Postman testing |
| Decode UTF-16BE hexadecimal SMS content | Verified | API experiments and automated tests |
| Send SMS through HTTP API | Verified | Postman and Home Assistant testing |
| Send Spanish accented characters and `ñ` | Verified | Successful real-device SMS reception using `UNICODE` |
| Configure modem host in Home Assistant | Verified | Home Assistant testing |
| Configure default SMS recipients | Verified | Home Assistant configuration and options testing |
| Send SMS using `zte_sms.send_sms` | Verified | Home Assistant and real-device testing |
| Send SMS using `notify.zte_sms` | Verified | Home Assistant and real-device testing |

## Implemented but not fully verified

| Capability | Status | Limitation |
|---|---|---|
| Multiple default recipients | Implemented | Sending to multiple distinct recipients has not been fully tested on real hardware |
| On-demand SMS reading in the HTTP client | Implemented | Not exposed as an incoming-message feature in Home Assistant |
| SMS API response handling | Basic implementation | Comprehensive failure scenarios have not been tested |

## Not implemented or not verified

| Capability | Status |
|---|---|
| Incoming SMS entities, events, or automation triggers | Not implemented |
| Automatic incoming SMS polling | Not implemented |
| Cellular signal and network monitoring | Not implemented |
| SMS storage-capacity monitoring | Not implemented |
| Automatic deletion of integration-generated SMS | Not implemented |
| Delivery receipts or confirmed delivery status | Not verified |
| Multipart or long-message behavior | Not verified |
| Emoji support | Not verified |
| Compatibility with other ZTE modem models | Not verified |
| Compatibility across different MF833U1 firmware versions | Not verified |

## Environment

The verified installation uses:

- **Modem:** ZTE MF833U1.
- **Modem HTTP address:** `192.168.0.1`.
- **Router:** MikroTik hEX S.
- **Automation platform:** Home Assistant OS.
- **Cellular operator:** Movistar.

The modem provides LTE Internet fallback through the MikroTik router. SMS functionality has been tested without changing that failover configuration.

The exact Home Assistant version and modem firmware version have not been recorded as part of the compatibility evidence.

## Interpretation of results

**Verified** means the capability was successfully exercised in the stated test environment. It does not guarantee operation with other hardware, firmware, Home Assistant versions, or mobile operators.

**Implemented** means the capability exists in the source code but may lack complete real-device validation.

**Not verified** means no sufficient evidence is available to claim compatibility or correct behavior.

A successful SMS sending API response indicates modem acceptance, not independent confirmation of delivery. Where real SMS reception was observed, that is recorded separately as test evidence.

## Adding compatibility claims

Before adding another device or firmware version:

1. Record the exact modem model and firmware version, when available.
2. Verify the relevant HTTP API behavior.
3. Test the Home Assistant integration against the actual device.
4. Document any differences, limitations, and safety implications.
5. Update this matrix using reproducible evidence.

Do not change modem firmware, USB mode, APN, or router failover configuration merely to establish compatibility.

## Related documentation

- [MF833U1 HTTP API findings](api/mf833u1.md)
- [Architecture](architecture.md)
- [Research log](research-log.md)
- [Troubleshooting](troubleshooting.md)