# Advanced 4.4: API security. Checked against the OWASP API Security Top 10 (2023 edition), RFC 6585 (HTTP 429,
# 2012) and RFC 9110 (HTTP semantics, 2022), the OpenAPI Specification 3.1, the GraphQL specification (October 2021),
# Pen Test Partners on Peloton (May 2021), KrebsOnSecurity on the USPS Informed Visibility API (November 2018),
# Optus and Australian government statements on the September 2022 breach, T-Mobile's SEC filing of 19 January 2023,
# Twitter's August 2022 notice on the 5.4 million account API dataset, Facebook's "View As" token notices (September
# and October 2018), Egor Homakov's Rails mass assignment demonstration on GitHub (March 2012), and the US Department
# of Justice complaint on the Capital One breach (July 2019).
from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq, scene
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk, attack, safe

chapter('cy-api')
K = Kit()

K.code('bola_api', r'''
# A tiny orders API, first without and then with an owner check (all data made up)
ORDERS = {
    1001: {"owner": "mallory", "item": "2 phone cases"},
    1002: {"owner": "asha", "item": "laptop", "address": "14 Lake Rd"},
    1003: {"owner": "ravi", "item": "headphones", "address": "7 Hill St"},
}

def get_order_unsafe(caller, order_id):
    # checks only that the caller is logged in
    if caller is None:
        return 401, "log in first"
    order = ORDERS.get(order_id)
    return (200, order) if order else (404, "not found")

def get_order_safe(caller, order_id):
    if caller is None:
        return 401, "log in first"
    order = ORDERS.get(order_id)
    if order is None or order["owner"] != caller:
        # answer 404 for both cases so an attacker cannot even learn which IDs exist
        return 404, "not found"
    return 200, order

for fn in (get_order_unsafe, get_order_safe):
    print(fn.__name__)
    for oid in (1001, 1002, 1003):
        code, body = fn("mallory", oid)
        print(f"  mallory asks for {oid}: {code} {body}")
''')

K.code('token_bucket', long=True, src=r'''
# Token bucket rate limiting, the same numbers as the animation: a bot sends 10 login tries a second from 10 IPs
class TokenBucket:
    def __init__(self, capacity, refill_per_sec):
        self.capacity, self.rate, self.tokens = capacity, refill_per_sec, float(capacity)

    def refill(self, seconds):
        self.tokens = min(self.capacity, self.tokens + self.rate * seconds)

    def allow(self):
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False          # the API answers 429 Too Many Requests

def attack(mode, target=40, seconds=12, ips=10):
    if mode == "per IP":
        buckets = [TokenBucket(2, 0.5) for _ in range(ips)]
    elif mode == "per account":
        buckets = [TokenBucket(5, 0.2)]
    else:
        buckets = None
    tested = refused = 0
    for t in range(1, seconds + 1):
        if buckets and t > 1:
            for b in buckets:
                b.refill(1)
        for ip in range(ips):
            b = None if buckets is None else buckets[ip if mode == "per IP" else 0]
            if b is None or b.allow():
                tested += 1
                if tested == target:
                    return f"{mode:12s} broken in at second {t}, {refused} tries refused"
            else:
                refused += 1
    return f"{mode:12s} still out after {seconds} s: {tested} tested, {refused} refused"

for mode in ("no limit", "per IP", "per account"):
    print(attack(mode))
''')

K.code('mass_assign', r'''
# Mass assignment and excessive data exposure, and the two lists that fix them
user = {"id": 7, "name": "Ravee", "email": "r@old.example", "role": "user", "credits": 10,
        "password_hash": "$2b$12$QeX0..."}
body = {"name": "Ravi", "email": "ravi@example.com", "role": "admin", "credits": 9999}

def update_unsafe(user, body):
    user = dict(user)
    user.update(body)                     # trusts every field the client sent
    return user, user                     # and returns the whole record

WRITABLE = {"name", "email"}              # what a user may change
READABLE = {"id", "name", "email"}        # what a user may see

def update_safe(user, body):
    unknown = set(body) - WRITABLE
    user = dict(user)
    user.update({k: v for k, v in body.items() if k in WRITABLE})
    reply = {k: user[k] for k in READABLE}
    return user, reply, sorted(unknown)

stored, reply = update_unsafe(user, body)
print("unsafe stored:", {k: stored[k] for k in ("role", "credits")})
print("unsafe reply keys:", sorted(reply))
stored, reply, dropped = update_safe(user, body)
print("safe stored:  ", {k: stored[k] for k in ("role", "credits")})
print("safe reply:   ", reply)
print("ignored fields (log them, they are a sign of probing):", dropped)
''')

