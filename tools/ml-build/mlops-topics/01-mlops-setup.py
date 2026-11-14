# MLOps 1.1: setting up your computer for machine learning on macOS, Windows, Linux and ChromeOS. Checked against
# the Python documentation (Using Python on Windows, macOS and Unix, and the venv module), the Python Packaging User
# Guide (installing packages in a virtual environment), PEP 668 (externally managed environments), the uv
# documentation (astral.sh), the Git and Visual Studio Code setup guides, Docker's install guides for Docker Desktop
# and Docker Engine, Microsoft's WSL install guide, Google's "Set up Linux on your Chromebook" help page, and the
# PyTorch install selector for CUDA and Apple MPS.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, term, leet_items
from mlkit import link, ossteps

chapter('mlops-setup')
K = Kit()
K.code('check_setup', r'''
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
''', long=True)

K.code('venv_demo', r'''
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
''', long=True)

K.code('pin_check', r'''
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
''', long=True)


WHY_VENV = 'It creates a real virtual environment and starts a second python program, which the browser version of Python cannot do.'

PY_MAC = ('<ol><li>Open <b>Terminal</b> (press Command and Space, type Terminal, press Return).</li>'
          '<li>Install Apple&rsquo;s command line tools. They include Git and the compilers some packages need. A window asks you to confirm.</li>'
          '<li>Install Python 3.14 with the official installer from python.org/downloads (a .pkg file that works on Apple silicon and Intel), or with Homebrew if you use it.</li>'
          '<li>On macOS the command is <code>python3</code>. A plain <code>python</code> usually does not exist until you activate a virtual environment.</li></ol>'
          + term(['xcode-select --install', '', '# optional, with Homebrew (brew.sh) instead of the python.org installer', 'brew install python@3.14', '',
                  'python3 --version          # Python 3.14.x', 'uname -m                   # arm64 = Apple silicon, x86_64 = Intel'], 'Terminal (macOS)'))
PY_WIN = ('<ol><li>Open <b>PowerShell</b> (press the Windows key, type PowerShell, press Enter). Windows Terminal is a good home for it.</li>'
          '<li>Install Python 3.14 from python.org/downloads, or with winget, which ships with Windows 10 and 11. In the python.org installer, tick <b>Add python.exe to PATH</b>.</li>'
          '<li>Close and reopen PowerShell so it sees the new PATH, then check the version. The <code>py</code> launcher also works and can pick between installed versions.</li>'
          '<li>If typing <code>python</code> opens the Microsoft Store, turn off the python.exe and python3.exe entries in Settings, Apps, Advanced app settings, App execution aliases.</li></ol>'
          + term(['winget install Python.Python.3.14', '', 'python --version           # Python 3.14.x', 'py --list                  # every Python the launcher can find'], 'PowerShell (Windows)'))
PY_LINUX = ('<ol><li>Open a terminal (Ctrl, Alt and T on Ubuntu).</li>'
            '<li>Most distributions already have Python 3. Install the venv module, pip and Git from the package manager. Ubuntu 24.04 ships Python 3.12, which is new enough.</li>'
            '<li>Do not use <code>sudo pip install</code>. Debian, Ubuntu and Fedora mark the system Python as <b>externally managed</b> (PEP 668), and pip refuses to change it outside a virtual environment.</li>'
            '<li>For a newer Python than your distribution offers, install uv (next lesson) and run <code>uv python install 3.14</code>.</li></ol>'
            + term(['# Ubuntu and Debian', 'sudo apt update', 'sudo apt install -y python3 python3-venv python3-pip git', '',
                    '# Fedora', 'sudo dnf install -y python3 python3-pip git', '', 'python3 --version'], 'Terminal (Linux)'))
PY_CHROME = ('<ol><li>Open <b>Settings</b>, choose <b>About ChromeOS</b>, then <b>Developers</b>, and turn on the <b>Linux development environment</b>. Give it at least 20 GB of disk if you can. A <b>Terminal</b> app appears.</li>'
             '<li>The Linux part is a Debian container, so every Linux command on this site works in it. Its Python may be older than 3.12, so install a newer one with uv.</li>'
             '<li>Files you want to use in Linux go in the <b>Linux files</b> folder of the Files app.</li>'
             '<li>School or work Chromebooks may have Linux turned off by the administrator. Then use Google Colab or Kaggle notebooks in the browser, and the in page Python of this site.</li></ol>'
             + term(['sudo apt update', 'sudo apt install -y python3 python3-venv python3-pip git curl', '',
                     'curl -LsSf https://astral.sh/uv/install.sh | sh     # installs uv', 'uv python install 3.14', 'python3 --version'], 'Terminal (ChromeOS Linux)'))

