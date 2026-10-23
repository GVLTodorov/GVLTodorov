# Multi-Agent Dev Team Template (Claude Code)

A starter template for running **one "brain" (orchestrator)** that clarifies requirements
and hands work to **five specialist sub-agents** that work in parallel:

| Agent | Responsibility | Model | Effort | Runs in parallel with |
|---|---|---|---|---|
| **brain** (main session) | Triages the task, asks clarifying questions, writes the spec + API contract, splits work, merges results, reports cost | `opus` | high | — |
| `frontend` | UI, client state, API client code | `sonnet` | medium | backend, devops |
| `backend` | API, business logic, data layer, migrations, Swagger | `sonnet` | medium | frontend, devops |
| `devops` | Dockerfile, compose, CI/CD, versioning, coverage badges, `.vscode` | `sonnet` | medium | frontend, backend |
| `tester` | Unit/integration/e2e tests against the spec | `sonnet` | medium | after implementation (or alongside, from the contract) |
| `security` | Read-only review: OWASP, secrets, deps, container hardening | `opus` | high | after implementation |

### Model per agent — and why

| Agent | Model | Why this model |
|---|---|---|
| **brain** | `opus` | The hardest thinking in the whole flow: turning vague requirements into a spec and contract, splitting ownership, resolving merge conflicts, judging fix loops. A mistake here repeats across all five agents. |
| `frontend` | `sonnet` | Well-specified implementation work against a fixed contract. Sonnet is fast and strong at code, and runs in parallel at lower cost. |
| `backend` | `sonnet` | Same as frontend: the contract has already settled the hard design decisions. |
| `devops` | `sonnet` | Mostly following known patterns (Dockerfile, CI, `.vscode`) that the templates spell out. |
| `tester` | `sonnet` | Writes tests from explicit acceptance criteria; high volume, well-defined. |
| `security` | `opus` | Has to reason across files (auth flows, IDOR, data paths) to find issues nobody pointed it at. Missed findings are costly, and it is read-only, so its token use stays modest. |

