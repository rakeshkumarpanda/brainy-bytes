# 1.1 Set up your computer for machine learning
# Example "check_setup" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Check that your computer is ready for the MLOps chapters.
# Run it inside your activated virtual environment: python check_setup.py
import platform
import sys
from importlib.metadata import PackageNotFoundError, version

print('Python  ', platform.python_version(), '(needs 3.12 or newer)', 'OK' if sys.version_info >= (3, 12) else 'TOO OLD')
print('System  ', platform.system(), platform.machine())
print('Inside a virtual environment:', sys.prefix != sys.base_prefix)

packages = ['numpy', 'pandas', 'scikit-learn', 'scipy', 'joblib', 'flask', 'fastapi', 'uvicorn', 'django', 'pydantic']
missing = []
for name in packages:
    try:
        print(f'  {name:13s} {version(name)}')
    except PackageNotFoundError:
        print(f'  {name:13s} not installed')
        missing.append(name)
if missing:
    print('Install the missing ones with:  pip install ' + ' '.join(missing))
else:
    print('Everything is installed.')