VENV_MAC = ('<p>macOS, Linux and ChromeOS use the same commands. The environment folder is <code>.venv</code> and the activate script is in <code>.venv/bin</code>.</p>'
            + term(['mkdir ml-project && cd ml-project', 'python3 -m venv .venv', 'source .venv/bin/activate      # the prompt now starts with (.venv)', '',
                    'python -m pip install --upgrade pip', 'pip install numpy pandas scikit-learn joblib', 'pip freeze > requirements.txt', 'deactivate                     # leave the environment'], 'Terminal (macOS)'))
VENV_WIN = ('<p>Windows keeps the scripts in <code>.venv&#92;Scripts</code>. PowerShell blocks scripts by default, so allow local ones once for your account.</p>'
            + term(['mkdir ml-project; cd ml-project', 'py -3.14 -m venv .venv', 'Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # once, answer Y',
                    '.venv\\Scripts\\Activate.ps1          # in Command Prompt: .venv\\Scripts\\activate.bat', '',
                    'python -m pip install --upgrade pip', 'pip install numpy pandas scikit-learn joblib', 'pip freeze > requirements.txt', 'deactivate'], 'PowerShell (Windows)'))
VENV_LINUX = ('<p>The same as macOS. If <code>python3 -m venv</code> says ensurepip is not available, install the <code>python3-venv</code> package first.</p>'
              + term(['mkdir ml-project && cd ml-project', 'python3 -m venv .venv', 'source .venv/bin/activate', '',
                      'python -m pip install --upgrade pip', 'pip install numpy pandas scikit-learn joblib', 'pip freeze > requirements.txt'], 'Terminal (Linux)'))
VENV_CHROME = ('<p>Inside the Linux terminal the commands are the Debian ones. With uv you skip the separate pip step, and uv also installs the Python version you ask for.</p>'
               + term(['mkdir ml-project && cd ml-project', 'uv venv --python 3.14          # creates .venv with Python 3.14', 'source .venv/bin/activate',
                       'uv pip install numpy pandas scikit-learn joblib', 'uv pip freeze > requirements.txt'], 'Terminal (ChromeOS Linux)'))

GIT_MAC = term(['git --version                                  # came with xcode-select', 'brew install --cask visual-studio-code         # or download from code.visualstudio.com'], 'Terminal (macOS)')
GIT_WIN = term(['winget install Git.Git', 'winget install Microsoft.VisualStudioCode', '# close and reopen PowerShell, then', 'git --version'], 'PowerShell (Windows)')
GIT_LINUX = term(['git --version                                  # installed with the python packages above', 'sudo snap install code --classic               # Ubuntu, or the .deb or .rpm from code.visualstudio.com'], 'Terminal (Linux)')
GIT_CHROME = ('<p>Download the <b>.deb</b> build of VS Code for your Chromebook&rsquo;s processor (x64 for Intel and AMD, Arm64 for Arm) into Linux files, then install it. It appears in the launcher under Linux apps.</p>'
              + term(['git --version', 'sudo apt install -y ./code_*.deb'], 'Terminal (ChromeOS Linux)'))

DOCKER_MAC = ('<p>Install <b>Docker Desktop</b> for Mac, choosing the Apple silicon or Intel download, and start it once from Applications. It runs a small Linux virtual machine for the containers.</p>'
              + term(['brew install --cask docker     # or the download from docker.com', 'docker run hello-world'], 'Terminal (macOS)'))
DOCKER_WIN = ('<p>Docker on Windows runs Linux containers inside <b>WSL 2</b>, the Windows Subsystem for Linux. Install WSL first (it needs a restart), then Docker Desktop, and keep the WSL 2 based engine option on.</p>'
              + term(['wsl --install                 # in PowerShell as administrator, then restart', 'winget install Docker.DockerDesktop', 'docker run hello-world'], 'PowerShell (Windows)'))
DOCKER_LINUX = ('<p>On Linux you install <b>Docker Engine</b> directly, no virtual machine needed. Docker&rsquo;s script adds its package repository and installs the engine. Adding yourself to the docker group lets you run docker without sudo after you log out and back in.</p>'
                + term(['curl -fsSL https://get.docker.com -o get-docker.sh', 'sudo sh get-docker.sh', 'sudo usermod -aG docker $USER     # then log out and back in', 'docker run hello-world'], 'Terminal (Linux)'))
DOCKER_CHROME = ('<p>Docker Engine can be installed in the Linux container with the same script as Debian. It needs disk space, so raise the Linux disk size in Settings if needed. On a managed Chromebook this may be blocked, and a cloud machine or GitHub Codespaces is the alternative.</p>'
                 + term(['curl -fsSL https://get.docker.com -o get-docker.sh', 'sudo sh get-docker.sh', 'sudo usermod -aG docker $USER', 'docker run hello-world'], 'Terminal (ChromeOS Linux)'))

