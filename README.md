# Claude knowledge

### 1. Update config file
````
  "model": "sonnet", // default is opus
  "env": {
    "MAX_THINKING_TOKENS": "10000", // default is 31,999
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50", // default is 95
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku" // default is inherit
  }
````

### 2. Building blocks of a Claude Code setup

Claude Code can be customized with several kinds of files. They differ in **when they are loaded**, **who triggers them**, and **whether they are guaranteed to run**.

| Building block | Location | Loaded / triggered | Purpose |
|---|---|---|---|
| `CLAUDE.md` (memory) | `./CLAUDE.md`, `~/.claude/CLAUDE.md`, `CLAUDE.local.md` | Always, at session start | Standing instructions: project overview, architecture, commands, global rules |
| Rules | `.claude/rules/**/*.md` | Always, or only for matching files (`paths:` frontmatter) | Split a large `CLAUDE.md` into focused topics (naming, git, per-layer rules) |
| Skills | `.claude/skills/<name>/SKILL.md` | On demand: Claude picks it by its description, or you type `/<name>` | Reusable workflows + reference material ("how to add a new screen", "release checklist") |
| Subagents | `.claude/agents/<name>.md` | When Claude delegates, or you ask for the agent by name | Specialized workers with their own context window, tools and model (reviewer, test writer, explorer) |
| Workflows | `.claude/workflows/<name>.js`, `~/.claude/workflows/` | You type `/<name>`, write `ultracode:` / "use a workflow", or turn on `/effort ultracode` | A JavaScript script that orchestrates dozens to hundreds of subagents in the background (audits, large migrations, fix-until-green loops) |
| Agent memory | `.claude/agent-memory/<agent>/MEMORY.md` | Loaded into a subagent's prompt when it starts (only if the agent sets `memory:`) | Notes a subagent keeps for itself between runs, like auto memory for the main session |
| Output styles | `.claude/output-styles/<name>.md`, `~/.claude/output-styles/` | Every response, once selected with `/output-style` or `outputStyle` | Change Claude's tone, length and response format (or its whole role) for the session |
| Slash commands (legacy) | `.claude/commands/<name>.md` | You type `/<name>` | Saved prompts. Skills replace these now; existing commands still work |
| Hooks | Scripts in `.claude/hooks/`, registered in `settings.json` | Automatically on events (`PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`, …) | Checks that **always** run: block dangerous commands, run formatters, scan for secrets |
| Settings | `.claude/settings.json` (shared), `.claude/settings.local.json` (personal, gitignored), `~/.claude/settings.json` (user) | At startup | Model, env vars, permissions (allow/deny tools), hook registration |
| MCP servers | `.mcp.json` | At startup; their tools are called by Claude | Connect external systems (GitHub, Jira, Figma, databases) as tools |
| Plugins | Installed via `/plugin` | At startup | Package skills + agents + hooks + MCP servers to share across projects and teams |

#### CLAUDE.md — project memory
- Plain Markdown that is added to the context of **every** session, so keep it short and high-signal: what the app is, the architecture, the build/test/lint commands, and rules that apply everywhere.
- Loaded from several levels and merged: user (`~/.claude/CLAUDE.md`) → project (`./CLAUDE.md`) → personal (`CLAUDE.local.md`, gitignored). A `CLAUDE.md` inside a subdirectory is read when Claude works on files in that directory.
- Other files can be pulled in with `@path/to/file.md` imports.
- In this repo: the root `CLAUDE.md` is the entry point and indexes the other rule files.

#### Rules — `.claude/rules/`
- Same idea as `CLAUDE.md`, split into focused files so each one stays readable.
- Add `paths:` frontmatter to load a rule only when Claude touches matching files, which keeps context small:
  ```markdown
  ---
  paths:
    - "domain/**/*.kt"
  ---
  # Domain rules
  - No android.* imports ...
  ```
- In this repo: `GUIDELINES.md` (principles), `naming.md`, `git.md`, and one file per layer (`app/`, `domain/`, `data/`).

#### Skills — `.claude/skills/`
- A folder with a `SKILL.md` (plus optional scripts, templates, reference docs). Frontmatter `name` + `description`.
- Only the **description** stays in context all the time. The full body loads when Claude decides the skill is relevant or when you type `/<skill-name>`. This means you can have many skills without filling the context.
- Use for repeatable procedures and knowledge you don't want in every session: "create a feature module", "add a Room migration", "write a ViewModel test".
  ```markdown
  ---
  name: new-feature-screen
  description: Scaffold a new Compose screen with ViewModel, UiState, UseCase and tests. Use when the user asks to add a new screen or feature.
  ---
  1. Create `<Feature>UiState` sealed interface (Loading/Success/Error) ...
  ```