K.code('ssrf_guard', r'''
# A webhook API fetches a URL that the customer supplies. Refuse internal addresses (no network is used here).
import ipaddress
from urllib.parse import urlsplit

def parse_host(host):
    # also catch numeric forms such as 2852039166, which is 169.254.169.254 written as one number
    try:
        return ipaddress.ip_address(int(host)) if host.isdigit() else ipaddress.ip_address(host)
    except ValueError:
        return None

def check_webhook(url):
    parts = urlsplit(url)
    if parts.scheme != "https":
        return "refuse: https only"
    ip = parse_host(parts.hostname or "")
    if ip is None:
        return "resolve the name, then run this same check on every address it returns"
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
        return f"refuse: {ip} is an internal address"
    return "allow"

for url in ["https://hooks.example.com/in", "https://169.254.169.254/latest/meta-data/",
            "https://2852039166/", "https://127.0.0.1:8080/admin", "https://10.0.3.7/",
            "http://hooks.example.com/in", "https://93.184.215.14/hook"]:
    print(f"{url:45s} {check_webhook(url)}")
''')

K.code('api_inventory', r'''
# Find shadow and zombie APIs: compare what the documentation says with what the gateway logs show
documented = {("GET", "/v2/orders/{id}"), ("POST", "/v2/orders"), ("GET", "/v2/users/me"),
              ("PATCH", "/v2/users/me")}
retired = {("GET", "/v1/orders/{id}")}          # old version, meant to be switched off

log = ["GET /v2/orders/1001", "GET /v1/orders/1002", "GET /v1/orders/1003", "POST /v2/orders",
       "GET /v2/users/me", "GET /internal/debug/config", "GET /v2/orders/1004", "PATCH /v2/users/me"]

def to_route(line):
    method, path = line.split()
    parts = ["{id}" if p.isdigit() else p for p in path.split("/")]
    return method, "/".join(parts)

seen = {}
for line in log:
    r = to_route(line)
    seen[r] = seen.get(r, 0) + 1

for route, n in sorted(seen.items()):
    kind = "documented" if route in documented else "ZOMBIE (retired but still answering)" if route in retired else "SHADOW (nobody documented it)"
    print(f"{route[0]:6s} {route[1]:28s} {n} call{'s' if n != 1 else ' '}  {kind}")
''')

# ------------------------------------------------------------------------------------------------ lessons
K.lesson('why', 'APIs: the doors behind every app', f'''
{talk('When you open a shopping app, the screen you see is only the front. Every tap sends a request to an API, an application programming interface, which is a set of web addresses that accept data and send data back, usually as JSON over HTTPS. Phone apps, web pages, smart devices and other companies’ servers all talk to the same APIs. That makes APIs the place where attackers look first. They do not need the app at all. They can send requests straight to the API with a script, change any field, and try any ID. In this chapter you will see the bugs that keep appearing in APIs, from changing one number in a URL to sneaking an extra field into a request, and the simple rules that stop them.')}
{wwh('APIs are web endpoints that programs call to read and change data. Most modern apps are a thin screen on top of them.',
     'Every check that lives only in the app’s screen can be skipped, because attackers talk to the API directly. API flaws have exposed millions of records at Optus, T-Mobile, USPS and Peloton.',
     'Check who the caller is and what they may touch on every request, accept only the fields you expect, return only the fields they may see, limit how fast and how much they can ask for, and keep a list of every API you run.')}
{table(['OWASP API Security Top 10 (2023)', 'In plain words'], [
    ['API1 Broken object level authorisation', 'Change an ID, get someone else’s data'],
    ['API2 Broken authentication', 'Weak logins, leaked keys, tokens not checked'],
    ['API3 Broken object property level authorisation', 'Set fields you should not set, see fields you should not see'],
    ['API4 Unrestricted resource consumption', 'No limits on rate, size or cost'],
    ['API5 Broken function level authorisation', 'A normal user calls an admin function'],
    ['API6 Unrestricted access to sensitive business flows', 'Bots buy all the tickets or create fake accounts'],
    ['API7 Server side request forgery', 'The API fetches a URL you choose, including internal ones'],
    ['API8 Security misconfiguration', 'Open CORS, verbose errors, missing TLS'],
    ['API9 Improper inventory management', 'Old or forgotten API versions still running'],
    ['API10 Unsafe consumption of APIs', 'Trusting data from a partner API without checking it']])}
{scene('Around you', '<p>Open your browser’s developer tools (F12), choose the Network tab, and reload a site you use. Every row marked fetch or XHR is an API call. Click one and look at the Response tab. That raw JSON is exactly what an attacker sees, including any field the page chooses not to show you.</p>')}
''', kw=['API', 'REST', 'JSON', 'HTTP methods', 'endpoint', 'OWASP API Security Top 10', 'API security', 'developer tools', 'client side checks'])