GPU_MAC = '<p>Macs have no NVIDIA GPU, so CUDA is not available. On Apple silicon, PyTorch uses the built in GPU through <b>MPS</b> (Metal Performance Shaders): move tensors to <code>torch.device("mps")</code>. Check with <code>torch.backends.mps.is_available()</code>.</p>'
GPU_WIN = '<p>With an NVIDIA card, install the newest NVIDIA driver, then pick the CUDA build on the PyTorch install page. <code>nvidia-smi</code> shows the card and driver. The same driver also gives CUDA inside WSL 2, so Linux tools work too.</p>' + term(['nvidia-smi', 'python -c "import torch; print(torch.cuda.is_available())"'], 'PowerShell (Windows)')
GPU_LINUX = '<p>Install the NVIDIA driver from your distribution (on Ubuntu: <code>sudo ubuntu-drivers install</code>), restart, and check with <code>nvidia-smi</code>. For GPUs inside Docker, add the NVIDIA Container Toolkit and run containers with <code>--gpus all</code>.</p>' + term(['sudo ubuntu-drivers install', 'nvidia-smi', 'docker run --rm --gpus all ubuntu nvidia-smi    # after the NVIDIA Container Toolkit'], 'Terminal (Linux)')
GPU_CHROME = '<p>Chromebooks have no GPU access for machine learning in the Linux container. Train on the CPU for small models, and use Google Colab or Kaggle, which give free GPU time in the browser, for anything larger.</p>'

K.lesson('tools', 'What you need and why', f'''
{src('The Python Packaging User Guide, the Python documentation on venv, and the setup guides of Git, Visual Studio Code and Docker.')}
{viz('mlpath')}
{wwh('A machine learning setup has six parts: <b>Python</b> itself, a <b>terminal</b> to type commands, a <b>virtual environment</b> per project, a <b>package installer</b> (pip or uv), <b>Git</b> to track versions, and an <b>editor</b> such as VS Code. For serving and deployment you add <b>Docker</b>, and for big models a <b>GPU</b> or a cloud notebook.',
     'Every later chapter of this subject runs these tools. The same steps also mean that a model behaves the same on your laptop, a teammate&rsquo;s laptop and a server, which is the first promise of MLOps.',
     'Install Python, open a terminal, create one virtual environment for each project, install packages into it, and save the exact versions in requirements.txt. Then add Git, an editor and Docker. The lessons below give the steps for macOS, Windows, Linux and ChromeOS. Open only the panel for your system.')}
{table(['Tool', 'What it is', 'Why ML needs it'], [
    ['Python 3.12 or newer', 'The language and its interpreter', 'NumPy, pandas, scikit-learn and PyTorch need a recent Python'],
    ['Terminal', 'A window where you type commands', 'Installing, running scripts, Git, Docker'],
    ['Virtual environment', 'A folder with its own Python and packages', 'Each project keeps its own versions'],
    ['pip or uv', 'Package installers', 'Install libraries from PyPI, the Python package index'],
    ['Git', 'Version control', 'History of code and configs, teamwork, CI'],
    ['VS Code', 'Editor with Python and Jupyter support', 'Write, run and debug code and notebooks'],
    ['Docker', 'Runs apps in containers', 'Ship the model with everything it needs'],
    ['GPU or cloud notebook', 'Fast parallel hardware', 'Training deep networks in hours, not days']])}
{run('check_setup')}
{note('Run this check after each part of the setup. The output above is from the computer that built this page: Python 3.14.6 on Linux inside a virtual environment, with every package installed. Inside this web page, the same program runs in the browser&rsquo;s own Python, so it reports a different system and that the web packages are not installed.', 'tip')}
''', kw=['setup', 'Python', 'terminal', 'PATH', 'virtual environment', 'pip', 'uv', 'Git', 'VS Code', 'Docker', 'GPU'])

K.lesson('python', 'Install Python and open a terminal', f'''
{src('Python documentation: Using Python on Windows, Using Python on macOS, and Using Python on Unix platforms, plus PEP 668 and Google&rsquo;s help page Set up Linux on your Chromebook.')}
{wwh('A <b>terminal</b> (also called a shell or command line) is a text window for running programs. <b>Python</b> is installed once per computer, and you can have several versions side by side. The <b>PATH</b> setting lists the folders the terminal searches when you type a command.',
     'Most problems beginners hit are not about ML at all: the wrong Python runs, or the terminal cannot find it. Knowing where Python is installed and how PATH works saves hours.',
     'Pick your system below and follow the steps. Finish with <code>python3 --version</code> (or <code>python --version</code> on Windows) and check that it says 3.12 or newer.')}
{ossteps('Install Python 3.14', PY_MAC, PY_WIN, PY_LINUX, PY_CHROME)}
{note('Two names, one idea: macOS, Linux and ChromeOS call it <code>python3</code>, Windows calls it <code>python</code> or <code>py</code>. Inside an activated virtual environment, <code>python</code> works everywhere.', 'exam')}
''', kw=['install Python', 'terminal', 'PowerShell', 'python3', 'py launcher', 'PATH', 'PEP 668', 'externally managed', 'ChromeOS Linux', 'Homebrew', 'winget'])

