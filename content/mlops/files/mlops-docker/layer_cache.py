# 2.3 Docker and CI/CD for models
# Example "layer_cache" from the lesson.
# From the Brainy Bytes MLOps subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

# Which Dockerfile steps run again after a change? A small model of Docker's layer cache.
# A step runs again if the files it copies changed, or if any step before it ran again.
# Step times are seconds from real builds of the chapter's project.
GOOD = [('FROM python:3.14-slim', [], 0), ('WORKDIR /app', [], 0),
        ('COPY requirements.txt .', ['requirements.txt'], 0), ('RUN pip install -r requirements.txt', [], 18),
        ('COPY train.py app.py ./', ['train.py', 'app.py'], 0), ('RUN python train.py', [], 1.6),
        ('RUN useradd appuser', [], 0.1)]
BAD = [('FROM python:3.14-slim', [], 0), ('WORKDIR /app', [], 0),
       ('COPY . .', ['requirements.txt', 'train.py', 'app.py'], 0.4), ('RUN pip install -r requirements.txt', [], 18.6),
       ('RUN python train.py', [], 1.2)]


def rebuild(steps, changed):
    again, total = False, 0.0
    for instruction, files, seconds in steps:
        if any(f in changed for f in files):
            again = True
        if again:
            total += seconds
        print(f'    {"runs again" if again else "CACHED    "}  {instruction}')
    return total


for name, steps in [('Good order', GOOD), ('Bad order', BAD)]:
    for changed in [{'app.py'}, {'requirements.txt'}]:
        print(f'{name}, changed {sorted(changed)[0]}:')
        print(f'    about {rebuild(steps, changed):.1f} s of steps ran again')
