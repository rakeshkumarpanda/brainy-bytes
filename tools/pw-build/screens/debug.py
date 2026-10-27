"""Record real screenshots of Playwright's own tools for the debugging and reporting chapters.

Runs a small Brainy Shop project with one passing and one failing test (the Notebook is out of stock, so its
Add to cart button never appears), then opens the tools that read the results:
  the trace viewer and the HTML report, served over HTTP and captured with Playwright,
  UI mode, served with --ui-host and --ui-port and captured the same way,
  the Playwright Inspector, which needs a real window, so it runs under Xvfb and is captured with ImageMagick.
Output: content/playwright/img/debug-*.jpg and report-*.jpg
Run:  tools/pw-build/box/.venv/bin/python tools/pw-build/screens/debug.py   (needs Xvfb, ImageMagick and python-xlib)"""
import os
import shutil
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
PW = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PW))
BOX = os.path.join(PW, 'box')
IMG = os.path.join(ROOT, 'content', 'playwright', 'img')
PROJ = '/tmp/shop-tests'      # a short neutral path, since the report shows it
ENV = {**os.environ, 'PATH': os.path.join(BOX, 'node_modules', '.bin') + os.pathsep + os.environ['PATH'],
       'PLAYWRIGHT_BROWSERS_PATH': os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '/opt/pw-browsers'), 'PW_TEST_HTML_REPORT_OPEN': 'never'}
for k in [k for k in ENV if k == 'CI' or k.startswith('CLAUDE')]:
    ENV.pop(k)

CONFIG = '''import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 10_000,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://localhost:4173',
    trace: 'on',
    screenshot: 'only-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
'''

TEST = '''import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('asha@shop.example');
  await page.getByLabel('Password').fill('s3cret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByText('Hello, Asha')).toBeVisible();
  await expect(page.getByRole('listitem')).toHaveCount(5);
});

test('add the lamp to the cart', async ({ page }) => {
  await page.getByTestId('product-3').getByRole('button', { name: 'Add to cart' }).click();
  await expect(page.getByTestId('cart-count')).toHaveText('1');
});

test('add the notebook to the cart', async ({ page }) => {
  await page.getByTestId('product-4').getByRole('button', { name: 'Add to cart' }).click();
  await expect(page.getByTestId('cart-count')).toHaveText('1');
});
'''

PAUSE = '''import { test, expect } from '@playwright/test';

test.use({ viewport: { width: 900, height: 600 } });

test('look at the products before clicking', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByRole('listitem')).toHaveCount(5);
  await page.pause();
  await page.getByTestId('product-4').getByRole('button').click();
});
'''


def jpg(png, name, crop=None):
    out = os.path.join(IMG, name + '.jpg')
    args = ['convert', png] + (['-crop', crop, '+repage'] if crop else []) + ['-resize', '1200x>', '-quality', '82', out]
    subprocess.run(args, check=True)
    print('saved', out)


def wait_http(url, secs=30):
    import urllib.request
    end = time.time() + secs
    while time.time() < end:
        try:
            urllib.request.urlopen(url, timeout=2)
            return
        except Exception:
            time.sleep(0.5)
    raise SystemExit('not up: ' + url)


