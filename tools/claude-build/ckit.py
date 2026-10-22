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


def hook(script, events, label, name='.claude/hooks/hook.py', settings=None, more=None, **kw):
    """Run a hook script for real: each event is piped on stdin the way Claude Code sends it,
    and the exit code, stdout and stderr are printed. settings is the matching settings.json, shown with it."""
    files = {name: script}
    if settings:
        files['.claude/settings.json'] = json.dumps(settings, indent=2)
    files.update(more or {})
    runner, shown_runner = ('$PY', 'python3') if name.endswith('.py') else ('node', 'node')
    lines = []
    shown_lines = []
    for i, ev in enumerate(events):
        body = json.dumps(ev)
        files[f'events/{i + 1}.json'] = body
        lines.append(f'echo "--- event {i + 1}: {ev.get("tool_name") or ev.get("hook_event_name")}"; {runner} {name} < events/{i + 1}.json; echo "exit code: $?"')
        shown_lines.append(f"echo '{body}' | {shown_runner} {name}")
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


_SHOTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'content', 'claude', 'shots')


def _png_size(name):
    with open(os.path.join(_SHOTS, name + '.png'), 'rb') as f:
        head = f.read(24)
    return int.from_bytes(head[16:20], 'big'), int.from_bytes(head[20:24], 'big')


def shots(title, steps):
    """A step by step guide with one picture per step, shown one step at a time with Back and Next buttons.
    steps is a list of (picture name in content/claude/shots, step title, step text as HTML).
    term-* pictures are real terminal output from shots/capture.py. ui-* pictures are illustrated mockups."""
    items = []
    for i, (img, head, text) in enumerate(steps, 1):
        w, h = _png_size(img)
        real = img.startswith('term-')
        kind = ('<span class="cl-kind real">✅ Real terminal output</span>' if real
                else '<span class="cl-kind mock">🎨 Illustrated mockup, the real screen may look a little different</span>')
        items.append(f'<li class="cl-step"{"" if i == 1 else " hidden"}><div class="cl-step-text"><b>Step {i}. {head}</b><p>{text}</p>{kind}</div>'
                     f'<a href="./shots/{img}.png" target="_blank" rel="noopener"><img src="./shots/{img}.png" width="{w}" height="{h}" loading="lazy" '
                     f'alt="Step {i}: {head}"></a></li>')
    dots = ''.join(f'<button type="button" class="cl-dot" aria-label="Go to step {i}"{" aria-current=\"step\"" if i == 1 else ""}>{i}</button>' for i in range(1, len(steps) + 1))
    return (f'<div class="cl-shots"><div class="cl-shots-head"><b>📸 {title}</b><span class="cl-dots">{dots}</span></div>'
            f'<ol class="cl-shot-list">{"".join(items)}</ol>'
            '<div class="cl-shots-nav"><button type="button" class="cl-prev">← Back</button><span class="cl-count"></span><button type="button" class="cl-next">Next →</button></div></div>')