K.lesson('venv', 'Virtual environments and packages', f'''
{src('Python documentation, venv module, the Python Packaging User Guide, Installing packages using pip and virtual environments, and the uv documentation.')}
{viz('mlvenvs')}
{wwh('A <b>virtual environment</b> is a folder, usually called <code>.venv</code>, that holds its own copy of the Python program and its own <b>site-packages</b> folder for libraries. <b>Activating</b> it puts its folder at the front of PATH. <b>pip</b> installs packages from PyPI. <b>uv</b> is a newer, much faster tool that does the work of pip and venv and can also install Python itself. <b>requirements.txt</b> lists the exact versions.',
     'Different projects need different versions: an old model may need NumPy 1.26 while a new one needs NumPy 2.4. One shared install can hold only one version, so installing one project breaks another. With an environment per project and pinned versions, anyone can rebuild the same set of packages, which is what makes results reproducible.',
     'Create the environment inside the project folder, activate it every time you work on the project, install packages, and save them with pip freeze. Never commit the .venv folder to Git, commit requirements.txt instead.')}
{ossteps('Create a project environment', VENV_MAC, VENV_WIN, VENV_LINUX, VENV_CHROME)}
{local('venv_demo', WHY_VENV)}
{note('The program shows what python -m venv creates: a bin folder (Scripts on Windows), include and lib folders, and pyvenv.cfg. The new python reports that it is inside a virtual environment, its packages go to the environment&rsquo;s own site-packages, and include-system-site-packages = false means it cannot see packages installed for the whole computer.', 'exam')}
{run('pin_check')}
{note('The check finds two problems: NumPy 2.4.6 is installed but the file asks for 2.3.5, and MLflow is missing. Running pip install -r requirements.txt fixes both, which is exactly what a CI job or a new teammate does first.', 'tip')}
{table(['Command', 'pip and venv', 'uv'], [
    ['Create an environment', '<code>python3 -m venv .venv</code>', '<code>uv venv</code>'],
    ['Install packages', '<code>pip install pandas</code>', '<code>uv pip install pandas</code>'],
    ['Install from a file', '<code>pip install -r requirements.txt</code>', '<code>uv pip install -r requirements.txt</code>'],
    ['Save exact versions', '<code>pip freeze &gt; requirements.txt</code>', '<code>uv pip freeze &gt; requirements.txt</code>'],
    ['Install a Python version', 'Use the python.org installer', '<code>uv python install 3.14</code>']])}
''', kw=['virtual environment', 'venv', 'activate', 'site-packages', 'pip', 'uv', 'requirements.txt', 'pip freeze', 'dependency hell', 'reproducibility'])

K.lesson('gitcode', 'Git, VS Code and Jupyter', f'''
{src('Pro Git, chapter 1.6 First time Git setup, and the Visual Studio Code documentation for Python and Jupyter.')}
{wwh('<b>Git</b> records every change to your code so you can go back, branch and work with others. <b>VS Code</b> is a free editor with a Python extension (running, debugging, picking the environment) and a Jupyter extension for notebooks. <b>Jupyter</b> notebooks mix code, output and notes, which suits exploring data.',
     'MLOps starts with version control: the training code, the configs and the requirements must all be in Git so a model can be traced back to the exact code that made it. Notebooks are great for exploring, and scripts in Git are better for anything that must run again.',
     'Install Git and VS Code, set your name and email once, install the Python and Jupyter extensions, and choose your .venv as the interpreter (VS Code asks, or use the command Python: Select Interpreter). Add .venv to .gitignore.')}
{ossteps('Install Git and VS Code', GIT_MAC, GIT_WIN, GIT_LINUX, GIT_CHROME)}
{term(['git config --global user.name "Your Name"', 'git config --global user.email "you@example.com"', 'git init', 'echo ".venv/" >> .gitignore', 'pip install jupyterlab ipykernel     # notebooks inside the project environment', 'jupyter lab'], 'Every system, inside the project folder')}
{link('git', 'New to Git?', 'The Git and CI/CD subject teaches commits, branches, merging and GitHub Actions step by step.', 'Open Git and CI/CD')}
''', kw=['Git', 'git config', 'gitignore', 'VS Code', 'Python extension', 'interpreter', 'Jupyter', 'JupyterLab', 'ipykernel'])

