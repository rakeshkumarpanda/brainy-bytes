// Shared code for every Brainy Shop page: the header, sign in state and the API helper.
const Shop = (() => {
  const token = () => localStorage.getItem('token');
  async function api(path, opts = {}) {
    const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
    if (token()) headers.Authorization = 'Bearer ' + token();
    const res = await fetch(path, { ...opts, headers, body: opts.body ? JSON.stringify(opts.body) : undefined });
    const body = res.status === 204 ? null : await res.json();
    return { ok: res.ok, status: res.status, body };
  }
  async function header() {
    const h = document.createElement('header');
    h.innerHTML = `<a class="brand" href="/">🛍️ Brainy Shop</a>
      <nav aria-label="Main"><a href="/products">Products</a><a href="/forms">Feedback</a><a href="/widgets">Widgets</a><a href="/orders">Orders</a></nav>
      <span id="hello"></span>
      <a class="cart" href="/cart" aria-label="Cart">🛒 <span data-testid="cart-count">0</span></a>
      <a id="auth" href="/login">Sign in</a>`;
    document.body.prepend(h);
    if (!token()) return;
    const me = await api('/api/me');
    if (!me.ok) { localStorage.removeItem('token'); return; }
    h.querySelector('#hello').textContent = `Hello, ${me.body.name}`;
    const a = h.querySelector('#auth');
    a.textContent = 'Sign out';
    a.href = '#';
    a.onclick = async e => { e.preventDefault(); await api('/api/logout', { method: 'POST' }); localStorage.removeItem('token'); location.href = '/login'; };
    refreshCount();
  }
  async function refreshCount() {
    if (!token()) return;
    const c = await api('/api/cart');
    if (c.ok) document.querySelector('[data-testid=cart-count]').textContent = c.body.count;
  }
  const rupees = n => '₹' + n.toLocaleString('en-IN');
  return { api, header, refreshCount, rupees, token };
})();
Shop.header();
