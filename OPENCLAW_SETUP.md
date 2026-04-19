# OpenClaw Enterprise Setup Guide

> **OpenClaw** (formerly Molty/Molt.bot) — a self-hosted AI agent with full autonomy, multi-channel support, and extensible MCP/skills architecture. GitHub: [openclaw/openclaw](https://github.com/openclaw/openclaw) · 360k stars.

This guide configures OpenClaw for the Enterprise AI Workflow: Slack-driven task intake → multi-project context → auto branch/code → GitHub report.

---

## Table of Contents

1. [Installation](#1-installation)
2. [Core Configuration (`openclaw.json`)](#2-core-configuration-openclawjson)
3. [Workspace Bootstrap Files](#3-workspace-bootstrap-files)
4. [Skills Setup](#4-skills-setup)
5. [MCP Servers (GitHub, Notion, Jira)](#5-mcp-servers-github-notion-jira)
6. [Slack App Setup](#6-slack-app-setup)
7. [Proxy API Integration](#7-proxy-api-integration)
8. [Multi-Project `.agent/` Folder](#8-multi-project-agent-folder)
9. [Full Workflow Walkthrough](#9-full-workflow-walkthrough)
10. [Daily Maintenance](#10-daily-maintenance)

---

## 1. Installation

### Prerequisites

```bash
# Node.js 20+ required
node --version   # v20.x or higher

# Install OpenClaw globally
npm install -g openclaw

# Verify
openclaw --version
```

### First-time setup wizard

```bash
openclaw
# → Select: Local
# → Choose workspace folder: ~/.openclaw/workspace
# → Pick model: (skip for now, we configure via proxy below)
```

---

## 2. Core Configuration (`openclaw.json`)

Save to `~/.openclaw/openclaw.json`:

```json5
{
  // ─── Identity ───────────────────────────────────────────────────────────────
  identity: {
    name: "Clawd",
    theme: "senior Angular developer and DevOps engineer working for Blogic Systems",
    emoji: "🦞",
  },

  // ─── Environment Variables ──────────────────────────────────────────────────
  env: {
    GITHUB_TOKEN: "${GITHUB_TOKEN}",
    NOTION_TOKEN: "${NOTION_TOKEN}",
    JIRA_TOKEN: "${JIRA_TOKEN}",
    JIRA_EMAIL: "${JIRA_EMAIL}",
    PROXY_API_KEY: "${PROXY_API_KEY}",
  },

  // ─── Model via Proxy API ─────────────────────────────────────────────────────
  // Connects to proxy-ai.zenkiet.dev (OpenAI-compatible endpoint)
  models: {
    mode: "merge",
    providers: {
      "zenkiet-proxy": {
        baseUrl: "https://proxy-ai.zenkiet.dev/v1",
        apiKey: "${PROXY_API_KEY}",
        api: "openai-responses",
        models: [
          {
            id: "claude-opus-4-5",
            name: "Claude Opus 4.5 (via ZenKiet Proxy)",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 32000,
          },
          {
            id: "claude-sonnet-4-5",
            name: "Claude Sonnet 4.5 (via ZenKiet Proxy)",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 32000,
          },
          {
            id: "gpt-4o",
            name: "GPT-4o (via ZenKiet Proxy)",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            maxTokens: 16384,
          },
        ],
      },
    },
  },

  // ─── Agent Configuration ─────────────────────────────────────────────────────
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
      model: {
        primary: "zenkiet-proxy/claude-opus-4-5",
        fallbacks: ["zenkiet-proxy/claude-sonnet-4-5", "zenkiet-proxy/gpt-4o"],
      },
      thinkingDefault: "high",
      verboseDefault: "off",
      elevatedDefault: "on",        // Full autonomy: allow exec, file ops, git
      timeoutSeconds: 1800,          // 30 min for complex tasks
      contextInjection: "always",
    },
    list: [
      {
        id: "main",
        default: true,
        thinkingDefault: "high",
      },
    ],
  },

  // ─── Tools (Full Autonomy) ───────────────────────────────────────────────────
  tools: {
    allow: ["exec", "process", "read", "write", "edit", "apply_patch", "browser"],
    exec: {
      backgroundMs: 30000,
      timeoutSec: 1800,
    },
    elevated: {
      enabled: true,
      allowFrom: {
        slack: ["${SLACK_OWNER_USER_ID}"],  // Your Slack User ID (U...)
      },
    },
  },

  // ─── Slack Channel ───────────────────────────────────────────────────────────
  channels: {
    slack: {
      enabled: true,
      mode: "socket",                        // Socket Mode (no public URL needed)
      appToken: "${SLACK_APP_TOKEN}",        // xapp-...
      botToken: "${SLACK_BOT_TOKEN}",        // xoxb-...

      // DM: allow owner to DM the bot directly
      dm: {
        enabled: true,
        dmPolicy: "allowlist",
        allowFrom: ["${SLACK_OWNER_USER_ID}"],
      },

      // Channel access
      groupPolicy: "allowlist",
      channels: {
        // Main AI task channel
        "#ai-tasks": {
          allow: true,
          requireMention: false,             // No need to @mention in this channel
          users: ["${SLACK_OWNER_USER_ID}"], // Only owner can trigger
        },
        // DevOps channel
        "#devops": {
          allow: true,
          requireMention: true,
          users: ["${SLACK_OWNER_USER_ID}"],
        },
      },

      // Threading: reply in thread to keep channel clean
      replyToMode: "thread",

      // Native slash commands
      commands: {
        native: true,
        ownerAllowFrom: ["slack:${SLACK_OWNER_USER_ID}"],
      },

      // Exec approvals: owner approves dangerous commands via Slack
      execApprovals: {
        enabled: true,
        approvers: ["${SLACK_OWNER_USER_ID}"],
        target: "origin",                    // Reply in same thread
      },
    },
  },

  // ─── MCP Servers ─────────────────────────────────────────────────────────────
  // Note: OpenClaw uses skills for MCP integration.
  // MCP servers are configured via skills.load.extraDirs or workspace skills.
  // See Section 5 for MCP server setup.

  // ─── Skills ──────────────────────────────────────────────────────────────────
  skills: {
    load: {
      extraDirs: [
        "~/.openclaw/workspace/skills",
        "~/.openclaw/workspace/.agents/skills",
      ],
      watch: true,
    },
    install: {
      nodeManager: "npm",
    },
  },

  // ─── Session ─────────────────────────────────────────────────────────────────
  session: {
    scope: "per-sender",
    dmScope: "per-channel-peer",
    reset: {
      mode: "daily",
      atHour: 4,
      idleMinutes: 120,
    },
    resetTriggers: ["/new", "/reset"],
  },

  // ─── Logging ─────────────────────────────────────────────────────────────────
  logging: {
    level: "info",
    file: "~/.openclaw/logs/openclaw.log",
    consoleLevel: "info",
    consoleStyle: "pretty",
  },

  // ─── Gateway ─────────────────────────────────────────────────────────────────
  gateway: {
    mode: "local",
    port: 18789,
    bind: "loopback",
    controlUi: {
      enabled: true,
      basePath: "/openclaw",
    },
  },

  // ─── Routing ─────────────────────────────────────────────────────────────────
  routing: {
    queue: {
      mode: "collect",
      debounceMs: 1500,
      cap: 10,
    },
  },

  // ─── Messages ────────────────────────────────────────────────────────────────
  messages: {
    ackReaction: "👀",
    ackReactionScope: "all",
  },
}
```

### Environment variables file

Create `~/.openclaw/.env` (never commit this file):

```bash
# Model Proxy
PROXY_API_KEY=your-proxy-api-key-here

# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# Notion
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxxxxxx

# Jira / Atlassian
JIRA_TOKEN=your-atlassian-api-token
JIRA_EMAIL=kiet@blogicsystems.com

# Slack
SLACK_APP_TOKEN=xapp-1-xxxxxxxxxxxx
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxx
SLACK_OWNER_USER_ID=U0XXXXXXXXX   # Your Slack User ID
```

Load env on startup by adding to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export $(grep -v '^#' ~/.openclaw/.env | xargs)
```

---

## 3. Workspace Bootstrap Files

These files live in `~/.openclaw/workspace/` and are loaded at the start of every session.

### `AGENTS.md` — Operating Instructions

```markdown
---
# Operating Instructions for Clawd (Enterprise AI Agent)
---

## Identity
You are Clawd, the AI development assistant for Blogic Systems.
You work with Kiet Le (Frontend Angular Leader & DevOps).

## Core Responsibilities
1. Read task requirements from Notion/Jira links
2. Ask clarifying questions (UI changes? Business logic?)
3. Create a detailed plan.md and wait for approval
4. After approval: create branch, scaffold code, commit, push to GitHub
5. Report completion with branch name and summary

## Multi-Project Awareness
When given a task, ALWAYS:
1. Identify which project it belongs to
2. Read `.agent/ARCHITECTURE.md`, `.agent/RULES.md`, `.agent/SKILL.md` from that project
3. Store project context in memory for the session
4. Apply project-specific patterns strictly

## Task Workflow (MANDATORY)
```
STEP 1: Read requirement (Notion/Jira URL or description)
STEP 2: Ask clarifying questions:
  - "Does this task involve UI changes?"
  - "Does this task involve business logic/API integration?"
  - "Which project is this for? (if not specified)"
STEP 3: Generate plan.md and send to Slack for approval
STEP 4: Wait for "approved" or "lgtm" or "ok go" from Kiet
STEP 5: Execute plan (create branch, scaffold, commit, push)
STEP 6: Report to Slack: branch name, files changed, summary
```

## Code Quality Rules (Non-negotiable)
- Smart/Dumb component separation (ALWAYS)
- Declarative over imperative (ALWAYS)
- No unnecessary files (ALWAYS check shared/ first)
- Clean, minimal code — no boilerplate bloat
- OnPush change detection for all Dumb components
- Reactive patterns with RxJS (no manual subscriptions without takeUntilDestroyed)

## Git Conventions
- Branch format: `feature/[task-id]-[short-description]`
- Commit format: `feat(scope): description`
- Never push to main directly
- Always create PR after pushing branch

## Communication Style
- Be concise in Slack messages
- Use bullet points for plans
- Use code blocks for file paths and commands
- Always confirm before executing destructive operations
```

### `SOUL.md` — Persona

```markdown
# Clawd — Soul

## Personality
- Professional, direct, efficient
- Senior-level Angular developer mindset
- DevOps-aware (Docker, CI/CD, Jenkins)
- Proactive: anticipates issues before they arise
- Asks questions before acting, never assumes

## Communication
- Vietnamese or English (match Kiet's language)
- Concise Slack messages — no fluff
- Technical precision: exact file paths, exact commands
- Emoji: minimal, only 🦞 for identity

## Values
- Code quality > speed
- Reuse > create new
- Ask > assume
- Minimal > complex
```

### `USER.md` — User Profile

```markdown
# User: Kiet Le

## Role
- Frontend Angular Leader at Blogic Systems
- DevOps Engineer (Docker, Jenkins, CI/CD)
- GitHub: zenkiet / blogic-kietle

## Technical Stack
- Angular (latest), TypeScript, RxJS, TailwindCSS
- Docker, Jenkins, GitHub Actions
- Jira: blogicsystems.atlassian.net
- Notion: workspace for requirements

## Preferences
- Smart/Dumb component pattern (strict)
- Declarative code style
- Minimal, clean code — no bloat
- Shared utilities in shared/ folder
- Always check existing shared components before creating new

## Approval Keywords
- "approved", "lgtm", "ok go", "go ahead", "làm đi", "ok"

## Projects (5 total)
- All on GitHub under zenkiet or blogic-kietle org
- Each has `.agent/` folder with project-specific context
- AI must read `.agent/` before starting any task
```

### `IDENTITY.md` — Agent Identity

```markdown
# Identity: Clawd

Name: Clawd
Emoji: 🦞
Vibe: Senior Angular developer + DevOps engineer
Workspace: Blogic Systems Enterprise AI Agent
Version: 1.0.0
```

### `TOOLS.md` — Available Tools

```markdown
# Tools & Conventions

## Git Operations
- Use `git` CLI for all operations
- Branch creation: `git checkout -b feature/[task-id]-[description]`
- Commit: `git commit -m "feat(scope): description"`
- Push: `git push origin [branch-name]`

## GitHub Operations
- Use `gh` CLI for PR creation
- PR title: same as commit message
- PR body: include plan.md content

## MCP Servers Available
- **GitHub MCP**: create branches, commits, PRs via API
- **Notion MCP**: read pages and databases
- **Jira MCP** (mcp-atlassian): read issues, update status
  - Domain: blogicsystems.atlassian.net
  - Command: `uvx mcp-atlassian`

## Project Detection
When a task is given:
1. Check if project path is mentioned
2. If not, ask: "Which project is this for?"
3. cd into project directory
4. Read `.agent/ARCHITECTURE.md`, `.agent/RULES.md`, `.agent/SKILL.md`
5. Apply rules for the entire session

## Angular CLI
- Generate component: `ng g c [name] --standalone`
- Generate service: `ng g s [name]`
- Generate module: `ng g m [name]`
- Always use `--dry-run` first to preview
```

---

## 4. Skills Setup

Skills live in `~/.openclaw/workspace/skills/`. Each skill is a folder with a `SKILL.md` file.

### Skill: `task-intake`

```bash
mkdir -p ~/.openclaw/workspace/skills/task-intake
```

Create `~/.openclaw/workspace/skills/task-intake/SKILL.md`:

```markdown
---
name: task_intake
description: Handle incoming tasks from Slack — read Notion/Jira, ask questions, generate plan
---

# Task Intake Skill

## Trigger
Activate when a message contains:
- A Notion URL (notion.so/...)
- A Jira URL (blogicsystems.atlassian.net/...)
- A task description starting with "task:", "feature:", "fix:", "devops:"

## Workflow

### Step 1: Read Requirement
- If Notion URL: use Notion MCP to fetch page content
- If Jira URL: use mcp-atlassian to fetch issue details
- If plain text: use as-is

### Step 2: Ask Clarifying Questions
Send these questions in ONE Slack message:
```
📋 *Task received!* Let me ask a few questions:

1. Does this task involve **UI changes**? (new components, layout changes)
2. Does this task involve **business logic** or API integration?
3. Which project is this for? (if not already clear)
4. Any specific constraints or deadlines?
```

### Step 3: Generate Plan
After receiving answers, create a `plan.md` with this structure:

```markdown
# Plan: [Task Title]

## Overview
[2-3 sentence summary]

## Scope
- [ ] UI Changes: Yes/No
- [ ] Business Logic: Yes/No
- [ ] Project: [project-name]
- [ ] Branch: feature/[task-id]-[description]

## Files to Create
- `src/app/features/[feature]/[name].component.ts` (Smart)
- `src/app/features/[feature]/[name]-ui/[name]-ui.component.ts` (Dumb)
- `src/app/shared/[shared-util].ts` (if needed)

## Files to Modify
- `src/app/[existing-file].ts` — [what changes]

## Shared Components Check
- Checked: `src/app/shared/` — [found/not found: list]

## Estimated Effort
[S/M/L — Small/Medium/Large]
```

Send plan to Slack and wait for approval.

### Step 4: Execute After Approval
Only proceed when Kiet responds with an approval keyword.
```

### Skill: `angular-scaffold`

```bash
mkdir -p ~/.openclaw/workspace/skills/angular-scaffold
```

Create `~/.openclaw/workspace/skills/angular-scaffold/SKILL.md`:

```markdown
---
name: angular_scaffold
description: Scaffold Angular components following Smart/Dumb pattern, declarative style, minimal code
---

# Angular Scaffold Skill

## Rules (Non-negotiable)
1. ALWAYS separate Smart (container) and Dumb (presentational) components
2. ALWAYS check `src/app/shared/` before creating new utilities
3. NEVER create unnecessary files
4. ALWAYS use OnPush change detection for Dumb components
5. ALWAYS use declarative patterns (async pipe, signals, computed)
6. ALWAYS use `takeUntilDestroyed()` for subscriptions

## Smart Component Template
```typescript
// [name].component.ts
import { Component, inject, OnInit } from '@angular/core';
import { CommonModule, AsyncPipe } from '@angular/common';
import { Observable } from 'rxjs';
import { [Name]Service } from './[name].service';
import { [Name]UiComponent } from './[name]-ui/[name]-ui.component';

@Component({
  selector: 'app-[name]',
  standalone: true,
  imports: [CommonModule, AsyncPipe, [Name]UiComponent],
  template: `
    <app-[name]-ui
      [data]="data$ | async"
      (action)="onAction($event)">
    </app-[name]-ui>
  `,
})
export class [Name]Component {
  private readonly service = inject([Name]Service);
  readonly data$ = this.service.getData();

  onAction(event: unknown): void {
    this.service.handleAction(event);
  }
}
```

## Dumb Component Template
```typescript
// [name]-ui.component.ts
import { Component, input, output, ChangeDetectionStrategy } from '@angular/core';

@Component({
  selector: 'app-[name]-ui',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<!-- Pure presentational template -->`,
})
export class [Name]UiComponent {
  readonly data = input<[Type] | null>(null);
  readonly action = output<[EventType]>();
}
```

## Shared Check Procedure
Before creating any utility/pipe/directive:
1. `find src/app/shared -name "*.ts" | xargs grep -l "[keyword]"`
2. If found: import and reuse
3. If not found: create in `src/app/shared/[category]/`
```

### Skill: `git-workflow`

```bash
mkdir -p ~/.openclaw/workspace/skills/git-workflow
```

Create `~/.openclaw/workspace/skills/git-workflow/SKILL.md`:

```markdown
---
name: git_workflow
description: Manage git operations for task branches — create, commit, push, report
---

# Git Workflow Skill

## Branch Creation
```bash
# Always from latest main/develop
git checkout main && git pull origin main
git checkout -b feature/[task-id]-[kebab-description]
```

## Commit Convention
```bash
# Format: type(scope): description
git commit -m "feat(user-profile): add smart/dumb component scaffold"
git commit -m "fix(auth): resolve token refresh race condition"
git commit -m "refactor(shared): extract reusable form validators"
git commit -m "chore(devops): update Dockerfile base image"
```

## Push and Report
```bash
git push origin [branch-name]
```

After push, send Slack report:
```
✅ *Task Complete!*

📌 Branch: `feature/[task-id]-[description]`
📁 Files created:
  - `src/app/features/[feature]/[name].component.ts`
  - `src/app/features/[feature]/[name]-ui/[name]-ui.component.ts`

📝 Summary: [2-3 sentence description of what was done]

🔗 Next: Review the branch and implement business logic
```

## PR Creation (optional, if requested)
```bash
gh pr create \
  --title "feat([scope]): [description]" \
  --body "$(cat plan.md)" \
  --base main \
  --head feature/[task-id]-[description]
```
```

### Skill: `devops-tasks`

```bash
mkdir -p ~/.openclaw/workspace/skills/devops-tasks
```

Create `~/.openclaw/workspace/skills/devops-tasks/SKILL.md`:

```markdown
---
name: devops_tasks
description: Handle DevOps tasks — Docker, Jenkins, CI/CD, infrastructure
---

# DevOps Tasks Skill

## Trigger
Activate when task contains: "docker", "jenkins", "ci/cd", "deploy", "infra", "devops"

## Workflow
Same as task-intake but adapted for DevOps:
1. Read requirement
2. Ask: "Is this a config change, new pipeline, or infrastructure update?"
3. Generate plan
4. Wait for approval
5. Execute
6. Report to Slack

## Common DevOps Patterns

### Dockerfile update
```bash
# Always use multi-stage builds
# Always pin base image versions
# Always minimize layers
```

### Jenkins pipeline
```groovy
// Jenkinsfile template
pipeline {
  agent any
  stages {
    stage('Build') { ... }
    stage('Test') { ... }
    stage('Deploy') { ... }
  }
}
```

## Report Format
```
✅ *DevOps Task Complete!*

🔧 Type: [Docker/Jenkins/CI-CD]
📌 Branch: `chore/devops-[description]`
📝 Changes: [summary]
```
```

---

## 5. MCP Servers (GitHub, Notion, Jira)

OpenClaw integrates MCP servers via the `exec` tool or as skill subprocess calls. Configure them in `TOOLS.md` and invoke via skills.

### GitHub MCP

Uses the official `@modelcontextprotocol/server-github`:

```bash
# Install globally
npm install -g @modelcontextprotocol/server-github

# Test
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx npx @modelcontextprotocol/server-github
```

Add to `~/.openclaw/workspace/TOOLS.md`:

```markdown
## GitHub MCP Server
- Command: `npx @modelcontextprotocol/server-github`
- Env: `GITHUB_PERSONAL_ACCESS_TOKEN`
- Capabilities: create_branch, create_commit, create_pull_request, get_file_contents, list_branches
```

### Notion MCP

Uses the official `@notionhq/notion-mcp-server`:

```bash
# Install globally
npm install -g @notionhq/notion-mcp-server

# Test
OPENAPI_MCP_HEADERS='{"Authorization":"Bearer secret_xxx","Notion-Version":"2022-06-28"}' \
  npx @notionhq/notion-mcp-server
```

Add to `TOOLS.md`:

```markdown
## Notion MCP Server
- Command: `npx @notionhq/notion-mcp-server`
- Env: `OPENAPI_MCP_HEADERS` (JSON with Authorization and Notion-Version)
- Capabilities: read pages, databases, blocks
```

### Jira MCP (mcp-atlassian)

Uses `mcp-atlassian` from [sooperset/mcp-atlassian](https://github.com/sooperset/mcp-atlassian):

```bash
# Install uv (Python package manager)
pip install uv

# Test
JIRA_URL=https://blogicsystems.atlassian.net \
JIRA_USERNAME=kiet@blogicsystems.com \
JIRA_API_TOKEN=your-atlassian-api-token \
  uvx mcp-atlassian
```

Add to `TOOLS.md`:

```markdown
## Jira MCP Server (mcp-atlassian)
- Command: `uvx mcp-atlassian`
- Env: `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`
- Jira URL: https://blogicsystems.atlassian.net
- Capabilities: get_issue, search_issues, update_issue, add_comment
```

### MCP Invocation in Skills

In any skill, instruct the agent to call MCP servers:

```markdown
## Reading a Notion Page
Use exec to call Notion MCP:
```bash
OPENAPI_MCP_HEADERS='{"Authorization":"Bearer ${NOTION_TOKEN}","Notion-Version":"2022-06-28"}' \
  npx @notionhq/notion-mcp-server --page-id [page-id]
```

## Reading a Jira Issue
```bash
JIRA_URL=https://blogicsystems.atlassian.net \
JIRA_USERNAME=${JIRA_EMAIL} \
JIRA_API_TOKEN=${JIRA_TOKEN} \
  uvx mcp-atlassian --issue-key [PROJ-123]
```
```

---

## 6. Slack App Setup

### Create Slack App

1. Go to [api.slack.com/apps/new](https://api.slack.com/apps/new)
2. Choose **From a manifest**
3. Paste this manifest:

```json
{
  "display_information": {
    "name": "Clawd",
    "description": "Enterprise AI Agent for Blogic Systems",
    "background_color": "#1a1a2e"
  },
  "features": {
    "bot_user": {
      "display_name": "Clawd",
      "always_online": true
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    }
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "app_mentions:read",
        "channels:history",
        "channels:read",
        "chat:write",
        "chat:write.customize",
        "commands",
        "emoji:read",
        "files:read",
        "files:write",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "reactions:read",
        "reactions:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "socket_mode_enabled": true,
    "event_subscriptions": {
      "bot_events": [
        "app_mention",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim"
      ]
    },
    "interactivity": {
      "is_enabled": true
    },
    "org_deploy_enabled": false,
    "token_rotation_enabled": false
  }
}
```

4. Click **Create App**
5. Go to **Basic Information** → **App-Level Tokens** → Generate token with `connections:write` scope → Copy `xapp-...`
6. Go to **Install App** → Install to workspace → Copy `xoxb-...`
7. Go to **Socket Mode** → Enable Socket Mode

### Get Your Slack User ID

In Slack: Click your profile → **View full profile** → **More** → **Copy member ID** (format: `U0XXXXXXXXX`)

---

## 7. Proxy API Integration

Your proxy at `https://proxy-ai.zenkiet.dev` is already configured in Section 2 under `models.providers["zenkiet-proxy"]`.

### Verify Connection

```bash
curl -X POST https://proxy-ai.zenkiet.dev/v1/chat/completions \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-opus-4-5",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

### If Proxy Uses Different Model IDs

Check available models:

```bash
curl https://proxy-ai.zenkiet.dev/v1/models \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

Then update `models.providers["zenkiet-proxy"].models[].id` in `openclaw.json` to match.

---

## 8. Multi-Project `.agent/` Folder

Each project repository should have a `.agent/` folder:

```
your-project/
├── .agent/
│   ├── ARCHITECTURE.md   # Project architecture, folder structure, patterns
│   ├── RULES.md          # Coding standards, naming conventions
│   └── SKILL.md          # Project-specific tools, commands, gotchas
├── src/
├── Jenkinsfile
└── package.json
```

### How OpenClaw Reads Project Context

Add this to `AGENTS.md` (already included in Section 3):

```markdown
## Multi-Project Context Loading
When working on a task for a specific project:
1. `cd` into the project directory
2. Read `.agent/ARCHITECTURE.md` → understand folder structure and patterns
3. Read `.agent/RULES.md` → apply coding standards
4. Read `.agent/SKILL.md` → know available tools and commands
5. Store this context for the entire session
6. Apply STRICTLY — no deviations without asking Kiet first
```

### Template Files

See the `.agent/` template files in this repository:
- `.agent/ARCHITECTURE.md` — copy and customize per project
- `.agent/RULES.md` — copy and customize per project
- `.agent/SKILL.md` — copy and customize per project

---

## 9. Full Workflow Walkthrough

### Example: Kiet sends a Jira link in `#ai-tasks`

```
Kiet: https://blogicsystems.atlassian.net/browse/FE-123
```

**Clawd responds:**

```
👀 (reaction — reading task...)

📋 Task received! Let me ask a few questions:

1. Does this task involve **UI changes**? (new components, layout changes)
2. Does this task involve **business logic** or API integration?
3. Which project is this for?
4. Any specific constraints?
```

**Kiet replies:**

```
1. Yes, new user profile page
2. Yes, needs to call /api/users/:id
3. frontend-dashboard project
4. No deadline
```

**Clawd generates plan:**

```
📝 Here's my plan for FE-123:

# Plan: User Profile Page

## Overview
Create a user profile page with Smart/Dumb component pattern,
fetching user data from /api/users/:id.

## Scope
- ✅ UI Changes: Yes (new page)
- ✅ Business Logic: Yes (API call)
- 📁 Project: frontend-dashboard
- 🌿 Branch: feature/FE-123-user-profile-page

## Files to Create
- `src/app/features/user-profile/user-profile.component.ts` (Smart)
- `src/app/features/user-profile/user-profile-ui/user-profile-ui.component.ts` (Dumb)
- `src/app/features/user-profile/user-profile.service.ts`
- `src/app/features/user-profile/user-profile.routes.ts`

## Files to Modify
- `src/app/app.routes.ts` — add /profile/:id route

## Shared Check
- ✅ Found: `src/app/shared/components/avatar/` — will reuse
- ✅ Found: `src/app/shared/pipes/date-format.pipe.ts` — will reuse
- ❌ Not found: user-card component — will create in shared/

Approve to proceed? Reply "approved" 🦞
```

**Kiet replies:** `approved`

**Clawd executes:**

```
🦞 Starting execution...

✅ Task Complete!

📌 Branch: `feature/FE-123-user-profile-page`
📁 Files created (6):
  - src/app/features/user-profile/user-profile.component.ts
  - src/app/features/user-profile/user-profile-ui/user-profile-ui.component.ts
  - src/app/features/user-profile/user-profile.service.ts
  - src/app/features/user-profile/user-profile.routes.ts
  - src/app/shared/components/user-card/user-card.component.ts
  - src/app/shared/components/user-card/user-card.component.html

📝 Summary:
- Smart component handles data fetching via UserProfileService
- Dumb component renders UI with OnPush detection
- Reused existing AvatarComponent and DateFormatPipe
- Created UserCardComponent in shared/ for reuse

🔗 Next: Pull branch and implement API endpoint + business logic
```

---

## 10. Daily Maintenance

### Start OpenClaw

```bash
# Load env vars
export $(grep -v '^#' ~/.openclaw/.env | xargs)

# Start gateway
openclaw gateway

# Or run in background
openclaw gateway &
```

### Useful Commands

```bash
# Check status
openclaw channels status --probe

# View logs
openclaw logs --follow

# Health check
openclaw doctor

# List loaded skills
openclaw skills list

# Restart gateway
openclaw gateway restart

# Open Control UI
open http://localhost:18789/openclaw
```

### Update AGENTS.md with Learnings

After each task, update `~/.openclaw/workspace/AGENTS.md` with:
- New patterns discovered
- Mistakes to avoid
- Project-specific gotchas
- Improved prompts

This is the "daily improvement" loop that makes the AI smarter over time.

### Weekly Review

Every week:
1. Review `~/.openclaw/logs/openclaw.log` for errors
2. Update `.agent/RULES.md` in each project with new patterns
3. Add new shared components to project `SKILL.md`
4. Refine `SOUL.md` and `AGENTS.md` based on feedback

---

## Quick Reference

| Action | Command/Location |
|--------|-----------------|
| Config file | `~/.openclaw/openclaw.json` |
| Workspace | `~/.openclaw/workspace/` |
| Skills | `~/.openclaw/workspace/skills/` |
| Logs | `~/.openclaw/logs/openclaw.log` |
| Start | `openclaw gateway` |
| Status | `openclaw channels status --probe` |
| Doctor | `openclaw doctor` |
| Control UI | `http://localhost:18789/openclaw` |
| Slack channel | `#ai-tasks` |
| Approval keywords | `approved`, `lgtm`, `ok go`, `làm đi` |

---

*Generated for Kiet Le — Blogic Systems Enterprise AI Workflow*
*OpenClaw version: 2026.4.x | Proxy: proxy-ai.zenkiet.dev*
