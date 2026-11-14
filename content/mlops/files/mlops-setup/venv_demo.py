# 1.1 Set up your computer for machine learning
# Example "venv_demo" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# What a virtual environment really is: a folder with its own python and its own site-packages.
# This program creates one in a temporary folder, asks its python where it lives, then deletes it.
import os
import subprocess
import sys
import tempfile
import venv

with tempfile.TemporaryDirectory() as tmp:
    env_dir = os.path.join(tmp, '.venv')
    venv.create(env_dir, with_pip=False)                  # the same as: python -m venv .venv
    print('Created:', sorted(os.listdir(env_dir)))
    folder = 'Scripts' if os.name == 'nt' else 'bin'      # Windows uses Scripts, macOS and Linux use bin
    env_python = os.path.join(env_dir, folder, 'python.exe' if os.name == 'nt' else 'python')
    ask = 'import sys, site; print(sys.prefix != sys.base_prefix); print(site.getsitepackages()[0])'
    inside, packages = subprocess.run([env_python, '-c', ask], capture_output=True, text=True).stdout.split('\n')[:2]
    print('The new python says it is inside a virtual environment:', inside)
    print('Its packages go to:', packages.replace(tmp, '<temp>'))
    print('pyvenv.cfg says:')
    for line in open(os.path.join(env_dir, 'pyvenv.cfg')):
        if line.startswith(('include-system-site-packages', 'version')):
            print('   ', line.strip())
print('This python (outside it) is', sys.version.split()[0])
