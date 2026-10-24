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

Use English for:

- Source code and comments.
- Documentation.
- Commit messages.
- Branch names.
- Issues and pull requests.
- Test descriptions and diagnostic messages.

Home Assistant user-facing translations may use other languages.

Existing Spanish translations should be preserved where appropriate.

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

The intended workflow uses two long-lived branches:

| Branch | Purpose |
|---|---|
| `main` | Stable, validated, release-ready code |
| `develop` | Integration branch for upcoming changes |

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

### Branch workflow activation

This workflow is being introduced as part of the project's documentation and repository organization.

Until `develop` exists and branch protections are configured, the repository may still be operating under its previous direct-to-`main` workflow.

Do not assume branch protection is active merely because it is described here.

The initial documentation alignment may be committed to `main` before the new workflow is activated.

After activation, normal feature and documentation changes should follow the branch and pull request process described below.

## Standard contribution workflow

### 1. Start from `develop`

Synchronize the local repository and create a short-lived branch from the latest `develop`.

For example:

```text id="rbd4r9"
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

```bash id="uvbfsy"
python -m unittest discover -s tests -v
```

GitHub Actions provides automated validation for pushed changes and pull requests.

The maintainer may use GitHub Desktop without a local Python development environment.

If local tests cannot be run, state that clearly and use GitHub Actions for the available checks.

A passing workflow does not replace real Home Assistant compatibility testing.

### 4. Commit and push

Use clear, concise commit messages in English.

Suggested format:

```text id="7j99ta"
type: short description
```

Examples:

```text id="yluhci"
fix: handle modem connection timeout
feat: add optional signal monitoring
docs: clarify SMS storage safety
test: cover notification failures
chore: update GitHub Actions workflow
```

Prefer one coherent change per commit.

A coordinated documentation alignment may reasonably be committed as one commit.

Push the branch to GitHub when the change is ready for review.

### 5. Open a pull request

Open a pull request from the working branch into `develop`.

The pull request should explain:

- What changed and why.
- Which behavior was verified.
- Which tests were run.
- Which tests could not be run.
- Whether any live-device testing is required.
- Any privacy, SMS storage, or LTE failover implications.

Do not claim real-device testing unless it actually occurred.

### 6. Review and merge

Review the code, documentation, and automated test results.

Resolve identified problems before merging.

Prefer squash merging for small, focused feature branches when appropriate.

Delete short-lived branches after successful merging when they are no longer needed.

## Promoting `develop` to `main`

When a group of changes is ready for release:

1. Confirm that the intended changes are complete.
2. Run the available automated checks.
3. Perform any necessary, explicitly authorized Home Assistant or modem tests.
4. Review the compatibility matrix and documentation.
5. Confirm that no unsafe SMS behavior or unexpected polling has been introduced.
6. Open a pull request from `develop` into `main`.
7. Review the final changes and merge only after validation.
8. Create a version tag and GitHub release when release criteria are satisfied.

The version declared in `manifest.json` must remain consistent with the intended release.

Do not assume that a manifest version automatically creates a Git tag or release.

## GitHub Desktop workflow

GitHub Desktop is a supported workflow for the project maintainer.

A typical contribution can be completed using:

1. **Fetch origin** and update the local `develop` branch.
2. Create a new branch from `develop`.
3. Edit the files locally.
4. Review changed files in the **Changes** tab.
5. Commit the changes with an English message.
6. Select **Publish branch** or **Push origin**, as appropriate.
7. Open a pull request on GitHub targeting `develop`.
8. Wait for automated checks and complete the review before merging.

Before committing, check the diff for accidental changes, sensitive data, unrelated files, and unintended deletions.

For the initial documentation alignment, the maintainer may continue editing locally and make one coordinated commit on `main` before the new workflow is activated.

## Branch protection

The intended repository protections are:

### `main`

- Require changes through pull requests.
- Require relevant GitHub Actions checks to pass.
- Prevent accidental direct pushes.
- Prevent force pushes and branch deletion.

### `develop`

- Require changes through pull requests.
- Require relevant GitHub Actions checks to pass.
- Prevent force pushes and branch deletion.

Exact GitHub settings should be selected based on repository capabilities and the available CI workflows.

For a small project with a single maintainer, do not enable approval rules that make normal maintenance impossible without another reviewer.

**These are intended protections, not a claim that they are already configured.**

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

The project is currently in early development. The existence of working SMS functionality does not by itself mean that every release criterion has been met.