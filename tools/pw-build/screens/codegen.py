"""Record a real codegen session for every language and save the pictures and the generated code.

Starts Brainy Shop on port 4173, a virtual display (Xvfb), and `playwright codegen` for each target. It clicks and types
into the real recording browser, so the code on the page is exactly what codegen wrote.
Output: content/playwright/img/codegen-*.png and tools/pw-build/screens/out/codegen-*.txt
Run:  python3 tools/pw-build/screens/codegen.py   (needs Xvfb, ImageMagick and python-xlib)"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PW = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PW))
IMG = os.path.join(ROOT, 'content', 'playwright', 'img')
OUT = os.path.join(HERE, 'out')
DISP = ':97'


def main():
    os.makedirs(IMG, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    xv = subprocess.Popen(['Xvfb', DISP, '-screen', '0', '1600x900x24', '-nolisten', 'tcp', '-ac'], stderr=subprocess.DEVNULL)
    app = subprocess.Popen(['node', os.path.join(PW, 'app', 'server.mjs')], env={**os.environ, 'PORT': '4173'}, stdout=subprocess.PIPE, text=True)
    app.stdout.readline()
    time.sleep(1)
    os.environ['DISPLAY'] = DISP
    sys.path.insert(0, HERE)
    import xdrive as X
    env = {**os.environ, 'PLAYWRIGHT_BROWSERS_PATH': os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '/opt/pw-browsers')}
    try:
        for target, name in (('playwright-test', 'ts'), ('python-pytest', 'py'), ('java-junit', 'java'), ('javascript', 'js-library')):
            outfile = os.path.join(OUT, f'codegen-{name}.txt')
            cg = subprocess.Popen([os.path.join(PW, 'box', 'node_modules', '.bin', 'playwright'), 'codegen', '--target', target, '--output', outfile,
                                   '--viewport-size=800,600', 'http://localhost:4173/login'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(7)
            if name == 'ts':
                X.shot(os.path.join(IMG, 'codegen-start.png'))
            X.click(240, 284)
            X.type_text('asha@shop.example')
            X.click(240, 366)
            X.type_text('s3cret')
            X.click(240, 455, wait=2.5)
            X.shot(os.path.join(IMG, f'codegen-{name}.png'))
            cg.terminate()
            cg.wait()
            time.sleep(1)
            print(name, open(outfile).read() if os.path.exists(outfile) else '(no file)', sep='\n')
        for f in os.listdir(IMG):
            if f.startswith('codegen-') and f.endswith('.png'):
                src = os.path.join(IMG, f)
                subprocess.run(['convert', src, '-crop', '1600x700+0+0', '+repage', '-resize', '1200x', '-quality', '82', src[:-4] + '.jpg'], check=True)
                os.remove(src)
    finally:
        app.terminate()
        xv.terminate()


if __name__ == '__main__':
    main()
