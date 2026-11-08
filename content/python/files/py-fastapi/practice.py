# 5.2 FastAPI: fast, typed APIs with automatic docs
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: Write a Pydantic model for products
# Finish the model Product, the same kind of model FastAPI uses for a request body. name: 2 to 40
# characters after stripping spaces. price: a number greater than 0. sku: three capital letters, a
# hyphen and four digits, such as TEA-0001. stock: a whole number, 0 or more, 0 by default. tags: a
# list of text that is stripped, lower case, without empty tags and without repeats, in the order
# given. parse_product(data) returns ["ok", the data] or ["errors", the sorted names of the bad
# fields].
# Hint: Field(min_length=2, max_length=40), Field(gt=0), Field(pattern="^[A-Z]{3}-[0-9]{4}$") and
# Field(default=0, ge=0) cover the rules. A @field_validator("tags") cleans the list.

from pydantic import BaseModel, Field, ValidationError, field_validator


class Product(BaseModel):
    name: str
    price: float
    sku: str
    stock: int = 0
    tags: list[str] = []


def parse_product(data):
    try:
        product = Product(**data)
    except ValidationError as error:
        return ["errors", sorted(".".join(str(part) for part in problem["loc"]) for problem in error.errors())]
    return ["ok", product.model_dump()]


# ================================================================== task 2: Build dependency injection like Depends
# Write solve(func, request, cache), a small version of what FastAPI does with Depends. Look at the
# parameters of func with inspect.signature. A parameter whose default is Need(provider) gets the
# result of solve(provider, ...), and each provider runs only once per request, so keep results in
# cache. Any other parameter comes from the request dict, or uses its default, or raises
# KeyError("missing NAME"). run_request shows which providers ran.
# Hint: param.default is the Need object. Check isinstance(param.default, Need). Pass the same cache
# dict into every recursive call, and use inspect.Parameter.empty to see that a parameter has no
# default.

import inspect


class Need:
    """Marks a parameter that another function must provide, like FastAPI's Depends."""

    def __init__(self, provider):
        self.provider = provider


def solve(func, request, cache=None):
    """Call func. Parameters with a Need default are solved first (each provider once per request),
    the others are read from the request dict."""
    args = {}
    for name, param in inspect.signature(func).parameters.items():
        if name in request:
            args[name] = request[name]
    return func(**args)


CALLS = []


def get_db():
    CALLS.append("db")
    return {"ann": ["buy milk"], "bob": []}


def get_user(token, db=Need(get_db)):
    CALLS.append("user")
    name = token.removeprefix("secret-")
    return name if name in db else None


def list_notes(user=Need(get_user), db=Need(get_db), limit=10):
    if user is None:
        return [401, "not logged in"]
    return [200, db[user][:limit]]


def run_request(request):
    CALLS.clear()
    try:
        result = solve(list_notes, request)
    except KeyError as error:
        result = [422, str(error).strip("'")]
    return [result, list(CALLS)]


# ================================================================== task 3: Build a router that reads type hints
# Finish TypedRouter.call. Read the parameters of the handler with inspect.signature. Each value
# comes from the path, or else from the query string, and is converted to the parameter's type hint
# with convert(), which is ready. A missing value without a default gives "NAME: field required".
# Collect every error and return [422, errors], or return [200, handler(**args)]. Matching the URL
# is done for you.
# Hint: param.annotation is the type hint, or inspect.Parameter.empty when there is none (use str
# then). Catch ValueError from convert and keep going, so all errors are listed at once.

import inspect


def convert(name, text, kind):
    """Turn the text from a URL into the type of the parameter, or raise ValueError with a message."""
    if kind is int:
        if not text.lstrip("-").isdigit():
            raise ValueError(f"{name}: must be an integer")
        return int(text)
    if kind is float:
        try:
            return float(text)
        except ValueError:
            raise ValueError(f"{name}: must be a number") from None
    if kind is bool:
        if text.lower() not in ("true", "false", "1", "0"):
            raise ValueError(f"{name}: must be true or false")
        return text.lower() in ("true", "1")
    return text


class TypedRouter:
    def __init__(self):
        self.routes = []

    def get(self, pattern):
        def register(handler):
            self.routes.append((pattern.strip("/").split("/"), handler))
            return handler
        return register

    def handle(self, url):
        path, _, query = url.partition("?")
        params = dict(pair.split("=", 1) for pair in query.split("&") if "=" in pair)
        parts = path.strip("/").split("/")
        for pattern, handler in self.routes:
            if len(pattern) != len(parts):
                continue
            found = {}
            for want, got in zip(pattern, parts):
                if want.startswith("{") and want.endswith("}"):
                    found[want[1:-1]] = got
                elif want != got:
                    break
            else:
                return self.call(handler, found, params)
        return [404, "Not Found"]

    def call(self, handler, path_values, query_values):
        args = dict(query_values)
        args.update(path_values)
        return [200, handler(**args)]


router = TypedRouter()


@router.get("/items/{item_id}")
def read_item(item_id: int, details: bool = False):
    return {"item_id": item_id, "details": details}


@router.get("/prices")
def prices(min_price: float, currency: str = "EUR"):
    return {"min_price": min_price, "currency": currency}


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Write a Pydantic model for products", [('parse_product({"name": " Green tea ", "price": 3.5, "sku": "TEA-0001", "tags": ["Hot", "drink", "hot ", ""]})', ['ok', {'name': 'Green tea', 'price': 3.5, 'sku': 'TEA-0001', 'stock': 0, 'tags': ['hot', 'drink']}]), ('parse_product({"name": "Cake", "price": "5", "sku": "CAK-0042", "stock": "7"})', ['ok', {'name': 'Cake', 'price': 5.0, 'sku': 'CAK-0042', 'stock': 7, 'tags': []}]), ('parse_product({"name": "X", "price": 0, "sku": "tea-1", "stock": -1})', ['errors', ['name', 'price', 'sku', 'stock']]), ('parse_product({"price": 2})', ['errors', ['name', 'sku']]), ('parse_product({"name": "Pie", "price": "cheap", "sku": "PIE-0007"})', ['errors', ['price']])]))
    results.append(check("Task 2: Build dependency injection like Depends", [('run_request({"token": "secret-ann"})', [[200, ['buy milk']], ['db', 'user']]), ('run_request({"token": "secret-ann", "limit": 0})', [[200, []], ['db', 'user']]), ('run_request({"token": "secret-zed"})', [[401, 'not logged in'], ['db', 'user']]), ('run_request({})', [[422, 'missing token'], []])]))
    results.append(check("Task 3: Build a router that reads type hints", [('router.handle("/items/42")', [200, {'item_id': 42, 'details': False}]), ('router.handle("/items/42?details=true")', [200, {'item_id': 42, 'details': True}]), ('router.handle("/items/abc?details=maybe")', [422, ['item_id: must be an integer', 'details: must be true or false']]), ('router.handle("/prices?min_price=2.5")', [200, {'min_price': 2.5, 'currency': 'EUR'}]), ('router.handle("/prices?currency=USD")', [422, ['min_price: field required']]), ('router.handle("/prices?min_price=x")', [422, ['min_price: must be a number']]), ('router.handle("/nothing/here")', [404, 'Not Found'])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
