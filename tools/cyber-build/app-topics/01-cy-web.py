# Application Security 1.1: the web, sessions, tokens and the OWASP Top 10. Checked against RFC 9110 (HTTP
# semantics), RFC 6265 and the RFC 6265bis draft (cookies), RFC 6454 (origins), the WHATWG Fetch standard (CORS),
# RFC 7519 and RFC 7518 (JWT and its algorithms), RFC 8725 (JWT best current practice), the OWASP Top 10 2021 and
# 2025, the OWASP Session Management and HTTP Headers cheat sheets, and MDN.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-web')
K = Kit()

K.code('cookie_audit', r'''
# Audit Set-Cookie headers: session cookies need Secure, HttpOnly and SameSite
def parse_set_cookie(header):
    parts = [p.strip() for p in header.split(";")]
    name, value = parts[0].split("=", 1)
    attrs = {}
    for p in parts[1:]:
        key, _, val = p.partition("=")
        attrs[key.lower()] = val or True
    return name, value, attrs

def audit(header):
    name, value, a = parse_set_cookie(header)
    problems = []
    if "secure" not in a:
        problems.append("no Secure: can be sent over plain HTTP and sniffed")
    if "httponly" not in a:
        problems.append("no HttpOnly: JavaScript (and so XSS) can read it")
    same = str(a.get("samesite", "")).lower()
    if same not in ("lax", "strict"):
        problems.append("SameSite missing or None: sent on cross site requests (CSRF risk)")
    if name.startswith("__Host-") and ("domain" in a or a.get("path") != "/"):
        problems.append("__Host- prefix needs Path=/ and no Domain")
    return name, problems

headers = [
    "session=8f3a91c2; Path=/",
    "session=8f3a91c2; Path=/; Secure; HttpOnly; SameSite=Lax",
    "__Host-sid=77ab; Path=/; Secure; HttpOnly; SameSite=Strict",
    "sid=91ce; Path=/; Secure; SameSite=None",
]
for h in headers:
    name, problems = audit(h)
    print(f"{name:11} {'OK' if not problems else str(len(problems)) + ' problem(s)'}")
    for p in problems:
        print("            -", p)
''', long=True)

K.code('same_origin', r'''
# The same origin policy: two URLs share an origin only if scheme, host and port all match
from urllib.parse import urlsplit

DEFAULT_PORT = {"http": 80, "https": 443}

def origin(url):
    u = urlsplit(url)
    return (u.scheme, u.hostname, u.port or DEFAULT_PORT[u.scheme])

def same_origin(a, b):
    return origin(a) == origin(b)

page = "https://shop.example.com/cart"
tests = [
    "https://shop.example.com/account?id=7",   # same scheme, host, port
    "http://shop.example.com/cart",            # scheme differs
    "https://api.example.com/cart",            # host differs (subdomain)
    "https://shop.example.com:8443/cart",      # port differs
    "https://shop.example.com:443/help",       # explicit default port: same
    "https://shop.example.com.evil.io/cart",   # looks similar, different host
]
print("page origin:", origin(page))
for t in tests:
    o = origin(t)
    why = "same origin" if o == origin(page) else "different " + ", ".join(
        name for name, x, y in zip(("scheme", "host", "port"), o, origin(page)) if x != y)
    print(f"{t:42} {why}")
''', long=True)

K.code('jwt_hs256', r'''
# JSON Web Tokens signed with HMAC-SHA-256, built from scratch, and the classic "alg": "none" trick
import base64, hashlib, hmac, json

def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def b64url_decode(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))

def sign(payload, key):
    header = {"alg": "HS256", "typ": "JWT"}
    h = b64url(json.dumps(header, separators=(",", ":")).encode())
    p = b64url(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(key, f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{b64url(sig)}"

def verify(token, key, now):
    h, p, s = token.split(".")
    header = json.loads(b64url_decode(h))
    if header.get("alg") != "HS256":                     # never let the token choose the algorithm
        return False, "rejected: algorithm " + str(header.get("alg"))
    good = hmac.new(key, f"{h}.{p}".encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(good, b64url_decode(s)):  # constant time comparison
        return False, "rejected: bad signature"
    payload = json.loads(b64url_decode(p))
    if payload["exp"] < now:
        return False, "rejected: expired"
    return True, payload

KEY = b"server-secret-key-32-bytes-long!"
NOW = 1_700_000_000
token = sign({"sub": "alice", "role": "user", "exp": NOW + 900}, KEY)
print("token:", token[:60] + "...")
print("valid token:      ", verify(token, KEY, NOW))

h, p, s = token.split(".")
evil_p = b64url(json.dumps({"sub": "alice", "role": "admin", "exp": NOW + 900}, separators=(",", ":")).encode())
print("edited payload:   ", verify(f"{h}.{evil_p}.{s}", KEY, NOW))

none_h = b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
print("alg none, no sig: ", verify(f"{none_h}.{evil_p}.", KEY, NOW))
print("after 15 minutes: ", verify(token, KEY, NOW + 901))
print("payload is only encoded, not encrypted:", json.loads(b64url_decode(p)))
''', long=True)

