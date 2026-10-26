Set up the multi-agent team template in this empty project.

1. Download the template exactly (do not use a web-fetch/summarize tool):
   curl -fsSL https://raw.githubusercontent.com/GVLTodorov/GVLTodorov/main/tutorials/ai/template.md -o template-source.md
   Read template-source.md in full before creating anything.

2. Run `git init` if this isn't a git repo yet.

3. Create these files from the template's code blocks. Copy each block's content
   exactly: no outer fence (``` or ````), and no rewording, shortening or "improving".
   - CLAUDE.md ← section 3
   - .claude/skills/task/SKILL.md ← section 4 "SKILL.md"
   - .claude/skills/task/init.md ← section 4 "init.md"
   - .claude/skills/task/skeleton.md ← section 4 "skeleton.md"
   - .claude/skills/task/integration.md ← section 4 "integration.md"
   - .claude/skills/task/mobile.md ← section 4 "mobile.md"
   - .claude/skills/task/security.md ← section 4 "security.md"
   - .claude/skills/task/ship.md ← section 4 "ship.md"
   - .claude/settings.json ← section 5
   - .claude/agents/planner.md ← section 6 "planner.md"
   - .claude/agents/frontend.md ← section 6 "frontend.md"
   - .claude/agents/backend.md ← section 6 "backend.md"
   - .claude/agents/devops.md ← section 6 "devops.md"
   - .claude/agents/tester.md ← section 6 "tester.md"
   - .claude/agents/security.md ← section 6 "security.md"
   - .claude/templates/backend-setup.md ← section 7
   - .claude/templates/devops-setup.md ← section 7
   - .claude/templates/swagger-topbar.js ← section 7
   - .claude/templates/ci.yml ← section 7
   - .claude/templates/vscode-launch.jsonc ← section 7
   - .claude/templates/vscode-tasks.jsonc ← section 7
     Do NOT create .vscode/, .github/, docs/spec.md, docs/api-contract.md or any app code.
     devops creates those later from the templates.

4. Ask me in ONE question round, with a recommended default for each:
   project name, frontend framework, backend framework (Node.js), database, test tools.
   Then replace every <placeholder> in CLAUDE.md with my answers, including the Commands
   section. Leave the other files exactly as copied.

5. Delete template-source.md. Make the first commit:
   "chore: add multi-agent team template".

/task init

## Available commands

```
/task init                  // one-time project setup: folders, Docker, compose, CI, .vscode
/task <request>             // build or fix something: triage S/M/L → questions → plan → backend → frontend → devops → tests → merge
/task continue              // resume an interrupted run from the first unfinished stage in docs/tasks.md
/task integration [scope]   // build and run integration + e2e tests (all untested ACs, or the given pages/flows/AC IDs)
/task mobile [pages]        // responsive pass for phones/tablets + mobile e2e checks (all pages, or the named ones)
/task security [base]       // security review of everything since the last review (or since base)
```

