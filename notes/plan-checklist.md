# Plan checklist — txn-screening-svc

Apply to every `plans/<issue>.md` before approving its PR. Target: **3½ minutes per plan**.
Any **Reject** line fails the plan; any **Escalate** line needs a second reviewer before `plan-approved`.

## 1. Completeness (30 s)

- [ ] All nine sections present, in order, as `##` headings: **Goal · Files to change · Steps · Tests to add · Success criteria · Risks · Rollback / escalation · Evidence to attach · Out of scope**
- [ ] No text before `## Goal` or after `## Out of scope`
- [ ] Steps are numbered and each is small enough to review on its own
- [ ] File paths are repo-relative (`app/models.py`, never `/home/runner/...`)

## 2. Scope check against the issue (60 s)

- [ ] Every file in *Files to change* is justified by the issue's Context / Expected output
- [ ] Nothing in the plan contradicts the issue's *Out of scope*
- [ ] `infra/` is listed under *Out of scope* — **Reject** if it appears in *Files to change*
- [ ] No "while I'm here" extras (refactors, renames, dependency bumps) the issue didn't ask for

## 3. Test coverage (45 s)

- [ ] Every behaviour change has at least one named test under `tests/`
- [ ] Edge cases from the issue's *Test expectations* / *Acceptance criteria* are covered (bounds, empty / whitespace input, duplicates)
- [ ] *Tests to add* lists tests, not steps ("run the full suite" is a step)

## 4. Risk flags (45 s)

| Touches… | Action |
|---|---|
| `infra/` | **Reject** |
| `.github/workflows/`, `.github/agents/`, CODEOWNERS | **Reject** (change it by hand, plan-first, in its own PR) |
| Auth, tokens, secrets, `SECURITY.md` | **Reject** |
| Data deletion or bulk changes in `app/store.py` | **Escalate** |
| Screening `RULES`, scores or decision thresholds in `app/screening.py` | **Escalate** — changes who gets flagged; *Risks* must say how decisions change |
| Real customer / transaction data in examples | **Reject** — synthetic data only |

- [ ] *Risks* names the effect on screening results / alert behaviour (or says "none" and why)

## 5. Success, rollback, evidence (30 s)

Added from [Learn — PR template that requires a structured plan](https://learn.microsoft.com/en-us/training/modules/design-agent-architecture-integration/5-pull-request-governance-controls#implementation-pr-template-that-requires-a-structured-plan).

- [ ] *Success criteria* are verifiable (a request → expected status/result, CI green), not "works correctly"
- [ ] *Rollback / escalation* says how to undo (revert the PR? data to restore?) and who decides if screening results change
- [ ] *Evidence to attach* names what the implementation PR must show (CI run, test output, before/after decision counts for rule changes)

## Verdict

- **Approve** → merge the plan PR → add label `plan-approved` → assign the implementer
- **Request changes** → cite the checklist line(s) by number
- **Reject** → close the PR unmerged, keep the file in `plans/` with `> **REJECTED** — <reason, checklist line>` at the top, never assign the implementer

## Manual gate (fallback if `plan-gate.yml` isn't merged)

The implementer is assigned **only** when the issue has `plan-approved` **and** its `plans/<issue>.md` PR is merged. Checked by: the reviewer, before assigning.
