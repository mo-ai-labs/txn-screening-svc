# Day 3 — The planner who can't pick up a pen

## Bets

- **Bet A** — What does `tools: []` do in an agent profile? **My guess: Disables all tools**
  - Result: **Hit** — actual: *Disables all tools* ([GitHub Docs](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tools))
- **Bet B** — The read-only planner is told **"just fix it"**. What happens? **My guess: It says it can't, and returns a plan**
  - Result: **Hit (mostly)** — actual: *It returned a full six-section plan and made no edit, but it never said it can't; it silently ignored "just fix it"*

![Planning vs execution: two agents, two tool belts](img/d03-planning-vs-execution.svg)

## Lessons (Mission 1 — Anatomy of an agent profile)

- Profiles live in `.github/agents/NAME.agent.md`; the prompt body can be up to **30,000 characters** ([GitHub Docs](https://docs.github.com/en/copilot/reference/custom-agents-configuration))
- **Only `description` is required.** Optional: `name`, `target` (`vscode` / `github-copilot`, default both), `tools` (default all), `model`, `disable-model-invocation` (default `false`), `user-invocable` (default `true`), `mcp-servers`, `metadata` ([YAML frontmatter properties](https://docs.github.com/en/copilot/reference/custom-agents-configuration#yaml-frontmatter-properties))
- `infer` is **retired** → use `disable-model-invocation` **and** `user-invocable` *(correction: the plan names only `disable-model-invocation`)*
- `tools`: omitted or `["*"]` → all tools · a list → only those (unknown names silently ignored) · `[]` → **no tools** · MCP: `server/tool` or `server/*` ([Tools](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tools))
- Aliases: `read` · `edit` · `search` · `execute` (`shell`/`Bash`/`powershell`) · `agent` · `web` · `todo` — **`web` and `todo` don't apply to the cloud agent** ([Tool aliases](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tool-aliases))
- Mnemonic: **D-N-T-T-M + two switches** (Description, Name, Target, Tools, Model + `disable-model-invocation` / `user-invocable`)

## Why split planning from execution (Mission 2)

Source: [Learn — Separate planning, reasoning, and execution](https://learn.microsoft.com/en-us/training/modules/design-agent-architecture-integration/4-plan-reason-execution)

- **Planning** = what and why (PR description / issue comment) · **Execution** = concrete changes (commits) · **Validation** = evidence against success criteria (checks, scans, reviews)
- Four enforcement mechanisms: **read-only planning agent**, **explicit handoff** after approval, **tool gating** in orchestrators, **plan mode**
- Plan-first for high-risk work (workflows, infra, auth, production) → in this repo, any screening rule or threshold change

> "Treat 'instructions not to edit' as guidance; treat tool allowlists and gates as enforcement."

1. **Reviewable intent** — A plan shows *what* and *why* before any diff exists, so a reviewer checks the approach, not just the final code.
2. **Cheaper correction** — Fixing a wrong step in a plan costs a sentence; fixing it after execution costs a reverted PR and a rerun.
3. **Least privilege for the planning step** — Planning only needs `read` + `search`; without `edit`/`execute` the planner *can't* change anything, whatever the prompt says.

## Lessons (Mission 3 — The planner)

- `planner.agent.md` has `tools: ["read", "search"]` only: no `edit`, no `execute` → it **can't** write files or run commands (enforcement)
- The six-section plan shape and "do not modify any file" live in the prompt body → the model is **asked** (guidance)
- Twist: the docs' own *Implementation planner* example has `edit` so it can save plans as markdown. Mine can't write `plans/<issue>.md`, so tomorrow the plan has to reach the PR another way

## Lessons (Mission 4 — The implementer)

| Agent | Tools | Enforced by tools | Only asked by instructions |
|---|---|---|---|
| `planner` | `read`, `search` | Can't edit files or run commands | Six-section plan shape; "don't modify files" |
| `implementer` | `read`, `edit`, `execute` | — (it *can* edit any file) | Only the approved plan; only listed files; never `infra/` |

- The implementer's scope limits are **guidance**: `edit` works on any file. What catches drift is the plan-to-diff review in the PR, plus CI
- No `search` on purpose (per the plan); add it only if the agent struggles to find files

## Lessons (Mission 5 — Making the agents selectable)

Source: [GitHub Docs — Using custom agents](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents#using-custom-agents)

- A profile is only available after it's **merged into the default branch** (PR `agents/d03` → `main`)
- Pick the agent from the dropdown in the **agents panel / agents tab**, or when **assigning an issue** to Copilot; in Copilot CLI use `/agent`
- Org-level agents live in the org's `.github` or `.github-private` repo; a **repo-level agent with the same name overrides** the org one

## "Just fix it" (Mission 6)

- **Prompt:** "In `app/models.py`, `NoteIn.author` and `AssignIn.assignee` accept whitespace-only strings like `"   "`. Just fix it." (agent: **planner**, model: GPT-6 Luna, 0.3 AI credits)
- **Session log tools:** read/view only. It never *tried* `edit` or a shell
- **Edit / commit / branch / PR:** none
- **What it said:** no refusal. It went straight to the plan, even though its instructions say to reply "I only plan" first → the prompt body was only partly obeyed (**guidance**)
- **Drift spotted:** "Files to change" used absolute runner paths (`/home/runner/work/txn-screening-svc/txn-screening-svc/app/models.py`) instead of repo-relative ones → tighten the profile before M7

![Planner returns a plan instead of editing](img/d03-planner-no-edit.png)

**Tools or words?** This run can't fully tell: it never attempted an edit, so the missing `edit` tool was never tested. What it *does* show: the words steered it to plan, and it still skipped one of the words' rules. The tool allowlist is the part that holds even when the words don't.

## Plan runs

Required shape: **Goal · Files to change · Steps (numbered) · Tests to add · Risks · Out of scope**

| Run | Task | Exact structure? | What drifted | Profile change |
|---|---|---|---|---|
| 0 | Whitespace fix, M6 "just fix it" (pre-tightening) | ❌ | Absolute runner paths in *Files to change* (`/home/runner/work/...`); instruction conflict meant no "I only plan" line | Repo-relative paths required; "just fix it" rule rewritten so it no longer clashes with "no text before Goal" → **count restarted** |
| 1 | Whitespace-only `NoteIn.author` / `AssignIn.assignee` → 422 ([screenshot](img/d03-plan-run1.png)) | ✅ | Nothing: six headings in order, `app/models.py` + `tests/test_alerts.py`, numbered steps, `infra/` out of scope | — |
| 2 | Optional `limit` (1–100) on `GET /alerts` ([screenshot](img/d03-plan-run2.png)) | ✅ | Nothing: six headings, repo-relative paths, 4 named tests incl. both bounds, `infra/` out of scope | — |
| 3 | Duplicate watchlist names (case-insensitive, trimmed) → 409 ([screenshot](img/d03-plan-run3.png)) | ✅ | Structure exact. Minor content drift: *Tests to add* opens with a sentence and ends with a "run the full suite" bullet (a step, not a test) | None needed for structure. Optional: "Tests to add = test names only" |

**Observation:** Run 1 ran on GPT-6 Sol (4.2 AI credits) and showed GitHub's **plan-mode** panel ("Plan ready for review" → *Approve plan and start work* / *Exit plan mode*); Run 2 ran on GPT-6 Luna (0.3 credits). Same six-section shape from both models, which points to the profile rather than the model driving the shape (assuming **planner** was selected in each run). The approve button is mechanism #4 (**plan mode**) from Mission 2 in the real UI.

**Result: 3 plans in the exact structure, in a row ✅**

Run 3 stood out on risk: it kept the duplicate check and insert under one `store.lock` (no race), noted that one `WATCHLIST_NAME` hit already scores 70 ≥ review threshold 50 (so decisions don't change), and put `RULES`, thresholds and `_normalise` explicitly out of scope. That's the plan a reviewer can approve *before* any code exists.
