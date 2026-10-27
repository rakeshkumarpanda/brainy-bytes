// Fast set up through the API, so UI tests only click what they are testing
export class ShopApi {
  constructor(request) {
    this.request = request;
  }

  async signIn(user) {
    const response = await this.request.post('/api/login', { data: { email: user.email, password: user.password } });
    if (!response.ok()) throw new Error(`Sign in failed for ${user.email}: ${response.status()}`);
    return (await response.json()).token;
  }

  async addToCart(token, productId, qty = 1) {
    const response = await this.request.post('/api/cart', {
      data: { productId, qty },
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok()) throw new Error(`Could not add product ${productId}: ${response.status()}`);
  }
}
