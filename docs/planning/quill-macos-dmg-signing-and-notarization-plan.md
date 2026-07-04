# QUILL macOS DMG Signing and Notarization Plan

Last updated: 2026-07-02
Owner: Release Engineering
Scope: macOS distribution artifacts produced in GitHub Actions for QUILL

## 1. Executive decision

Yes, GitHub Actions can build a working DMG for QUILL and automate signing plus notarization.

GitHub itself does not provide Apple trust. We must provide Apple Developer credentials and certificate material through repository or environment secrets.

Recommendation: for any external beta, sign and notarize. Unsigned beta builds should be limited to internal engineering only.

## 2. Why this matters

If we distribute an unsigned or non-notarized macOS app/DMG, users can see Gatekeeper warnings such as unknown developer, app cannot be opened safely, or quarantine prompts that require bypass steps. This causes:

- Lower install success rate.
- Higher support burden.
- Reduced user trust, especially for accessibility users who need predictable setup.
- Potential security policy blocks in enterprise or managed devices.

For QUILL, this is a product trust and accessibility issue, not only a technical detail.

## 3. Beta policy recommendation

Policy recommendation:

- Internal alpha (dev team only): unsigned allowed temporarily.
- Private beta with external testers: sign and notarize required.
- Public beta or release candidate: sign and notarize required.
- Production release: sign and notarize mandatory.

Practical answer to must I sign for beta:

- If beta includes anyone outside core engineering, yes.
- If strictly internal and short-lived, unsigned can be tolerated with explicit risk acceptance.

## 4. Delivery plan

## Phase 0 - Prerequisites and ownership

Tasks:

- Confirm active Apple Developer Program membership.
- Confirm Team ID and account ownership model (shared org account preferred).
- Generate or renew Developer ID Application certificate.
- Export certificate as P12 and verify password custody.
- Decide notarization auth method:
  - Preferred: App Store Connect API key.
  - Alternate: Apple ID + app-specific password.
- Assign two maintainers for credential rotation and break-glass recovery.

Exit criteria:

- Certificate and notarization credentials validated locally on one macOS machine.

## Phase 1 - Secret and keychain design in GitHub

Tasks:

- Create GitHub environment for release automation (example: macos-release).
- Add required secrets with environment-level protection and least-privilege access.
- Enforce branch protection for workflow changes touching release pipeline.
- Add environment approval gate for release and public beta jobs.

Expected secrets (name examples):

- MAC_CSC_LINK or BUILD_CERTIFICATE_BASE64.
- MAC_CSC_KEY_PASSWORD or P12_PASSWORD.
- APPLE_TEAM_ID.
- One notarization path only:
  - API key path: APPLE_API_KEY_B64, APPLE_API_KEY_ID, APPLE_API_ISSUER, APPLE_TEAM_ID.
  - Apple ID path: APPLE_ID, APPLE_APP_SPECIFIC_PASSWORD.
- Optional hardening:
  - KEYCHAIN_PASSWORD (ephemeral keychain in runner).

Workflow-aligned signing variables:

- MACOS_CODESIGN_IDENTITY (for example, Developer ID Application: Team Name (TEAMID)).
- BUILD_CERTIFICATE_BASE64 and P12_PASSWORD.

Exit criteria:

- Secrets present, masked, and scoped to protected environment.

## Phase 2 - Build, sign, notarize pipeline

Tasks:

- Add or update GitHub Actions workflow running on macOS runner.
- Build QUILL macOS app artifact.
- Sign the app with Developer ID certificate.
- Create DMG artifact for distribution.
- Submit artifact for notarization.
- Staple notarization ticket to final DMG or app bundle as appropriate.
- Upload signed and notarized artifacts.

Quality gates:

- Fail pipeline if signing fails.
- Fail pipeline if notarization fails or times out beyond threshold.
- Preserve notarization logs as build artifacts.

Exit criteria:

- One green CI run produces installable signed/notarized DMG.

## Phase 3 - Verification and user acceptance

Tasks:

- Verify on clean macOS test VM/device:
  - Download from release artifact location.
  - Install without bypass commands.
  - Launch without unidentified developer warnings.
- Run quick accessibility smoke checks after first launch.
- Confirm update/reinstall behavior for signed lineage.

Exit criteria:

- Testers can install and launch with no manual security bypass.

## Phase 4 - Beta rollout controls

Tasks:

- Gate beta publication on successful signed/notarized workflow only.
- Add release checklist item requiring artifact signature verification.
- Add rollback path to prior known-good notarized build.

Exit criteria:

- Beta process cannot publish unsigned artifacts accidentally.

