# Day 2 — The one-liner vs the contract

## Bets

- **Bet A** — Which PR touches more files? **My guess: Vague one-liner**
  - Result: **Miss** — actual: *About the same* (2 files each)

## Evidence (Mission 6)

| | Vague — PR #10 (issue #9 "make alerts better") | Templated — PR #12 (issue #11) |
|---|---|---|
| What it built | Blocked notes on closed alerts (409) — Copilot picked its own problem | `min_risk_score` filter on `GET /alerts` — exactly what was asked |
| Files changed | 2 (`app/routers/alerts.py`, `tests/test_alerts.py`) | 2 (same two files) |
| Lines | +9 / -0 | +51 / -1 |
| Tests added | 1 | 5 (threshold, boundary ==, >100, <0, combined filters) |
| Out-of-scope files touched | None | None (`screening.py`, `models.py`, `infra/`, deps untouched) |
| Plan commit | Yes ("Initial plan") | Yes ("Initial plan") |
| Description vs diff | Matches the diff, but can't be checked against intent — the issue had none | Matches the diff; every acceptance criterion traceable |
| Test suite (local run) | 40 passed | 44 passed |

**Key observation:** the vague issue did *not* cause scope creep — it caused **scope substitution**. Copilot chose a small, plausible, well-tested change that solved *a* problem, not *our* problem. With no acceptance criteria there is nothing to review it against.

## Anti-pattern → template field (Mission 7)

### Observed in PR #10 (vague) and prevented in PR #12 (templated)

| Anti-pattern observed | What happened in #10 | Template field that prevented it in #12 |
|---|---|---|
| Vague scope → **scope substitution** | Copilot picked its own problem (notes on closed alerts) | **Context** + **Expected output** |
| No acceptance criteria | Nothing to review the PR against; "better" can't be verified | **Acceptance criteria** |
| Thin tests | 1 test, for a change nobody asked for | **Test expectations** (named cases → 5 tests, incl. boundary and 422s) |
| Unbounded blast radius (risk, not observed) | Happened to stay small, but nothing stopped it touching `screening.py` or `infra/` | **Out of scope** + file list in **Inputs** |

### What a template can NOT prevent — and what does

| Anti-pattern | Why a template can't stop it | Control that does |
|---|---|---|
| Too many tools | Tool access is set in repo config, not in the issue | Allowlist specific **read-only** MCP tools in the cloud agent's MCP config instead of `*`: the agent uses configured tools autonomously, without asking for approval ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/extend-cloud-agent-with-mcp)) |
| Agent grading its own work | The agent's own tests and summary are what "passed" | Independent checks it didn't write (required CI status checks, CodeQL) + **CODEOWNERS / required human review**; "CI passed" is necessary, not sufficient ([Learn](https://learn.microsoft.com/en-us/training/modules/design-agent-architecture-integration/3-inputs-outputs-success-criteria#example-task-contract-vulnerability-remediation)) |
| Auto-merge without review ("blind trust") | Merge policy lives on the branch, not the issue | Ruleset requiring a PR + approvals + status checks on `main`; CODEOWNERS; risk-based approvals ([Learn](https://learn.microsoft.com/en-us/training/modules/foundations-agentic-ai/5-identify-risks-traceability#common-risks-and-anti-patterns)) |
| Hidden reasoning | The issue says *what*, not how the agent decided | Require a plan in the PR (PR template), link workflow runs, record decisions in PR comments ([Learn](https://learn.microsoft.com/en-us/training/modules/foundations-agentic-ai/5-identify-risks-traceability#common-risks-and-anti-patterns)) |

**Takeaway:** the issue form controls **what the agent is asked to do**. Repo settings (tools, rulesets, CODEOWNERS, PR template) control **what it's allowed to do and how its work gets accepted**. You need both.