**Where the model is set:**
- Sub-agents: the `model:` (and `effort:`) lines in each `.claude/agents/<name>.md` frontmatter.
  Model values: `opus`, `sonnet`, `haiku`, `inherit` (use the main session's model), or a full
  model ID such as `claude-opus-5-5`.
- Brain: the `model: opus` line in `.claude/skills/task/SKILL.md` switches the session to Opus
  while `/task` runs. You can also just run `/model opus` before starting.
- The brain may override a model for a single run (e.g. a light security pass on `sonnet`), as described in its Phase 4.

**When to change it:**
- Tight budget → put `security` on `sonnet` too; keep the brain on `opus`.
- Hard or unfamiliar domain (complex algorithms, tricky concurrency) → raise `backend` to `opus`.
- `haiku` only for very mechanical work: the brain's repo scan in Phase 0, or agents you might add
  later (docs, formatting). Don't use it for the five above.

---

## 1. How it fits together

```
                 ┌──────────────────────────────┐
   you  ───────► │  BRAIN (main Claude session) │  ← only the main session can ask you
                 │  T. triage: S / M / L        │    questions and spawn sub-agents
                 └──────────────┬───────────────┘
              S (small) ────────┤──────── M / L
     brain does it alone        │ clarify → docs/spec.md + docs/api-contract.md
     or with ONE agent          │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
       frontend             backend              devops        ← Phase 2: parallel
     (worktree)            (worktree)          (worktree)        only the agents that have work
            └───────────────────┼───────────────────┘
                                ▼
                     brain merges branches
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
              tester                       security            ← Phase 4: parallel
                 └──────────────┬──────────────┘                 (security only if risky files changed)
                                ▼
         brain: fix loop (continue same agents) → report + cost table
```

**Two rules make parallelism work:**

1. **Contract first.** Frontend and backend never wait on each other because the brain
   writes `docs/api-contract.md` (endpoints, request/response shapes, error codes) *before*
   spawning them. Both sides build against the contract, not against each other's code.
2. **Isolated worktrees + file ownership.** Each implementer works in its own git worktree
   and only touches its own folders. The brain is the only one who merges.

> **Why the brain is the main session, not a sub-agent:** in Claude Code, sub-agents can't
> spawn other sub-agents and can't interactively ask you questions. So the brain must be
> your main conversation. We package it as a **skill** (`/task`) you invoke to start.

---

## 2. Folder layout to create in your project

```
your-project/
├── CLAUDE.md                        # project facts + token rules every agent reads
├── Dockerfile                       # ONE image: builds frontend + backend, backend serves the UI
├── .nvmrc                           # the ONE runtime version (Dockerfile, CI, engines all follow it)
├── frontend/                        # ┐
├── backend/                         # │ created empty (with .gitkeep) by /task init,
├── e2e/                             # ┘ then filled by the owning agents
├── .github/
│   ├── workflows/                   # CI by devops
│   └── scripts/                     # ALL helper scripts/tools by devops (no root infra/ folder)
├── .vscode/                         # launch.json + tasks.json by devops: F5 runs backend + UI together
├── docs/
│   ├── spec.md                      # written by brain after clarification
│   ├── api-contract.md              # written by brain, the frontend↔backend contract
│   ├── tasks.md                     # brain's task board (who does what, status)
│   └── cost-log.md                  # brain appends a cost table after every /task
└── .claude/
    ├── settings.json                # blocks reading generated folders, pre-allows slow build/test commands
    ├── skills/
    │   └── task/SKILL.md            # the orchestrator ("brain") → invoke with /task
    ├── agents/
    │   ├── frontend.md
    │   ├── backend.md
    │   ├── devops.md
    │   ├── tester.md
    │   └── security.md
    └── templates/                   # long reference code, read ONLY when needed
        ├── swagger-topbar.js
        ├── ci.yml
        ├── vscode-launch.jsonc
        └── vscode-tasks.jsonc
```

Copy each block below into the matching file. Replace anything in `<angle brackets>`.

---

## 3. `CLAUDE.md` (shared project context)

Every agent reads this automatically, so keep it short; it is paid for on every agent start.

```markdown
# Project: <name>

## Stack
- Runtime:  <e.g. Node 22.12>  → single source of truth: `.nvmrc` (+ `engines` in each package.json)
- Frontend: <e.g. React 19 + Vite + TypeScript + Tailwind>   → lives in `frontend/`
- Backend:  <e.g. Node 22 + Fastify + PostgreSQL + Prisma>   → lives in `backend/`
- Infra:    <e.g. Docker Compose, GitHub Actions, Traefik>   → root `Dockerfile`/compose, `.github/` (scripts in `.github/scripts/`)
- Tests:    <e.g. Vitest, Playwright, Supertest>             → `*/tests/`, `e2e/`

## Commands
- Install:  <npm ci>
- Dev:      <docker compose up>
- Lint:     <npm run lint>
- Test:     <npm test -- --reporter=dot>  /  e2e: <npx playwright test --reporter=line>
- Test one file: <npm test -- path/to/file.test.ts --reporter=dot>

## Rules
- The API contract in `docs/api-contract.md` is the source of truth. Don't change it
  without the brain's approval — report the needed change instead.
- **Dev/test config keys are committed on purpose.** Each app keeps a committed
  `.env.development` and `.env.test` with working values (DB passwords, JWT secrets, test API
  keys…), so a fresh clone runs (F5) and tests pass with no setup. Don't gitignore them, don't
  move them out of the repo, and don't replace them with placeholders.
- These keys are for **local/test only**. Production secrets never go in the repo: they come from
  GitHub Actions secrets or the deployment host's environment. Code must not fall back to a test key
  in production.
- Commit only on your own branch; never push to main.
- Use Conventional Commits (`feat:`, `fix:`, `chore:`, `feat!:` …). CI derives the image
  version from them, so the wrong prefix gives the wrong version bump.
- **Lockfiles must install on Linux:** after changing dependencies, verify with a clean `npm ci`
  and check new deps' `engines` against `.nvmrc`. A lockfile made on Windows/macOS can miss
  Linux optional binaries; the Docker build is the real check.
- **Local services: use `127.0.0.1`, not `localhost`,** in server-side connection strings and
  proxy targets (DB, SMTP, dev-server proxy). Docker publishes ports on IPv4, and Node can
  resolve `localhost` to `::1` (IPv6) first, especially on Windows.
- **Clean up what you start:** stop every server/container you started before you report, so
  ports are free for the next agent and for the user's F5.

## Token rules (every agent)
- Read only what your task needs: your task IDs' sections of `docs/spec.md` and
  `docs/api-contract.md`, and files in your folders. Use Grep/Glob to find code, then read the
  relevant part, not whole large files.
- Never read generated folders: `node_modules`, `dist`, `build`, `coverage`, lockfiles.
- Quiet commands: tests with `--reporter=dot` (or `--silent`), installs with `--silent`,
  and pipe long output through `| tail -n 50`. **Exception:** never `--silent` inside a
  Dockerfile or CI step; use `--loglevel=error` so a failure still shows its cause.
- Slow commands (image builds, cold installs, e2e suites) can take 10+ minutes: run them in the
  background with a long timeout instead of letting them time out and retrying.
- While fixing, run only the affected test files. Run the full suite once, at the end.
- Read files in `.claude/templates/` only when your task creates or changes that piece.
- Reports: **max ~150 words or one table.** No full logs: quote only the failing lines
  (max 20), and never paste whole files or diffs.
```

---

## 4. The brain — `.claude/skills/task/SKILL.md`

```markdown
---
name: task
model: opus
description: Orchestrator for a feature. Triages the task, clarifies requirements with the user, writes the spec and API contract, then dispatches frontend/backend/devops/tester/security sub-agents in parallel, integrates their work and reports the cost. Use on /task or when the user wants to start a new feature with the agent team.
---

You are the **lead engineer and orchestrator**. For M/L tasks you do not write feature code
yourself; you clarify, plan, delegate, integrate, and verify. You run on the most expensive
model, so delegate reading and doing, and keep your own context small.

## Phase T — Triage (always first)
Classify the request and say which size you picked and why, in one line:
- **init** (`/task init`, or `.github/workflows/ci.yml` / `.vscode/launch.json` are
  missing): a one-time setup run. First create the empty project folders yourself
  (`frontend/`, `backend/`, `e2e/`, `docs/`, `.github/scripts/`), each with a `.gitkeep` so git
  keeps them. Never create a root `infra/` folder;
  skip any that already exist and never overwrite files. Then spawn only `devops` to create the
  single-image Dockerfile, compose, CI with coverage badges + versioned image release, and
  `.vscode`. Then skip to Phase 6.
- **S (small)**: a bug fix or small change in ≤ ~3 files in one area. **No team.** Skip
  the spec/contract docs. Do it yourself, or spawn the ONE owning agent with a short prompt. Run
  the affected tests, then go to Phase 6.
- **M (medium)**: one area, or a small change across areas. Clarify briefly, update only
  the affected parts of the docs, and spawn **only the agents that have tasks**.
- **L (large)**: a new feature across frontend + backend. Run all phases.
Never spawn `devops` for a feature unless it changes Docker, compose, CI, env files or `.vscode`.

## Phase 0 — Clarify (M/L)
1. Read `CLAUDE.md`. To learn what exists, spawn the built-in `Explore` agent with
   `model: "haiku"` and ask for a ≤150-word summary of the relevant code. Don't skim the
   repo yourself.
2. Ask the user **at most 5 focused questions** in one AskUserQuestion call, covering
   only what you can't infer:
   - Goal & users: what problem, who uses it, what does "done" look like?
   - Scope: must-have vs. nice-to-have; explicitly out of scope?
   - Data: what entities/fields; any existing DB/API to integrate with?
   - Non-functional: auth model, performance, expected load, browsers/devices.
   - Deployment: where does it run, which environments, any CI constraints?
   Offer a recommended default for each so the user can just accept.
3. Restate the requirements in 5–10 bullet points and get an explicit "yes" before Phase 1.

## Phase 1 — Spec & contract (M/L)
Write these files, then show the user a short summary:
- `docs/spec.md` — user stories with **acceptance criteria** (Given/When/Then, IDs like `AC-3`),
  out-of-scope list. Use one heading per area so agents can read only their section.
  If there is a UI, always include a responsive criterion: usable at 360px / 768px / 1280px
  with no horizontal page scroll.
- `docs/api-contract.md` — every endpoint: method, path, auth, request schema, response
  schema, error codes, example payloads. Include shared types/enums.
- `docs/tasks.md` — task table: `ID | Agent | Task | Files owned | Depends on | Status`.
  Each file/folder is owned by exactly ONE agent. No overlaps.

## Phase 2 — Parallel build
Spawn **only the agents with tasks**, **in the same message** so they run in parallel,
each with `isolation: "worktree"`. Keep every prompt short (≤ ~200 words) and self-contained:
- The task IDs it owns, the exact folders it may edit, and the acceptance-criteria IDs it covers.
- Which sections of `docs/spec.md` / `docs/api-contract.md` to read (by heading). Point to
  files; don't paste their content.
- "Done means": builds, lints, its own unit tests pass, branch committed.
- "Report back in ≤150 words: branch, files changed, check results (pass/fail + failing lines
  only), open questions, any contract change you need (do NOT make it yourself)."
Record each agent's **name/ID** so you can continue it later (Phase 5).

## Phase 3 — Integrate
1. Review each report. If an agent requests a contract change, decide, update
   `docs/api-contract.md`, and continue the affected agents.
2. Merge the branches into an integration branch; resolve conflicts yourself.
3. Run build + lint + tests with quiet output (`| tail -n 50`). If broken, send the failing
   lines to the owning agent.
4. **Image smoke (before Phase 4, every time deps, Dockerfile or compose changed):** build and
   start the app image the way CI does (e.g. `docker compose … up -d --build --wait`, in the
   background with a long timeout), then hit the health endpoint and `/`. If it fails, send
   the failing build lines to the owner of that stage (devops for Dockerfile/compose,
   frontend/backend for their lockfile/deps) and fix it **before** spawning the tester.
   A broken image found during e2e costs the most time of anything in this workflow.
5. Leave the stack running for Phase 4 and note its URLs (app, mail sink, etc.).

## Phase 4 — Verify (parallel)
Spawn in the same message, against the integration branch:
- `tester`: always for M/L. Its prompt must give the running stack's URLs (e.g. `BASE_URL`)
  and say: "Don't build or start the app yourself; if it isn't reachable, report that at once."
  Give it a time box: one full run, then `--last-failed`, at most 2 reruns, then report.
- `security`, depending on what the diff touches:
  - auth, sessions, user data access, input handling, dependencies, Dockerfile/CI or `.env*`:
    full review on its default model (`opus`).
  - anything else (UI-only, copy, styling, internal refactor): a light pass with
    `model: "sonnet"`, limited to the changed files, or skip it and say so in the report.

## Phase 5 — Fix loop
- Route each failed test / finding to the owning agent by **continuing that same agent with
  SendMessage** (it keeps its context and doesn't re-read the repo). Spawn a new agent only
  if the original can't be continued.
- Send only the exact evidence (failing test name + ≤20 lines). Tell it to rerun only the
  affected tests.
- Max **2 fix rounds**; after that, stop and ask the user how to proceed.
- Security findings rated High/Critical block completion. Medium/Low → list them for the user.
- Batch: collect tester + security results first, then send each owner ONE message with all its
  items, so a round isn't spent per finding.
- After a fix merges, **restart/rebuild the running stack before re-testing**; testing against
  a stale build produces false failures.

## Phase 6 — Report
Give the user, briefly: what was built (mapped to acceptance criteria ✅/❌), test results,
security summary, how to run it, open risks/TODOs. Do not commit to main or push unless
the user explicitly asks. Stop the stack and any processes you started (free the ports).

Finish with **two cost tables**. Each sub-agent's completion result includes its usage (total
tokens, tool uses, duration).

**1. Per sub-agent**: one row per agent. Add up every run of the same agent (first spawn +
each continued fix round):

| Agent | Model | Runs | Tool uses | Tokens | Duration | Est. cost |
|---|---|---|---|---|---|---|
| explore | haiku | 1 | … | … | … | $… |
| frontend | sonnet | 2 | … | … | … | $… |
| … | | | | | | |
| **Sub-agents total** | | | | **…** | **…** | **$…** |

**2. Per model**: one row per model used, summing the rows above (e.g. tester and security
on `sonnet` share one row). Use it to see where the money goes:

| Model | Agents | Runs | Tokens | Share of tokens | Est. cost |
|---|---|---|---|---|---|
| opus | security | 1 | … | …% | $… |
| sonnet | frontend, backend, tester | 5 | … | …% | $… |
| haiku | explore | 1 | … | …% | $… |
| **Total** | | **…** | **…** | 100% | **$…** |

- Est. cost = tokens × the blended $/1M-token rate for that model from `docs/cost-log.md`.
  Label it an estimate. If no rates are filled in, leave the column as `—`.
- The brain's own usage isn't in these tables. Tell the user to run `/cost` for the exact
  session total, which includes the brain.
- Append **both** tables, under one dated heading with the task title and size (S/M/L), to
  `docs/cost-log.md`.

## Rules
- Never let two agents edit the same file.
- Never invent requirements — if unsure, ask.
- Keep sub-agent prompts self-contained: they don't see this conversation.
- Prefer fewer agents. Each spawn starts cold and re-reads files.
- Background agents can't answer permission prompts; a blocked command looks like a hang.
  Long-running commands they need must be allowed in `.claude/settings.json`.
- Agents running in parallel must not share mutable test state (same test DB, same port).
  If two agents' tests run at once, failures like deadlocks or 401s are noise; rerun before routing.
```

### `docs/cost-log.md` (starter)

```markdown
# Cost log

Blended $ per 1M tokens, used by the brain for estimates. Fill in from
https://www.anthropic.com/pricing (a blend of input/output/cache; rough is fine):

| Model | $/1M tokens (blended) |
|---|---|
| opus | <fill in> |
| sonnet | <fill in> |
| haiku | <fill in> |

<!-- The brain appends one dated entry per /task below, newest on top:
     a per-sub-agent table and a per-model table. -->
```

---

## 5. `.claude/settings.json` (block token-wasting reads, pre-allow slow commands)

`deny` stops every agent from opening or searching generated folders. `allow` pre-approves the
long build/test commands: sub-agents run in the background and **can't answer a permission
prompt**, so an un-allowed `docker build` or e2e run just stalls. Adjust the list to your stack;
on Windows add the same entries as `PowerShell(...)`.

```json
{
  "permissions": {
    "allow": [
      "Bash(npm ci:*)",
      "Bash(npm install:*)",
      "Bash(npm run:*)",
      "Bash(npm test:*)",
      "Bash(npx playwright:*)",
      "Bash(docker build:*)",
      "Bash(docker compose:*)",
      "Bash(docker ps:*)",
      "Bash(curl:*)"
    ],
    "deny": [
      "Read(./**/node_modules/**)",
      "Read(./**/dist/**)",
      "Read(./**/build/**)",
      "Read(./**/coverage/**)",
      "Read(./**/package-lock.json)",
      "Read(./**/pnpm-lock.yaml)",
      "Read(./**/yarn.lock)"
    ]
  }
}
```

---

## 6. Sub-agents — `.claude/agents/*.md`

### `frontend.md`

```markdown
---
name: frontend
description: Frontend implementer. Builds UI, client state, and the API client strictly from docs/api-contract.md. Use when the brain assigns frontend tasks.
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
effort: medium
---

You are a senior frontend engineer. Follow the token rules in `CLAUDE.md`.

**Before coding:** read your task IDs in `docs/tasks.md` and only the sections of
`docs/spec.md` / `docs/api-contract.md` the brain named.

**You may edit only:** `frontend/**` (and anything else explicitly assigned to you).

**How to work**
- Build against the contract. Until the backend is merged, mock the API with the contract's
  example payloads (e.g. MSW or a fixtures file) — never wait on the backend.
- Generate/define API types from the contract; one typed API client module, no ad-hoc fetches.
- Handle loading, empty, and error states for every screen. Accessible markup (labels, roles, keyboard).
- **Responsive, mobile-first:** every screen works on mobile, tablet and desktop. Base styles
  target ~360px, then `min-width` breakpoints (e.g. 640 / 1024px). Fluid layouts (flex/grid,
  `minmax`, %), no fixed widths, no horizontal page scroll at 360px. Viewport meta tag present.
  Touch targets ≥44×44px; nothing hover-only. Navigation collapses to a menu; wide tables
  become cards or scroll inside their own container; media scales (`max-width: 100%`).
- Follow existing components/styles; don't add a UI library without being told.
- Write unit/component tests for logic and key components.
- Dev-server proxy targets use `127.0.0.1` (e.g. `'/api': 'http://127.0.0.1:<PORT>'`), not `localhost`.
- New dependencies must support the runtime in `.nvmrc` (check their `engines`; bundlers with
  native bindings often need a newer minor). Don't downgrade a tool to dodge an old runtime pin:
  report it so devops bumps the runtime.

**Done means:** `lint`, `typecheck`, `build`, and your tests pass; a clean `npm ci` works; if
you changed dependencies, the image's frontend stage builds (`docker build --target <frontend-stage> .`,
run in the background, since cold installs are slow); every new/changed screen
checked at 360px, 768px and 1280px widths; work committed on your branch.

**Report back (≤150 words):** branch, files changed, check results (failing lines only),
responsive check (widths verified, any known issues), acceptance criteria covered, open questions,
contract changes you need (describe — do not edit the contract).
```

### `backend.md`

```markdown
---
name: backend
description: Backend implementer. Builds API endpoints, business logic, data models, migrations and Swagger exactly as specified in docs/api-contract.md. Use when the brain assigns backend tasks.
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
effort: medium
---

You are a senior backend engineer (Node.js). Follow the token rules in `CLAUDE.md`.

**Before coding:** read your task IDs in `docs/tasks.md` and only the sections of
`docs/spec.md` / `docs/api-contract.md` the brain named.

**You may edit only:** `backend/**` (and anything else explicitly assigned to you).

**How to work**
- Implement every endpoint exactly as the contract says: paths, status codes, error shapes.
- Validate all input at the boundary (schema validation); never trust the client.
- Parameterized queries / ORM only. AuthN/AuthZ checks on every protected route.
- Migrations are forward-only and reversible where possible; include seed data for dev.
- Config via env vars. Add every new key with a working local/test value to the committed
  `backend/.env.development` and `backend/.env.test` (with a comment saying what it is).
- Structured logging; no secrets or PII in logs.
- On startup log exactly `Listening on http://localhost:<PORT>`. The VS Code launch config
  watches for this line to open Swagger.
- The app ships as **one Docker image**: in production the backend also serves the built
  frontend (static files from a configurable dir, e.g. `STATIC_DIR`, with SPA fallback to
  `index.html` for non-API routes). Keep API routes under a prefix (e.g. `/api`) so they never
  clash with UI routes.
- Write unit tests for logic and integration tests per endpoint (happy path + main errors).
- **Isolated test DB per run:** test setup creates its own database or schema (e.g.
  `?schema=test_<pid|worker-id>`), migrates it, and drops it after. Never share one fixed test DB:
  parallel agents/workers then deadlock or wipe each other's data.
- **Make time testable:** background workers, schedulers and delays read their interval from env
  (fast values in `.env.test`, e.g. a mail worker every 500 ms). Behind `NODE_ENV=test` only, expose
  test hooks so e2e never waits on the wall clock: e.g. `POST /api/test/jobs/:name/run` to trigger
  a scheduled job now, and a clock override. List them in the contract under "Test-only"; they
  must not exist in production builds.
- Bind dev/test servers to `127.0.0.1`, and use `127.0.0.1` in local DB/SMTP URLs.
- Don't put codegen that needs source files (ORM client generation etc.) only in `postinstall`:
  in the Dockerfile, `npm ci` runs before the source is copied. Run it in the `build` script, or
  tell devops which files must be copied before install.

**Swagger / OpenAPI (required)**
- Serve an OpenAPI 3 spec that matches `docs/api-contract.md` (every endpoint, schema, error
  response and example). Serve Swagger UI at **`/swagger`** and the raw spec at `/swagger.json`.
  Use the framework's standard package (Express: `swagger-ui-express`; Fastify: `@fastify/swagger`
  + `@fastify/swagger-ui`; NestJS: `@nestjs/swagger`).
- If the API uses auth, add a `bearer` security scheme so Swagger's **Authorize** button works.
- **Top-bar link buttons:** a horizontal row of buttons in the Swagger UI top bar that open the
  app's UIs in a new tab (default: one **`UI`** button; one more per extra app or dev tool).
  This makes Swagger the dev home page: start the backend, open Swagger, and go to the frontend in one click.
  URLs come from env vars (e.g. `UI_URL`, default `http://localhost:5173`) in the committed
  `.env.development` / `.env.test`.
  **When you first set this up, read `.claude/templates/swagger-topbar.js` and use its styling
  and script exactly** (same as the Rubik/Browse projects). Don't read it otherwise.
- Integration test: `GET /swagger.json` returns 200 with every contract path, and `/swagger`
  HTML contains the `app-links` style.

**Done means:** lint, build, and tests pass; a clean `npm ci` works; if you changed dependencies,
the image's backend stage builds (`docker build --target <backend-stage> .`, in the background);
the server starts; `/swagger` loads with the top-bar buttons; work committed on your branch.

**Report back (≤150 words):** branch, endpoints implemented, files changed, check results
(failing lines only), new env vars, open questions, contract changes you need (describe — do not edit the contract).
```

### `devops.md`

````markdown
---
name: devops
description: DevOps engineer. Owns the single-image Dockerfile, docker-compose, CI/CD pipelines (coverage badges, versioned image release), environment configuration and the .vscode run setup. Use for /task init or when the brain assigns infra/build/deploy tasks.
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
effort: medium
---

You are a senior DevOps engineer. Follow the token rules in `CLAUDE.md`.

**Before working:** read your task IDs in `docs/tasks.md` (if present) and `CLAUDE.md`.
Read a file from `.claude/templates/` only when you create or change that piece.

**Helper scripts and tools go in `.github/`, never in a root `infra/` folder.** Workflows in
`.github/workflows/`, every helper script (build, release, badge generation, DB backup, setup…)
in `.github/scripts/`, called from CI by that path. Don't create `infra/`, `scripts/` or `tools/`
at the repo root.

**You may edit only:** `.github/**`, `Dockerfile*`, `docker-compose*.yml`,
`.dockerignore`, root-level `.env.*` files (backend/frontend own their own `.env.development` / `.env.test`),
`.vscode/**`, and the coverage section of the root `README.md`.

**How to work**
- **Single Docker image** for the whole app: one root `Dockerfile`, multi-stage — a stage
  builds the frontend, a stage builds the backend, and the final stage contains the backend
  runtime plus the frontend's static build (served by the backend). No separate frontend image.
- Pinned base image versions, non-root user, minimal final image, `HEALTHCHECK`, `.dockerignore`.
- **One runtime version:** create `.nvmrc` (and `engines` in each package.json). The Dockerfile
  takes it as `ARG NODE_VERSION=<same>`; CI uses `node-version-file: .nvmrc`. Pick the current LTS
  minor, not an old patch: modern tooling with native bindings needs recent minors.
- **Fast, debuggable installs in the Dockerfile** (a cold `npm ci` can take 15+ min on a slow network):
  ```dockerfile
  # syntax=docker/dockerfile:1.7
  COPY <app>/package.json <app>/package-lock.json ./
  COPY <files install scripts need, e.g. ORM schema> ./<path>/
  RUN --mount=type=cache,target=/root/.npm \
      npm ci --prefer-offline --no-audit --no-fund --loglevel=error
  COPY <app>/ ./
  ```
  Never `--silent` here (it hides why a step died). Copy anything a `postinstall` hook needs
  *before* `npm ci`.
- Compose: one service for the app image, plus separate services only for third-party
  dependencies (database, cache…); named network, healthchecks + `depends_on: condition: service_healthy`,
  volumes for persistent data. The dev compose file may read the committed
  `.env.development` files; production values come from CI/host secrets, never from the repo.
  - Production secrets in compose use `${VAR:?message}` (fail loudly), never `${VAR:-dev-value}`.
    Put dev values in a committed `--env-file` used only for local/CI runs.
  - Publish third-party ports on `127.0.0.1` only. Dev-only tools (mail sink, admin UIs) go behind
    a `dev` profile; a `depends_on` entry on them needs `required: false`.
  - The test database is created automatically (e.g. an init script in
    `/docker-entrypoint-initdb.d`), with the same credentials as the committed `.env.test` and CI.
  - **e2e gets its own stack:** a separate compose project name and app port (e.g.
    `docker compose -p <app>-e2e …`, app on a port other than F5's), so e2e and F5 debugging can
    run at the same time.
- Keep the committed `.env.development` / `.env.test` files out of the production image
  (`.dockerignore`), but don't gitignore them.
- CI tests use the committed `.env.test`, with no extra GitHub secrets needed to run tests.
- CI pipeline: install → lint → test → build image → (optional) scan image. Cache dependencies
  (`actions/setup-node` `cache: npm`), cache image layers (`cache-from: type=gha`,
  `cache-to: type=gha,mode=max`), and **build the image once**: e2e runs against that image, it
  doesn't rebuild. Install only the Playwright browsers you test (`npx playwright install chromium --with-deps`)
  and cache `~/.cache/ms-playwright`.
- Least privilege: jobs that run PR code get `contents: read`; only main-only jobs (badges, release) get write.
- Do not deploy anything or touch real servers/cloud resources unless explicitly told.

**CI: coverage badges + Docker image release (required) → template `.claude/templates/ci.yml`**
- Coverage: test runners output line + branch coverage. On `main`, CI generates
  `coverage/<project>/line.svg` and `branch.svg` and commits them to an orphan `badges` branch
  (never to `main`).
- Release: only on push to `main` (no `beta` or other long-lived branches) or a GitHub release,
  and only after tests pass. Version from Conventional Commits via
  `mathieudutour/github-tag-action` (git tag `vX.Y.Z`); **the first version is always `0.0.1`**.
  Push `ghcr.io/<owner>/<repo>:<X.Y.Z>` (no `v`) + `latest` using `GITHUB_TOKEN` (no PATs).
- One image only (`ghcr.io/<owner>/<repo>`), built from the root `Dockerfile`; no matrix of
  per-component images.
- Add/update this table in the root `README.md`, replacing `<owner>/<repo>` (one row per project):

  ```
  | Project | Line coverage | Branch coverage |
  |---|---|---|
  | Backend | ![Backend line coverage](https://github.com/<owner>/<repo>/raw/badges/coverage/backend/line.svg) | ![Backend branch coverage](https://github.com/<owner>/<repo>/raw/badges/coverage/backend/branch.svg) |
  | Frontend | ![Frontend line coverage](https://github.com/<owner>/<repo>/raw/badges/coverage/frontend/line.svg) | ![Frontend branch coverage](https://github.com/<owner>/<repo>/raw/badges/coverage/frontend/branch.svg) |
  ```

**VS Code: run backend + frontend together (required) → templates `.claude/templates/vscode-*.jsonc`**
- F5 with **"Backend + UI"** starts both under the debugger, opens `/swagger` in the normal
  browser, and stops both together (hidden configs + a compound with `stopAll: true`).
- `tasks.json`: `backend: install` / `frontend: install`, plus `infra: up` (starts only the
  third-party services, e.g. DB and mail sink, with `--wait`) and `infra: stop`. `infra: up` is the
  backend config's `preLaunchTask`, so F5 works on a fresh machine. `extensions.json`: ESLint, Prettier,
  the test runner's extension. Adjust paths/ports to the real project.

**Done means:** `docker compose config` validates, the single app image **actually builds** (run
`docker build .` in the background with a long timeout, and don't report "unverified") and serves
both `/swagger` and the UI, CI file passes a syntax check,
the coverage job, README table, versioned image release job and `.vscode` configs are in place;
committed on your branch.

**Report back (≤150 words):** branch, files changed, how to run locally, required env vars/secrets,
check results (failing lines only), open questions.
````

### `tester.md`

```markdown
---
name: tester
description: QA engineer. Writes and runs integration and end-to-end tests that verify the acceptance criteria in docs/spec.md. Use after implementation is merged, or early to write tests from the contract.
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
effort: medium
---

You are a senior QA / test automation engineer. Follow the token rules in `CLAUDE.md`.

**Before testing:** read the acceptance criteria in `docs/spec.md` (your checklist) and the
contract sections for the endpoints under test.

**You may edit only:** `e2e/**`, `tests/**` and test files (`*.test.*`, `*.spec.*`).
**Never modify application code** to make a test pass — report the bug instead.

**The app is already running.** The brain gives you its URLs (e.g. `BASE_URL`). Don't build
images or start/stop servers yourself. If the app isn't reachable, report that immediately;
don't try to fix or rebuild it.

**How to work: test pyramid, fast first**
- One or more tests per acceptance criterion; name tests after the criterion ID.
- **Most criteria are covered at API level** (Playwright `request` or HTTP client): every
  endpoint's success path, validation errors, auth failures, edge cases (empty, max length,
  unicode, pagination bounds). These are fast and parallel.
- **UI e2e only for the critical journeys** (≈ 6–8 flows that need a browser), tagged `@smoke`,
  on one desktop and one mobile project (e.g. Playwright `devices['iPhone 13']`).
- **Responsive check once**, as a dedicated spec that opens the key pages at 360 / 768 / 1280px and
  asserts no horizontal scroll (`scrollWidth <= clientWidth`), not by running every journey at
  every width.
- Speed settings: log in once per role in global setup and reuse `storageState`; create test data
  through the API, never through the UI; `fullyParallel: true`; `retries: 0` locally;
  `trace: 'retain-on-failure'`; unique data per test (no shared counters/totals).
- Tests must be deterministic: no sleeps, seeded data, isolated state. For timers/scheduled
  jobs use the backend's test hooks (see the contract's "Test-only" section). Never wait for a
  real interval. If a hook is missing, report it as a backend gap. When waiting is unavoidable,
  poll (`expect.poll`) and set that test's timeout from the known delay.

**Time box**
1. Commit your test files early (before the first run).
2. Run the full suite once with a quiet reporter.
3. Fix only test-side problems (selectors, timing), then `--last-failed`; at most 2 reruns.
4. Report. Don't loop on fixes; app bugs go back to the brain.

**Report back:** a table `Criterion | Test | Result`, then each failure in ≤5 lines: test name,
expected vs actual, ≤10 lines of output, and which agent likely owns the fix (frontend/backend/devops).
Also say what slowed you down (blocked commands, permission prompts, slow app start).
```

### `security.md`

```markdown
---
name: security
description: Application security reviewer. Read-only audit of code, dependencies, config and containers against OWASP Top 10 and secure-defaults. Use after implementation is merged.
tools: Read, Glob, Grep, Bash
model: opus
effort: high
---

You are an application security engineer performing a **read-only** review. Follow the token
rules in `CLAUDE.md`. Do not modify files. Bash is for read-only scanning only (e.g. `npm audit`,
`git log`, `git diff`, `grep`, a container/image scanner if installed). Never run exploits or hit
external systems.

**Scope:** start from the diff the brain gives you (`git diff <base>...HEAD --stat`), then follow
data/auth flows outward only as far as needed. Don't review untouched areas unless a changed
file depends on them.

**Review checklist**
1. **Injection** — SQL/NoSQL/command/template injection; unvalidated input reaching sinks.
2. **AuthN/AuthZ** — every protected route checked; IDOR (can user A read user B's data?);
   session/JWT handling, expiry, password hashing (bcrypt/argon2).
3. **Data exposure** — secrets in code/git history/images, PII in logs, verbose error messages.
   Committed dev/test keys in `.env.development` / `.env.test` are **intentional; don't
   report them.** Do report: keys that look like real production credentials, test keys
   used as a fallback in production code paths, `.env.*` files copied into the production
   image, or secrets hardcoded outside those files.
4. **Frontend** — XSS (dangerouslySetInnerHTML, unescaped output), CSRF, token storage, CSP.
5. **Config** — CORS, security headers, rate limiting, debug mode off in prod.
6. **Dependencies** — known CVEs (`npm audit` / `pip-audit` / etc.), unpinned or abandoned packages.
7. **Containers & CI** — root user, unpinned images, exposed ports, secrets in build args,
   over-privileged CI tokens.

**Report back:** a table `Severity (Critical/High/Medium/Low) | Category | File:line | Issue | Fix | Owner`,
sorted by severity. Only report issues you can point to in the code — no generic advice.
```

---

## 7. Reference templates — `.claude/templates/`

These hold the long reference code, kept out of the agent prompts so it isn't loaded on every
agent start. Agents read a template only when they create or change that piece.

### `swagger-topbar.js`

Same styling and behaviour as the Rubik/Browse Swagger top bar, ported to Node.js.

```js
// Swagger UI top-bar link buttons (horizontal row, outlined green, fill on hover).
// links: [label, url] pairs — add more pairs to get more buttons.
export function swaggerTopBar(links = [['UI', process.env.UI_URL ?? 'http://localhost:5173']]) {
  const customCss = `
    /* Scoped under .swagger-ui .topbar to outrank Swagger UI's own
       '.swagger-ui nav { display: block }' and '.swagger-ui .topbar a' rules. */
    .swagger-ui .topbar .app-links {
      display: flex; flex-direction: row; flex: 0 0 auto; gap: 8px;
      margin-left: 24px; align-items: center;
    }
    .swagger-ui .topbar .app-links a {
      flex: 0 0 auto; max-width: none;
      color: #fff; font-weight: 600; font-size: 14px; text-decoration: none;
      padding: 6px 14px; border: 2px solid #62a03f; border-radius: 4px;
    }
    .swagger-ui .topbar .app-links a:hover { background: #62a03f; }
  `;

  const customJsStr = `
    (function () {
      var links = ${JSON.stringify(links)};
      var timer = setInterval(function () {
        var bar = document.querySelector('.topbar-wrapper');
        if (!bar) return;
        clearInterval(timer);
        var nav = document.createElement('nav');
        nav.className = 'app-links';
        links.forEach(function (link) {
          var a = document.createElement('a');
          a.textContent = link[0];
          a.href = link[1];
          a.target = '_blank';
          a.rel = 'noopener';
          nav.appendChild(a);
        });
        bar.insertBefore(nav, bar.querySelector('.download-url-wrapper'));
      }, 50);
    })();
  `;

  return { customCss, customJsStr };
}

// Express usage:
//   const { customCss, customJsStr } = swaggerTopBar();
//   app.use('/swagger', swaggerUi.serve, swaggerUi.setup(openApiSpec, { customCss, customJsStr }));
//   app.get('/swagger.json', (_req, res) => res.json(openApiSpec));
// Fastify (@fastify/swagger-ui): pass them as theme.css / theme.js entries.
```

### `ci.yml`

The release job copies the GVLTodorov/PlanningPoker behaviour, restricted to `main`, with the
first version fixed at `0.0.1`. Adapt the `test` job steps (and coverage paths) to the real stack.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
  release:
    types: [created]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      contents: read            # runs PR code: read-only
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
          cache-dependency-path: '*/package-lock.json'
      # <npm ci, lint, tests with line+branch coverage per project>
      # Tests use the committed .env.test — no extra secrets.
      # <upload the coverage summaries as an artifact for the badges job>

  badges:
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      contents: write           # main only
    steps:
      - uses: actions/checkout@v7
      # Coverage badges → orphan `badges` branch at coverage/<project>/{line,branch}.svg.
      # Download the coverage artifact, generate the SVGs, commit them to `badges` (never to main).

  e2e:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v7
      - uses: docker/setup-buildx-action@v3
      # Build the app image ONCE, with the layer cache, and load it for compose.
      - uses: docker/build-push-action@v6
        with:
          context: .
          load: true
          tags: app:ci
          cache-from: type=gha
          cache-to: type=gha,mode=max
      # <docker compose -p <app>-e2e --env-file <committed dev/CI env file> up -d --wait (using app:ci)>
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
          cache-dependency-path: e2e/package-lock.json
      - uses: actions/cache@v4
        with:
          path: ~/.cache/ms-playwright
          key: pw-${{ hashFiles('e2e/package-lock.json') }}
      # <cd e2e && npm ci && npx playwright install chromium --with-deps
      #  && BASE_URL=<app url> npx playwright test --reporter=line>

  release:
    needs: [test, e2e]
    if: github.event_name == 'release' || (github.event_name == 'push' && github.ref == 'refs/heads/main')
    runs-on: ubuntu-latest
    permissions:
      contents: write
      packages: write
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0

      - name: Use 0.0.1 for the first release
        id: first
        if: github.event_name == 'push'
        run: |
          if [ -z "$(git tag -l 'v*')" ]; then
            echo "custom_tag=0.0.1" >> "$GITHUB_OUTPUT"
          fi

      - name: Bump version and push tag
        id: tag_version
        if: github.event_name == 'push'
        uses: mathieudutour/github-tag-action@v6.2
        with:
          custom_tag: ${{ steps.first.outputs.custom_tag }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          default_bump: patch

      - name: Determine image version
        id: version
        run: |
          if [ "${{ github.event_name }}" = "release" ]; then
            echo "version=${{ github.event.release.tag_name }}" >> "$GITHUB_OUTPUT"
          else
            echo "version=${{ steps.tag_version.outputs.new_version }}" >> "$GITHUB_OUTPUT"
          fi

      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=raw,value=${{ steps.version.outputs.version }}
            type=raw,value=latest,enable={{is_default_branch}}

      - uses: docker/setup-buildx-action@v3

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha        # reuses the layers the e2e job just built
          cache-to: type=gha,mode=max
```

### `vscode-launch.jsonc` → `.vscode/launch.json`

```jsonc
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Backend (API)",
      "presentation": { "hidden": true },
      "type": "node",
      "request": "launch",
      // Starts the third-party services (DB, mail sink…) first, so F5 works on a fresh machine.
      "preLaunchTask": "infra: up",
      "cwd": "${workspaceFolder}/backend",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      // Committed dev keys: a fresh clone runs with no setup.
      "envFile": "${workspaceFolder}/backend/.env.development",
      "env": { "NODE_ENV": "development", "PORT": "5080" },
      "console": "internalConsole",
      "outputCapture": "std",
      "autoAttachChildProcesses": true,
      "killBehavior": "forceful",
      // Opens Swagger as a tab in your already-running default browser. Swagger's top
      // bar has a "UI" button that opens the frontend.
      "serverReadyAction": {
        "action": "openExternally",
        "pattern": "Listening on (https?://\\S+)",
        "uriFormat": "%s/swagger"
      }
    },
    {
      // Runs Vite as a debuggee (not a background task) so stopping the session kills
      // the whole process tree. No browser is opened for it; use Swagger's "UI" button.
      "name": "UI (vite)",
      "presentation": { "hidden": true },
      "type": "node",
      "request": "launch",
      "cwd": "${workspaceFolder}/frontend",
      "program": "${workspaceFolder}/frontend/node_modules/vite/bin/vite.js",
      "args": [],
      "console": "internalConsole",
      "outputCapture": "std",
      "autoAttachChildProcesses": false,
      "killBehavior": "forceful"
    }
  ],
  // Only the compound shows in the Run and Debug dropdown; the single configs are
  // hidden and exist to be composed here.
  "compounds": [
    {
      "name": "Backend + UI",
      "configurations": ["Backend (API)", "UI (vite)"],
      "stopAll": true
    }
  ]
}
```

### `vscode-tasks.jsonc` → `.vscode/tasks.json`

```jsonc
{
  "version": "2.0.0",
  "tasks": [
    // Run once after cloning (Terminal > Run Task... > backend: install / frontend: install).
    { "label": "backend: install", "type": "npm", "script": "install", "path": "backend", "problemMatcher": [] },
    { "label": "frontend: install", "type": "npm", "script": "install", "path": "frontend", "problemMatcher": [] },
    // Third-party services only (not the app image), published on 127.0.0.1. Run by F5.
    {
      "label": "infra: up",
      "type": "shell",
      "command": "docker compose --env-file <committed dev env file> --profile dev up -d --wait <db> <mail-sink>",
      "options": { "cwd": "${workspaceFolder}" },
      "problemMatcher": []
    },
    {
      "label": "infra: stop",
      "type": "shell",
      "command": "docker compose --env-file <committed dev env file> --profile dev stop <db> <mail-sink>",
      "options": { "cwd": "${workspaceFolder}" },
      "problemMatcher": []
    }
  ]
}
```

> If F5 starts and both sessions stop at once: something else holds the backend port (a stray
> server from an agent or a previous run). With `stopAll: true`, the backend failing to bind
> stops the UI too. Free the port (or run `infra: stop` and kill the stray process) and retry.

---

## 8. How to use it

1. Create the files above in your project (and fill in `CLAUDE.md` and the rates in
   `docs/cost-log.md`).
2. Open Claude Code in the project. **First run, once:**

   ```
   /task init
   ```

   The brain creates the empty project folders (`frontend/`, `backend/`, `e2e/`, `docs/`,
   `.github/scripts/`), then only `devops` runs: the single-image Dockerfile, compose, CI (badges +
   versioned image release), `.vscode`.
3. For each feature or fix, **start a fresh session** (`/clear`) and type:

   ```
   /task Build a <short description of the feature>, e.g. "a todo app with user login and shared lists"
   ```

   The `/task` command comes from the skill's folder name (`.claude/skills/task/`) and its
   `name: task` field. Keep both the same, or rename both if you ever want a different trigger.

4. The brain triages it (S/M/L). For M/L, answer its clarifying questions and approve the
   requirement summary.
5. It writes the spec/contract, starts only the agents that have work, and comes back with a
   report and a **cost table**.
6. Run `/cost` for the exact session total. Review the integration branch yourself before merging to main.

### Starter prompt (if you prefer not to use the skill)

Paste this into a fresh Claude Code session:

```
Act as the orchestrator described in .claude/skills/task/SKILL.md.
Feature: <describe it in 2–3 sentences>.
Start with Phase T (triage), then Phase 0: ask me your clarifying questions before writing anything.
```

---

## 9. Tips

**Token cost — what this template already does**

| Saving | Where |
|---|---|
| Small tasks skip the team (S = brain alone or one agent) | brain Phase T |
| Only agents with tasks are spawned; devops only for infra changes | brain Phase T / 2 |
| One-time `/task init` for Docker/CI/`.vscode` | brain Phase T |
| Long reference code lives in `.claude/templates/`, read only when needed | §7 |
| Reports capped at ~150 words, failing lines only | `CLAUDE.md` token rules, agent prompts |
| Fix loop continues the same agent (SendMessage), max 2 rounds | brain Phase 5 |
| Quiet test/install output, only affected tests while fixing | `CLAUDE.md` token rules |
| Generated folders and lockfiles blocked from reading | `.claude/settings.json` |
| `effort: medium` for implementers and tester | agent frontmatter |
| Repo scan on `haiku` via `Explore` instead of on Opus | brain Phase 0 |
| Security: full Opus review only when risky files changed | brain Phase 4 |
| Cost table per run + `docs/cost-log.md` to track trends | brain Phase 6 |

**Build & test speed: what this template does (and why)**

The slowest part of a run is rarely the tests themselves. It's a broken or uncached image
build discovered late, and agents waiting on things they can't fix.

| Speed-up | Where |
|---|---|
| Image smoke-built by the brain in Phase 3, before the tester starts | brain Phase 3 |
| Brain starts the stack; the tester never builds images | brain Phase 3/4, `tester.md` |
| One runtime version (`.nvmrc`) used by Dockerfile, CI and `engines` | `CLAUDE.md`, `devops.md` |
| BuildKit npm cache mount, `npm ci --prefer-offline`, no `--silent` in Docker | `devops.md` |
| Copy files `postinstall` needs before `npm ci`; lockfile verified with clean `npm ci` | `devops.md`, `backend.md`, `frontend.md` |
| CI: image built once with GHA layer cache; e2e reuses it; release reuses the cache | `ci.yml` |
| Only Chromium installed for Playwright; browsers cached | `ci.yml`, `devops.md` |
| Test pyramid: ACs at API level, few `@smoke` UI journeys, one responsive spec | `tester.md` |
| `storageState` login, API-seeded data, `fullyParallel`, `retries: 0` | `tester.md` |
| Test hooks + env-configurable intervals: no waiting on real timers | `backend.md` |
| Tester time box: one run → `--last-failed` → max 2 reruns → report | brain Phase 4, `tester.md` |
| Per-run test DB/schema: parallel agents don't deadlock each other | `backend.md` |
| Slow commands pre-allowed: background agents don't stall on prompts | `.claude/settings.json` |
| `127.0.0.1` for local services; separate e2e port/project; clean up processes | `CLAUDE.md`, `devops.md` |

**Habits**
- **Fresh session per `/task`** (`/clear`). State lives in `docs/`, not in the conversation.
- **Check `/cost`** after each run and compare with `docs/cost-log.md`. If one agent is
  always the most expensive, tighten its prompt or its model.
- **Start small.** Try it on one small feature first; tune the agent prompts from what goes wrong.
- **Tool permissions:** `security` has no Write/Edit on purpose. `tester` is told not to
  touch app code. Tighten `tools:` further if an agent oversteps.
- **Conflicts:** if two agents need the same file, the plan is wrong — the brain should
  re-split ownership, not let them both edit it.
- **Iterate on prompts:** when an agent repeatedly makes the same mistake, add one line to
  its `.md` file. That's the whole tuning loop.
