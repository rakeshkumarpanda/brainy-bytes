"""A local HTTPS copy of https://www.selenium.dev/selenium/web/ for the examples, with the CDN files those pages load.

The Chromium wrapper written by setup.sh sends www.selenium.dev, cdn.jsdelivr.net, unpkg.com and code.jquery.com to
127.0.0.1:8443, so an example can keep the real URL a reader would type and still run without the internet.
The pages in site/selenium/web/ are copied unchanged from the Selenium repository (common/src/web, Apache 2.0).

Usage:  python3 tools/se-build/siteserver.py [port]      (runner.py starts it when it is not running)
"""
import http.server
import os
import ssl
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, 'site')
NODE = os.path.join(HERE, 'box', 'node', 'node_modules')
TYPES = {'.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'application/javascript', '.png': 'image/png',
         '.gif': 'image/gif', '.json': 'application/json', '.txt': 'text/plain'}


def resolve(host, path):
    """Map a request to a file. Returns None when there is no such file."""
    path = path.split('?')[0].split('#')[0]
    host = host.split(':')[0]
    if host == 'cdn.jsdelivr.net' and path.startswith('/npm/'):
        pkg, _, rest = path[5:].partition('/')
        return os.path.join(NODE, pkg.split('@')[0], rest)
    if host == 'unpkg.com':
        pkg, _, rest = path[1:].partition('/')
        return os.path.join(NODE, pkg.split('@')[0], rest)
    if host == 'code.jquery.com':
        return os.path.join(NODE, 'jquery', 'dist', 'jquery.min.js') if path.startswith('/jquery-') else None
    full = os.path.normpath(os.path.join(SITE, path.lstrip('/')))
    if full.endswith(os.sep) or os.path.isdir(full):
        full = os.path.join(full, 'index.html')
    return full if full.startswith(SITE) else None


class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        f = resolve(self.headers.get('Host', ''), self.path)
        if not f or not os.path.isfile(f):
            self.send_response(404)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<title>404 Not Found</title><h1>Not Found</h1>')
            return
        body = open(f, 'rb').read()
        self.send_response(200)
        self.send_header('Content-Type', TYPES.get(os.path.splitext(f)[1], 'application/octet-stream'))
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def serve(port=8443):
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), H)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(os.path.join(HERE, 'box', 'cert.pem'), os.path.join(HERE, 'box', 'key.pem'))
    srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
    srv.serve_forever()


if __name__ == '__main__':
    serve(int(sys.argv[1]) if len(sys.argv) > 1 else 8443)