K.lesson('bola', 'Broken object level authorisation: change one number', f'''
{talk('The most common serious API bug is also the simplest. An API takes an ID in the URL, such as orders slash 1001, checks that the caller is logged in, and returns the order. It never checks whether that order belongs to the caller. So a logged in customer changes 1001 to 1002 and reads a stranger’s order. OWASP calls this broken object level authorisation, BOLA, and older guides call it an insecure direct object reference, IDOR. It is number one on the API list because it is everywhere and needs no skill to exploit. A close cousin is broken function level authorisation, where a normal user calls an admin function, for example by changing GET to DELETE, or by guessing a path like slash admin slash users. In the animation below, try the three designs. Watch how random looking IDs only slow the attacker down, while a one line owner check stops her.')}
{viz('cybola')}
{run('bola_api')}
{table(['Case', 'Year', 'What happened'], [
    ['USPS Informed Visibility', '2018', 'Any logged in user could query other users’ account details, about 60 million users exposed'],
    ['Peloton', '2021', 'API returned private profile data for any user ID, found by Pen Test Partners'],
    ['Optus', '2022', 'Reported to be an API with no login and sequential customer IDs, about 10 million customers affected']])}
{steps('Stopping BOLA and BFLA', ['On every endpoint that takes an ID, load the object, then check that its owner (or the caller’s role) allows this action.',
       'Put the check in one shared place, such as a policy function or middleware, so new endpoints cannot forget it.',
       'Deny by default: admin functions need an explicit role check, not a hidden URL.',
       'Return 404 rather than 403 if you do not want to confirm that an ID exists.',
       'Write tests with two users: user A must never read, change or delete user B’s objects.'])}
{note('Random IDs (UUIDs) are good practice because they stop counting through records, but they are not access control. IDs leak in shared links, logs, emails and other API responses.')}
''', kw=['BOLA', 'IDOR', 'insecure direct object reference', 'object level authorisation', 'BFLA', 'function level authorisation', 'owner check', 'UUID', 'Optus', 'Peloton', 'USPS', 'two user test'])

K.lesson('auth', 'Broken authentication: keys, tokens and logins', f'''
{talk('Before an API can decide what you may do, it has to know who you are. Most APIs use one of three things. An API key is a long secret string that identifies a program, not a person, and it is often leaked by being pasted into a mobile app or pushed to a public code repository. A session cookie works for browsers. A bearer token, often a JSON web token, is sent in the Authorization header and proves who the user is until it expires. The Authentication chapter (Network and Systems 2.1) shows how JWTs are built and the classic mistakes, such as accepting alg none. For APIs the common failures are simpler: endpoints that forget to require a token at all, tokens that never expire, tokens that are not checked for audience, and login or password reset endpoints with no rate limit, which invite password guessing. In 2018 a bug in Facebook’s View As feature let attackers steal access tokens for about 30 million accounts, which shows that a token is as good as a password.')}
{table(['Credential', 'Identifies', 'Typical mistake', 'Better practice'], [
    ['API key', 'A program or customer account', 'Hard coded in an app or committed to Git', 'Keep keys on servers, scope them, rotate them, turn on secret scanning'],
    ['Session cookie', 'A browser session', 'Missing Secure, HttpOnly or SameSite flags', 'Set all three, expire idle sessions'],
    ['Bearer token (JWT or opaque)', 'A user, for a short time', 'Never expires, signature or audience not checked', 'Short lifetime, verify signature, issuer, audience and expiry'],
    ['OAuth access token', 'A user’s consent for one app', 'Scopes too wide', 'Ask for the smallest scopes, use PKCE in apps'],
    ['Mutual TLS', 'A server, by certificate', 'Certificates never rotated', 'Automate issuing and rotation']])}
{steps('An authentication checklist for an API', ['Require authentication on every endpoint by default, and mark the few public ones explicitly.',
       'Verify tokens fully: signature, expiry, issuer and audience.',
       'Keep tokens short lived and support revoking them.',
       'Rate limit login, password reset and one time code endpoints per account, not only per IP.',
       'Never put long lived secrets in mobile apps or front end code.'])}
''', kw=['broken authentication', 'API key', 'bearer token', 'JWT', 'session cookie', 'OAuth scopes', 'PKCE', 'mutual TLS', 'secret scanning', 'token expiry', 'Facebook View As', 'password reset'])

K.lesson('limits', 'Rate limits and resource consumption', f'''
{talk('An API that answers as fast as anyone can ask will be abused. A bot with a leaked list of passwords can test thousands of logins, a scraper can copy your whole catalogue, and a single huge request can tie up a database. OWASP calls this unrestricted resource consumption. The usual fix is a rate limit, and a common way to build one is a token bucket. Each client has a bucket that holds a few tokens and refills slowly. Each request spends a token, and an empty bucket means the API answers 429 Too Many Requests, often with a Retry-After header. The key question is what you count. In the animation, a bot spreads its guesses over ten IP addresses. A per IP limit gives it ten buckets and it still gets in. A per account limit puts every guess into one small bucket, and the attack crawls. Limits are not only about speed. Cap page sizes, upload sizes and the cost of each query, especially for GraphQL, where one request can ask for deeply nested data or bundle hundreds of login attempts using aliases.')}
{viz('cyratelimit')}
{run('token_bucket')}
{fxs(fx('Token bucket', 'tokens = min(capacity, tokens + rate &times; elapsed time), then spend 1 per request', 'Allows short bursts up to the capacity, then a steady rate.', key=True),
     fx('Requests allowed in time T', 'allowed &le; capacity + rate &times; T', 'Bucket 5, rate 0.2 per second, T = 12 s: at most 5 + 2.4 = 7 requests.', key=True),
     fx('Time to try a list', 'time &asymp; (list size &minus; capacity) / rate', '1,000 passwords at 0.2 per second: about 83 minutes.'))}
{table(['What to limit', 'Example', 'Why'], [
    ['Requests per account', '5 login tries, then 1 every 5 s', 'Stops guessing spread over many IPs'],
    ['Requests per IP and per API key', '100 a minute', 'Stops simple floods and scrapers'],
    ['Page size', 'limit at most 100', 'Stops "give me all 10 million users"'],
    ['Payload size', 'Body at most 1 MB', 'Stops memory exhaustion'],
    ['GraphQL depth and cost', 'Depth at most 7, cost budget per request', 'Stops nested queries and alias batching'],
    ['Paid actions', 'SMS or email sends per hour', 'Stops attackers running up your bill']])}
''', kw=['rate limiting', 'token bucket', 'leaky bucket', '429 Too Many Requests', 'Retry-After', 'credential stuffing', 'per account limit', 'resource consumption', 'pagination', 'GraphQL', 'query depth', 'alias batching', 'scraping'])