K.code('idor', r'''
# Broken access control, number 1 in the OWASP Top 10 2021: an insecure direct object reference (IDOR)
INVOICES = {
    1001: {"owner": "alice", "amount": 499},
    1002: {"owner": "bob", "amount": 12000},
    1003: {"owner": "alice", "amount": 75},
}

def get_invoice_buggy(user, invoice_id):
    # The login check passed, so the code trusts the id in the URL: /invoices/1002
    return INVOICES.get(invoice_id, "not found")

def get_invoice_fixed(user, invoice_id):
    inv = INVOICES.get(invoice_id)
    if inv is None or inv["owner"] != user:   # check ownership on the server, every time
        return "not found"                    # same answer for "missing" and "not yours", so ids leak nothing
    return inv

print("alice asks for 1001 (hers):  ", get_invoice_buggy("alice", 1001))
print("alice asks for 1002 (bob's): ", get_invoice_buggy("alice", 1002), " <- data leak")
print("fixed, alice asks for 1002:  ", get_invoice_fixed("alice", 1002))
print("fixed, alice asks for 1003:  ", get_invoice_fixed("alice", 1003))

# Walking the ids is trivial when they are sequential, so attackers loop over them
leaked = [i for i in range(1000, 1005) if isinstance(get_invoice_buggy("alice", i), dict) and INVOICES[i]["owner"] != "alice"]
print("ids alice can read that are not hers (buggy):", leaked)
leaked = [i for i in range(1000, 1005) if isinstance(get_invoice_fixed("alice", i), dict) and INVOICES[i]["owner"] != "alice"]
print("ids alice can read that are not hers (fixed):", leaked)
''', long=True)

K.code('headers_audit', r'''
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
''', long=True)

K.lesson('idea', 'How the web works, and why it is attacked so often', f'''
{talk('Tim Berners-Lee built the World Wide Web at CERN between 1989 and 1991 to share documents. A browser sends an HTTP request, such as GET /cart, and the server sends back a response with a status code, headers and a body. HTTP is stateless: each request stands alone, and the server does not remember the last one. Shopping carts and logins need memory, so in 1994 Lou Montulli at Netscape invented cookies, small values the server asks the browser to store and send back. A year later Netscape added JavaScript, and with it the same origin policy, so that a script from one site could not read pages from another. These three ideas, stateless requests, cookies and origins, explain most web attacks. Today the web is the main way people use software, so it is also the largest attack surface. Web applications take input from anyone on the internet, often talk to databases and other services, and hold valuable data. Verizon’s Data Breach Investigations Reports have found basic web application attacks behind a large share of breaches year after year. The Open Worldwide Application Security Project, OWASP, a non profit founded in 2001, publishes free guides, tools and the famous OWASP Top 10 list of the most critical web risks, first released in 2003. HTTPS, which wraps HTTP in TLS as you saw in the cryptography section, protects the traffic in transit. It does nothing about bugs in the application itself, and that is what this section is about.')}
{src('RFC 9110 HTTP Semantics (2022), RFC 6265 HTTP State Management (2011) and the RFC 6265bis draft, RFC 6454 The Web Origin Concept (2011), WHATWG Fetch Standard (CORS), RFC 6797 HSTS (2012), RFC 7519 JSON Web Token and RFC 7518 JSON Web Algorithms (2015), RFC 8725 JWT Best Current Practices (2020), OWASP Top 10 2021 and 2025, OWASP Session Management, HTTP Headers and Authorization cheat sheets, MDN Web Docs, Tim McLean, Critical vulnerabilities in JSON Web Token libraries (2015).')}
{safe('Test only your own applications or deliberately vulnerable practice apps such as OWASP Juice Shop or DVWA running on your own machine. Probing a real website without written permission is illegal even if you mean no harm.')}
{wwh('A <b>web application</b> is a program that answers HTTP requests from browsers and other clients. <b>Web security</b> keeps its data and users safe from requests that are crafted to abuse it.',
     'Web apps face everyone on the internet, handle money and personal data, and are built quickly from many parts. Most breaches of organisations touch a web app or API somewhere.',
     'Protect the session (cookies with the right flags, short lived tokens), rely on the browser’s same origin policy, check authorisation on the server for every request, validate and encode all input and output, send security headers, and keep components updated.')}
{table(['Piece', 'What it does', 'Security angle'], [
    ['HTTP request', 'Method, path, headers, optional body', 'Every part is attacker controlled input'],
    ['HTTP response', 'Status, headers, body', 'Headers can switch on browser defences'],
    ['Cookie', 'Small value the browser stores and sends back', 'Session cookies are as good as a password'],
    ['Origin', 'Scheme + host + port', 'The same origin policy isolates sites from each other'],
    ['HTTPS (TLS)', 'Encrypts and authenticates the connection', 'Stops sniffing and tampering, not app bugs'],
    ['API (JSON over HTTP)', 'Machine to machine requests', 'Same bugs as pages, often less tested']])}
''', kw=['web security', 'HTTP', 'stateless', 'cookie', 'same origin policy', 'HTTPS', 'OWASP', 'Tim Berners-Lee', 'Lou Montulli', 'web application', 'API'])

