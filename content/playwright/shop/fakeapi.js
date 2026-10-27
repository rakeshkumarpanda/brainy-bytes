/* Brainy Shop without a server, for the playground on the Playwright pages.
   The build copies the shop pages into content/playwright/shop/ and loads this file first. It answers every
   /api/ call in the browser with the same rules as app/server.mjs, and it routes alert, confirm and prompt to the
   playground so a test can accept or dismiss them. The shop data lives in the parent page, so it survives
   navigation between the shop pages, just like a real server would. */
(() => {
  const host = (() => { try { return window.frameElement && window.frameElement.__pghost ? window.frameElement.__pghost : null; } catch (e) { return null; } })();
  const S = host ? host.state : (window.__pgLocal = window.__pgLocal || { sessions: {}, orders: {}, nextOrder: 1001, people: {}, nextPerson: 1, token: null });
  const PRODUCTS = [
    { id: 1, name: 'Gel pen', price: 20, stock: 120, category: 'Stationery' },
    { id: 2, name: 'Coffee mug', price: 199, stock: 35, category: 'Kitchen' },
    { id: 3, name: 'Desk lamp', price: 1299, stock: 8, category: 'Home' },
    { id: 4, name: 'Notebook', price: 60, stock: 0, category: 'Stationery' },
    { id: 5, name: 'Water bottle', price: 349, stock: 50, category: 'Kitchen' },
  ];
  const USERS = { 'asha@shop.example': { name: 'Asha', password: 's3cret', role: 'customer' },
    'ravi@shop.example': { name: 'Ravi', password: 'admin123', role: 'admin' } };
  const later = ms => new Promise(r => setTimeout(r, ms));
  const json = (status, body) => new Response(status === 204 ? null : JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
  const cartView = s => {
    const items = Object.entries(s.cart).map(([id, qty]) => { const p = PRODUCTS.find(x => x.id === Number(id)); return { id: p.id, name: p.name, price: p.price, qty }; });
    return { items, count: items.reduce((a, i) => a + i.qty, 0), total: items.reduce((a, i) => a + i.qty * i.price, 0) };
  };

  // localStorage of the shop pages is kept in the parent too, so a fresh context really starts empty.
  const store = S.storage = S.storage || {};
  const ls = { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; }, clear: () => { for (const k in store) delete store[k]; } };
  try { Object.defineProperty(window, 'localStorage', { value: ls, configurable: true }); } catch (e) { /* keep the real one */ }

  async function api(path, method, body, headers) {
    const url = new URL(path, 'http://localhost:4173');
    const p = url.pathname;
    const auth = headers.Authorization || headers.authorization || '';
    const tok = auth.startsWith('Bearer ') ? auth.slice(7) : null;
    const sess = tok && S.sessions[tok] ? S.sessions[tok] : null;
    if (p === '/api/health') return json(200, { status: 'ok' });
    if (p === '/api/login' && method === 'POST') {
      await later(150);
      const u = body && USERS[body.email];
      if (!u || u.password !== body.password) return json(401, { error: 'Wrong email or password' });
      const token = 't' + Math.random().toString(36).slice(2, 12);
      S.sessions[token] = { email: body.email, cart: {} };
      return json(200, { token, name: u.name, role: u.role });
    }
    if (p === '/api/logout' && method === 'POST') { if (tok) delete S.sessions[tok]; return json(200, { ok: true }); }
    if (p === '/api/me') { if (!sess) return json(401, { error: 'Not signed in' }); const u = USERS[sess.email]; return json(200, { email: sess.email, name: u.name, role: u.role }); }
    if (p === '/api/products' && method === 'GET') {
      await later(Number(url.searchParams.get('delay') ?? (host && host.productDelay !== undefined ? host.productDelay : 600)));
      const q = (url.searchParams.get('q') || '').toLowerCase();
      return json(200, PRODUCTS.filter(x => x.name.toLowerCase().includes(q)));
    }
    if (p.startsWith('/api/cart') || p.startsWith('/api/orders')) {
      if (!sess) return json(401, { error: 'Not signed in' });
      if (p === '/api/cart' && method === 'GET') return json(200, cartView(sess));
      if (p === '/api/cart' && method === 'POST') {
        const x = body && PRODUCTS.find(y => y.id === body.productId);
        if (!x) return json(400, { error: 'Unknown product' });
        if (x.stock === 0) return json(409, { error: `${x.name} is out of stock` });
        sess.cart[x.id] = (sess.cart[x.id] || 0) + (body.qty || 1);
        return json(201, cartView(sess));
      }
      if (p === '/api/cart' && method === 'DELETE') { sess.cart = {}; return json(200, cartView(sess)); }
      if (p === '/api/orders' && method === 'POST') {
        const v = cartView(sess);
        if (!v.count) return json(400, { error: 'Your cart is empty' });
        await later(300);
        const order = { id: S.nextOrder++, email: sess.email, ...v, status: 'PLACED' };
        S.orders[order.id] = order;
        sess.cart = {};
        return json(201, order);
      }
    }
    return json(404, { error: 'Not found' });
  }

  const realFetch = window.fetch.bind(window);
  window.fetch = async (input, init = {}) => {
    const path = typeof input === 'string' ? input : input.url;
    if (!/^\/api\//.test(path)) return realFetch(input, init);
    let body = null;
    try { body = init.body ? JSON.parse(init.body) : null; } catch (e) { body = null; }
    const method = (init.method || 'GET').toUpperCase();
    if (host && host.route) {
      const routed = await host.route(path, method, body);
      if (routed) return routed;
    }
    if (host) host.net(method, path);
    const res = await api(path, method, body, init.headers || {});
    if (host) host.net(method, path, res.status);
    return res;
  };

  // The /ws/stock feed, answered in the browser like the server does: "subscribe" gets the stock of the lamp.
  window.WebSocket = class {
    constructor(url) {
      this.url = String(url);
      setTimeout(() => (this.url.endsWith('/ws/stock') ? this.onopen && this.onopen({}) : this.onerror && this.onerror({})), 0);
    }
    send(text) {
      if (text !== 'subscribe') return;
      const lamp = PRODUCTS.find(x => x.id === 3);
      setTimeout(() => this.onmessage && this.onmessage({ data: JSON.stringify({ product: lamp.name, left: lamp.stock }) }), 0);
    }
    close() {}
  };

  // Dialogs go to the playground, which accepts or dismisses them like Playwright does.
  if (host) {
    window.alert = m => { host.dialog('alert', String(m), null); };
    window.confirm = m => host.dialog('confirm', String(m), null) !== false;
    window.prompt = (m, d) => host.dialog('prompt', String(m), d === undefined ? '' : String(d));
    window.open = u => { host.popup(u); return null; };
    window.addEventListener('error', e => host.pageError(e.message));
    const cl = console.log.bind(console), cw = console.warn.bind(console);
    console.log = (...a) => { host.console('log', a.join(' ')); cl(...a); };
    console.warn = (...a) => { host.console('warning', a.join(' ')); cw(...a); };
  }
})();