K.lesson('docker', 'Docker on each system', f'''
{src('Docker documentation: Install Docker Desktop on Mac, Install Docker Desktop on Windows, Install Docker Engine (convenience script), and Microsoft Learn, How to install Linux on Windows with WSL.')}
{wwh('<b>Docker</b> packages an app with its Python, libraries and files into an <b>image</b>, and runs it as a <b>container</b>, which behaves the same on any computer with Docker. <b>Docker Desktop</b> is the app for macOS and Windows. Linux runs <b>Docker Engine</b> directly.',
     'A model that works on your laptop often fails on a server because of a different Python, library or system package. A container fixes that by shipping the whole environment. Chapter 2.3 of this subject builds a container for a model API.',
     'Install Docker for your system as below, start it, and run the hello-world container to check. Containers are Linux programs, so macOS and Windows run them inside a small Linux virtual machine, and on Windows that is WSL 2.')}
{ossteps('Install Docker', DOCKER_MAC, DOCKER_WIN, DOCKER_LINUX, DOCKER_CHROME)}
{note('If hello-world prints Hello from Docker!, the install works. Permission denied on /var/run/docker.sock on Linux means you have not logged out and back in since joining the docker group.', 'tip')}
''', kw=['Docker', 'Docker Desktop', 'Docker Engine', 'container', 'image', 'WSL 2', 'hello-world', 'docker group'])

K.lesson('gpu', 'GPUs, the cloud and common problems', f'''
{src('PyTorch Get Started (install selector), PyTorch documentation for the MPS backend, NVIDIA CUDA on WSL user guide, and the NVIDIA Container Toolkit install guide.')}
{wwh('A <b>GPU</b> runs thousands of small calculations at once, which is what training neural networks needs. NVIDIA GPUs use <b>CUDA</b>, Apple silicon uses <b>MPS</b>, and cloud notebooks such as Google Colab and Kaggle lend you a GPU in the browser.',
     'Classical ML from the Machine Learning subject (scikit-learn, gradient boosting) runs well on any CPU. Deep learning on images or text can be 10 to 50 times faster on a GPU, so it decides whether an experiment takes minutes or a whole day.',
     'Start on the CPU. When a model is too slow, use your own GPU if you have one (steps below) or a free cloud GPU, and only then pay for cloud machines.')}
{ossteps('Use a GPU', GPU_MAC, GPU_WIN, GPU_LINUX, GPU_CHROME)}
{table(['Problem', 'System', 'Fix'], [
    ['<code>python: command not found</code>', 'macOS, Linux, ChromeOS', 'Use <code>python3</code>, or activate the .venv'],
    ['Typing python opens the Microsoft Store', 'Windows', 'Turn off the App execution aliases for python'],
    ['Running scripts is disabled on this system', 'Windows PowerShell', '<code>Set-ExecutionPolicy -Scope CurrentUser RemoteSigned</code>'],
    ['<code>error: externally-managed-environment</code>', 'Debian, Ubuntu, Fedora, ChromeOS', 'Install inside a virtual environment, never with sudo pip'],
    ['ensurepip is not available', 'Debian, Ubuntu, ChromeOS', '<code>sudo apt install python3-venv</code>'],
    ['A package installed but import fails', 'All', 'pip and python come from different places: use <code>python -m pip</code>'],
    ['Linux option missing in Settings', 'ChromeOS', 'Managed device: ask the administrator or use Colab'],
    ['Docker permission denied', 'Linux, ChromeOS', 'Join the docker group, then log out and back in']])}
''', kw=['GPU', 'CUDA', 'nvidia-smi', 'MPS', 'Apple silicon', 'Google Colab', 'Kaggle', 'troubleshooting', 'python -m pip'])

K.lesson('versus', 'venv, uv, conda and Docker compared', f'''
{versus('Ways to give a project its own environment', ['', 'venv and pip', 'uv', 'conda', 'Docker'], [
    ['What it isolates', 'Python packages', 'Python packages and Python versions', 'Python and non Python libraries', 'The whole system: OS libraries, Python, packages'],
    ['Comes with Python', 'Yes', 'No, one small install', 'No, a separate distribution', 'No, a separate app'],
    ['Speed', 'Fine', 'Very fast', 'Slower', 'Slow to build, fast to start'],
    ['Lock file', 'requirements.txt', 'uv.lock or requirements.txt', 'environment.yml', 'Dockerfile plus requirements'],
    ['Best for', 'Learning, small projects', 'Everyday work, CI', 'Science stacks with C and CUDA libraries', 'Serving and deploying']],
    'learn with venv and pip, work day to day with uv, reach for conda when a library needs system packages, and ship with Docker.')}
''', kw=['venv vs conda', 'uv vs pip', 'Docker vs virtual environment'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Install Python, open a terminal, make a folder for your project, and give it its own environment so its packages do not mix with others.</p>',
    '<p>Use pip or uv with requirements.txt, Git with a .gitignore, VS Code with the right interpreter, and Docker for a first container, on your own system.</p>',
    '<p>Pin versions with lock files, set up the same environment in CI and in containers, use GPUs locally and in the cloud, and fix PATH, permission and driver problems quickly.</p>',
    '<p>Design reproducible environments for a team: base images, dev containers, hermetic builds, GPU drivers in clusters, and software supply chain checks for packages.</p>')}
{grow('Set up Python and a project environment.',
      'Set up a complete ML workstation on any system.',
      'Make environments reproducible for a whole team.')}
