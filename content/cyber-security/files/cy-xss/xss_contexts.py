# 1.3 Cross site attacks: XSS, CSP, CSRF and clickjacking
# Example "xss_contexts" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Output encoding depends on WHERE the data goes. One payload, four places in a page, four different fixes.
import html, json
from urllib.parse import quote, urlsplit

name = '"><script>steal()</script>'
link = "javascript:steal()"

print("1. HTML body")
print("   buggy: <p>Hello " + name + "</p>")
print("   safe:  <p>Hello " + html.escape(name) + "</p>")

print("2. HTML attribute (always quote it, and escape quotes too)")
print('   buggy: <input value="' + name + '">')
print('   safe:  <input value="' + html.escape(name, quote=True) + '">')

print("3. Inside a JavaScript string")
print("   buggy: <script>var user = '" + name + "';</script>")
safe_js = json.dumps(name).replace("<", "\\u003c").replace(">", "\\u003e")   # JSON string, with < > made harmless
print("   safe:  <script>var user = " + safe_js + ";</script>")

print("4. A URL in href: escaping is not enough, check the scheme")
def safe_href(url):
    return url if urlsplit(url).scheme in ("http", "https") else "#"
print('   buggy: <a href="' + html.escape(link) + '">profile</a>   (still runs when clicked)')
print('   safe:  <a href="' + html.escape(safe_href(link)) + '">profile</a>')
print('   query value: /search?q=' + quote(name, safe=""))