#### Subagents — `.claude/agents/`
- A Markdown file with frontmatter (`name`, `description`, optional `tools`, `model`) and a system prompt in the body.
- Each subagent runs in its **own context window** and returns only a summary to the main conversation. Useful for:
  - **Keeping the main context clean** — large searches or log reading happen elsewhere.
  - **Specialization** — a focused prompt, e.g. "Kotlin code reviewer that checks Clean Architecture rules".
  - **Restricting tools** — a reviewer that can read but not edit.
  - **Cost/speed** — run simple jobs on a cheaper model (see `CLAUDE_CODE_SUBAGENT_MODEL` above).
  ```markdown
  ---
  name: android-reviewer
  description: Reviews Kotlin changes against the project's architecture and naming rules. Use after code changes.
  tools: Read, Grep, Glob, Bash
  model: sonnet
  ---
  You are a senior Android reviewer. Check the diff for ...
  ```
- Manage with `/agents`.

**Skill vs. subagent:** a skill adds *instructions* to the current conversation; a subagent is a *separate worker* with its own context. Skill = "how to do X", subagent = "who does X".

#### Agent memory — `.claude/agent-memory/`
- Lets a subagent **remember what it learned** between runs. Turn it on with the `memory:` field in the agent's frontmatter:
  ```markdown
  ---
  name: android-reviewer
  description: Reviews Kotlin changes against the project's architecture rules.
  memory: project
  ---
  ```
- The subagent writes and maintains its own `MEMORY.md`; you don't edit it. The first 200 lines (up to 25KB) are loaded into its prompt each time it starts. Example of what it might contain:
  ```markdown
  # android-reviewer memory
  ## Patterns seen
  - Network calls return ApiResult<T>, never throw
  ## Recurring issues
  - ViewModels in feature/profile inject ProfileRepository directly
  ```
- Where it is stored, by `memory:` value:
  - `project` → `.claude/agent-memory/<agent>/` (committed, shared with the team)
  - `local` → `.claude/agent-memory-local/<agent>/` (this project only, meant to stay out of git)
  - `user` → `~/.claude/agent-memory/<agent>/` (your machine, across all projects)
- Separate from your main session's auto memory (in `~/.claude/projects/`). Each subagent only reads and writes its own file.

#### Workflows — `.claude/workflows/`
- A **dynamic workflow** is a JavaScript script that coordinates many subagents. Claude writes the script; a runtime executes it **in the background** while your session stays usable.
- The difference from skills and subagents is **who holds the plan**: with skills and subagents, Claude decides the next step turn by turn and every result lands in its context. With a workflow, the **script** holds the loop, branching and intermediate results, so Claude's context only receives the final answer.

  | | Subagents | Skills | Workflows |
  |---|---|---|---|
  | Who decides what runs next | Claude, turn by turn | Claude, following the prompt | The script |
  | Where intermediate results live | Claude's context | Claude's context | Script variables |
  | Scale | A few tasks per turn | Same as subagents | Dozens to hundreds of agents per run |
  | Interruption | Restarts the turn | Restarts the turn | Resumable in the same session |

- **How to run one:**
  - Built-in: `/deep-research <question>` (fans out web research, cross-checks sources, returns a cited report).
  - Ask for one: start the prompt with `ultracode:` or say "use a workflow", e.g.
    `use a workflow to run ./gradlew detekt and keep fixing the reported issues until it passes or two rounds make no progress`
  - Let Claude decide: `/effort ultracode` makes Claude plan a workflow for every substantial task in the session (uses a lot more tokens).
- **Watch / control:** `/workflows` lists runs. Keys: `Enter` open, `p` pause/resume, `x` stop, `r` restart an agent, `s` save.
- **Save for reuse:** in `/workflows`, select a finished run and press `s`. Save to `.claude/workflows/` (shared with the team) or `~/.claude/workflows/` (personal). It then runs as `/<name>`. You normally don't write these files by hand. What a saved one looks like:
  ```javascript
  export const meta = {
    name: 'audit-viewmodels',
    description: 'Check every ViewModel for repositories injected without a UseCase',
  }

  const found = await agent('List every *ViewModel.kt file under app/.', {
    schema: { type: 'object', required: ['files'], properties: { files: { type: 'array', items: { type: 'string' } } } },
  })

  const audits = await pipeline(found.files, file =>
    agent(`Check ${file}: does it inject a Repository directly instead of a UseCase?`, { label: file }),
  )

  return audits.filter(Boolean)
  ```
  `agent()` spawns one subagent, `pipeline()` runs one per item, `parallel()` runs several at once, and `phase()` groups agents in the progress view. Saved workflows can take input through the `args` global.
