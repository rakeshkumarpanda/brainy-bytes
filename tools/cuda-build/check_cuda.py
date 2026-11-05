"""Compile every CUDA listing of the GPU Programming chapters, so the code on the pages is known to compile.

There is no nvcc in the cloud container, so the check uses clang (which compiles CUDA) with a CUDA tree put together
from the NVIDIA pip wheels. Set it up once:

    python3 -m venv /tmp/cu && /tmp/cu/bin/pip install nvidia-cuda-runtime-cu12 nvidia-cuda-nvcc-cu12 nvidia-curand-cu12 nvidia-cuda-cccl-cu12
    python3 tools/cuda-build/check_cuda.py --make /tmp/cu /tmp/cuda      (copies headers, ptxas and libdevice into /tmp/cuda)
    export BB_CUDA_PATH=/tmp/cuda

Then every build compiles each listing twice: device code for sm_80 through ptxas, and host code with -fsyntax-only.
Without BB_CUDA_PATH the check is skipped with a note.
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile


def make(venv, dest):
    site = glob.glob(os.path.join(venv, 'lib', 'python3*', 'site-packages', 'nvidia'))[0]
    os.makedirs(os.path.join(dest, 'include'), exist_ok=True)
    os.makedirs(os.path.join(dest, 'bin'), exist_ok=True)
    for pkg in ('cuda_runtime', 'cuda_nvcc', 'curand', 'cuda_cccl'):
        inc = os.path.join(site, pkg, 'include')
        if os.path.isdir(inc):
            shutil.copytree(inc, os.path.join(dest, 'include'), dirs_exist_ok=True)
    shutil.copy(os.path.join(site, 'cuda_nvcc', 'bin', 'ptxas'), os.path.join(dest, 'bin', 'ptxas'))
    if not os.path.exists(os.path.join(dest, 'nvvm')):
        os.symlink(os.path.join(site, 'cuda_nvcc', 'nvvm'), os.path.join(dest, 'nvvm'))
    open(os.path.join(dest, 'version.txt'), 'w').write('12.9\n')
    print('CUDA tree ready in', dest)


def run(listings):
    cp = os.environ.get('BB_CUDA_PATH')
    todo = [x for x in listings if x[2]]
    if not cp:
        print(f'cuda check: skipped {len(todo)} listings (set BB_CUDA_PATH, see tools/cuda-build/check_cuda.py)')
        return
    base = ['clang++', '-std=c++17', '-x', 'cuda', f'--cuda-path={cp}', '--cuda-gpu-arch=sm_80', '-Wno-unknown-cuda-version']
    bad = []
    with tempfile.TemporaryDirectory() as d:
        for i, (path, src, _) in enumerate(todo):
            f = os.path.join(d, f'l{i}.cu')
            open(f, 'w', encoding='utf-8').write(src)
            for extra in (['--cuda-device-only', '-c', f, '-o', os.devnull], ['--cuda-host-only', '-fsyntax-only', f]):
                r = subprocess.run(base + extra, capture_output=True, text=True)
                if r.returncode:
                    bad.append(f'{path}:\n{r.stderr[:1500]}')
                    break
    if bad:
        raise SystemExit('CUDA listings that do not compile:\n' + '\n'.join(bad))
    print(f'cuda check: {len(todo)} listings compile (device code through ptxas for sm_80, host code syntax)')


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--make':
        make(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
