# Contributing to ZTE SMS

Thank you for your interest in contributing to ZTE SMS, a Home Assistant custom integration for compatible ZTE LTE modems.

This project is in early development. Contributions should prioritize reliability, safety, maintainability, and reproducible testing.

Before contributing, read:

- [README.md](README.md) — project overview and current functionality.
- [AGENTS.md](AGENTS.md) — development and safety instructions.
- [TODO.md](TODO.md) — current priorities.
- [Architecture](docs/architecture.md) — implementation structure.
- [Compatibility](docs/compatibility.md) — verified support.
- [Research log](docs/research-log.md) — experimental evidence.

## Language

**English is the primary language of this repository.**

Use English for source code, comments, documentation, commit messages, branch names, issues, pull requests, test descriptions, and diagnostic messages.

Home Assistant user-facing translations may use other languages. Existing Spanish translations should be preserved where appropriate.

## Development principles

- Make small, focused changes.
- Prefer fixing reliability problems before adding features.
- Keep modem communication separate from Home Assistant-specific code.
- Follow supported Home Assistant integration conventions.
- Use synthetic data and mocks for automated tests.
- Clearly distinguish verified behavior from assumptions.
- Update documentation when implementation behavior changes.
- Avoid unnecessary dependencies and background tasks.

Do not introduce periodic SMS inbox polling or cellular monitoring by default.

## Safety requirements

### Protect LTE Internet fallback

The tested ZTE MF833U1 provides LTE Internet fallback through a MikroTik hEX S router.

Contributions must not modify:

- MikroTik routing or failover configuration.
- Modem firmware or USB mode.
- APN or cellular network configuration.
- Existing Internet connectivity settings.

SMS functionality must not interfere with the working LTE connection.

### Protect stored SMS

Never automatically delete received messages, manually sent messages, or messages whose origin is uncertain.

Automatic deletion of integration-generated messages may only be considered when both conditions are reliably established:

1. The exact stored message was created by this integration.
2. Its exact modem message identifier is known and verified.

Recipient number, message content, timestamp, and folder membership are not sufficient evidence of ownership.

If safe identification cannot be guaranteed, do not implement automatic deletion.

### Avoid unintended sending

Automated tests must never send real SMS or contact a live modem.

Real-device tests may incur charges and require explicit authorization.

Do not introduce automatic retries when an uncertain outcome could produce duplicate SMS.

A successful modem API response must not be represented as independently verified delivery.

### Protect private information

Never commit or expose:

- Real phone numbers in full.
- Private SMS contents.
- Credentials.
- Session cookies.
- Authentication tokens.
- Unredacted HTTP captures containing sensitive information.

Apply these protections to all diagnostic logging levels, including DEBUG.

## Branching strategy

The project uses two long-lived branches:

| Branch | Purpose |
|---|---|
| `main` | Stable, validated, release-ready code |
| `develop` | Integration branch for upcoming changes |

Both branches are published and protected by active GitHub rulesets.

Short-lived branches are created from `develop`.

Use the following naming conventions:

| Branch prefix | Purpose | Example |
|---|---|---|
| `feature/` | New functionality | `feature/signal-monitoring` |
| `fix/` | Bug fixes | `fix/sms-timeout-handling` |
| `docs/` | Documentation changes | `docs/update-installation-guide` |
| `test/` | Test coverage | `test/notify-entity` |
| `refactor/` | Internal restructuring | `refactor/http-client` |
| `chore/` | Maintenance and tooling | `chore/update-ci` |

Keep branch names short, descriptive, and in English.

### Branch protection status

GitHub rulesets named `Protect main` and `Protect develop` are configured and active.

Both target their respective branches and are configured to:

- Require changes through pull requests.
- Require the `unit` status check from GitHub Actions.
- Require pull request branches to be up to date before merging.
- Prevent branch deletion.
- Block force pushes.
- Require zero approving reviews, allowing maintenance by a single maintainer.

The rulesets were configured in October 2026. Their end-to-end enforcement has not yet been verified through a completed pull request.

The current settings in GitHub remain authoritative if they change.

## Standard contribution workflow

### 1. Start from `develop`

Synchronize the local repository and create a short-lived branch from the latest `develop`.

For example:

```text
develop
   |
   +-- fix/sms-timeout-handling
```

Do not base normal feature branches on `main` unless the project explicitly adopts a separate hotfix process.

### 2. Make a focused change

Keep each branch limited to one coherent task or closely related group of changes.

Read the relevant documentation and tests before editing.

