"""Screenshots of a real report that a run wrote, for the reporting chapter.

Called by the reporting chapter's build hooks right after a run, while its report folder still exists:
  python report_shot.py <folder> <page> <kind> <out-name> [part of the failed test's name]
kind is one of: extent, pytest-html, allure, playwright. The folder is served over http on a free port,
because Allure loads its data with fetch. Files the reports load from a CDN are served from copies
(see offline_assets), since this machine has no direct internet access. Output: content/playwright/img/<out-name>-*.jpg
"""
import functools
import http.server
import os
import socketserver
import subprocess
import sys
import threading

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
IMG = os.path.join(ROOT, 'content', 'playwright', 'img')


def serve(folder):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=folder)
    handler.log_message = lambda *a: None
    srv = socketserver.TCPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


VENDOR = os.path.join(os.path.dirname(HERE), 'box', 'vendor')


def offline_assets(route):
    """The Extent report loads its styles from cdn.jsdelivr.net and Font Awesome from stackpath, which this
    build machine cannot reach. The same files come from GitHub raw and from the font-awesome npm package."""
    import re
    import urllib.request
    url = route.request.url
    m = re.match(r'https://cdn\.jsdelivr\.net/gh/([^/]+)/([^@]+)@([^/]+)/(.+)', url)
    if m:
        raw = f'https://raw.githubusercontent.com/{m[1]}/{m[2]}/{m[3]}/{m[4]}'
        body = urllib.request.urlopen(raw, timeout=30).read()
        ctype = 'text/css' if raw.endswith('.css') else 'application/javascript' if raw.endswith('.js') else 'image/png'
        return route.fulfill(body=body, content_type=ctype)
    m = re.match(r'https://stackpath\.bootstrapcdn\.com/font-awesome/4\.7\.0/(.+?)(\?.*)?$', url)
    if m:
        return route.fulfill(path=os.path.join(VENDOR, 'font-awesome-4.7.0', m[1]))
    return route.abort()


def jpg(png, name):
    out = os.path.join(IMG, name + '.jpg')
    subprocess.run(['convert', png, '-quality', '84', out], check=True)
    os.remove(png)
    print('saved', out)


def main(folder, page_name, kind, name, failed=''):
    srv = serve(folder)
    url = f'http://127.0.0.1:{srv.server_address[1]}/{page_name}'
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 1360, 'height': 820}, device_scale_factor=1, color_scheme='light')
        ctx.route(lambda u: not u.startswith('http://127.0.0.1'), offline_assets)
        pg = ctx.new_page()
        pg.goto(url, wait_until='networkidle')
        tmp = os.path.join(folder, '_shot.png')
        if kind == 'extent':
            pg.wait_for_selector('li.test-item')
            pg.locator('li.test-item[status="fail"]').first.click()
            pg.wait_for_timeout(600)
            pg.screenshot(path=tmp)
            jpg(tmp, name + '-tests')
            pg.locator('[onclick="toggleView(\'dashboard-view\')"]').first.click()
            pg.wait_for_timeout(1200)
            pg.screenshot(path=tmp)
            jpg(tmp, name + '-dashboard')
        elif kind == 'pytest-html':
            pg.wait_for_selector('#results-table')
            pg.locator('td.col-result', has_text='Failed').first.click()
            pg.wait_for_timeout(400)
            pg.screenshot(path=tmp, full_page=True)
            jpg(tmp, name)
        elif kind == 'playwright':
            pg.get_by_text(failed).first.wait_for()
            pg.screenshot(path=tmp)
            jpg(tmp, name + '-list')
            pg.get_by_text(failed).first.click()
            pg.wait_for_timeout(1200)
            pg.screenshot(path=tmp)
            jpg(tmp, name + '-failed')
        elif kind == 'allure':
            pg.wait_for_timeout(2500)
            pg.screenshot(path=tmp)
            jpg(tmp, name + '-overview')
            pg.get_by_text(failed, exact=False).first.click()      # the failed test, by part of its name
            pg.wait_for_timeout(1500)
            pg.screenshot(path=tmp)
            jpg(tmp, name + '-failed')
        b.close()
    srv.shutdown()


if __name__ == '__main__':
    main(*sys.argv[1:6])
