"""The demo shop that chapter 15 automates: an Express server, one HTML page and its script."""

SHOP_FILES = {
    'server.js': r'''
import express from "express";
import { fileURLToPath } from "node:url";

// The demo shop that every UI test on this page runs against
const app = express();
app.use(express.json());
app.use(express.static(fileURLToPath(new URL("./site", import.meta.url))));
const products = [
  { id: 1, name: "Gel pen", price: 20 },
  { id: 2, name: "Coffee mug", price: 199 },
  { id: 3, name: "Desk lamp", price: 1299 },
];
app.post("/api/login", (req, res) =>
  req.body.password === "s3cret" ? res.json({ name: req.body.email.split("@")[0] }) : res.status(401).json({ error: "Wrong email or password" }));
app.get("/api/products", (req, res) => setTimeout(() => res.json(products), 600));   // a slow API on purpose
app.post("/api/orders", (req, res) => setTimeout(() => res.status(201).json({ id: 1042, ...req.body }), 300));
export function startShop(port = 0) {
  return new Promise(resolve => { const server = app.listen(port, () => resolve(server)); });
}

if (import.meta.main) {                          // run directly: node server.js
  const server = await startShop(Number(process.env.PORT ?? 4173));
  console.log(`shop on http://localhost:${server.address().port}`);
}
''',
    'site/index.html': r'''
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Demo Shop</title></head>
<body>
  <header>
    <h1>Demo Shop</h1>
    <span id="hello"></span>
    <a href="#cart" aria-label="Cart">🛒 <span data-testid="cart-count">0</span></a>
  </header>

  <form id="login" aria-label="Sign in">
    <label>Email <input name="email" type="email" required></label>
    <label>Password <input name="password" type="password" required></label>
    <button>Sign in</button>
    <p role="alert" hidden></p>
  </form>

  <main id="shop" hidden>
    <p class="loading">Loading products…</p>
    <ul aria-label="Products"></ul>
    <section aria-label="Cart summary">
      <p>Total: <output id="total">₹0</output></p>
      <button id="checkout" disabled>Place order</button>
      <p role="status"></p>
    </section>
  </main>
  <script src="app.js"></script>
</body>
</html>
''',
    'site/app.js': r'''
const $ = s => document.querySelector(s);
const cart = [];

$("#login").addEventListener("submit", async e => {
  e.preventDefault();
  const form = e.target;
  const res = await fetch("/api/login", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: form.elements.email.value, password: form.elements.password.value }),
  });
  const body = await res.json();
  if (!res.ok) { form.querySelector("[role=alert]").textContent = body.error; form.querySelector("[role=alert]").hidden = false; return; }
  form.hidden = true;
  $("#hello").textContent = `Hello, ${body.name}`;
  $("#shop").hidden = false;
  loadProducts();
});

async function loadProducts() {
  const res = await fetch("/api/products");
  if (!res.ok) { $(".loading").textContent = "Could not load products. Try again later."; return; }
  const products = await res.json();
  $(".loading").remove();
  $("ul").innerHTML = products.map(p => `
    <li data-testid="product">
      <h2>${p.name}</h2><span class="price">₹${p.price.toLocaleString("en-IN")}</span>
      <button data-id="${p.id}">Add to cart</button>
    </li>`).join("");
  $("ul").addEventListener("click", e => {
    const b = e.target.closest("button");
    if (!b) return;
    cart.push(products.find(p => p.id === Number(b.dataset.id)));
    $("[data-testid=cart-count]").textContent = cart.length;
    $("#total").textContent = "₹" + cart.reduce((s, p) => s + p.price, 0).toLocaleString("en-IN");
    $("#checkout").disabled = false;
  });
}

$("#checkout").addEventListener("click", async () => {
  $("#checkout").disabled = true;
  const res = await fetch("/api/orders", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ items: cart.map(p => p.id) }) });
  const order = await res.json();
  $("[role=status]").textContent = `Order ${order.id} placed`;
});
''',
}