''', kw=['beginner', 'expert', 'reproducible environments'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'An ML workstation needs <b>Python</b> 3.12 or newer, a <b>terminal</b>, a <b>virtual environment</b> per project, <b>pip or uv</b>, <b>Git</b>, an <b>editor</b>, and later <b>Docker</b> and a <b>GPU</b> or cloud notebook.',
    'The terminal runs the first match it finds in <b>PATH</b>. Activating .venv puts its folder first, so python and pip mean the project&rsquo;s own copies.',
    'macOS and Linux use <code>python3</code> and <code>.venv/bin</code>. Windows uses <code>python</code> or <code>py</code> and <code>.venv&#92;Scripts</code>. ChromeOS runs a Debian container where the Linux steps apply.',
    'Save exact versions with <b>pip freeze &gt; requirements.txt</b> and rebuild with <b>pip install -r requirements.txt</b>. Commit requirements.txt, never .venv.',
    'Docker Desktop runs containers on macOS and Windows (through WSL 2), Docker Engine runs them natively on Linux, and <b>hello-world</b> checks the install.'],
    'MLOps 1.2 explains the MLOps lifecycle and how to make a project reproducible from data to deployment.')}
{files('Three tasks: reading a requirements line, checking a version against it, and finding a command on PATH.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A virtual environment is', ['A virtual machine', 'A folder with its own Python and its own installed packages', 'A cloud server', 'A Docker image'], 1, 'Just a folder.', 'Activate it to use it.')
K.quiz('e', 'On macOS and Linux, the Python command outside a virtual environment is usually', ['py', 'python3', 'pip', 'conda'], 1, 'With a 3.', 'python appears after activating a .venv.')
K.quiz('e', 'Which file lists the exact package versions of a project?', ['README.md', 'requirements.txt', '.gitignore', 'pyvenv.cfg'], 1, 'Made by pip freeze.', 'Commit it to Git.')
K.quiz('e', 'On a Chromebook, Python for this subject runs in', ['The Chrome browser only', 'The Linux development environment, a Debian container', 'Android apps', 'Nowhere'], 1, 'Turn it on in Settings.', 'Or use Colab if Linux is blocked.')
K.quiz('m', 'When you type python, the terminal runs', ['The newest Python', 'The first python found in the folders listed in PATH', 'A random Python', 'Always the system Python'], 1, 'Searched in order.', 'Activating a venv puts it first.')
K.quiz('m', 'Where is the activate script of a virtual environment on Windows?', ['.venv/bin', '.venv&#92;Scripts', 'C:&#92;Windows', '.venv/lib'], 1, 'Scripts on Windows.', 'bin on macOS and Linux.')
K.quiz('m', 'Ubuntu says error: externally-managed-environment when you run pip install. What should you do?', ['Use sudo pip install', 'Create and activate a virtual environment, then install', 'Delete Python', 'Reinstall Ubuntu'], 1, 'PEP 668.', 'Never change the system Python with pip.')
K.quiz('m', 'Why should .venv not be committed to Git?', ['It is secret', 'It is large and specific to one computer, and requirements.txt rebuilds it', 'Git cannot store folders', 'It contains your password'], 1, 'Rebuild, do not copy.', 'Add .venv to .gitignore.')
K.quiz('m', 'Docker on Windows runs Linux containers using', ['Hyper threading', 'WSL 2, the Windows Subsystem for Linux', 'PowerShell only', 'The Microsoft Store'], 1, 'wsl --install first.', 'Docker Desktop uses the WSL 2 engine.')
K.quiz('m', 'A package installs fine but import fails. The safest way to install so pip matches python is', ['pip3 install', 'python -m pip install', 'sudo pip install', 'conda install'], 1, 'Same interpreter.', 'pip may belong to another Python.')
K.quiz('h', 'On an Apple silicon Mac, PyTorch uses the GPU through', ['CUDA', 'MPS (Metal Performance Shaders)', 'ROCm', 'OpenCL only'], 1, 'No NVIDIA on Macs.', 'torch.device("mps").')
K.quiz('h', 'Which tool isolates system libraries as well as Python packages?', ['venv', 'Docker', 'pip', 'requirements.txt'], 1, 'The whole system.', 'A container ships OS libraries too.')
K.quiz('x', 'In the style of an MLOps engineer interview: a model gives different results on a teammate&rsquo;s laptop. The first thing to compare is', ['Screen size', 'Python and package versions, using the pinned requirements file', 'Keyboard layout', 'Internet speed'], 1, 'Same code, different libraries.', 'Then data versions and random seeds.')
K.quiz('x', 'In the style of a cloud certification question: the best way to make the same environment run in CI and on a server is', ['Install packages by hand on each machine', 'Build one container image from a pinned requirements file and run it everywhere', 'Copy the .venv folder', 'Use the newest version of every package'], 1, 'Build once, run anywhere.', 'Images are versioned too.')

K.calc('e', 'The Python installer is 60 MB and your connection is 8 megabits per second. Download time in seconds?', '60', '8 bits in a byte.', ['60 MB = 60 &times; 8 = 480 megabits.', 'Divide by the speed.', eq('480 / 8 = 60 seconds')], check=60)
K.calc('e', 'PATH lists 6 folders and python is first found in folder 4. How many folders does the terminal check?', '4', 'It stops at the first match.', ['Folders 1, 2 and 3 have no python.', 'Folder 4 has it, so the search stops.', eq('4 folders')], check=4)
K.calc('e', 'Python versions get about 5 years of support after release. Python 3.14 came out in October 2025. Support ends in which year?', '2030', 'Add 5.', ['Release year 2025.', 'Support lasts about 5 years.', eq('2025 + 5 = 2030')], check=2030)
K.calc('m', 'Three projects each have a .venv of 450 MB. Total disk used by the environments, in MB?', '1350', 'Each project has its own copy.', ['One environment: 450 MB.', 'Three separate folders.', eq('3 &times; 450 = 1,350 MB')], check=1350)
K.calc('m', 'You asked pip for 12 packages and pip freeze lists 31. How many came in as dependencies?', '19', 'Packages need other packages.', ['pip freeze lists everything installed.', 'Subtract the ones you asked for.', eq('31 &minus; 12 = 19')], check=19)
K.calc('m', 'A Docker image has layers of 80 MB (base system), 350 MB (Python and libraries), 40 MB (your code) and 5 MB (the model). Image size in MB?', '475', 'Add the layers.', ['80 + 350 = 430.', '430 + 40 = 470.', eq('470 + 5 = 475 MB')], check=475)
K.calc('m', 'Docker Desktop is given 6 GB of a 16 GB laptop. Fraction of memory given to containers?', '0.375', 'Part over whole.', ['Given: 6 GB.', 'Total: 16 GB.', eq('6 / 16 = 0.375')], check=0.375)
K.calc('h', 'A model has 7 billion parameters stored in 16 bit floats. Memory for the weights alone, in GB (1 GB = 10<sup>9</sup> bytes)?', '14', '16 bits = 2 bytes.', ['Each parameter takes 2 bytes.', '7 &times; 10<sup>9</sup> &times; 2 = 14 &times; 10<sup>9</sup> bytes.', eq('14 GB')], check=14)
K.calc('h', 'Training takes 2 hours on the CPU and a GPU is 25 times faster. Minutes on the GPU?', '4.8', 'Convert to minutes first.', ['2 hours = 120 minutes.', 'Divide by the speed up.', eq('120 / 25 = 4.8 minutes')], check=4.8)
K.calc('x', 'In the style of a cloud cost question: a cloud GPU costs 1.20 dollars per hour and you train for 30 hours a month, plus 20 dollars of storage. Monthly cost in dollars?', '56', 'Compute plus storage.', ['GPU: 30 &times; 1.20 = 36 dollars.', 'Storage: 20 dollars.', eq('36 + 20 = 56 dollars')], check=56)

K.assign('parse_requirement', 'e', 'Read one line of requirements.txt',
         '<p>Write <code>parse_requirement(line)</code> that returns <code>[name, operator, version]</code> for lines such as <code>numpy==2.4.6</code> or <code>joblib&gt;=1.4</code> (operators <code>==</code> and <code>&gt;=</code>), and <code>None</code> for blank lines and comments. Ignore spaces and anything after a <code>#</code>.</p>',
         """
def parse_requirement(line):
    # your code here
    pass
""", [("parse_requirement('numpy==2.4.6')", ['numpy', '==', '2.4.6']), ("parse_requirement('joblib >= 1.4  # any newer one')", ['joblib', '>=', '1.4']), ("parse_requirement('# comment')", None), ("parse_requirement('')", None)],
         """
def parse_requirement(line):
    line = line.split('#')[0].strip()
    if not line:
        return None
    for op in ('==', '>='):
        if op in line:
            name, version = line.split(op)
            return [name.strip(), op, version.strip()]
    return None
""", 'Cut off the comment, strip spaces, and split on whichever operator appears.', '<p>Real requirement lines can also have extras, markers and other operators. The packaging library parses all of them, and this task covers the two you see most.</p>')
K.assign('version_ok', 'm', 'Does the installed version satisfy the requirement?',
         '<p>Write <code>version_ok(installed, op, wanted)</code> that compares dotted versions such as <code>2.4.6</code> number by number (so 1.10 is newer than 1.9). For <code>==</code> return whether they are equal, for <code>&gt;=</code> whether installed is at least wanted.</p>',
         """
def version_ok(installed, op, wanted):
    # your code here
    pass
""", [("version_ok('2.4.6', '==', '2.4.6')", True), ("version_ok('1.10.0', '>=', '1.9')", True), ("version_ok('2.3.5', '>=', '2.4')", False), ("version_ok('2.4.6', '==', '2.3.5')", False)],
         """
def version_ok(installed, op, wanted):
    a = [int(p) for p in installed.split('.')]
    b = [int(p) for p in wanted.split('.')]
    n = max(len(a), len(b))
    a, b = a + [0] * (n - len(a)), b + [0] * (n - len(b))
    return a == b if op == '==' else a >= b
""", 'Turn each version into a list of numbers, pad the shorter one with zeros, and compare the lists.', '<p>Comparing versions as text gets 1.10 against 1.9 wrong, because the character 1 sorts before 9. Comparing numbers fixes it.</p>')
K.assign('find_on_path', 'm', 'Find a command on PATH',
         '<p>Write <code>find_on_path(path, contents, command)</code>. <code>path</code> is a list of folder names in search order and <code>contents</code> is a dictionary from folder name to the list of programs in it. Return the first folder that contains the command, or <code>\'not found\'</code>.</p>',
         """
def find_on_path(path, contents, command):
    # your code here
    pass
""", [("find_on_path(['/usr/bin', '/bin'], {'/usr/bin': ['python3'], '/bin': ['ls']}, 'python')", 'not found'),
      ("find_on_path(['.venv/bin', '/usr/bin'], {'.venv/bin': ['python', 'pip'], '/usr/bin': ['python3']}, 'python')", '.venv/bin'),
      ("find_on_path(['/usr/bin', '.venv/bin'], {'.venv/bin': ['python3'], '/usr/bin': ['python3']}, 'python3')", '/usr/bin')],
         """
def find_on_path(path, contents, command):
    for folder in path:
        if command in contents.get(folder, []):
            return folder
    return 'not found'
""", 'Walk the folders in order and return the first one whose list holds the command.', '<p>The last test shows why order matters: with .venv/bin second, the system python3 wins. Activating an environment puts its folder first.</p>')

K.must('The toolbox', 'Python 3.12 or newer, terminal, .venv per project, pip or uv, Git, VS Code, later Docker and a GPU or Colab.')
K.must('PATH', 'The first match in PATH runs. activate puts .venv first. python -m pip keeps pip and python together.')
K.must('Per system', 'macOS and Linux: python3, .venv/bin. Windows: python or py, .venv&#92;Scripts, execution policy. ChromeOS: Linux container, Debian steps.')
K.must('Reproducible', 'pip freeze &gt; requirements.txt, pip install -r requirements.txt. Commit requirements, ignore .venv. Never sudo pip.')
K.must('Docker', 'Desktop on macOS and Windows (WSL 2), Engine on Linux, docker group, docker run hello-world.')
K.must('GPU', 'NVIDIA: driver, nvidia-smi, CUDA build of PyTorch. Apple silicon: MPS. Chromebook: Colab or Kaggle.')

T = K.topic(
    slug='mlops-setup', topic='mlops-setup', step=(1, 'Set up and plan', 'mlops-s1', 'Get your computer ready on macOS, Windows, Linux or ChromeOS, and learn what MLOps is and how to make a project reproducible.', 'Beginner'),
    title='Set up your computer for machine learning', short='Setup on every system', badge='1.1', minutes=50,
    lead='Install Python, a terminal, virtual environments, pip and uv, Git, VS Code, Docker and GPU support, with separate steps for macOS, Windows, Linux and ChromeOS, and fix the problems people hit most.',
    desc='setup, install Python, terminal, PATH, virtual environment, venv, pip, uv, requirements.txt, pip freeze, PEP 668, Git, VS Code, Jupyter, Docker Desktop, Docker Engine, WSL 2, ChromeOS Linux, GPU, CUDA, MPS, Google Colab, troubleshooting.',
    summary='Python, virtual environments, Git, VS Code, Docker and GPUs set up on macOS, Windows, Linux and ChromeOS.',
    keywords=['setup', 'install Python', 'virtual environment', 'pip', 'uv', 'requirements.txt', 'Docker', 'WSL 2', 'ChromeOS Linux', 'GPU'],
    recap='<p>Give every project its own environment, write its versions down, and keep the code in Git. Then the same model runs the same way on macOS, Windows, Linux, ChromeOS and a server.</p>',
    added='2026-11-14', leet=leet_items())
