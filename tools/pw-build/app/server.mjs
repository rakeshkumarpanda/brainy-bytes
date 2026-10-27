// Brainy Shop: the small web app every Playwright example in this subject runs against.
// Plain Node.js, no packages, so the JavaScript, TypeScript, Python and Java examples can all use it.
// Start it with:  node server.mjs        (PORT=4173 by default)
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const SITE = path.join(path.dirname(fileURLToPath(import.meta.url)), 'site');
const PORT = Number(process.env.PORT || 4173);
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.png': 'image/png', '.svg': 'image/svg+xml', '.txt': 'text/plain; charset=utf-8', '.csv': 'text/csv' };

const PRODUCTS = [
  { id: 1, name: 'Gel pen', price: 20, stock: 120, category: 'Stationery' },
  { id: 2, name: 'Coffee mug', price: 199, stock: 35, category: 'Kitchen' },
  { id: 3, name: 'Desk lamp', price: 1299, stock: 8, category: 'Home' },
  { id: 4, name: 'Notebook', price: 60, stock: 0, category: 'Stationery' },
  { id: 5, name: 'Water bottle', price: 349, stock: 50, category: 'Kitchen' },
];
const USERS = { 'asha@shop.example': { name: 'Asha', password: 's3cret', role: 'customer' },
  'ravi@shop.example': { name: 'Ravi', password: 'admin123', role: 'admin' } };

const sessions = new Map();       // token -> { email, cart: Map(productId -> qty) }
const orders = new Map();
const people = new Map();         // a small CRUD resource for the API testing chapter
let nextOrder = 1001, nextPerson = 1;

function send(res, status, body, headers = {}) {
  const json = typeof body !== 'string';
  res.writeHead(status, { 'Content-Type': json ? 'application/json' : 'text/plain; charset=utf-8', ...headers });
  res.end(json ? JSON.stringify(body) : body);
}
function readBody(req) {
  return new Promise(resolve => {
    let s = '';
    req.on('data', c => { s += c; });
    req.on('end', () => { try { resolve(s ? JSON.parse(s) : {}); } catch { resolve(null); } });
  });
}
function cookie(req, name) {
  const m = (req.headers.cookie || '').match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  return m ? decodeURIComponent(m[1]) : null;
}
function session(req) {
  const auth = req.headers.authorization || '';
  const token = auth.startsWith('Bearer ') ? auth.slice(7) : cookie(req, 'session');
  return token && sessions.get(token) ? { token, ...sessions.get(token) } : null;
}
const later = ms => new Promise(r => setTimeout(r, ms));
const cartView = s => {
  const items = [...s.cart].map(([id, qty]) => { const p = PRODUCTS.find(x => x.id === id); return { id, name: p.name, price: p.price, qty }; });
  return { items, count: items.reduce((a, i) => a + i.qty, 0), total: items.reduce((a, i) => a + i.qty * i.price, 0) };
};