K.lesson('sessions', 'Sessions and cookies: staying logged in safely', f'''
{talk('After you log in, the server creates a session: a record of who you are, stored on the server and found by a long random session id. The id goes to the browser in a Set-Cookie header and comes back in every request. Anyone who learns the id is you, for as long as the session lasts, so protecting it is the core of web session security. In 2010 Eric Butler released Firesheep, a Firefox add on that let anyone on a café Wi-Fi click to take over other people’s Facebook and Twitter sessions, because those sites used HTTPS only for the login page and sent the session cookie in the clear afterwards. Within a few years the big sites moved to HTTPS everywhere. Three cookie flags block three different attacks. Secure tells the browser never to send the cookie over plain HTTP. HttpOnly hides the cookie from JavaScript, so a cross site scripting bug cannot simply read it. SameSite controls whether the cookie is sent on requests that start from another site: Strict never, Lax only on top level link clicks, and None always, which then requires Secure. Chrome made Lax the default in 2020. The cookie prefix __Host- adds a further guarantee that the cookie was set by this exact host over HTTPS. Good session handling also means making a new session id at login, to stop session fixation, expiring idle sessions, and deleting the session on the server at logout, not just in the browser.')}
{viz('cycookie')}
{run('cookie_audit')}
{fxs(fx('Session id strength', 'bits = log<sub>2</sub>(number of possible ids)', '32 random hex characters: 32 &times; 4 = 128 bits. OWASP asks for at least 64 bits of entropy.', key=True),
     fx('Time to guess any live session', 't = 2<sup>b</sup> / (guesses per second &times; live sessions)', '64 bits, 10<sup>9</sup> guesses per second, 10<sup>6</sup> sessions: about 5.1 hours. 128 bits: about 10<sup>10</sup> years.', key=True),
     fx('Birthday collisions', 'P(any two ids equal) &asymp; n<sup>2</sup> / 2<sup>b+1</sup>', 'n = 2<sup>32</sup> ids of 64 bits: P &asymp; 0.5. Another reason to use 128 bits.'))}
{table(['Flag', 'Stops', 'Does not stop'], [
    ['Secure', 'Sniffing the cookie on plain HTTP', 'XSS, CSRF'],
    ['HttpOnly', 'Scripts reading document.cookie', 'XSS doing actions inside the page, CSRF'],
    ['SameSite=Lax or Strict', 'Most cross site request forgery', 'Attacks from the same site, XSS'],
    ['__Host- prefix', 'A subdomain or HTTP page overwriting the cookie', 'Theft once set'],
    ['Short expiry, logout on server', 'Long use of a stolen id', 'Use within the window']])}
{scene('Firesheep, October 2010', '<p>At the ToorCon conference in San Diego, Eric Butler showed a browser add on with a sidebar listing the people around him on the same open Wi-Fi, with their names and profile photos. Double click one, and you were logged in as them. Nothing about it was new to security experts, but it made the risk obvious to everyone. It spread quickly, and within a few years Facebook, Twitter and Google had moved to full time HTTPS.</p>')}
''', kw=['session', 'session id', 'cookie flags', 'Secure', 'HttpOnly', 'SameSite', '__Host- prefix', 'session hijacking', 'session fixation', 'Firesheep', 'logout', 'entropy'])

K.lesson('sop', 'The same origin policy and CORS', f'''
{talk('Your browser is logged in to many sites at once: email, bank, work tools. Without a rule, any web page you visit could send a request to your bank, with your cookies, and read the answer. The same origin policy, introduced with JavaScript in Netscape Navigator 2.0 in 1995, is that rule. A script may only read responses from its own origin, where the origin is the scheme, host and port together. https://shop.example.com and http://shop.example.com are different origins, and so are shop.example.com and api.example.com. The policy restricts reading, not sending: a page can still submit a form or load an image from another site, which is why cross site request forgery is possible and why SameSite cookies were added. When a site really does want to share, for example a front end on one origin calling its own API on another, the server uses Cross Origin Resource Sharing, CORS. It replies with an Access-Control-Allow-Origin header naming the origins it trusts, and for unusual requests the browser first sends a preflight OPTIONS request to ask permission. CORS mistakes are common. Reflecting whatever Origin header arrives while also allowing credentials is the worst: it switches the protection off for every site on the internet.')}
{viz('cysop')}
{run('same_origin')}
{fxs(fx('Origin', 'origin = (scheme, host, port)', 'Default ports: http 80, https 443. https://a.com and https://a.com:443 are the same origin.', key=True),
     fx('Same origin test', 'same(a, b) &hArr; scheme<sub>a</sub> = scheme<sub>b</sub> &and; host<sub>a</sub> = host<sub>b</sub> &and; port<sub>a</sub> = port<sub>b</sub>', 'All three, exactly. A look alike host such as shop.example.com.evil.io is a different site.', key=True))}
{table(['CORS response header', 'Meaning', 'Safe use'], [
    ['Access-Control-Allow-Origin: https://app.example.com', 'This origin may read the response', 'List exact trusted origins'],
    ['Access-Control-Allow-Origin: *', 'Anyone may read it', 'Only for truly public data, never with credentials'],
    ['Access-Control-Allow-Credentials: true', 'Cookies may be included', 'Only with an exact origin, never a reflected one'],
    ['Access-Control-Allow-Methods / -Headers', 'Answers a preflight', 'Allow only what the API needs']])}
''', kw=['same origin policy', 'origin', 'scheme host port', 'CORS', 'Access-Control-Allow-Origin', 'preflight', 'cross origin', 'CORS misconfiguration'])

