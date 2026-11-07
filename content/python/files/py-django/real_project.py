# 4.1 Django basics: project, URLs, views, templates, models and admin
# Example "real_project" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import os
import subprocess
import sys
import tempfile

# The same commands you type in a terminal, run from Python so you can see each step and its output
work = tempfile.mkdtemp()


def run(*command, cwd=None):
    print("$", " ".join(command))
    result = subprocess.run([sys.executable, *command], cwd=cwd or work, capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip()
    if output:
        print("  " + output.replace("\n", "\n  "))
    return result


run("-m", "django", "startproject", "mysite")
site = os.path.join(work, "mysite")
run("manage.py", "startapp", "books", cwd=site)

for folder, _, names in sorted(os.walk(site)):
    depth = folder[len(site):].count(os.sep)
    if "__pycache__" not in folder and "migrations" not in folder:
        print("  " * depth + os.path.basename(folder) + "/", " ".join(sorted(n for n in names if n.endswith(".py"))))

with open(os.path.join(site, "books", "models.py"), "w") as f:
    f.write(
        "from django.db import models\n\n\n"
        "class Book(models.Model):\n"
        "    title = models.CharField(max_length=200)\n"
        "    year = models.PositiveIntegerField()\n"
    )
settings_path = os.path.join(site, "mysite", "settings.py")
text = open(settings_path).read().replace('"django.contrib.staticfiles",', '"django.contrib.staticfiles",\n    "books",')
open(settings_path, "w").write(text)

run("manage.py", "makemigrations", "books", cwd=site)
run("manage.py", "sqlmigrate", "books", "0001", cwd=site)
result = run("manage.py", "migrate", cwd=site)
run("manage.py", "check", cwd=site)
