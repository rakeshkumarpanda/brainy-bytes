# 1.3 Cross site attacks: XSS, CSP, CSRF and clickjacking
# Example "sanitiser" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Allowing some HTML (bold, italics) in comments: blocklists fail, an allow list parser works
import html, re
from html.parser import HTMLParser

def blocklist_filter(text):
    return re.sub(r"<script>", "", text, flags=re.I)              # remove the word, once

class AllowList(HTMLParser):
    ALLOWED = {"b", "i", "em", "strong"}                             # tags only, no attributes at all
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
    def handle_starttag(self, tag, attrs):
        if tag in self.ALLOWED:
            self.out.append(f"<{tag}>")
    def handle_endtag(self, tag):
        if tag in self.ALLOWED:
            self.out.append(f"</{tag}>")
    def handle_data(self, data):
        self.out.append(html.escape(data))

def allowlist_filter(text):
    p = AllowList()
    p.feed(text)
    p.close()
    return "".join(p.out)

comments = [
    "Great post, <b>thanks</b>!",
    "<script>steal()</script>",
    "<scr<script>ipt>steal()</script>",
    '<img src=x onerror="steal()">',
    '<a href="javascript:steal()">click</a>',
    "<svg onload=steal()>",
]
for c in comments:
    print(f"input:     {c}")
    print(f"blocklist: {blocklist_filter(c)}")
    print(f"allowlist: {allowlist_filter(c)}")
    print()
print("In real projects use a maintained sanitiser (for example nh3 in Python, DOMPurify in browsers).")