Avoid combining unrelated features, fixes, and documentation updates in one pull request.

### 3. Test the change

Run the available automated tests where a Python environment is available:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions provides automated validation for pushed changes and pull requests.

The maintainer may use GitHub Desktop without a local Python development environment.

If local tests cannot be run, state that clearly and use GitHub Actions for the available checks.

A passing workflow does not replace real Home Assistant compatibility testing.

### 4. Commit and push

Use clear, concise commit messages in English.

Suggested format:

```text
type: short description
```

Examples:

```text
fix: handle uncertain SMS submission outcomes
docs: update contribution workflow
test: cover notification failures
```

Push the working branch to GitHub. Do not push directly to `main` or `develop`.

### 5. Open a pull request to `develop`

Open a pull request from the short-lived working branch into `develop`.

Describe:

- The purpose of the change.
- Relevant implementation details.
- Tests performed and their results.
- Any unverified behavior or required hardware testing.
- Safety implications, especially for SMS sending and storage.

Wait for the required GitHub Actions checks to pass before merging.

Do not merge a change that fails required checks.

### 6. Integrate validated changes into `main`

After changes have been integrated and validated on `develop`, open a pull request from `develop` into `main` when preparing a stable release.

Ensure the required checks pass and the release criteria are satisfied.

Do not treat every merge into `develop` as a release.

## Branch protection

### `main`

- Require changes through pull requests.
- Require the `unit` GitHub Actions check to pass.
- Require branches to be up to date before merging.
- Prevent force pushes and branch deletion.

### `develop`

- Require changes through pull requests.
- Require the `unit` GitHub Actions check to pass.
- Require branches to be up to date before merging.
- Prevent force pushes and branch deletion.

Both rulesets currently require zero approving reviews.

These protections are configured in GitHub, not enforced by documentation alone.

## Testing expectations

### Automated tests

Tests must:

- Use mocks, fixtures, or simulated HTTP responses.
- Avoid live network access.
- Avoid sending or deleting real SMS.
- Use fictional phone numbers and synthetic message bodies.
- Cover relevant success and failure paths.

### Home Assistant tests

Where practical, validate:

- Integration setup and unload.
- Configuration and options flows.
- Action registration and execution.
- Notification entity setup and sending.
- Error propagation.
- Behavior when no default recipients are configured.

### Real-device tests

Real-device tests require explicit approval.

Record:

- The tested device and firmware version, if available.
- The Home Assistant version, if available.
- The operation performed.
- The expected and observed results.
- Any limitations or unexpected behavior.

Never publish real SMS contents or full recipient numbers.

## Documentation updates

Use each document for its intended purpose:

| Document | Responsibility |
|---|---|
| `README.md` | Public overview, installation, and usage |
| `AGENTS.md` | Instructions and constraints for AI coding agents |
| `TODO.md` | Current actionable work and priorities |
| `CONTRIBUTING.md` | Development and contribution workflow |
| `docs/architecture.md` | Current implementation architecture |
| `docs/compatibility.md` | Verified device and feature support |
| `docs/api/mf833u1.md` | Observed HTTP API behavior |
| `docs/research-log.md` | Chronological research evidence |
| `docs/troubleshooting.md` | Known problems and diagnostic steps |
| `docs/decisions/` | Architecture decision records |

Avoid duplicating detailed technical content across documents.

When completing work, update the relevant task in `TODO.md` and any affected documentation.

## AI-assisted contributions

AI coding agents must follow [AGENTS.md](AGENTS.md).

Agents should inspect the current repository before proposing changes and must not rely solely on previous conversation context.

When working with a maintainer who replaces files manually, provide complete file contents unless another format is requested.

Do not perform live modem operations or modify network configuration without explicit authorization.

Do not assume that a passing CI workflow proves Home Assistant runtime compatibility.

## Reporting issues

When reporting a bug, provide:

- A concise description of the problem.
- Steps to reproduce it.
- Expected and actual behavior.
- Relevant Home Assistant and modem versions, if known.
- Sanitized error messages.
- Whether the issue was reproduced on real hardware or only in tests.

Never include credentials, session cookies, real SMS contents, or full phone numbers.

## Release readiness

A release should be considered only when:

- The intended functionality has been validated.
- Available automated checks pass.
- Known limitations are documented.
- The compatibility matrix is accurate.
- Privacy and SMS storage safeguards remain intact.
- No unintended polling or router changes have been introduced.
- Installation instructions match the release contents.

The project is currently in early development. Working SMS functionality and passing unit tests do not by themselves establish production readiness.