def inspector(tmp):
    """--debug opens a headed browser and the Inspector, paused before the first step. Resume runs on to page.pause()."""
    xv = subprocess.Popen(['Xvfb', ':97', '-screen', '0', '1920x1080x24', '-nolisten', 'tcp', '-ac'], stderr=subprocess.DEVNULL)
    time.sleep(1)
    os.environ['DISPLAY'] = ':97'
    sys.path.insert(0, HERE)
    import xdrive as X
    run = subprocess.Popen(['npx', 'playwright', 'test', '--config', 'debug.config.js', '--debug'], cwd=PROJ,
                           env={**ENV, 'DISPLAY': ':97'}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(30)                       # the browser and the Inspector open slowly on a virtual display
        X.click(1266, 25, wait=6)            # the green Resume button in the Inspector toolbar
        X.shot(os.path.join(tmp, 'inspector.png'))
    finally:
        run.terminate()
        xv.terminate()


def main():
    os.makedirs(IMG, exist_ok=True)
    shutil.rmtree(PROJ, ignore_errors=True)
    os.makedirs(os.path.join(PROJ, 'tests'))
    os.symlink(os.path.join(BOX, 'node_modules'), os.path.join(PROJ, 'node_modules'))
    open(os.path.join(PROJ, 'package.json'), 'w').write('{ "name": "shop-tests", "private": true, "type": "module" }\n')
    open(os.path.join(PROJ, 'playwright.config.js'), 'w').write(CONFIG)
    open(os.path.join(PROJ, 'tests', 'cart.spec.js'), 'w').write(TEST)
    os.makedirs(os.path.join(PROJ, 'debug'))                          # its own folder and config, so the report only has the cart tests
    open(os.path.join(PROJ, 'debug', 'pause.spec.js'), 'w').write(PAUSE)
    open(os.path.join(PROJ, 'debug.config.js'), 'w').write(CONFIG.replace("testDir: './tests'", "testDir: './debug'"))
    tmp = os.path.join(PROJ, 'png')
    os.makedirs(tmp)
    app = subprocess.Popen(['node', os.path.join(PW, 'app', 'server.mjs')], env={**os.environ, 'PORT': '4173'}, stdout=subprocess.PIPE, text=True)
    app.stdout.readline()
    procs = []
    try:
        r = subprocess.run(['npx', 'playwright', 'test'], cwd=PROJ, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        print(r.stdout[-1500:])
        trace = os.path.join(PROJ, 'test-results', 'cart-add-the-notebook-to-the-cart-chromium', 'trace.zip')
        procs.append(subprocess.Popen(['npx', 'playwright', 'show-trace', '--host', '127.0.0.1', '--port', '9400', trace], cwd=PROJ, env=ENV,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        procs.append(subprocess.Popen(['npx', 'playwright', 'show-report', '--host', '127.0.0.1', '--port', '9401'], cwd=PROJ, env=ENV,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        procs.append(subprocess.Popen(['npx', 'playwright', 'test', '--ui-host=127.0.0.1', '--ui-port=9402'], cwd=PROJ, env=ENV,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        wait_http('http://127.0.0.1:9400/')
        wait_http('http://127.0.0.1:9401/')
        wait_http('http://127.0.0.1:9402/')
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={'width': 1440, 'height': 860})
            # the trace viewer: the failed click, its log, and the network tab
            pg.goto('http://127.0.0.1:9400/')
            pg.get_by_text('Action', exact=True).first.wait_for()
            pg.wait_for_timeout(2000)
            pg.get_by_text('Log', exact=True).click()
            pg.wait_for_timeout(800)
            pg.screenshot(path=os.path.join(tmp, 'trace-log.png'))
            pg.get_by_text('Network', exact=True).click()
            pg.wait_for_timeout(800)
            pg.screenshot(path=os.path.join(tmp, 'trace-network.png'))
            # the HTML report: the list, then the failed test
            pg.goto('http://127.0.0.1:9401/')
            pg.get_by_text('add the notebook to the cart').first.wait_for()
            pg.wait_for_timeout(800)
            pg.screenshot(path=os.path.join(tmp, 'report-list.png'))
            pg.get_by_text('add the notebook to the cart').first.click()
            pg.wait_for_timeout(1500)
            pg.screenshot(path=os.path.join(tmp, 'report-failed.png'), full_page=False)
            # UI mode: run everything, then open the failed test
            pg.goto('http://127.0.0.1:9402/')
            pg.get_by_title('Run all — F5').click()
            pg.get_by_test_id('test-tree').get_by_text('add the notebook to the cart').wait_for()
            pg.wait_for_timeout(16000)
            pg.get_by_test_id('test-tree').get_by_text('add the notebook to the cart').click()
            pg.wait_for_timeout(2500)
            pg.screenshot(path=os.path.join(tmp, 'ui-mode.png'))
            b.close()
        inspector(tmp)
        jpg(os.path.join(tmp, 'trace-log.png'), 'debug-trace-log')
        jpg(os.path.join(tmp, 'trace-network.png'), 'debug-trace-network')
        jpg(os.path.join(tmp, 'report-list.png'), 'report-html-list', crop='1440x560+0+0')
        jpg(os.path.join(tmp, 'report-failed.png'), 'report-html-failed')
        jpg(os.path.join(tmp, 'ui-mode.png'), 'debug-ui-mode')
        jpg(os.path.join(tmp, 'inspector.png'), 'debug-inspector', crop='1630x700+0+0')
    finally:
        for pr in procs:
            pr.terminate()
        app.terminate()


if __name__ == '__main__':
    main()
