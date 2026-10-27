from playwright.sync_api import APIRequestContext

from framework.data.users import User


# Fast set up through the API, so UI tests only click what they are testing
class ShopApi:
    def __init__(self, request: APIRequestContext):
        self.request = request

    def sign_in(self, user: User) -> str:
        response = self.request.post("/api/login", data={"email": user.email, "password": user.password})
        assert response.ok, f"Sign in failed for {user.email}: {response.status}"
        return response.json()["token"]

    def add_to_cart(self, token: str, product_id: int, qty: int = 1):
        response = self.request.post("/api/cart", data={"productId": product_id, "qty": qty},
                                     headers={"Authorization": f"Bearer {token}"})
        assert response.ok, f"Could not add product {product_id}: {response.status}"
