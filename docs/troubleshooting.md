# Troubleshooting and observed failure modes

## `{"sms_data_total":""}` instead of `messages`

On the tested MF833U1, a Postman GET without `Referer` returned an empty value. Adding `Referer: http://192.168.0.1/index.html` yielded `messages`. Ensure the full query includes `page`, `data_per_page`, `mem_store`, `tags`, and `order_by` as documented in `api/mf833u1.md`.

## Multi-command state query returns one empty key

For a comma-separated `cmd`, add `multi_data=1`. This was observed for status queries; do not blindly add it to the working inbox query.

## RouterOS has no serial port

The tested ZTE enumerated as `lte1`, with no `/port` entries and unsupported `at-chat`. The HTTP API is the current research path; do not alter the working LTE fallback configuration.

## Home Assistant cannot reach modem

Not yet tested. Confirm routing and reachability from the Home Assistant OS host/container before diagnosing the API. Do not change MikroTik routing without a specific, evidenced need.
