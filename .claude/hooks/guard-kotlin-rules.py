#!/usr/bin/env python3
"""Claude Code PreToolUse hook (Edit|Write|MultiEdit).

Blocks new production Kotlin that breaks the project's coding and
architecture rules (.claude/rules/, android-sdlc code patterns). Only the text
being written is checked, so existing legacy code is never flagged.
Exit code 2 stops the tool call and shows stderr to Claude.

Install at: .claude/hooks/guard-kotlin-rules.py   (chmod +x)
"""
import json
import re
import sys

RULES_HINT = ".claude/rules/ and .claude/skills/android-sdlc/reference/code-patterns.md"
COMMENT_PREFIXES = ("//", "/*", "*")


def everywhere(path, text):
    return True


def in_domain_layer(path, text):
    return "/domain/" in path or "/core/model/" in path


def in_view_model(path, text):
    return path.endswith("ViewModel.kt")


def outside_di_module(path, text):
    return "@Provides" not in text


# (pattern, rule, applies_to)
CHECKS = [
    (r"[\w)\]]!!", "No `!!`: use `?.`, `?:` or `requireNotNull(x) { \"reason\" }`.", everywhere),
    (r"\bGlobalScope\b", "No `GlobalScope`: use viewModelScope, a suspend function or WorkManager.", everywhere),
    (r"\brunBlocking\b", "No `runBlocking` in production code.", everywhere),
    (r"\bText\(\s*(text\s*=\s*)?\"", "No hard-coded UI text: use `stringResource(R.string.…)`.", everywhere),
    (
        r"\bDispatchers\.(IO|Default)\b",
        "Inject dispatchers (`@IoDispatcher`, `@DefaultDispatcher`) instead of hard-coding them.",
        outside_di_module,
    ),
    (
        r"^\s*import\s+(android|androidx|retrofit2|okhttp3|dagger\.hilt\.android)\.",
        "The domain layer is pure Kotlin: no Android, Retrofit, OkHttp or Hilt-Android imports.",
        in_domain_layer,
    ),
    (r"\b[A-Z]\w*Repository(Impl)?\b", "ViewModels call UseCases, never repositories.", in_view_model),
]


def read_tool_call():
    """Returns the target path and the new text: Write content, Edit new_string or MultiEdit edits."""
    tool_input = json.load(sys.stdin).get("tool_input", {})
    parts = [tool_input.get("content", ""), tool_input.get("new_string", "")]
    parts += [edit.get("new_string", "") for edit in tool_input.get("edits", [])]
    return tool_input.get("file_path", ""), "\n".join(parts)


def find_violations(path, text):
    code_lines = [line for line in text.splitlines() if not line.strip().startswith(COMMENT_PREFIXES)]
    violations = []
    for pattern, rule, applies_to in CHECKS:
        if not applies_to(path, text):
            continue
        hits = [line.strip() for line in code_lines if re.search(pattern, line)]
        if hits:
            violations.append((rule, hits))
    return violations


def main():
    try:
        path, text = read_tool_call()
    except ValueError:
        return 0
    if not (path.endswith(".kt") and "/src/main/" in path):
        return 0

    violations = find_violations(path, text)
    if not violations:
        return 0

    print(f"Blocked by guard-kotlin-rules hook: {path}", file=sys.stderr)
    for rule, hits in violations:
        print(f"- {rule}", file=sys.stderr)
        for hit in hits:
            print(f"    {hit}", file=sys.stderr)
    print(f"Fix the new code and try again. Rules: {RULES_HINT}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
