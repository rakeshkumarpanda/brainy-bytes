# Master the Claude chapter builder

Builds the fourteen chapter pages in `content/claude/` from the topic files in `topics/`, and writes the
`claudeModules()` block in `data/catalog.js`. The Interview Questions page is built separately by
`tools/interview-build/build.py master-claude`.

## Set up once

```bash
python3 -m venv tools/claude-build/box/.venv
tools/claude-build/box/.venv/bin/pip install -r tools/claude-build/box/requirements.txt
```

## Build

```bash
python3 tools/claude-build/build.py                 # every chapter
python3 tools/claude-build/build.py claude-mcp      # one chapter by slug
python3 tools/interview-build/build.py --run master-claude
```

Run outputs are cached in `.cache/` by the hash of the example, so a rebuild only reruns what changed.

## Writing a topic file

Each file in `topics/` defines `MODULE`, `CODES`, `PARTS`, `INFO`, `REAL`, `SAY`, `QUIZ`, `CALC`, `EX`
and `T`, and optionally `DG` for animations. Helpers come from `ckit.py`:

| Helper | Use it for |
| - | - |
| `part(id, emoji, title, html, easy=True, files=[...])` | one part. `easy=True` keeps it on the beginner path |
| `md`, `js_`, `cli`, `prompt`, `show` | files and commands that are shown, not run |
| `test` | a small Python project run with a command (`$PY` is the box Python) |
| `hook(script, events, label, settings=...)` | a hook script run with the JSON Claude Code sends on stdin |
| `api_run(script, label, replies)` | Python SDK code run against the local stand-in API in `box/api/` |

## Checks the build runs

- Narration in all six languages for every part, plus `top` and `practice`.
- No em dashes, en dashes or semicolons in prose.
- At least one easy part per chapter.
- Part ids must be unique. Chapters have no coding exercises, so `EX = []` and the quiz carries the practice narration.
- Code examples are Python only. Leave a code block out when a table or a short text explains the point just as well.

## Gotchas

- Version 2 of the Python `mcp` package uses `from mcp.server import MCPServer`. `FastMCP` is gone.
- Read every run output after a build. Quiz and number practice answers quote those outputs.
- The stand-in API in `box/api/standin.py` only follows `replies.json`. Label anything it prints as scripted.
