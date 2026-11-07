# 1.1 HTTP and REST: how the web talks
# Example "status_codes" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from http import HTTPStatus

for code in (200, 201, 204, 301, 304, 400, 401, 403, 404, 409, 422, 429, 500, 503):
    print(code, HTTPStatus(code).phrase)

print(HTTPStatus.NOT_FOUND.value, "-", HTTPStatus.NOT_FOUND.description)


def kind(code):
    if 200 <= code < 300:
        return "success"
    if 300 <= code < 400:
        return "redirect"
    if 400 <= code < 500:
        return "client error: fix the request"
    if 500 <= code < 600:
        return "server error: maybe try again later"
    return "not an HTTP status"


for code in (204, 302, 422, 503, 99):
    print(code, kind(code))