## 5. Risk register

Risk: Unsigned or non-notarized beta distributed externally.

- Impact: High.
- Likelihood without controls: Medium.
- User effect: Security warnings, failed installs, trust erosion.
- Mitigation: Block publish unless signed/notarized check passes.

Risk: Certificate expiration or revocation.

- Impact: High.
- Likelihood: Medium.
- User effect: New builds fail trust checks.
- Mitigation: Calendar renewal reminders, dual owner custody, pre-expiry rotation drill.

Risk: Secret leakage or mis-scoped access.

- Impact: High.
- Likelihood: Low to Medium.
- User effect: Signing abuse and incident response overhead.
- Mitigation: GitHub environments, limited maintainers, mandatory reviews, secret rotation playbook.

Risk: Notarization service outage or API changes.

- Impact: Medium.
- Likelihood: Low to Medium.
- User effect: Delayed beta drops.
- Mitigation: Retry policy, timeout policy, queue visibility, fallback release window buffer.

## 6. Implementation checklist

- Apple Developer membership confirmed.
- Developer ID Application certificate exported and secured.
- Notarization auth method selected.
- GitHub environment and secrets configured.
- Workflow updated for sign and notarize.
- CI failure gates configured.
- Clean-device validation completed.
- Beta publish gate enforced.
- Runbook documented for renewal and incident handling.

## 7. Recommended go/no-go rule for QUILL

Go for external beta only when all are true:

- Signed app.
- Notarized artifact.
- Stapled ticket.
- Clean-device install test passed.

No-go if any are missing.

## 8. Suggested follow-on docs

- Add a release runbook under docs/release with credential rotation procedures.
- Add a short tester-facing install expectation note in beta release notes.
- Add a CI troubleshooting page for common signing/notarization failures.

## 9. Magical execution path (do this now)

Use this as the straight path from fresh Apple account to first green signed and notarized DMG run.

### 9.1 Apple portal setup (one time)

Tasks:

- In Apple Developer, create or confirm a Developer ID Application certificate.
- Export the certificate as a .p12 file from Keychain Access on macOS.
- Generate an App Store Connect API key (.p8), and record:
  - Key ID.
  - Issuer ID.
  - Team ID.
- Capture the exact signing identity string from macOS keychain, for example:
  - Developer ID Application: Team Name (TEAMID)

### 9.2 GitHub CLI setup commands (run from terminal)

Run from the repository root (PowerShell):

```powershell
cd S:\quill
gh auth status
gh repo set-default Community-Access/quill
```

Create the protected environment used by the workflow:

```powershell
gh api --method PUT repos/Community-Access/quill/environments/macos-release
```

Set file-based secrets (replace paths):

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\path\to\DeveloperID.p12")) | gh secret set -e macos-release BUILD_CERTIFICATE_BASE64
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\path\to\AuthKey_ABC123XYZ.p8")) | gh secret set -e macos-release APPLE_API_KEY_B64
```

Set prompt-based text secrets (CLI prompts for values):

```powershell
gh secret set -e macos-release P12_PASSWORD
gh secret set -e macos-release KEYCHAIN_PASSWORD
gh secret set -e macos-release MACOS_CODESIGN_IDENTITY
gh secret set -e macos-release APPLE_API_KEY_ID
gh secret set -e macos-release APPLE_API_ISSUER
gh secret set -e macos-release APPLE_TEAM_ID
```

Verify secrets were created:

```powershell
gh secret list -e macos-release
```

### 9.3 First live run

Run the workflow on your branch:

```powershell
gh workflow run macos-release.yml --ref feature/agent-harness-buildout
gh run list --workflow macos-release.yml --limit 5
gh run watch
```

Optional:

```powershell
gh run view --web
```

### 9.4 First-pass success criteria

- Workflow finishes green.
- DMG artifact exists in the run outputs.
- No signing or notary rejection in logs.
- Local install on clean macOS machine succeeds without bypass steps.

### 9.5 If first run fails, fast triage

- Signing failure: validate MACOS_CODESIGN_IDENTITY text exactly matches certificate identity.
- Certificate import failure: re-export .p12 and verify P12_PASSWORD.
- Notary auth failure: verify APPLE_API_KEY_ID, APPLE_API_ISSUER, APPLE_TEAM_ID, and .p8 source key.
- Notary rejection: inspect notarization logs and confirm hardened runtime and entitlements are applied.

## 10. Operator notes for maintainers

- Keep release credential ownership with at least two maintainers.
- Rotate certificate and API key on a calendar before expiry.
- Do not publish external beta artifacts unless the macOS signed/notarized job is green.