K.lesson('tokens', 'Tokens: JWTs, OAuth 2.0 and OpenID Connect', f'''
{talk('Many modern apps, especially APIs and mobile apps, use tokens instead of server side sessions. The most common format is the JSON Web Token, standardised in RFC 7519 in 2015. A JWT has three parts, each base64url encoded and joined by dots: a header naming the signing algorithm, a payload of claims such as the user id, role and expiry time, and a signature. With HS256 the server signs with HMAC-SHA-256 and a secret key, the same HMAC you met in the hashing chapter. With RS256 or ES256 it signs with an RSA or elliptic curve private key, so other services can verify with only the public key. The payload is encoded, not encrypted, so anyone holding the token can read it. Never put secrets in it. The signature only stops changes. In 2015 Tim McLean showed that several JWT libraries trusted the header’s alg field: an attacker could set it to none and drop the signature, or switch RS256 to HS256 and sign with the public key as if it were an HMAC secret. The fix, now written into RFC 8725, is that the server decides which algorithm it accepts. Tokens cannot easily be revoked before they expire, so access tokens are kept short, often 5 to 15 minutes, with a refresh token to get new ones. OAuth 2.0, from 2012, is the framework behind "Sign in with Google": it lets one service get limited access to your account at another without your password. OpenID Connect, from 2014, adds a signed ID token on top of OAuth so the app learns who you are.')}
{viz('cyjwt')}
{run('jwt_hs256')}
{fxs(fx('HS256 signature', 'sig = HMAC-SHA-256(key, base64url(header) + "." + base64url(payload))', 'Verify by recomputing and comparing in constant time with hmac.compare_digest.', key=True),
     fx('Base64url length', 'chars = &lceil;4n / 3&rceil; (no padding)', 'A 32 byte HMAC tag becomes 43 characters.', key=True),
     fx('Guessing a weak HS256 key', 't = (alphabet size)<sup>length</sup> / guesses per second', '6 lower case letters at 10<sup>8</sup> HMACs per second: 26<sup>6</sup>/10<sup>8</sup> &asymp; 3.1 s. RFC 7518 requires a key of at least 256 bits.'))}
{versus('Sessions or tokens', ['', 'Server session + cookie', 'JWT access token'], [
    ['Where state lives', 'Server database or cache', 'Inside the signed token'],
    ['Revoke at once', 'Easy: delete the session', 'Hard: wait for expiry or keep a deny list'],
    ['Scales across services', 'Needs a shared store', 'Any service with the key can verify'],
    ['Main risks', 'Stolen cookie, CSRF', 'Stolen token, alg confusion, weak keys, long lifetimes'],
    ['Good default for', 'Classic web apps', 'APIs between services, mobile apps']],
    'For a normal website, a server session in a Secure, HttpOnly, SameSite cookie is simpler and easier to revoke. Use JWTs where many services must verify identity without a shared store.')}
''', kw=['JWT', 'JSON Web Token', 'HS256', 'RS256', 'alg none', 'algorithm confusion', 'RFC 7519', 'RFC 8725', 'refresh token', 'OAuth 2.0', 'OpenID Connect', 'bearer token', 'base64url'])

K.lesson('owasp', 'The OWASP Top 10', f'''
{talk('The OWASP Top 10 is the best known list in application security. OWASP builds it from data contributed by testing companies and from a survey of practitioners, and it is used as a training syllabus, a checklist and a requirement in standards such as PCI DSS for card payments. The 2021 edition put broken access control at number one: in tested apps, some form of it showed up more than any other weakness. Broken access control means a logged in user can do or see things they should not, such as changing the invoice number in a URL to read someone else’s invoice. This kind is called an insecure direct object reference, or IDOR. In 2019 First American Financial exposed about 885 million mortgage documents this way, and in 2022 the Australian telecom Optus lost data on about 9.8 million customers through an exposed API that took sequential ids. The fix is simple to state and easy to forget: check, on the server, for every request, that this user may access this object. The 2025 edition keeps broken access control at the top, moves security misconfiguration to second, and adds two new categories: software supply chain failures, which grew out of vulnerable and outdated components, and mishandling of exceptional conditions, such as code that fails open when an error occurs. Server side request forgery, which had its own place in 2021, is now part of broken access control. Many items on the list get their own lessons in the next two chapters: injection, cross site scripting and request forgery.')}
{run('idor')}
{run('headers_audit')}
{table(['2025', 'Category', 'In 2021', 'Typical fix'], [
    ['A01', 'Broken Access Control (now includes SSRF)', 'A01, and A10 SSRF', 'Deny by default, check ownership on the server for every request'],
    ['A02', 'Security Misconfiguration', 'A05', 'Hardened defaults, no debug pages, security headers, automated checks'],
    ['A03', 'Software Supply Chain Failures', 'A06 Vulnerable and Outdated Components', 'SBOM, pinned and verified dependencies, fast updates'],
    ['A04', 'Cryptographic Failures', 'A02', 'TLS everywhere, strong algorithms, no home made crypto, proper key storage'],
    ['A05', 'Injection (including XSS)', 'A03', 'Parameterised queries, output encoding, safe APIs'],
    ['A06', 'Insecure Design', 'A04', 'Threat modelling, secure design patterns, abuse cases'],
    ['A07', 'Authentication Failures', 'A07', 'MFA, rate limits, breached password checks, safe session handling'],
    ['A08', 'Software or Data Integrity Failures', 'A08', 'Signed updates and artifacts, safe deserialisation'],
    ['A09', 'Security Logging and Alerting Failures', 'A09', 'Log security events centrally and alert on them'],
    ['A10', 'Mishandling of Exceptional Conditions', 'new', 'Fail closed, handle errors safely, no stack traces to users']])}
{attack([
    ['Change an id in the URL or API call (IDOR)', 'Server side ownership check on every object, random ids as a second layer'],
    ['Read version banners to pick exploits', 'Remove Server and X-Powered-By details, patch anyway'],
    ['Downgrade to HTTP and sniff', 'HSTS with a long max-age, Secure cookies'],
    ['Inject script into pages', 'Output encoding plus a Content Security Policy'],
    ['Frame the site to trick clicks (clickjacking)', 'Content-Security-Policy frame-ancestors, or X-Frame-Options'],
    ['Abuse debug pages and default accounts', 'Hardened configuration, removed samples, automated config checks']])}
{note('The banner in the sample, Apache/2.4.49, is the version hit by CVE-2021-41773, a path traversal flaw that was exploited within days of disclosure in October 2021. Hiding the banner does not fix the bug, but it stops advertising it.')}
''', kw=['OWASP Top 10', 'OWASP Top 10 2021', 'OWASP Top 10 2025', 'broken access control', 'IDOR', 'insecure direct object reference', 'security misconfiguration', 'supply chain failures', 'SSRF', 'security headers', 'HSTS', 'Content-Security-Policy', 'clickjacking', 'First American', 'Optus'])

