
```.claude/
├── CLAUDE.md              # Main instructions — loaded into every session
├── CLAUDE.local.md        # Personal overrides, gitignored (optional)
├── settings.json          # Permissions, hooks, allowed tools — committed
├── settings.local.json    # Personal settings — gitignored
├── rules/                 # Split-out instruction files (scoped by path)
├── skills/                # Reusable workflows
│   └── your-skill/
│       └── SKILL.md
├── agents/                # Subagent personas (own system prompt, tool access)
├── commands/               # Legacy slash commands (skills supersede these now)
├── hooks/                  # Scripts on tool events (pre/post tool use, etc.)
└── docs/                   # Reference docs skills pull in on demand (unofficial but common pattern)