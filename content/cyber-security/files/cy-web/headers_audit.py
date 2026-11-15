# 1.1 The web: sessions, origins, tokens and the OWASP Top 10
# Example "headers_audit" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Check a response for the security headers OWASP recommends
response_headers = {
    "Content-Type": "text/html; charset=utf-8",
    "Server": "Apache/2.4.49 (Unix)",
    "X-Powered-By": "PHP/7.2.1",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
}

WANTED = {
    "Strict-Transport-Security": "browsers must use HTTPS for this site",
    "Content-Security-Policy": "limits where scripts may load from, the main XSS backstop",
    "X-Content-Type-Options": "stops the browser guessing file types",
    "Referrer-Policy": "stops full URLs leaking to other sites",
    "Permissions-Policy": "turns off camera, microphone and other powerful features",
}
LEAKY = ["Server", "X-Powered-By"]

have = {k.lower(): v for k, v in response_headers.items()}
score = 0
for name, why in WANTED.items():
    ok = name.lower() in have
    score += ok
    print(f"{'present' if ok else 'MISSING':8} {name:27} {why}")
for name in LEAKY:
    if name.lower() in have:
        print(f"{'LEAKS':8} {name:27} reveals {have[name.lower()]}, which tells attackers which CVEs to try")
print(f"score {score}/{len(WANTED)}")
