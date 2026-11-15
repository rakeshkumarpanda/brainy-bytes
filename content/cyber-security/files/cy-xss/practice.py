# 1.3 Cross site attacks: XSS, CSP, CSRF and clickjacking
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.


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


# ================================================================== task 1: Escape text for HTML
# Write escape_html(text) without using the html module. Replace & with &amp; first, then < with
# &lt;, > with &gt;, " with &quot; and ' with &#x27;.
# Hint: Do the ampersand first, or the & inside &lt; gets escaped again.

def escape_html(text):
    # your code here
    pass


# ================================================================== task 2: A safe link target
# Write safe_href(url) that returns the URL unchanged if its scheme (from urllib.parse.urlsplit,
# lower cased) is http or https, returns it unchanged if it is a relative link with no scheme that
# starts with "/", and returns "#" for anything else.
# Hint: Lower case the scheme: browsers accept JaVaScRiPt: too.

from urllib.parse import urlsplit

def safe_href(url):
    # your code here
    pass


# ================================================================== task 3: An HMAC CSRF token
# Write csrf_token(session_id, key) that returns the first 32 hex characters of HMAC-SHA-256(key,
# session_id), and csrf_ok(session_id, token, key) that recomputes it and compares with
# hmac.compare_digest.
# Hint: hmac.new(key, message, hashlib.sha256).hexdigest() gives 64 hex characters, keep 32.

import hashlib, hmac

def csrf_token(session_id, key):
    # your code here
    pass

def csrf_ok(session_id, token, key):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Escape text for HTML", [('escape_html("<b>")', '&lt;b&gt;'), ('escape_html("a & b")', 'a &amp; b'), ('escape_html(\'"><script>\')', '&quot;&gt;&lt;script&gt;'), ('escape_html("it\'s")', 'it&#x27;s'), ('escape_html("&lt;")', '&amp;lt;')]))
    results.append(check("Task 2: A safe link target", [('safe_href("https://example.org/a")', 'https://example.org/a'), ('safe_href("javascript:steal()")', '#'), ('safe_href("JaVaScRiPt:steal()")', '#'), ('safe_href("/profile/7")', '/profile/7'), ('safe_href("data:text/html,<script>x</script>")', '#')]))
    results.append(check("Task 3: An HMAC CSRF token", [('csrf_token("8f3a91c2", b"k")', 'dd0dcb0628bbbe2dbaf20b6f459909de'), ('csrf_token("abc", b"server-key")', '47d19a41e6e236b0198edeec77d8bd90'), ('csrf_ok("abc", "47d19a41e6e236b0198edeec77d8bd90", b"server-key")', True), ('csrf_ok("abc", "00000000000000000000000000000000", b"server-key")', False), ('csrf_ok("other", "47d19a41e6e236b0198edeec77d8bd90", b"server-key")', False)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
