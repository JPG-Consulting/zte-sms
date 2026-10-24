# Troubleshooting and observed failure modes

This document covers known issues, verified observations, and safe diagnostic steps for the ZTE SMS Home Assistant integration.

The initial tested device is the ZTE MF833U1, accessible at `192.168.0.1` in the reference environment.

For protocol details, see [MF833U1 HTTP API findings](api/mf833u1.md). For verified capabilities, see [Compatibility](compatibility.md).

## Home Assistant does not discover the integration

The integration is installed manually as a custom component.

Check that the directory structure is correct:

```text
/config/
└── custom_components/
    └── zte_sms/
        ├── __init__.py
        ├── client.py
        ├── config_flow.py
        ├── const.py
        ├── manifest.json
        ├── notify.py
        └── ...
```

The integration directory must be named `zte_sms`, not `zte-sms`.

After copying or updating the files, restart Home Assistant and try adding the integration again through **Settings → Devices & services**.

If Home Assistant reports an import or setup error, inspect its logs for the specific exception.

A passing GitHub Actions run does not guarantee that every Home Assistant runtime import or API is compatible.

## Home Assistant cannot reach the modem

The tested Home Assistant installation has successfully sent SMS through the MF833U1 HTTP API.

If another installation cannot reach the modem:

1. Confirm the configured modem host is correct. The tested address is `192.168.0.1`.
2. Check whether the modem web interface is reachable from the relevant network.
3. Verify that Home Assistant has a valid network path to the modem.
4. Review the Home Assistant error logs for connection or timeout failures.
5. Check for relevant firewall or network isolation rules without changing them blindly.

A browser reaching the modem from a separate computer does not prove that Home Assistant can reach it.

**Do not modify MikroTik routing, failover rules, modem USB mode, APN, or firmware merely to troubleshoot SMS access.**

## `{"sms_data_total":""}` instead of `messages`

On the tested MF833U1, a Postman GET without the `Referer` header returned an empty value.

Adding:

```http
Referer: http://192.168.0.1/index.html
```

produced a response containing `messages`.

The successful request also included the documented pagination and filtering parameters:

- `page`
- `data_per_page`
- `mem_store`
- `tags`
- `order_by`

See [MF833U1 HTTP API findings](api/mf833u1.md) for the complete verified request.

Do not assume that the same behavior applies to every ZTE model or firmware version.

## Multi-command state query returns one empty key

For a comma-separated list of modem status commands, the tested firmware required:

```text
multi_data=1
```

Without this parameter, the modem interpreted the combined command list as a single command name.

This was observed for status queries. Do not blindly add `multi_data=1` to the working SMS inbox query.

## RouterOS has no serial port

In the tested environment:

- The modem appeared as the `lte1` interface.
- `/port print` showed no serial ports.
- `/interface lte at-chat` reported `Modem unsupported!`.
- Native RouterOS SMS access was not available in the observed modem mode.

The integration uses the modem's local HTTP API instead.

Do not change the modem's USB mode or firmware to obtain a serial interface. The existing LTE Internet fallback must remain operational.

## `zte_sms.send_sms` is not available

The integration registers the action when its configuration entry is successfully set up.

If the action is missing:

1. Confirm that ZTE SMS is installed and configured.
2. Check whether the integration loaded successfully after the last Home Assistant restart.
3. Review the logs for setup or import errors.
4. Confirm that the installed files include the current `__init__.py`.

The action name is:

```text
zte_sms.send_sms
```

It requires one explicit destination number and a message.

Example:

```yaml
action: zte_sms.send_sms
data:
  number: "+34000000000"
  message: "Test message"
```

The phone number is fictional. Do not execute the example against a live modem unless sending the SMS is intended and authorized.

## `notify.zte_sms` is missing

The notification entity is provided by the integration's `notify.py` platform.

If it does not appear:

1. Confirm that the ZTE SMS integration has loaded.
2. Confirm that `notify.py` exists in the installed integration directory.
3. Restart Home Assistant after copying updated files.
4. Inspect the logs for notification platform setup errors.
5. Check the entity registry for the actual entity ID, which may differ if Home Assistant has assigned a suffix.

The tested entity ID is:

```text
notify.zte_sms
```

Use the modern Home Assistant notification action:

```yaml
action: notify.send_message
target:
  entity_id: notify.zte_sms
data:
  message: "Test notification"
```

The example sends a real SMS to configured recipients when executed. Do not run it without authorization.

## Notification entity displays an unknown state

