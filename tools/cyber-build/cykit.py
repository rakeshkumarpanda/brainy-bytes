"""Small boxes the Cybersecurity topic files use on top of cvkit, coreaikit, pykit and mlkit.

    talk(text)        the background talk of a lesson. It is not shown on the page. assets/voiceteach.js reads it
                      first when the reader presses "Listen to this lesson", so the voice note tells the story
                      behind the lesson (where the idea came from, why it matters, real incidents), not only the
                      words on the screen. Write it as plain spoken English with short sentences.
    safe(text)        a short box that says how to practise an attack idea safely and legally
    attack(steps)     an attacker and defender table: each row is (what the attacker does, what stops it)

The prose rules of the CV builder apply to every text here: no em dashes, en dashes, semicolons or emojis, and no
backslashes outside <pre> and <code>.
"""
from cvkit import table


def talk(text):
    return f'<div class="vt-talk" hidden>{text}</div>'


def safe(text):
    return f'<div class="cy-safe"><b>Practise safely and legally</b><div>{text}</div></div>'


def attack(rows, head=('What the attacker tries', 'What the defender does')):
    return table(list(head), [list(r) for r in rows], 'cy-ad')