- **Good fit:** repo-wide audits ("check every DAO returns `Flow`"), large migrations (RxJava → Coroutines across many files), fix-until-green loops, reviewing every file in a PR and merging findings.
- **Limits and cost:** each run can use far more tokens than a normal conversation. Try it on one module first. No user input mid-run; the script itself can't touch files or the shell (its agents do). By default up to 16 agents run at once and 1,000 per run. Turn off with `"disableWorkflows": true` or in `/config`.

#### Hooks — `.claude/hooks/`
- Shell commands run by Claude Code itself on lifecycle events. Unlike `CLAUDE.md` rules (which Claude *may* forget), hooks are **deterministic**.
- A hook receives the event as JSON on stdin. For `PreToolUse`, exiting with code `2` blocks the tool call and the stderr message goes back to Claude.
- In this repo:
  - `block-prod-db.sh` (`PreToolUse` on `Bash`) — blocks commands that touch production/staging databases.
  - `scan-secrets.sh` (`Stop`) — scans changed files for hard-coded secrets when Claude finishes.
- Scripts only run once registered in `.claude/settings.json` and made executable (`chmod +x`). This repo registers them like this:
  ```json
  {
    "hooks": {
      "PreToolUse": [
        { "matcher": "Bash", "hooks": [{ "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/block-prod-db.sh" }] }
      ],
      "Stop": [
        { "hooks": [{ "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/scan-secrets.sh" }] }
      ]
    }
  }
  ```

#### Settings — `settings.json`
- Precedence (highest first): enterprise managed → command-line flags → `.claude/settings.local.json` → `.claude/settings.json` → `~/.claude/settings.json`.
- Holds `model`, `env`, `permissions` (`allow` / `deny` / `ask` lists such as `"Bash(./gradlew test)"`), and `hooks`.

#### Output styles — `.claude/output-styles/`
- An output style is a set of instructions applied to **every response** in the session. It changes *how Claude talks and works*, not what it knows about the project.
- Built-in styles:
  | Style | What changes |
  |---|---|
  | `Default` | Standard software-engineering behavior (no extra instructions) |
  | `Proactive` | Starts work right away and makes reasonable assumptions instead of asking about routine decisions |
  | `Concise` | Leads with the result; no preamble, narration or recap |
  | `Explanatory` | Adds short `★ Insight` blocks explaining why it made each choice |
  | `Learning` | Like Explanatory, and leaves `TODO(human)` spots for you to write the key code yourself |
- Switch with `/output-style concise`, via `/config` → **Output style**, or with `"outputStyle": "Explanatory"` in a settings file (case-sensitive there). It applies from your next message.
- A custom style is a Markdown file. Put team-shared styles in `.claude/output-styles/`, personal ones in `~/.claude/output-styles/`:
  ```markdown
  ---
  name: Android mentor
  description: Explain Android/Kotlin decisions for junior developers
  keep-coding-instructions: true
  ---
  After each change, add a short "Why" note that links the decision to our
  Clean Architecture layers (app / domain / data) and the rule it follows.
  ```
- Important: a custom style **replaces** Claude Code's built-in coding instructions unless you set `keep-coding-instructions: true`. For a coding style, you almost always want `true`.
- Style files are read at startup, so restart Claude Code after creating or editing one. Styles affect the main conversation only; subagents keep their own prompts.

#### MCP servers & plugins
- **MCP (Model Context Protocol)** servers give Claude new tools that talk to external systems. Add with `claude mcp add ...` or a project `.mcp.json`.
- **Plugins** bundle skills, agents, hooks and MCP servers into one installable package (`/plugin`) — the way to share a whole setup across repos.

#### Which one should I use?
- A rule Claude should follow all the time → `CLAUDE.md` / `rules/`
- A rule only for certain files → `rules/` with `paths:`
- A procedure or reference Claude needs sometimes → **skill**
- A task that should run in isolation, with limited tools or a different model → **subagent**
- The same step across many files, or a multi-stage job you want to rerun → **workflow**
- A subagent that should get smarter about this codebase over time → **agent memory** (`memory:` in the agent file)
- A different tone, length or format for every response → **output style**
- Something that must happen every time, no exceptions → **hook**
- Access to an external system → **MCP server**
- Sharing all of the above across projects → **plugin**
