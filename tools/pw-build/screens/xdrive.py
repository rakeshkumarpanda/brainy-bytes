"""Tiny X11 driver for the screen recordings: move, click, type and take a screenshot of a virtual display.
Used by codegen.py to record a real codegen session under Xvfb. Needs python-xlib and ImageMagick's import."""
import os
import subprocess
import time

from Xlib import X, XK, display
from Xlib.ext import xtest

D = display.Display(os.environ['DISPLAY'])


def click(x, y, wait=0.6):
    xtest.fake_input(D, X.MotionNotify, x=x, y=y)
    D.sync()
    time.sleep(0.15)
    xtest.fake_input(D, X.ButtonPress, 1)
    xtest.fake_input(D, X.ButtonRelease, 1)
    D.sync()
    time.sleep(wait)


SHIFTED = {'@': 'at', '_': 'underscore', ':': 'colon', '!': 'exclam', '?': 'question'}


def key(name, shift=False):
    code = D.keysym_to_keycode(XK.string_to_keysym(name))
    if shift:
        xtest.fake_input(D, X.KeyPress, D.keysym_to_keycode(XK.string_to_keysym('Shift_L')))
    xtest.fake_input(D, X.KeyPress, code)
    xtest.fake_input(D, X.KeyRelease, code)
    if shift:
        xtest.fake_input(D, X.KeyRelease, D.keysym_to_keycode(XK.string_to_keysym('Shift_L')))
    D.sync()
    time.sleep(0.04)


def type_text(text, wait=0.5):
    names = {' ': 'space', '.': 'period', '-': 'minus', ',': 'comma', '/': 'slash'}
    for ch in text:
        if ch in SHIFTED:
            key(SHIFTED[ch], shift=True)
        elif ch.isupper():
            key(ch.lower(), shift=True)
        else:
            key(names.get(ch, ch))
    time.sleep(wait)


def shot(path, crop=None):
    subprocess.run(['import', '-window', 'root', path], check=True, env={**os.environ})
    if crop:
        w, h, x, y = crop
        subprocess.run(['convert', path, '-crop', f'{w}x{h}+{x}+{y}', '+repage', path], check=True)
