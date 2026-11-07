# 5.2 Modules and packages: import, the standard library and pip
# Example "platmod" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import platform, sys

print(platform.system())                 # Linux, Windows, Darwin (macOS), or Emscripten in a browser
print(platform.python_implementation())  # CPython, PyPy ...
print(platform.python_version_tuple()[:2])
print(sys.version_info >= (3, 10))
print(type(sys.path), len(sys.path) > 0)
