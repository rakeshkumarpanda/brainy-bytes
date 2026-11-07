# 1.1 HTTP and REST: how the web talks
# Example "cookies_cache" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from http.cookies import SimpleCookie

cookie = SimpleCookie()
cookie["session"] = "abc123"
cookie["session"]["httponly"] = True        # JavaScript in the page cannot read it
cookie["session"]["secure"] = True          # only sent over HTTPS
cookie["session"]["samesite"] = "Lax"       # not sent with most requests from other sites
cookie["session"]["max-age"] = 3600         # forget it after one hour
print(cookie.output())

incoming = SimpleCookie("session=abc123; theme=dark")    # the Cookie header a browser sends back
print({name: morsel.value for name, morsel in incoming.items()})


def answer(request_headers, current_etag):
    """What a server answers for a page whose version label (ETag) is current_etag."""
    if request_headers.get("If-None-Match") == current_etag:
        return 304, "Not Modified, no body"
    return 200, f"the full page, ETag {current_etag}"


print(answer({}, '"v7"'))
print(answer({"If-None-Match": '"v7"'}, '"v7"'))
print(answer({"If-None-Match": '"v6"'}, '"v7"'))
