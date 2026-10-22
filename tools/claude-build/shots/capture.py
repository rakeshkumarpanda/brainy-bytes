"""Run the real setup commands for skills, rules and MCP, and save what the terminal printed.

render.mjs turns captures.json into the terminal screenshots in content/claude/shots/.
Everything runs in a throwaway home folder, so your own ~/.claude and ~/.claude.json are never touched.
The throwaway folder is shown as ~ in the screenshots. Nothing else in the output is changed.

Usage:  python3 tools/claude-build/shots/capture.py
Needs:  the claude command (Claude Code) on PATH, git, zip, and the box venv from tools/claude-build/README.md.
        No Claude login is needed: these commands only write and read config files and start the local MCP server.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.dirname(HERE)
sys.path.insert(0, BUILD)
import qadev  # noqa: E402

TOPIC_MCP = open(os.path.join(BUILD, 'topics', '10-claude-mcp.py'), encoding='utf-8').read()
SERVER = re.search(r"SERVER = r'''(.*?)'''", TOPIC_MCP, re.S).group(1).lstrip('\n')
BOX_PY = os.path.join(BUILD, 'box', '.venv', 'bin', 'python')


def write(root, files):
    for name, body in files.items():
        p = os.path.join(root, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(body.lstrip('\n'))


def main():
    home = tempfile.mkdtemp(prefix='claude-shots-')
    shop = os.path.join(home, 'shop-app')
    exp = os.path.join(home, 'expenses-mcp')
    os.makedirs(shop)
    write(exp, {'server.py': SERVER})
    # The server's own venv, so the screenshot shows the path a reader would really have.
    subprocess.run([sys.executable, '-m', 'venv', os.path.join(exp, '.venv')], check=True)
    subprocess.run([os.path.join(exp, '.venv', 'bin', 'pip'), 'install', '-q', 'mcp==2.3.0'], check=True)

    env = {'PATH': os.environ['PATH'], 'HOME': home, 'TERM': 'dumb', 'LANG': 'C.UTF-8',
           'GIT_AUTHOR_NAME': 'Asha', 'GIT_AUTHOR_EMAIL': 'asha@example.com', 'GIT_COMMITTER_NAME': 'Asha', 'GIT_COMMITTER_EMAIL': 'asha@example.com'}

    def sh(cmd, cwd=shop):
        subprocess.run(cmd, shell=True, cwd=cwd, env=env, check=True, capture_output=True)

    # A small shop app on a feature branch, so git diff has something real to show.
    write(shop, {'app/__init__.py': '', 'app/cart/__init__.py': '', 'app/cart/pricing.py': 'def total(items):\n    return sum(items)\n',
                 'app/cart/coupons.py': 'def apply(code, amount):\n    return amount\n', **qadev.SHOP_FILES})
    sh('git init -q -b main && git add -A && git commit -qm "Shop app" && git update-ref refs/remotes/origin/main HEAD && git switch -qc free-delivery')
    write(shop, {'app/cart/pricing.py': 'def total(items):\n    return sum(items)\n\n\ndef delivery_fee(amount):\n    return 0 if amount >= 499 else 40\n',
                 'app/cart/shipping.py': 'FREE_FROM = 499\n'})
    sh('git add -A && git commit -qm "Free delivery from Rs 499"')

    def session(steps, cwd=shop):
        out = []
        for shown, real in steps:
            r = subprocess.run(real, shell=True, cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
            text = (r.stdout + r.stderr).rstrip('\n')
            out.append({'cmd': shown, 'out': text.replace(home, '~')})
        return out

    skill_dir = '.claude/skills/pick-regression'
    rules = {**qadev.QA_RULES, **qadev.DEV_RULES}
    cap = {'version': session([('claude --version', 'claude --version')])}

    # ---- skills ----
    cap['skill-make'] = session([
        (f'mkdir -p {skill_dir}/scripts', f'mkdir -p {skill_dir}/scripts'),
    ])
    write(shop, {f'{skill_dir}/SKILL.md': qadev.PICK_TESTS_SKILL, f'{skill_dir}/scripts/map_tests.py': qadev.MAP_TESTS})
    cap['skill-make'] += session([
        ('find .claude -type f | sort', 'find .claude -type f | sort'),
        (f'head -5 {skill_dir}/SKILL.md', f'head -5 {skill_dir}/SKILL.md'),
    ])
    cap['skill-run'] = session([
        ('git diff --name-only origin/main...HEAD', 'git diff --name-only origin/main...HEAD'),
        (f'python {skill_dir}/scripts/map_tests.py app/cart/pricing.py app/cart/shipping.py',
         f'{BOX_PY} {skill_dir}/scripts/map_tests.py app/cart/pricing.py app/cart/shipping.py'),
    ])
    cap['skill-zip'] = session([
        ('cd .claude/skills && zip -r pick-regression.zip pick-regression', 'cd .claude/skills && zip -r pick-regression.zip pick-regression'),
        ('unzip -l .claude/skills/pick-regression.zip', 'unzip -l .claude/skills/pick-regression.zip'),
    ])
    os.remove(os.path.join(shop, '.claude/skills/pick-regression.zip'))

    # ---- rules ----
    cap['rules-make'] = session([('mkdir -p .claude/rules/qa .claude/rules/dev', 'mkdir -p .claude/rules/qa .claude/rules/dev')])
    write(shop, rules)
    cap['rules-make'] += session([
        ('find .claude/rules -type f | sort', 'find .claude/rules -type f | sort'),
        ('head -4 .claude/rules/qa/ui-tests.md', 'head -4 .claude/rules/qa/ui-tests.md'),
    ])

    # ---- MCP ----
    vpy = os.path.join(exp, '.venv', 'bin', 'python')
    srv = os.path.join(exp, 'server.py')
    cap['mcp-add'] = session([
        ('claude mcp add --transport stdio expenses -- ~/expenses-mcp/.venv/bin/python ~/expenses-mcp/server.py',
         f'claude mcp add --transport stdio expenses -- {vpy} {srv}'),
    ])
    cap['mcp-list'] = session([('claude mcp list', 'claude mcp list'), ('claude mcp get expenses', 'claude mcp get expenses')])
    cap['mcp-project'] = session([
        ('claude mcp add --transport http claude-code-docs --scope project https://code.claude.com/docs/mcp',
         'claude mcp add --transport http claude-code-docs --scope project https://code.claude.com/docs/mcp'),
        ('cat .mcp.json', 'cat .mcp.json'),
        ('claude mcp list', 'claude mcp list'),
    ])
    cap['_meta'] = {'claude_version': cap['version'][0]['out'], 'cwd': '~/shop-app'}

    dest = os.path.join(HERE, 'captures.json')
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(cap, f, indent=1, ensure_ascii=False)
    shutil.rmtree(home)
    print('captured', len(cap) - 1, 'terminal sessions ->', os.path.relpath(dest, os.path.dirname(os.path.dirname(BUILD))))


if __name__ == '__main__':
    main()