K.lesson('versus', 'Web defences compared', f'''
{talk('Web defences are often confused because they sit close together. The same origin policy stops reading across sites, CORS relaxes it on purpose, SameSite stops cookies travelling with cross site requests, and a content security policy limits what scripts may run. Each answers a different question, and a secure site uses them together.')}
{versus('Which defence answers which question', ['', 'Same origin policy', 'CORS', 'SameSite cookies', 'CSP', 'HSTS'], [
    ['Question', 'Can a script read another site’s response', 'Which other origins may read mine', 'Does my cookie go on cross site requests', 'Which scripts and sources may run on my page', 'Must the browser always use HTTPS here'],
    ['Set by', 'The browser, always on', 'The server, response headers', 'The server, cookie attribute', 'The server, response header', 'The server, response header'],
    ['Stops', 'Cross site data theft', 'Nothing, it loosens the policy safely', 'Most CSRF', 'Much of XSS', 'SSL stripping and sniffing'],
    ['Common mistake', 'Thinking it stops sending', 'Reflecting any Origin with credentials', 'SameSite=None everywhere', 'Allowing unsafe-inline', 'Short max-age']],
    'Layer them: HTTPS with HSTS, careful CORS, Secure HttpOnly SameSite cookies, a strict CSP, and server side checks behind all of it.')}
''', kw=['comparison', 'SOP versus CORS', 'SameSite', 'CSP', 'HSTS'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner looks for the padlock, logs out on shared computers and uses a password manager. A college student can read raw HTTP, explain the same origin policy, audit cookies and headers, and find an IDOR in a practice app. A professional tests web apps and APIs with tools such as Burp Suite and OWASP ZAP and writes secure code reviews. Researchers find new browser level attack classes, such as cross site leaks and request smuggling, and design new browser defences.')}
{ladder(
    '<p>Check the address and the padlock, log out on shared devices, keep the browser updated, and use a password manager so that look alike sites get nothing.</p>',
    '<p>HTTP requests and responses, cookies and their flags, the same origin policy and CORS, JWT structure and verification, the OWASP Top 10, and IDOR.</p>',
    '<p>Test apps with Burp Suite or OWASP ZAP, review code for access control, design token lifetimes and refresh, set CSP and HSTS, and follow the OWASP ASVS checklist.</p>',
    '<p>HTTP request smuggling, cross site leaks (XS-Leaks), browser isolation models such as Site Isolation, formal models of web protocols such as OAuth, and automated access control testing.</p>')}
{grow('Explain what a cookie and a session are.',
      'Audit sessions, origins, tokens and headers in code.',
      'Test real apps with permission and design defences in depth.')}
''', kw=['beginner', 'expert', 'Burp Suite', 'OWASP ZAP', 'ASVS', 'request smuggling', 'XS-Leaks'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>The web</b>: stateless HTTP, cookies (1994) for memory, the same origin policy (1995) for isolation. HTTPS protects transport, not app logic.',
    '<b>Sessions</b>: a 128 bit random id in a cookie with Secure, HttpOnly and SameSite. New id at login, server side logout, idle expiry. Firesheep showed why.',
    '<b>Origins</b>: scheme + host + port must all match. SOP blocks reading, not sending. CORS lets a server share on purpose, with exact origins.',
    '<b>Tokens</b>: JWT = header.payload.signature, signed not encrypted. Fix the algorithm on the server, use strong keys, short lifetimes. OAuth 2.0 and OIDC.',
    '<b>OWASP Top 10</b>: broken access control is first in 2021 and 2025. Check ownership on every request. 2025 adds supply chain failures and exceptional conditions.',
    '<b>Headers</b>: HSTS, CSP, X-Content-Type-Options, Referrer-Policy, Permissions-Policy. Remove version banners.'],
    'Next, Application Security 1.2: injection, from SQL injection to command injection and server side request forgery.')}
{files('Three tasks: the origin of a URL, a cookie flag check, and HS256 JWT verification.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Why does the web need cookies?', ['To make pages load faster', 'HTTP is stateless, so cookies let the server recognise the same browser across requests', 'To encrypt traffic', 'To block ads'], 1, 'Stateless.', 'Each request stands alone without them.')
K.quiz('e', 'Which cookie flag stops the cookie being sent over plain HTTP?', ['HttpOnly', 'Secure', 'SameSite', 'Path'], 1, 'Secure.', 'Firesheep stole cookies sent in the clear on Wi-Fi.')
K.quiz('e', 'An origin is made of', ['Only the domain', 'Scheme, host and port', 'The full URL with path', 'The IP address'], 1, 'Three parts.', 'All three must match for the same origin.')
K.quiz('e', 'What is number one in both the OWASP Top 10 2021 and 2025?', ['Injection', 'Broken access control', 'Cryptographic failures', 'Logging failures'], 1, 'Access control.', 'For example changing an id in the URL to read another user’s data.')
K.quiz('m', 'HttpOnly on a session cookie means', ['It works only on HTTP', 'JavaScript cannot read it through document.cookie', 'It is encrypted', 'It expires at once'], 1, 'Hidden from scripts.', 'An XSS bug cannot simply copy it out.')
K.quiz('m', 'Are https://a.example.com and https://b.example.com the same origin?', ['Yes, same domain', 'No, the hosts differ', 'Yes, same scheme', 'Only on port 443'], 1, 'Host differs.', 'Subdomains are separate origins.')
K.quiz('m', 'What does the same origin policy restrict?', ['Sending any request', 'Reading responses from other origins', 'Loading images', 'Using HTTPS'], 1, 'Reading.', 'Sending is still possible, which is why CSRF exists.')
K.quiz('m', 'The payload of a JWT is', ['Encrypted with AES', 'Base64url encoded, readable by anyone holding the token', 'Hashed', 'Secret'], 1, 'Encoded only.', 'Never put secrets in it.')
K.quiz('m', 'An app shows /invoices/1001 to Alice. She changes it to 1002 and sees Bob’s invoice. This is', ['XSS', 'An IDOR, a form of broken access control', 'SQL injection', 'CSRF'], 1, 'IDOR.', 'Fix with a server side ownership check on every request.')
K.quiz('h', 'Why must a JWT verifier ignore the alg the token asks for?', ['For speed', 'Attackers can pick none, or switch RS256 to HS256 and sign with the public key', 'alg is optional', 'Only HS256 exists'], 1, 'Algorithm confusion.', 'RFC 8725 says the server fixes the accepted algorithms.')
K.quiz('h', 'A server replies with Access-Control-Allow-Origin set to whatever Origin it receives, plus Allow-Credentials: true. The effect is', ['Nothing', 'Any website can read logged in users’ responses from this API', 'Only same origin works', 'Cookies are blocked'], 1, 'Policy switched off.', 'List exact trusted origins instead.')
K.quiz('h', 'Why issue a fresh session id at login?', ['To save memory', 'To stop session fixation, where the attacker plants a known id before login', 'To log the user out', 'It is required by HTTP'], 1, 'Fixation.', 'An id chosen before login must not become an authenticated session.')
K.quiz('h', 'A JWT access token cannot easily be revoked. The usual answer is', ['Never expire it', 'Short lifetimes, 5 to 15 minutes, with refresh tokens that can be revoked', 'Store it in a URL', 'Use alg none'], 1, 'Short lived.', 'A stolen token is then useful only briefly.')
K.quiz('x', 'In the style of a Stanford CS 253 web security question: which header stops a page being framed by other sites for clickjacking?', ['Strict-Transport-Security', 'Content-Security-Policy: frame-ancestors (or X-Frame-Options)', 'Referrer-Policy', 'Set-Cookie'], 1, 'Framing control.', 'frame-ancestors lists who may embed the page.')
K.quiz('x', 'In the style of an IIT Madras secure systems exam: with 10<sup>6</sup> live sessions and an attacker making 10<sup>9</sup> guesses per second, which session id length keeps the expected time to a hit above a thousand years?', ['32 bits', '64 bits', '96 bits', 'Any length'], 2, '2<sup>b</sup>/10<sup>15</sup> seconds.', '64 bits gives about 5 hours, 96 bits about 2.5 million years. Use 128 to be safe.')

K.calc('e', 'A session id is 32 random hex characters. How many bits of entropy?', '128', '4 bits per hex digit.', ['Each hex digit has 16 values.', 'log<sub>2</sub> 16 = 4 bits.', eq('32 &times; 4 = 128 bits')], check=128)
K.calc('e', 'How many base64url characters encode 3 bytes?', '4', '6 bits per character.', ['3 bytes = 24 bits.', '24 / 6 = 4.', eq('4 characters')], check=4)
K.calc('e', 'A response has 2 of the 5 recommended security headers. What percent?', '40', 'Ratio.', ['2 / 5 = 0.4.', 'Times 100.', eq('40%')], check=40)
K.calc('m', '64 bit session ids, 10<sup>6</sup> live sessions, 10<sup>9</sup> guesses per second. Expected hours to hit any session? Round to 2 decimals.', '5.12', 'Divide by both rates.', ['2<sup>64</sup> = 1.845 &times; 10<sup>19</sup>.', 'Hits per guess are 10<sup>6</sup> times likelier, and there are 10<sup>9</sup> guesses per second: divide by 10<sup>15</sup>.', '18447 s / 3600.', eq('5.12 hours')], check=round(2 ** 64 / 1e15 / 3600, 2))
K.calc('m', 'How many base64url characters (no padding) encode a 32 byte HMAC-SHA-256 signature?', '43', '&lceil;4n/3&rceil;.', ['32 bytes = 256 bits.', '256 / 6 = 42.67.', eq('round up: 43')], check=43)
K.calc('m', 'An HS256 key is 6 lower case letters. At 10<sup>8</sup> guesses per second, how many seconds to try every key? Round to 2 decimals.', '3.09', '26<sup>6</sup>.', ['26<sup>6</sup> = 308915776.', 'Divide by 10<sup>8</sup>.', eq('3.09 s')], check=round(26 ** 6 / 1e8, 2))
K.calc('m', 'Invoice ids run from 1 to 1000. An attacker sends one request every 0.05 s. Seconds to walk them all?', '50', 'Multiply.', ['1000 requests.', '1000 &times; 0.05.', eq('50 s')], check=50)
K.calc('m', 'Of the 6 test URLs in the same origin program, how many share the page’s origin?', '2', 'Count matches.', ['The /account URL matches.', 'The explicit :443 URL matches, since 443 is the https default.', eq('2')], check=2)
K.calc('h', '2<sup>32</sup> random 64 bit ids are issued. Birthday estimate of the chance any two collide?', '0.5', 'n<sup>2</sup>/2<sup>b+1</sup>.', ['n<sup>2</sup> = 2<sup>64</sup>.', '2<sup>b+1</sup> = 2<sup>65</sup>.', eq('2<sup>64</sup>/2<sup>65</sup> = 0.5')], check=0.5)
K.calc('h', 'An HS256 key is 8 characters from a 62 symbol alphabet. At 10<sup>9</sup> guesses per second, how many days to try all? Round to 2 decimals.', '2.53', '62<sup>8</sup>.', ['62<sup>8</sup> = 2.18 &times; 10<sup>14</sup>.', 'Divide by 10<sup>9</sup>: 218340 s.', eq('218340 / 86400 = 2.53 days')], check=round(62 ** 8 / 1e9 / 86400, 2))
K.calc('h', 'An access token lives 15 minutes and is stolen at a uniformly random moment. Expected minutes it stays usable?', '7.5', 'Average of a uniform.', ['Remaining life is uniform between 0 and 15.', 'Mean = 15 / 2.', eq('7.5 minutes')], check=7.5)
K.calc('h', 'Expected years to hit any of 10<sup>6</sup> sessions with 128 bit ids at 10<sup>9</sup> guesses per second? Give 3 significant figures.', '1.08e10', '2<sup>128</sup>/10<sup>15</sup>.', ['2<sup>128</sup> = 3.40 &times; 10<sup>38</sup>.', 'Divide by 10<sup>15</sup>: 3.40 &times; 10<sup>23</sup> s.', eq('&divide; 3.156 &times; 10<sup>7</sup> s per year = 1.08 &times; 10<sup>10</sup> years')], check=float('%.3g' % (2 ** 128 / 1e21 / 3.15576e7)))
K.calc('x', 'Minimum session id bits b so that 10<sup>6</sup> sessions at 10<sup>9</sup> guesses per second take at least 10<sup>3</sup> years on average (1 year = 3.156 &times; 10<sup>7</sup> s)? Give the smallest whole b.', '85', 'Solve 2<sup>b</sup> &ge; 10<sup>15</sup> &times; 3.156 &times; 10<sup>10</sup>.', ['Need 2<sup>b</sup> &ge; 3.156 &times; 10<sup>25</sup>.', 'b &ge; log<sub>2</sub>(3.156 &times; 10<sup>25</sup>) = 84.7.', eq('b = 85')], check=85)
K.calc('x', 'A CORS rule should allow exactly 3 front end origins. An attacker controls 1 of 50 subdomains of the company. If the rule wrongly allows *.company.com, how many origins can read the API (counting the 3 front ends among the 50)?', '50', 'Wildcard covers every subdomain.', ['The wildcard matches all 50 subdomains.', 'That includes the attacker’s one.', eq('50 origins, 47 more than intended')], check=50)

K.assign('url_origin', 'e', 'The origin of a URL',
         '<p>Write <code>url_origin(url)</code> that returns the origin as a string <code>"scheme://host:port"</code>. Use <code>urllib.parse.urlsplit</code>, and fill in the default port 80 for http and 443 for https when none is given.</p>',
         '''
from urllib.parse import urlsplit

def url_origin(url):
    # your code here
    pass
''', [('url_origin("https://shop.example.com/cart")', 'https://shop.example.com:443'), ('url_origin("http://shop.example.com/x?y=1")', 'http://shop.example.com:80'), ('url_origin("https://api.example.com:8443/v1")', 'https://api.example.com:8443'), ('url_origin("https://shop.example.com:443/") == url_origin("https://shop.example.com/a")', True)],
         '''
from urllib.parse import urlsplit

def url_origin(url):
    u = urlsplit(url)
    port = u.port or {"http": 80, "https": 443}[u.scheme]
    return f"{u.scheme}://{u.hostname}:{port}"
''', 'urlsplit gives scheme, hostname and port. port is None when not written.', '<p>hostname is lower cased by urlsplit, which matches how browsers compare hosts.</p>')
K.assign('cookie_ok', 'm', 'Is this session cookie safe?',
         '<p>Write <code>cookie_ok(header)</code> for a Set-Cookie header value. Return True only if it has the Secure flag, the HttpOnly flag, and SameSite set to Lax or Strict. Attribute names and values are case insensitive.</p>',
         '''
def cookie_ok(header):
    # your code here
    pass
''', [('cookie_ok("sid=1; Path=/; Secure; HttpOnly; SameSite=Lax")', True), ('cookie_ok("sid=1; Path=/")', False), ('cookie_ok("sid=1; secure; httponly; samesite=strict")', True), ('cookie_ok("sid=1; Secure; HttpOnly; SameSite=None")', False), ('cookie_ok("sid=1; Secure; SameSite=Lax")', False)],
         '''
def cookie_ok(header):
    attrs = {}
    for part in header.split(";")[1:]:
        key, _, val = part.strip().partition("=")
        attrs[key.lower()] = val.lower()
    return "secure" in attrs and "httponly" in attrs and attrs.get("samesite") in ("lax", "strict")
''', 'Skip the first part (the name and value), then build a dictionary of lower case attributes.', '<p>A real browser also rejects SameSite=None without Secure, and treats a missing SameSite as Lax in Chrome.</p>')
K.assign('verify_hs256', 'h', 'Verify an HS256 JWT',
         '<p>Write <code>verify_hs256(token, key)</code>. Split the token into header, payload and signature. Return False unless the header’s alg is exactly "HS256" and HMAC-SHA-256(key, header + "." + payload), base64url encoded without padding, equals the signature (compare with <code>hmac.compare_digest</code>). Otherwise return the payload’s <code>sub</code> claim.</p>',
         '''
import base64, hashlib, hmac, json

def verify_hs256(token, key):
    # your code here
    pass
''', [('verify_hs256("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJib2IiLCJleHAiOjIwMDAwMDAwMDB9.zIp874XFP9-SZ04qEY7htT9HnTaRl6-uz4-tcnL8Eus", b"k3y-for-tests-0123456789abcdefgh")', 'bob'),
       ('verify_hs256("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MjAwMDAwMDAwMH0.zIp874XFP9-SZ04qEY7htT9HnTaRl6-uz4-tcnL8Eus", b"k3y-for-tests-0123456789abcdefgh")', False),
       ('verify_hs256("eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJib2IiLCJleHAiOjIwMDAwMDAwMDB9.", b"k3y-for-tests-0123456789abcdefgh")', False),
       ('verify_hs256("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJib2IiLCJleHAiOjIwMDAwMDAwMDB9.zIp874XFP9-SZ04qEY7htT9HnTaRl6-uz4-tcnL8Eus", b"wrong-key")', False)],
         '''
import base64, hashlib, hmac, json

def b64url_decode(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))

def verify_hs256(token, key):
    h, p, s = token.split(".")
    if json.loads(b64url_decode(h)).get("alg") != "HS256":
        return False
    good = hmac.new(key, f"{h}.{p}".encode(), hashlib.sha256).digest()
    mine = base64.urlsafe_b64encode(good).rstrip(b"=").decode()
    if not hmac.compare_digest(mine, s):
        return False
    return json.loads(b64url_decode(p))["sub"]
''', 'Decode the header to check alg, sign the first two parts as text, and compare base64url strings.', '<p>The second test reuses Bob’s real signature on an edited payload, and the third uses alg none with no signature. Both must fail. A full verifier also checks exp, iss and aud.</p>')

K.must('Web basics', 'HTTP is stateless. Cookies (Montulli 1994) add state. The same origin policy (Netscape 1995) isolates sites. HTTPS protects transport only.')
K.must('Sessions', 'Random id of 128 bits (at least 64). Cookie flags: Secure (no HTTP), HttpOnly (no JS), SameSite Lax or Strict (no cross site). New id at login, server logout, expiry.')
K.must('Origins', 'origin = (scheme, host, port), all must match. SOP blocks reading, not sending. CORS: exact Allow-Origin, never reflect with credentials. Preflight OPTIONS.')
K.must('JWT', 'header.payload.signature, base64url, signed not encrypted. HS256 = HMAC-SHA-256. Fix alg on the server (alg none, RS256 to HS256). Short life, refresh tokens. OAuth 2.0, OIDC.')
K.must('OWASP Top 10', 'A01 broken access control (IDOR, now with SSRF) in 2021 and 2025. 2025: misconfiguration A02, supply chain A03, crypto A04, injection A05, exceptional conditions A10.')
K.must('Headers', 'HSTS, CSP (frame-ancestors for clickjacking), X-Content-Type-Options nosniff, Referrer-Policy, Permissions-Policy. Hide Server and X-Powered-By.')

T = K.topic(
    slug='cy-web', topic='cy-web', step=(1, 'Attacking and defending the web', 'cy-a1', 'How the web works, the OWASP Top 10, and the injection, cross site and server side request attacks behind most web breaches.', 'Intermediate'),
    title='The web: sessions, origins, tokens and the OWASP Top 10', short='Web security', badge='1.1', minutes=80,
    lead='How the web keeps you logged in and keeps sites apart, and where it breaks: HTTP and cookies, session hijacking and the Secure, HttpOnly and SameSite flags, the same origin policy and CORS, JSON Web Tokens with real HS256 signing and the alg none trick, OAuth and OpenID Connect, broken access control and IDOR, and the OWASP Top 10 for 2021 and 2025.',
    desc='web security, HTTP, stateless, cookie, session, session id, session hijacking, session fixation, Secure, HttpOnly, SameSite, __Host- prefix, Firesheep, same origin policy, origin, CORS, Access-Control-Allow-Origin, preflight, JWT, JSON Web Token, HS256, RS256, alg none, algorithm confusion, RFC 8725, refresh token, OAuth 2.0, OpenID Connect, OWASP, OWASP Top 10, OWASP Top 10 2025, broken access control, IDOR, insecure direct object reference, SSRF, security misconfiguration, supply chain failures, security headers, HSTS, Content-Security-Policy, clickjacking, frame-ancestors, Burp Suite, OWASP ZAP',
    summary='HTTP and cookies, session security, same origin policy and CORS, JWTs and OAuth, broken access control and the OWASP Top 10.',
    keywords=['web security', 'cookies', 'session', 'SameSite', 'same origin policy', 'CORS', 'JWT', 'OAuth', 'OWASP Top 10', 'IDOR'],
    recap='<p>The browser keeps sites apart, cookies keep you logged in, and the server must check every request. Protect the session, respect origins, verify tokens strictly, and check access to every object.</p>',
    added='2026-11-15')