K.lesson('props', 'Mass assignment and excessive data exposure', f'''
{talk('Two more bugs come from trusting the shape of the data. The first is mass assignment. Frameworks make it easy to write user dot update with the whole request body, which copies every field the client sends into the database record. If the record has fields like role, is admin or credits, an attacker just adds them to the request. In March 2012 a developer used exactly this bug on GitHub, which is built with Ruby on Rails, to add a key to the Rails project there, to prove the point. The second is excessive data exposure. The API returns the whole database record and leaves it to the app to show only some fields on screen. Anyone who reads the raw response sees everything, such as password hashes, home addresses or internal flags. In 2022 Twitter confirmed that an API bug had let attackers match email addresses and phone numbers to about 5.4 million accounts. OWASP now groups both as broken object property level authorisation. In the animation, Ravi adds two fields by hand. Try it with and without an allow list.')}
{viz('cymassassign')}
{run('mass_assign')}
{versus('Trusting the body or using lists', ['', 'Copy everything', 'Allow lists and schemas'], [
    ['Incoming fields', 'Any field is saved', 'Only listed fields are saved, others ignored and logged'],
    ['Outgoing fields', 'Whole record returned', 'A response schema picks safe fields'],
    ['New database column', 'Becomes writable and visible by accident', 'Stays private until someone adds it on purpose'],
    ['Tools', 'user.update(request.body)', 'Data transfer objects, OpenAPI schemas, serializers with explicit fields']],
    'Decide on purpose which fields each role may write and read, and enforce it in code on the server, never in the app’s screen.')}
''', kw=['mass assignment', 'auto binding', 'excessive data exposure', 'object property level authorisation', 'allow list', 'response schema', 'DTO', 'serializer', 'Rails 2012', 'Twitter 2022', 'OpenAPI'])

K.lesson('consume', 'Webhooks, SSRF and trusting other APIs', f'''
{talk('Many APIs also call out to the world. A payment service sends webhooks to a URL the customer types in. A document tool fetches a picture from a link. If the API fetches whatever URL it is given, an attacker can point it at addresses that only the server can reach, such as an admin page on localhost or the cloud metadata service at 169 dot 254 dot 169 dot 254, which hands out temporary cloud keys. This is server side request forgery, SSRF. In 2019 an attacker used SSRF through a misconfigured firewall to take cloud keys from Capital One and copy data on about 106 million people. Application Security 1.2 covers SSRF in depth. The other half of this lesson is the reverse problem: your API consuming someone else’s. Data from a partner API is still untrusted input. Validate it, set timeouts, do not follow redirects blindly, and do not let a partner’s outage or a poisoned response break your own service.')}
{run('ssrf_guard')}
{steps('Safe outbound calls', ['Allow only https and, where possible, a fixed list of destination hosts.',
       'Resolve the host name and check every address it returns against private, loopback and link local ranges.',
       'Connect to the address you checked, so a second DNS answer cannot switch it (DNS rebinding).',
       'Turn off automatic redirects, or check each new location again.',
       'Use IMDSv2 in the cloud, and run the fetcher with no access to internal networks.',
       'Treat partner API responses as untrusted: validate their schema, set timeouts and size limits.'])}
''', kw=['SSRF', 'server side request forgery', 'webhook', 'metadata service', '169.254.169.254', 'IMDSv2', 'Capital One 2019', 'DNS rebinding', 'redirects', 'unsafe consumption of APIs', 'third party API'])

