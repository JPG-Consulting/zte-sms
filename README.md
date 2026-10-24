# ZTE SMS for Home Assistant

Exploratory, open-source Home Assistant custom integration for SMS-capable ZTE LTE modems, initially **ZTE MF833U1**.

> **Status: research scaffold / not installable yet.** Receiving SMS through the MF833U1 HTTP API has been demonstrated using a browser and Postman. Sending SMS, Home Assistant connectivity, authentication variants, and a complete integration are **not yet verified**.

## Goals

- Read SMS messages and decode their UTF-16 hexadecimal content.
- Detect new messages without duplicate automation triggers.
- Eventually send SMS via a Home Assistant action (pending API research).
- Preserve the modem's existing LTE Internet fallback configuration.
- Support additional ZTE models only after model-specific validation.

## Documentation

- [Research log](docs/research-log.md)
- [MF833U1 HTTP API findings](docs/api/mf833u1.md)
- [Architecture](docs/architecture.md)
- [Compatibility](docs/compatibility.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Architecture decision records](docs/decisions/0001-custom-integration.md)
- [Agent guidance](AGENTS.md)

## Development

The `custom_components/zte_sms` directory is reserved for a future Home Assistant integration. It deliberately contains no installable manifest yet. The `tests/` directory contains isolated decoding tests; no test contacts a real modem.

Run tests with `python -m unittest discover -s tests -v`.

## Security and privacy

Keep real phone numbers, SMS bodies, cookies, credentials, modem tokens, and complete private request/response dumps out of issues and commits. Do not expose the modem HTTP interface to the public Internet. Sending/deleting SMS must never happen automatically in tests.

## License

MIT; see [LICENSE](LICENSE).
