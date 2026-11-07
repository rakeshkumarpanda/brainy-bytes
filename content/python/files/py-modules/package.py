# 5.2 Modules and packages: import, the standard library and pip
# Example "package" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os, sys, tempfile

root = tempfile.mkdtemp()
pkg = os.path.join(root, "geometry")
os.makedirs(pkg)
files = {
    "__init__.py": 'print("geometry package loaded")\n'
                   'from .circle import area\n'           # a relative import
                   '__all__ = ["area", "circle", "square"]\n',
    "circle.py": 'import math\n'
                 'def area(r):\n'
                 '    return round(math.pi * r * r, 2)\n',
    "square.py": 'def area(side):\n'
                 '    return side * side\n',
}
for name, text in files.items():
    with open(os.path.join(pkg, name), "w") as f:
        f.write(text)
sys.path.insert(0, root)

import geometry                    # runs geometry/__init__.py
print(geometry.area(1))            # the circle area, re-exported by __init__.py
from geometry import square        # a submodule
print(square.area(3))
import geometry.circle as c
print(c.area(2), c.__name__)