K.lesson('inventory', 'Misconfiguration, forgotten APIs and business flows', f'''
{talk('Some API failures are not bugs in one endpoint but in how the whole set is run. Improper inventory management means nobody has a full list of the APIs in use. Old versions, like v1 left running after v2 launched, keep answering without the newer checks. Teams publish internal or test endpoints that no one documented. These are called zombie and shadow APIs, and attackers find them by guessing paths and reading mobile apps. Security misconfiguration covers things like a CORS policy that lets any website call the API with the user’s cookies, error messages that print stack traces and database names, and debug endpoints left switched on. Finally, unrestricted access to sensitive business flows is when every request is valid on its own but the pattern is harmful, such as bots buying every concert ticket in seconds or creating thousands of fake accounts to claim sign up bonuses. In early 2023 T-Mobile reported that an attacker had pulled data on about 37 million accounts through one API over about six weeks before it was noticed.')}
{run('api_inventory')}
{table(['Problem', 'Sign', 'Fix'], [
    ['Zombie API', 'Old version still answering', 'Switch it off on a set date, block it at the gateway'],
    ['Shadow API', 'Calls to paths not in the documentation', 'Generate an inventory from gateway logs and OpenAPI files'],
    ['Open CORS', 'Access-Control-Allow-Origin copies any origin with credentials allowed', 'Allow a fixed list of origins'],
    ['Verbose errors', 'Stack traces in responses', 'Generic errors to clients, details in server logs'],
    ['Business flow abuse', 'Thousands of sign ups or purchases from fresh accounts', 'Bot detection, per user limits, delays, human checks'],
    ['Slow detection', 'Abuse unnoticed for weeks', 'Alerts on unusual volume per token and per endpoint']])}
''', kw=['improper inventory management', 'zombie API', 'shadow API', 'API versioning', 'CORS', 'security misconfiguration', 'verbose errors', 'business flow', 'bots', 'scalping', 'T-Mobile 2023', 'API gateway'])

