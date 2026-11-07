# 5.2 Modules and packages: import, the standard library and pip
# Example "private" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os, sys, tempfile

folder = tempfile.mkdtemp()
with open(os.path.join(folder, "tools.py"), "w") as f:
    f.write('__all__ = ["slug"]\n'
            'def slug(text):\n'
            '    return _clean(text).replace(" ", "-")\n'
            'def _clean(text):\n'
            '    return text.strip().lower()\n'
            'def shout(text):\n'
            '    return text.upper()\n')
sys.path.insert(0, folder)

from tools import *               # takes only the names in __all__
print(slug("  Hello World "))
print("shout" in dir(), "_clean" in dir())
import tools
print(tools._clean(" Still Reachable "))   # _ means "please do not use", not "locked"
