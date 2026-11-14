# 1.1 Set up your computer for machine learning
# Example "pin_check" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Compare a requirements.txt with what is installed, the check a CI job or a teammate runs first.
from importlib.metadata import PackageNotFoundError, version

requirements = """
# requirements.txt for the MLOps chapters
numpy==2.3.5
pandas==3.0.2
scikit-learn==1.8.0
joblib>=1.4
mlflow==3.6.0
"""


def parse(text):
    wanted = []
    for line in text.splitlines():
        line = line.split('#')[0].strip()
        if not line:
            continue
        for op in ('==', '>='):
            if op in line:
                name, ver = line.split(op)
                wanted.append((name.strip(), op, ver.strip()))
                break
    return wanted


def as_tuple(v):
    return tuple(int(p) for p in v.split('.')[:3] if p.isdigit())


problems = 0
for name, op, ver in parse(requirements):
    try:
        have = version(name)
    except PackageNotFoundError:
        print(f'MISSING   {name} (wanted {op}{ver})')
        problems += 1
        continue
    ok = have == ver if op == '==' else as_tuple(have) >= as_tuple(ver)
    print(f'{"OK" if ok else "MISMATCH":9s} {name} {have} (wanted {op}{ver})')
    problems += not ok
print(f'{problems} problem(s). Fix them with: pip install -r requirements.txt')
