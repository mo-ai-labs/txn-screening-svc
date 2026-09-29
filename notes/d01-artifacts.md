# Day 1: Cloud agent run artifacts

> GH-600 · Week 1 · Day 1: *Hand the agent an issue (and read its rulebook)*

## Bets

| Bet | My guess | Actual | Result |
|---|---|---|---|
| **A**: Path-specific (`tests/**`) says *use fixtures*; repo-wide says *no fixtures*. What happens? | Only the path-specific file is sent | Both are sent; path-specific has higher priority | ❌ miss |
| **B**: Max execution time of one cloud agent session (minutes) | 5 | 59 (hard limit) | ❌ miss |

## SDLC fit

Which SDLC steps should go to an agent? *Agents propose; humans and policy accept.*

| ✅ Good for agents (scoped, testable, easy to verify) | ❌ Not for agents (judgment, high stakes, hard to undo) |
|---|---|
| **Well-scoped fixes**: a bug with clear repro steps and acceptance criteria | **Ambiguous product decisions**: open-ended tasks with no clear "done" |
| **Tests**: raising coverage on existing behaviour | **Cross-repo changes**: the agent can only change one repo per task |
| **Refactors / docs / dependency bumps**: small tech debt, README, Dependabot PRs | **Irreversible ops / production-critical**: deployments, infra, CI workflows, security/PII/auth |

**Screening-service example (good):** add input validation to `POST /transactions/screen` and tests for each `/alerts/{id}/close` disposition. Both are narrow, and CI proves them right or wrong.

**Screening-service example (not):** changing the alert threshold (score ≥ 50) or rule weights in `app/screening.py`, or touching `infra/` / `ci.yml`. That's compliance policy and platform risk, so a human decides and the agent can only write tests around it.

*Sources: [GitHub Docs: Choosing the right type of tasks](https://docs.github.com/en/copilot/tutorials/cloud-agent/get-the-best-results#choosing-the-right-type-of-tasks-to-give-to-copilot) · [MS Learn: Mapping SDLC stages to GitHub artifacts](https://learn.microsoft.com/en-us/training/modules/design-agent-architecture-integration/2-agent-responsibilities#mapping-sdlc-stages-to-github-artifacts)*

## Artifacts

Mission 5 issue: *Add input validation to POST /transactions/screen*. The agent ran **twice** (see timeline).

| Artifact | Link | Where does it live? |
|---|---|---|
| Issue | [#4](https://github.com/mo-ai-labs/txn-screening-svc/issues/4) *(check the number)* | GitHub **Issues**: the task definition, linked to the PR |
| Branch | `copilot/add-input-validation-to-post-transactions-screen-again` (deleted on merge; see the [PR](https://github.com/mo-ai-labs/txn-screening-svc/pull/6)) | **Git refs**: the agent's single `copilot/*` branch for the task |
| Commits | [489a683 Initial plan](https://github.com/mo-ai-labs/txn-screening-svc/commit/489a683) · [8354245 Validate transaction screening inputs](https://github.com/mo-ai-labs/txn-screening-svc/commit/8354245) · [af85d35 Keep screening fixture country valid](https://github.com/mo-ai-labs/txn-screening-svc/commit/af85d35) | **Git history** on that branch. Author `copilot-swe-agent[bot]`, co-authored by me (the assigner) |
| Pull request | [#6](https://github.com/mo-ai-labs/txn-screening-svc/pull/6), merged as [a455262](https://github.com/mo-ai-labs/txn-screening-svc/commit/a455262) | GitHub **Pull requests**: the one PR per task, where human review happens |
| Session log | [Agent task / session](https://github.com/mo-ai-labs/txn-screening-svc/tasks/268af309-5ea9-4f9d-8215-3f573269dc0f?session_id=0fb01dd0-e692-4192-91f6-54a787e28661) | **Agents tab / session view**: reasoning, tool calls, test runs. Not in git |
| Actions run (agent) | [Running Copilot cloud agent](https://github.com/mo-ai-labs/txn-screening-svc/actions/runs/36617632233) (15:12) | **Actions**: the agent's ephemeral environment runs as an Actions workflow |
| Actions run (CI `test`) | [❌ failed on 8354245](https://github.com/mo-ai-labs/txn-screening-svc/actions/runs/36617836323) (15:14:37), then [✅ passed on af85d35](https://github.com/mo-ai-labs/txn-screening-svc/actions/runs/36617878006) (15:14:58) | **Actions / PR Checks**: my `ci.yml` validating the agent's change |
| Other runs on PR #6 | [Code scanning AI findings](https://github.com/mo-ai-labs/txn-screening-svc/actions/runs/36617883171) · [Copilot Code Review](https://github.com/mo-ai-labs/txn-screening-svc/actions/runs/36618611387) · [CI on main after merge](https://github.com/mo-ai-labs/txn-screening-svc/actions/runs/36618887798) | **Actions**: GitHub's own security and review agents, also running on Actions |

### Timeline (EDT, from git)

| Time | Event |
|---|---|
| 15:04 | I commit the instruction files on `rules/d01` ([fed1da7](https://github.com/mo-ai-labs/txn-screening-svc/commit/fed1da7)) |
| 15:07 | **First agent run starts**: [PR #5](https://github.com/mo-ai-labs/txn-screening-svc/pull/5), branch `copilot/add-input-validation-to-post-transactions-screen` |
| 15:12 | [PR #3](https://github.com/mo-ai-labs/txn-screening-svc/pull/3) merged, so the instruction files reach `main` |
| 15:12 | **Second agent run starts**: PR #6, branch `…-again` |
| 15:14 | Agent pushes `8354245` (validation). **CI fails**: the old `"zz"` country in `test_screening.py` is now invalid |
| 15:14 | Agent pushes `af85d35` (fixture `"ZZ"`). **CI passes** |
| 15:21 | Copilot Code Review runs on PR #6 |
| 15:23 | I merge PR #6 |

**Lesson:** run 1 started *before* the rules were on `main`, so they weren't in the `main` branch it started from. Merge the rulebook first, then assign.

## Reflection

- What did the agent do that I didn't expect from the instructions I gave it?
- Financial-crime angle: which of today's artifacts would an auditor ask for first if an agent changed a screening rule?