The notification entity may display an unknown state in Home Assistant.

This alone does not mean that SMS sending has failed.

The tested notification entity successfully sent an SMS when invoked through `notify.send_message`.

To investigate an actual failure, inspect the result of the notification action and the relevant Home Assistant logs.

Do not infer SMS delivery status from the entity's displayed state.

## Notification fails because no default recipients are configured

The notification entity uses the default recipients saved in the integration configuration or options.

If the list is empty, sending through the notification entity fails.

Open the integration's options and configure at least one valid recipient.

The `zte_sms.send_sms` action is different: it receives its destination number explicitly and does not require default recipients.

## SMS arrives with corrupted accented characters

The MF833U1 was tested with Spanish accented characters and `ñ`.

When `encode_type=GSM7_default` was used, several accented characters arrived incorrectly.

Using:

```text
encode_type=UNICODE
```

with UTF-16BE hexadecimal message content preserved the tested characters.

The current integration uses `UNICODE`.

If accented characters arrive incorrectly:

1. Confirm that the current integration files are installed.
2. Check that the request uses the expected encoding mode.
3. Verify the hexadecimal encoding with synthetic test data.
4. Do not expose the real SMS body in logs or public bug reports.

Emoji and long-message behavior have not been fully verified.

## The modem accepts the SMS request, but the message does not arrive

The observed successful modem response is:

```json
{"result":"success"}
```

This means the modem accepted the sending request. It is **not independent confirmation of delivery**.

A missing SMS may involve cellular registration, signal conditions, operator handling, recipient details, or other factors.

The integration does not currently provide verified delivery receipts.

**Do not automatically retry a request with an uncertain outcome.** The first SMS might already have been submitted, and retrying could produce a duplicate.

When reporting a failure, record the approximate time, the Home Assistant action used, the non-sensitive error details, and whether the modem was reachable.

Do not include the full recipient number or SMS content.

## Only one recipient receives a notification

The notification entity submits a separate SMS request for each configured default recipient.

If multiple recipients are configured, check that:

- The intended recipients are present in the integration options.
- Their numbers use the supported international format.
- The configuration has been saved.

Sending to multiple distinct real recipients has not yet been fully verified in the reference environment.

A failure during a multi-recipient notification may occur after an earlier recipient's SMS has already been submitted. Do not blindly repeat the entire notification, as this could cause duplicates.

## SMS storage capacity appears to be filling up

The modem web interface has displayed:

```text
Device SMS (10/100)
```

The exact storage behavior of integration-generated outbound SMS has not yet been established.

The integration does not currently monitor storage capacity or automatically delete messages.

Do not delete messages based only on their recipient, content, timestamp, or sent-folder location.

Received messages and manually sent messages must remain protected. Automatic deletion may only be considered if the exact stored message and its integration origin can be established reliably.

## Incoming SMS does not trigger Home Assistant automations

Incoming SMS automation is not currently implemented.

Although the HTTP API has been investigated and the client contains on-demand message-reading functionality, the integration does not expose incoming SMS events, triggers, or entities.

It also does not periodically poll the inbox.

This is an expected limitation, not necessarily a malfunction.

## Cellular signal information is unavailable

Cellular signal and network registration monitoring are not currently exposed as Home Assistant entities.

A future implementation may provide optional monitoring, disabled by default.

The integration must not change the router or modem's cellular configuration to obtain this information.

Loss of signal must not be treated as proof of deliberate interference.

## Diagnostic logging and privacy

Home Assistant's native logging configuration can be used to control log verbosity.

However, comprehensive privacy-safe diagnostic logging is still a development task. Do not assume that every modem failure currently produces a detailed diagnostic message.

When collecting information for a bug report:

- Record the approximate time of the problem.
- Record the relevant action or integration component.
- Include the exception type and non-sensitive error details when available.
- Record the Home Assistant version and modem firmware version if known.
- Remove full phone numbers, SMS contents, credentials, cookies, and tokens.
- Avoid publishing raw HTTP requests or responses without careful redaction.

Never enable logging that exposes private SMS data merely to investigate a failure.

## Before reporting an issue

Confirm that the installed integration matches the current repository revision and that Home Assistant has been restarted after file updates.

Check [Compatibility](compatibility.md) to distinguish supported functionality from features that are not implemented or have not been verified.

If the issue requires testing with a real modem, obtain explicit authorization before sending SMS or performing any state-changing operation.

Preserve the working LTE Internet fallback throughout troubleshooting.