async function api(req, res, url) {
  const p = url.pathname, m = req.method;
  if (p === '/api/health') return send(res, 200, { status: 'ok' });
  if (p === '/api/login' && m === 'POST') {
    const b = await readBody(req);
    const u = b && USERS[b.email];
    await later(150);
    if (!u || u.password !== b.password) return send(res, 401, { error: 'Wrong email or password' });
    const token = 't' + Math.random().toString(36).slice(2, 12);
    sessions.set(token, { email: b.email, cart: new Map() });
    return send(res, 200, { token, name: u.name, role: u.role }, { 'Set-Cookie': `session=${token}; Path=/; HttpOnly; SameSite=Lax` });
  }
  if (p === '/api/logout' && m === 'POST') {
    const s = session(req);
    if (s) sessions.delete(s.token);
    return send(res, 200, { ok: true }, { 'Set-Cookie': 'session=; Path=/; Max-Age=0' });
  }
  if (p === '/api/me') {
    const s = session(req);
    if (!s) return send(res, 401, { error: 'Not signed in' });
    const u = USERS[s.email];
    return send(res, 200, { email: s.email, name: u.name, role: u.role });
  }
  if (p === '/api/products' && m === 'GET') {
    await later(Number(url.searchParams.get('delay') ?? 600));          // a slow API on purpose
    const q = (url.searchParams.get('q') || '').toLowerCase();
    return send(res, 200, PRODUCTS.filter(x => x.name.toLowerCase().includes(q)));
  }
  const prod = p.match(/^\/api\/products\/(\d+)$/);
  if (prod && m === 'GET') {
    const x = PRODUCTS.find(y => y.id === Number(prod[1]));
    return x ? send(res, 200, x) : send(res, 404, { error: 'No such product' });
  }
  if (p.startsWith('/api/cart') || p.startsWith('/api/orders')) {
    const s = session(req);
    if (!s) return send(res, 401, { error: 'Not signed in' });
    const live = sessions.get(s.token);
    if (p === '/api/cart' && m === 'GET') return send(res, 200, cartView(live));
    if (p === '/api/cart' && m === 'POST') {
      const b = await readBody(req);
      const x = b && PRODUCTS.find(y => y.id === b.productId);
      if (!x) return send(res, 400, { error: 'Unknown product' });
      if (x.stock === 0) return send(res, 409, { error: `${x.name} is out of stock` });
      live.cart.set(x.id, (live.cart.get(x.id) || 0) + (b.qty || 1));
      return send(res, 201, cartView(live));
    }
    if (p === '/api/cart' && m === 'DELETE') { live.cart.clear(); return send(res, 200, cartView(live)); }
    if (p === '/api/orders' && m === 'POST') {
      const v = cartView(live);
      if (!v.count) return send(res, 400, { error: 'Your cart is empty' });
      await later(300);
      const order = { id: nextOrder++, email: s.email, ...v, status: 'PLACED' };
      orders.set(order.id, order);
      live.cart.clear();
      return send(res, 201, order);
    }
    const o = p.match(/^\/api\/orders\/(\d+)$/);
    if (o && m === 'GET') {
      const x = orders.get(Number(o[1]));
      return x && x.email === s.email ? send(res, 200, x) : send(res, 404, { error: 'No such order' });
    }
  }
  if (p === '/api/people' && m === 'GET') return send(res, 200, [...people.values()]);
  if (p === '/api/people' && m === 'POST') {
    const b = await readBody(req);
    if (!b || !b.name || !/^[^@\s]+@[^@\s]+$/.test(b.email || '')) return send(res, 422, { error: 'name and a valid email are required' });
    const x = { id: nextPerson++, name: b.name, email: b.email, city: b.city || null };
    people.set(x.id, x);
    return send(res, 201, x, { Location: `/api/people/${x.id}` });
  }
  const per = p.match(/^\/api\/people\/(\d+)$/);
  if (per) {
    const id = Number(per[1]), x = people.get(id);
    if (!x) return send(res, 404, { error: 'No such person' });
    if (m === 'GET') return send(res, 200, x);
    if (m === 'PUT' || m === 'PATCH') {
      const b = await readBody(req);
      const y = m === 'PUT' ? { id, name: b.name, email: b.email, city: b.city || null } : { ...x, ...b, id };
      people.set(id, y);
      return send(res, 200, y);
    }
    if (m === 'DELETE') { people.delete(id); res.writeHead(204); return res.end(); }
  }
  return send(res, 404, { error: 'Not found' });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');
  if (url.pathname.startsWith('/api/')) return api(req, res, url);
  if (url.pathname === '/download/report.csv') {
    res.writeHead(200, { 'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename="orders-report.csv"' });
    return res.end('order,total\n1001,219\n1002,1299\n');
  }
  if (url.pathname === '/secret') {
    const want = 'Basic ' + Buffer.from('admin:letmein').toString('base64');
    if (req.headers.authorization !== want) { res.writeHead(401, { 'WWW-Authenticate': 'Basic realm="Brainy Shop"' }); return res.end('Login needed'); }
    res.writeHead(200, { 'Content-Type': 'text/html' });
    return res.end('<!doctype html><title>Secret</title><h1>Staff only area</h1>');
  }
  let f = path.normalize(path.join(SITE, url.pathname === '/' ? 'index.html' : url.pathname));
  if (!f.startsWith(SITE)) return send(res, 403, 'Forbidden');
  if (!path.extname(f)) f += '.html';
  fs.readFile(f, (err, data) => {
    if (err) return send(res, 404, 'Not found');
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' });
    res.end(data);
  });
});
// A tiny WebSocket feed at /ws/stock for the network chapter. The page sends "subscribe" and gets the stock of the lamp.
function wsSend(socket, text) {
  const data = Buffer.from(text);
  const head = data.length < 126 ? Buffer.from([0x81, data.length]) : Buffer.from([0x81, 126, data.length >> 8, data.length & 255]);
  socket.write(Buffer.concat([head, data]));
}
server.on('upgrade', (req, socket) => {
  if (new URL(req.url, 'http://localhost').pathname !== '/ws/stock') return socket.destroy();
  const accept = crypto.createHash('sha1').update(req.headers['sec-websocket-key'] + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest('base64');
  socket.write(`HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: ${accept}\r\n\r\n`);
  socket.on('data', buf => {
    const op = buf[0] & 15;
    let len = buf[1] & 127, at = 2;
    if (len === 126) { len = buf.readUInt16BE(2); at = 4; }
    const mask = buf.subarray(at, at + 4), body = buf.subarray(at + 4, at + 4 + len).map((b, i) => b ^ mask[i % 4]);
    if (op === 8) { socket.end(Buffer.from([0x88, 0])); return; }
    if (op === 1 && body.toString() === 'subscribe') {
      const lamp = PRODUCTS.find(x => x.id === 3);
      wsSend(socket, JSON.stringify({ product: lamp.name, left: lamp.stock }));
    }
  });
  socket.on('error', () => {});
});
server.listen(PORT, () => console.log(`Brainy Shop on http://localhost:${PORT}`));