K.lesson('defend', 'Building and testing secure APIs', f'''
{talk('Putting it together, a secure API is designed, not patched. Start with a written contract, usually an OpenAPI file, that lists every endpoint, who may call it, and the exact shape of each request and response. An API gateway in front of the services can then do the common jobs in one place: check tokens, apply rate limits, reject requests that do not match the schema, and log every call. Inside each service, authorisation still has to be checked against the actual object, because only the service knows who owns it. Test with two or more users in your automated tests, so that user A trying to read user B’s data fails every build that breaks it. Run API scanners and fuzzers against a test copy, and watch the production logs for unusual patterns per token. Bug bounty programmes pay outside researchers to find what you missed, and many of the cases in this chapter were reported that way.')}
{steps('A secure API life cycle', ['Design: write the OpenAPI contract with authentication, roles and schemas for each endpoint.',
       'Build: one shared authorisation layer, allow lists for input, response schemas for output.',
       'Protect: gateway with token checks, rate limits per account and per key, size limits.',
       'Test: two user authorisation tests, schema tests and fuzzing in CI.',
       'Run: inventory from logs, alerts on unusual volume, switch off old versions on schedule.',
       'Learn: bug bounty or disclosure programme, and fix every class of bug, not just the one report.'])}
{safe('Only test APIs you own or are explicitly allowed to test, for example through a bug bounty programme’s published scope. Changing IDs to read other people’s data on a live service is unauthorised access even when the API makes it easy. Practise on deliberately vulnerable labs such as OWASP crAPI or OWASP Juice Shop running on your own computer.')}
''', kw=['OpenAPI', 'API gateway', 'schema validation', 'authorisation tests', 'fuzzing', 'API scanner', 'CI', 'bug bounty', 'crAPI', 'Juice Shop', 'monitoring', 'secure design'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner understands that every app talks to an API and that the app’s screen is not a security boundary. A student can explain the OWASP API Top 10 and fix BOLA and mass assignment in code. A professional designs gateways, rate limits and authorisation layers and tests them in CI. Experts find new classes of API flaws, build policy engines and run API security for large companies.')}
{ladder(
    '<p>Apps are screens on top of APIs. Anyone can call an API directly, so the server must check who you are and what you may see on every request.</p>',
    '<p>OWASP API Top 10, BOLA and BFLA with owner checks, token buckets and 429, mass assignment and response schemas, SSRF guards for webhooks, zombie and shadow APIs.</p>',
    '<p>Design OpenAPI contracts with security, run gateways and per account limits, write two user authorisation tests, monitor per token behaviour and run disclosure programmes.</p>',
    '<p>Build policy engines for fine grained authorisation, research GraphQL and gRPC attack classes, detect business flow abuse with behaviour models, and lead API security programmes.</p>')}
{grow('Spot API calls in your browser and know what they reveal.',
      'Fix the common API bugs in your own code.',
      'Design, test and monitor secure APIs for a team.')}
''', kw=['beginner', 'expert', 'API security career'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>APIs</b>: the real doors behind apps. Client side checks can always be skipped. OWASP API Security Top 10, 2023.',
    '<b>BOLA and BFLA</b>: check the object’s owner and the caller’s role on every request. Random IDs help but are not access control. USPS 2018, Peloton 2021, Optus 2022.',
    '<b>Authentication</b>: keys stay on servers, tokens short lived and fully verified, login and reset rate limited per account.',
    '<b>Limits</b>: token bucket, allowed &le; capacity + rate &times; T, 429 with Retry-After. Limit per account, page size, payload size and GraphQL cost.',
    '<b>Properties</b>: allow lists in, response schemas out. Mass assignment (Rails 2012), excessive data exposure (Twitter 2022).',
    '<b>Outbound</b>: SSRF guards on webhooks, block internal ranges, IMDSv2. Capital One 2019. Treat partner APIs as untrusted.',
    '<b>Operations</b>: inventory from logs, switch off zombie versions, strict CORS, generic errors, watch per token volume. T-Mobile 2023.'],
    'Advanced 5.1: certification revision, which ties every chapter of this subject to the exams you may sit.')}
{files('Three tasks: an owner check for orders, a token bucket limiter, and an allow list for writable fields.')}
''', kw=['summary', 'recap'])

# ------------------------------------------------------------------------------------------------ quiz
K.quiz('e', 'Why can an attacker skip checks that exist only in an app’s screen?', ['They cannot', 'They can send requests straight to the API without the app', 'Apps are encrypted', 'Screens run on the server'], 1, 'Talk to the door directly.', 'Every check must run on the server.')
K.quiz('e', 'A logged in user changes /orders/1001 to /orders/1002 and sees a stranger’s order. What is this bug called?', ['XSS', 'Broken object level authorisation (BOLA)', 'SQL injection', 'Phishing'], 1, 'API1.', 'The server checked the login but not the owner.')
K.quiz('e', 'Which HTTP status code means Too Many Requests?', ['200', '404', '429', '500'], 2, 'RFC 6585.', '429, often with a Retry-After header.')
K.quiz('e', 'Where should an API key for a paid service never be stored?', ['On the server', 'Inside a mobile app or public code', 'In a secrets manager', 'In an environment variable on the server'], 1, 'Anyone can unpack an app.', 'Keys in apps and public repositories are found quickly.')
K.quiz('m', 'Why are random UUIDs not enough to stop BOLA?', ['They are too long', 'IDs leak through links, logs and other responses, and the owner is still not checked', 'They are guessable', 'They break databases'], 1, 'Hiding is not checking.', 'Access control means checking ownership.')
K.quiz('m', 'A normal user sends DELETE /api/users/42 and it works. Which OWASP API risk is this?', ['API1 BOLA', 'API5 Broken function level authorisation', 'API4 Resource consumption', 'API9 Inventory'], 1, 'An admin function.', 'The role was not checked for the action.')
K.quiz('m', 'What is mass assignment?', ['Sending many requests', 'Copying every field from the request body into a record, including ones the user should not set', 'Assigning IDs in bulk', 'A kind of DDoS'], 1, 'user.update(body).', 'Use an allow list of writable fields.')
K.quiz('m', 'Why does a per IP rate limit fail against credential stuffing?', ['IPs are slow', 'Bots spread guesses over many IP addresses', 'It is too strict', 'It blocks real users only'], 1, 'Many buckets.', 'Count per account as well.')
K.quiz('m', 'What is a zombie API?', ['An API with no users', 'An old version that was meant to be retired but still answers', 'A fast API', 'A GraphQL API'], 1, 'v1 still running.', 'It often lacks newer checks.')
K.quiz('h', 'Why might an API return 404 instead of 403 for another user’s order?', ['404 is faster', 'So an attacker cannot learn which IDs exist', 'Browsers require it', '403 is deprecated'], 1, 'Do not confirm existence.', 'Both refuse, but 404 reveals less.')
K.quiz('h', 'A webhook API is asked to fetch https://2852039166/. What is the risk?', ['None, it is a number', 'It is 169.254.169.254 written as one integer, the cloud metadata service', 'It is a public site', 'It is a phone number'], 1, 'Convert to dotted form.', 'Guards must normalise addresses before checking.')
K.quiz('h', 'How can GraphQL aliases defeat a simple rate limit?', ['They cannot', 'One HTTP request can carry hundreds of login mutations under different aliases', 'They encrypt requests', 'They hide the IP'], 1, 'Many operations, one request.', 'Limit by operation cost, not only by request count.')
K.quiz('h', 'Which CORS setting is dangerous for an API that uses cookies?', ['A fixed list of origins', 'Copying any Origin header into Access-Control-Allow-Origin with credentials allowed', 'No CORS headers', 'Allowing GET only'], 1, 'Any site, with your cookies.', 'Then any website can read the user’s data.')
K.quiz('x', 'In the style of a CMU 18-631 question: a token bucket has capacity 5 and refills 0.2 tokens per second. Maximum requests accepted in 12 seconds from a full start?', ['5', '7', '12', '17'], 1, 'Capacity + rate &times; T.', '5 + 0.2 &times; 12 = 7.4, so 7 whole requests.')
K.quiz('x', 'In the style of an IIT Bombay web security exam: which pair of controls closes OWASP API3?', ['TLS and HSTS', 'An allow list for writable fields and a response schema for readable fields', 'A WAF and a CDN', 'Rate limits and CAPTCHAs'], 1, 'Properties in and out.', 'API3 covers both mass assignment and excessive exposure.')

# ------------------------------------------------------------------------------------------------ problems
K.calc('e', 'A bot tries 10 passwords a second with no limit. How many seconds to reach password 40?', '4', '40 / 10.', ['10 tries every second.', '40 / 10.', eq('4 s')], check=40 / 10)
K.calc('e', 'Bucket capacity 5, refill 0.2 per second. Most requests allowed in 12 s, as a decimal bound?', '7.4', 'capacity + rate &times; T.', ['0.2 &times; 12 = 2.4.', '5 + 2.4.', eq('7.4, so 7 whole requests')], check=5 + 0.2 * 12)
K.calc('e', 'Order IDs run from 1001 to 1500. How many requests to try every one?', '500', 'Count the range.', ['1500 &minus; 1001 + 1.', 'Inclusive count.', eq('500')], check=1500 - 1001 + 1)
K.calc('m', 'At 0.2 allowed tries per second after a bucket of 5, how many minutes to test 1,000 passwords? Round to 1 decimal.', '82.9', '(1000 &minus; 5) / 0.2 seconds.', ['995 / 0.2 = 4,975 s.', '/ 60.', eq('&asymp; 82.9 minutes')], check=round((1000 - 5) / 0.2 / 60, 1))
K.calc('m', 'A per IP bucket starts with 2 tokens and gains 0.5 at each of seconds 2 to 12. Total tokens one IP receives?', '7.5', '2 + 0.5 &times; 11.', ['11 refills of 0.5 = 5.5.', '2 + 5.5.', eq('7.5, so 7 whole tries per IP and 70 across 10 IPs')], check=2 + 0.5 * 11)
K.calc('m', 'A UUID version 4 has 122 random bits. Roughly how many guesses on average to hit one specific ID? Give the power of 2.', '121', 'Half the space.', ['Space = 2<sup>122</sup>.', 'Average = half = 2<sup>121</sup>.', eq('2<sup>121</sup>')], check=121)
K.calc('m', '169.254.169.254 as one 32 bit integer?', '2852039166', '169 &times; 2<sup>24</sup> + 254 &times; 2<sup>16</sup> + 169 &times; 2<sup>8</sup> + 254.', ['169 &times; 16,777,216 = 2,835,349,504.', '+ 254 &times; 65,536 + 169 &times; 256 + 254.', eq('2,852,039,166')], check=169 * 2**24 + 254 * 2**16 + 169 * 2**8 + 254)
K.calc('h', 'T-Mobile 2023: about 37 million accounts over about 42 days. Average accounts pulled per hour? Round to the nearest thousand.', '37000', '37,000,000 / (42 &times; 24).', ['42 &times; 24 = 1,008 hours.', '37,000,000 / 1,008 &asymp; 36,706.', eq('&asymp; 37,000 per hour')], check=round(37e6 / (42 * 24), -3))
K.calc('h', 'A GraphQL query nests friends 5 levels deep and each user has 20 friends. How many user objects at the deepest level?', '3200000', '20<sup>5</sup>.', ['20 &times; 20 = 400, 8,000, 160,000.', '&times; 20.', eq('3,200,000')], check=20 ** 5)
K.calc('h', 'An API gets 12 requests per second for 1 hour from one token, against a usual 0.5. How many times the usual volume?', '24', '12 / 0.5.', ['Ratio of rates.', '12 / 0.5.', eq('24 times')], check=12 / 0.5)
K.calc('x', 'An anomaly detector flags 95% of abusive tokens and 1% of normal ones. 1 token in 500 is abusive. P(abusive | flagged)? Round to 3 decimals.', '0.16', 'Bayes.', ['P(flag) = 0.002 &times; 0.95 + 0.998 &times; 0.01 = 0.01188.', '0.0019 / 0.01188.', eq('&asymp; 0.160')], check=round(0.002 * 0.95 / (0.002 * 0.95 + 0.998 * 0.01), 3))

# ------------------------------------------------------------------------------------------------ assignments
K.assign('owner_check', 'e', 'Add an owner check',
         '<p>orders maps an order id to a dict with an "owner" key. Write <code>get_order(orders, caller, oid)</code> that returns <code>(200, order)</code> when the order exists and belongs to caller, and <code>(404, None)</code> otherwise, including when it belongs to someone else.</p>',
         '''
def get_order(orders, caller, oid):
    # your code here
    pass
''', [('get_order({1: {"owner": "a"}, 2: {"owner": "b"}}, "a", 1)', (200, {'owner': 'a'})),
      ('get_order({1: {"owner": "a"}, 2: {"owner": "b"}}, "a", 2)', (404, None)),
      ('get_order({}, "a", 9)', (404, None))],
         '''
def get_order(orders, caller, oid):
    order = orders.get(oid)
    if order is None or order["owner"] != caller:
        return 404, None
    return 200, order
''', 'Look up the order with .get, then compare its owner with caller.', '<p>Returning the same answer for "missing" and "not yours" stops attackers from mapping which IDs exist. The second test is the two user test every API should have.</p>')
K.assign('bucket', 'm', 'A token bucket limiter',
         '<p>Write <code>run_bucket(capacity, rate, times)</code>. The bucket starts full. times is a sorted list of request times in seconds. Before each request, add rate &times; (time since the last request) tokens, capped at capacity. If at least 1 token is left, spend it and record True, else record False. Return the list of results.</p>',
         '''
def run_bucket(capacity, rate, times):
    # your code here
    pass
''', [('run_bucket(2, 1.0, [0, 0, 0, 1, 1])', [True, True, False, True, False]),
      ('run_bucket(1, 0.5, [0, 1, 2, 3, 4])', [True, False, True, False, True]),
      ('run_bucket(3, 0, [])', [])],
         '''
def run_bucket(capacity, rate, times):
    tokens, last, out = float(capacity), None, []
    for t in times:
        if last is not None:
            tokens = min(capacity, tokens + rate * (t - last))
        last = t
        if tokens >= 1:
            tokens -= 1
            out.append(True)
        else:
            out.append(False)
    return out
''', 'Keep tokens and the last time. Refill by rate times the gap, cap it, then spend one if you can.', '<p>Real gateways keep one bucket per key in a fast store such as Redis, keyed by account, API key and IP, and answer 429 with a Retry-After header when a request is refused.</p>')
K.assign('allow_fields', 'h', 'Allow list for writable fields',
         '<p>Write <code>apply_patch(record, body, writable)</code> that returns a pair <code>(new_record, ignored)</code>. new_record is a copy of record with only the keys in writable updated from body. ignored is the sorted list of body keys that were not writable. Do not change record itself.</p>',
         '''
def apply_patch(record, body, writable):
    # your code here
    pass
''', [('apply_patch({"name": "a", "role": "user"}, {"name": "b", "role": "admin"}, {"name"})', ({'name': 'b', 'role': 'user'}, ['role'])),
      ('apply_patch({"x": 1}, {}, {"x"})', ({'x': 1}, [])),
      ('apply_patch({"e": "o"}, {"e": "n", "credits": 9, "admin": True}, {"e"})', ({'e': 'n'}, ['admin', 'credits']))],
         '''
def apply_patch(record, body, writable):
    new = dict(record)
    ignored = []
    for k, v in body.items():
        if k in writable:
            new[k] = v
        else:
            ignored.append(k)
    return new, sorted(ignored)
''', 'Copy with dict(record), loop over body, and split keys into written and ignored.', '<p>Logging the ignored keys is useful: a real user’s app never sends "role", so seeing it means someone is probing your API.</p>')

K.must('APIs', 'Web endpoints that apps call, usually JSON over HTTPS. Client side checks can be skipped. OWASP API Security Top 10 (2023): API1 BOLA to API10 unsafe consumption.')
K.must('BOLA and BFLA', 'Check object owner and caller role on every request. UUIDs are not access control. Return 404 for not yours. Two user tests. USPS 2018, Peloton 2021, Optus 2022.')
K.must('Authentication', 'Keys on servers only, scoped and rotated. Tokens short lived, verify signature, issuer, audience, expiry. Rate limit login and reset per account. Facebook 2018 token theft.')
K.must('Rate limits', 'Token bucket: allowed &le; capacity + rate &times; T. 429 Too Many Requests (RFC 6585) with Retry-After. Per account, per key, per IP. Page, payload and GraphQL cost limits.')
K.must('API3 properties', 'Mass assignment: allow list of writable fields. Excessive data exposure: response schema. Rails 2012, Twitter 2022 (5.4 million).')
K.must('Outbound and SSRF', 'Webhooks fetch user URLs. Block private, loopback, link local (169.254.169.254, also 2852039166). Check resolved IPs, no blind redirects, IMDSv2. Capital One 2019 (about 106 million).')
K.must('Operations', 'Inventory from logs and OpenAPI, retire zombie and shadow APIs, fixed CORS origins, generic errors, alerts per token. T-Mobile 2023 (about 37 million). Test only what you own.')

T = K.topic(
    slug='cy-api', topic='cy-api', step=(4, 'Beyond the web', 'cy-a4', 'Security for people, phones, connected devices, industrial systems and the APIs that link them.', 'Advanced'),
    title='API security: BOLA, rate limits, mass assignment and the OWASP API Top 10', short='API security', badge='4.4', minutes=80,
    lead='How the APIs behind every app are attacked and protected: changing one ID to read someone else’s data, weak keys and tokens, rate limits with token buckets, mass assignment and excessive data exposure, SSRF through webhooks, forgotten API versions, and how to build and test APIs safely.',
    desc='API security, OWASP API Security Top 10, BOLA, IDOR, broken object level authorisation, BFLA, broken authentication, API key, bearer token, JWT, rate limiting, token bucket, 429, credential stuffing, GraphQL, mass assignment, excessive data exposure, response schema, SSRF, webhook, metadata service, zombie API, shadow API, CORS, API gateway, OpenAPI, Optus, Peloton, USPS, T-Mobile, Capital One, Twitter',
    summary='The OWASP API Top 10, BOLA and BFLA with owner checks, API authentication, token bucket rate limits, mass assignment and response schemas, SSRF in webhooks, API inventory and misconfiguration, and a secure API life cycle.',
    keywords=['API', 'BOLA', 'IDOR', 'rate limit', 'token bucket', 'mass assignment', 'SSRF', 'GraphQL', 'OpenAPI', 'OWASP API Top 10'],
    recap='<p>Check the owner on every request, allow only the fields you expect in and out, limit per account as well as per IP, guard every outbound fetch, and keep a list of every API you run.</p>',
    added='2026-11-22')
