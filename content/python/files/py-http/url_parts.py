# 1.1 HTTP and REST: how the web talks
# Example "url_parts" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from urllib.parse import parse_qs, quote, unquote, urlencode, urljoin, urlsplit

url = "https://api.example.com:8443/v1/books/42?fields=title,year&lang=en#reviews"
parts = urlsplit(url)
print("scheme:", parts.scheme)
print("host:", parts.hostname, "port:", parts.port)
print("path:", parts.path)
print("query:", parts.query)
print("query as a dict:", parse_qs(parts.query))
print("fragment:", parts.fragment)          # never sent to the server, the browser keeps it

print(urlencode({"q": "python & web", "page": 2}))   # safe query text from a dict
print(quote("café menu/1"), unquote("caf%C3%A9"))
print(urljoin("https://example.com/docs/intro.html", "api.html"))
print(urljoin("https://example.com/docs/intro.html", "/api.html"))
