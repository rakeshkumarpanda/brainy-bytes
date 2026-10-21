"""Helpers for the Master the Claude topic files. Everything from tools/js-build/kit.py is available here too."""
import json
import os

from kit import run, dom, test, show, say, quiz, calc, ex, panel, pkg  # noqa: F401  (re-exported for the topic files)


def part(id, emoji, title, html, easy=False, files=None, kw=None):
    """One part of a chapter. easy=True keeps it on the beginner path. files names the real files and folders it teaches."""
    return {'id': id, 'emoji': emoji, 'title': title, 'html': html, 'easy': easy, 'files': files or [], 'kw': kw or [], 'qa': None, 'qa_why': None}


def md(code, label, note='📄 Ready to copy', result=None):
    """A Markdown file such as CLAUDE.md, SKILL.md or an agent file, shown so it can be copied."""
    return show(code, label, lang='md', note=note, result=result)


def js_(code, label, result=None):
    return show(code, label, lang='json', note='📄 Ready to copy', result=result)


def cli(code, label, result=None, note='⌨️ Type this in your terminal'):
    """Commands to type. These need a Claude login, so they are shown and not run here."""
    return show(code, label, lang='bash', note=note, result=result)


def prompt(text, label, result=None):
    """A prompt to type into Claude."""
    return show(text, label, lang='text', note='💬 Prompt to try', result=result)


def node_files(extra=None, type_module=True):
    files = {'package.json': pkg('demo', 'module' if type_module else None)}
    files.update(extra or {})
    return files


def hook(script, events, label, name='.claude/hooks/hook.mjs', settings=None, more=None, **kw):
    """Run a hook script for real: each event is piped on stdin the way Claude Code sends it,
    and the exit code, stdout and stderr are printed. settings is the matching settings.json, shown with it."""
    files = {name: script}
    if settings:
        files['.claude/settings.json'] = json.dumps(settings, indent=2)
    files.update(more or {})
    lines = []
    shown_lines = []
    for i, ev in enumerate(events):
        body = json.dumps(ev)
        files[f'events/{i + 1}.json'] = body
        lines.append(f'echo "--- event {i + 1}: {ev.get("tool_name") or ev.get("hook_event_name")}"; node {name} < events/{i + 1}.json; echo "exit code: $?"')
        shown_lines.append(f"echo '{body}' | node {name}")
    show_files = ([ '.claude/settings.json'] if settings else []) + [name] + list(more or {})
    spec = {'t': 'test', 'files': files, 'cmd': ' ; '.join(lines) + ' ; true', 'label': label, 'show': show_files,
            'shown_cmd': '\n$ '.join(shown_lines), 'badge': '🪝 Hook run for real with the JSON Claude Code sends'}
    spec.update(kw)
    return spec


_API = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'box', 'api')


def api_run(script, label, replies, name='app.py', more=None, log=True, **kw):
    """Run a Claude API example written with the real Python SDK against a local stand-in for the API.
    The stand-in's replies are scripted from replies, so the page labels them as not written by Claude."""
    files = {name: script, 'replies.json': json.dumps(replies, ensure_ascii=False)}
    for f in ('standin.py', 'run.py'):
        files[f] = open(os.path.join(_API, f)).read()
    files.update(more or {})
    spec = {'t': 'test', 'files': files, 'cmd': ('STANDIN_LOG=1 ' if log else '') + f'$PY run.py {name}', 'label': label,
            'show': [name] + list(more or {}), 'shown_cmd': f'python {name}', 'badge': '▶ Real SDK code, run against a local stand-in API with scripted replies'}
    spec.update(kw)
    return spec
