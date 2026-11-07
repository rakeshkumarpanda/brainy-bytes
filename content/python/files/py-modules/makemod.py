# 5.2 Modules and packages: import, the standard library and pip
# Example "makemod" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os, sys, tempfile, importlib

folder = tempfile.mkdtemp()                       # a folder only for this demo
with open(os.path.join(folder, "shapes.py"), "w") as f:
    f.write('print("loading shapes, __name__ is", __name__)\n'
            'PI = 3.14159\n'
            'def area(r):\n'
            '    return PI * r * r\n')

sys.path.insert(0, folder)        # tell Python to look in that folder too

import shapes                     # runs shapes.py once
import shapes                     # already in sys.modules: nothing is printed
print(shapes.area(2), shapes.PI)
print("shapes" in sys.modules, os.path.basename(shapes.__file__))
importlib.reload(shapes)          # run the file again on purpose
