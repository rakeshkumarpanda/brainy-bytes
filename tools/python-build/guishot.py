"""Take a real screenshot of a tkinter window program for the Python pages (the gui() helper in pykit.py).

usage: xvfb-run -a -s "-screen 0 1024x768x24" python3.14 tools/python-build/guishot.py prog.py out.png [wait_ms] [action]
When prog.py calls mainloop, this waits, runs the action (Python code with the program's globals, for example
'name_entry.insert(0, "Ann"); submit()'), takes a screenshot of the root window with ImageMagick import and closes
the window. Screenshots go to content/python/img/<slug>/."""
import os
import subprocess
import sys
import tkinter

prog, out = sys.argv[1], sys.argv[2]
wait = int(sys.argv[3]) if len(sys.argv) > 3 else 600
action = sys.argv[4] if len(sys.argv) > 4 else ''
g = {'__name__': '__main__', '__file__': prog}
orig = tkinter.Misc.mainloop


def fake(self, n=0):
    root = self._root()

    def act():
        if action:
            exec(action, g)

    def shoot():
        root.update()
        x, y, w, h = root.winfo_rootx(), root.winfo_rooty(), root.winfo_width(), root.winfo_height()
        subprocess.run(['import', '-window', 'root', '-crop', f'{w}x{h}+{x}+{y}', '+repage', out], check=True)
        print('shot', w, h)
        root.destroy()
    root.after(300, act)
    root.after(300 + wait, shoot)
    orig(self)


tkinter.Misc.mainloop = fake
src = open(prog, encoding='utf-8').read()
exec(compile(src, prog, 'exec'), g)
