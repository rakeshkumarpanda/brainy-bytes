# Application Security 1.3: cross site scripting, CSP, CSRF and clickjacking. Checked against CERT Advisory
# CA-2000-02 (2000), the OWASP XSS Prevention, DOM XSS, CSRF Prevention and Clickjacking Defense cheat sheets,
# W3C Content Security Policy Level 3, Weichselbaum et al., CSP Is Dead, Long Live CSP! (ACM CCS 2016), Zeller and
# Felten, Cross-Site Request Forgeries: Exploitation and Prevention (Princeton, 2008), the Samy worm write ups (2005),
# the UK ICO penalty notice to British Airways (2020), MDN and the Python html and html.parser documentation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-xss')
K = Kit()

K.code('xss_contexts', r'''
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
''', long=True)

K.code('sanitiser', r'''
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
''', long=True)

K.code('csp_check', r'''
# How a browser applies a Content Security Policy to the scripts on a page (a simplified model of CSP Level 3)
import base64, hashlib

def parse(policy):
    out = {}
    for part in policy.split(";"):
        words = part.split()
        if words:
            out[words[0]] = words[1:]
    return out

def allowed(policy, script):
    sources = policy.get("script-src", policy.get("default-src", ["*"]))
    kind, value, nonce = script
    if kind == "inline":
        if nonce and f"'nonce-{nonce}'" in sources:
            return True, "nonce matches"
        digest = base64.b64encode(hashlib.sha256(value.encode()).digest()).decode()
        if f"'sha256-{digest}'" in sources:
            return True, "hash matches"
        if "'unsafe-inline'" in sources:
            return True, "'unsafe-inline' allows every inline script"
        return False, "inline script without a valid nonce or hash"
    host = value.split("/")[2]
    if "'strict-dynamic'" in sources:
        return False, "'strict-dynamic': needs the nonce, or a trusted script must load it"
    if host in sources or "*" in sources:
        return True, "host is listed"
    return False, f"{host} is not in script-src"

page_scripts = [
    ("inline", "initMenu()", "r4nd0mN0nc3"),                       # the site's own script, given the nonce
    ("inline", "steal(document.cookie)", None),                    # injected by an attacker through XSS
    ("external", "https://cdn.example.com/lib.js", None),
    ("external", "https://evil.io/x.js", None),
]
policies = {
    "weak": "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.example.com",
    "allow list": "default-src 'self'; script-src 'self' cdn.example.com",
    "strict (nonce)": "default-src 'self'; script-src 'nonce-r4nd0mN0nc3' 'strict-dynamic'; object-src 'none'; base-uri 'none'",
}
for name, text in policies.items():
    p = parse(text)
    print(f"policy {name}: {text}")
    for s in page_scripts:
        ok, why = allowed(p, s)
        label = s[1] if s[0] == "external" else "inline " + s[1]
        print(f"   {'RUN  ' if ok else 'BLOCK'} {label:34} {why}")
    print()
''', long=True)

K.code('csrf_token', r'''
# Cross site request forgery: why the bank needs proof that a request came from its own page
import hashlib, hmac

SERVER_KEY = b"csrf-signing-key-only-the-server-knows"

def make_token(session_id):
    # a token bound to the session: HMAC(server key, session id)
    return hmac.new(SERVER_KEY, session_id.encode(), hashlib.sha256).hexdigest()[:32]

def transfer(request, check_token, samesite):
    if samesite == "Strict":
        cookie_sent = request["same_site"]
    elif samesite == "Lax":
        cookie_sent = request["same_site"] or request["top_level_get"]   # cross site only for link clicks
    else:
        cookie_sent = True                                                 # SameSite=None: always sent
    if not cookie_sent:
        return "refused: no session cookie arrived (SameSite)"
    if check_token and not hmac.compare_digest(request.get("token", ""), make_token(request["session"])):
        return "refused: missing or wrong CSRF token"
    return f"DONE: sent {request['amount']} to {request['to']}"

session = "8f3a91c2"
real = {"session": session, "same_site": True, "top_level_get": False, "to": "landlord", "amount": 900,
        "token": make_token(session)}
forged = {"session": session, "same_site": False, "top_level_get": False, "to": "attacker", "amount": 5000}

for check_token, samesite in [(False, "None"), (True, "None"), (False, "Lax"), (True, "Lax")]:
    print(f"token check {str(check_token):5}, SameSite={samesite:4} | real form: {transfer(real, check_token, samesite):28} | forged form: {transfer(forged, check_token, samesite)}")
print("\nThe attacker cannot read the token: the same origin policy hides the bank's pages from evil.io.")
''', long=True)

K.lesson('idea', 'Cross site scripting: three kinds, one cause', f'''
{talk('Cross site scripting, or XSS, lets an attacker run their own JavaScript inside someone else’s website, in the victim’s browser. Engineers at Microsoft gave it its name around the turn of the year 2000, and CERT warned about it in advisory CA-2000-02 in February 2000. It happens when a page includes text from an untrusted source in its HTML without encoding it, so that the browser reads the text as markup and code. Because the script arrives from the real site, the same origin policy treats it as the site’s own. It can read everything on the page, make requests as the logged in user, change what the user sees, and record keystrokes. There are three kinds. In stored XSS the payload is saved on the server, for example in a comment or profile, and runs for everyone who views it. In reflected XSS the payload travels in a link and is echoed back once, so the attacker must get each victim to click. In DOM based XSS the server never sees the payload: the site’s own JavaScript takes something like the part of the URL after the hash sign and writes it into the page with innerHTML. The most famous XSS is the Samy worm. On 4 October 2005 Samy Kamkar put a script in his MySpace profile that added him as a friend of anyone who viewed it and copied itself into their profile. Over a million users were infected in about 20 hours, MySpace had to shut down, and Samy was later sentenced to probation and community service. A related attack is changing a script the site loads from elsewhere. In 2018 attackers altered a script on the British Airways site to copy card details as customers typed them, affecting around 400000 people, and the UK regulator fined the airline 20 million pounds.')}
{src('CERT Advisory CA-2000-02, Malicious HTML Tags Embedded in Client Web Requests (2000), OWASP Cross Site Scripting Prevention, DOM based XSS Prevention, Cross-Site Request Forgery Prevention and Clickjacking Defense cheat sheets, W3C Content Security Policy Level 3 and Subresource Integrity, W3C Trusted Types, Weichselbaum, Spagnuolo, Lekies and Janc, CSP Is Dead, Long Live CSP! (ACM CCS 2016), Zeller and Felten, Cross-Site Request Forgeries: Exploitation and Prevention (2008), Samy Kamkar, MySpace worm technical explanation (2005), UK ICO penalty notice to British Airways (2020), Hansen and Grossman on clickjacking (2008), MDN Web Docs.')}
{safe('The programs build HTML strings and print them. Nothing is served to a browser. Practise XSS only on your own pages or on training labs such as PortSwigger Web Security Academy, Google XSS Game or OWASP Juice Shop.')}
{wwh('<b>Cross site scripting</b> is injection into a web page: untrusted text ends up in HTML or JavaScript in a way that lets it run as code in other users’ browsers.',
     'The script runs with the site’s origin, so it can do anything the user can: read private data, post, buy, change settings, or show a fake login. XSS is one of the most often reported web bugs in bug bounty programmes.',
     'Encode output for the exact context it lands in, sanitise any HTML you allow with an allow list library, avoid dangerous DOM functions such as innerHTML, and add a strict Content Security Policy and HttpOnly cookies as further layers.')}
{viz('cyxss')}
{table(['Kind', 'Where the payload lives', 'Who is hit', 'Example'], [
    ['Stored', 'In the server’s database', 'Everyone who views the page', 'Samy worm on MySpace (2005)'],
    ['Reflected', 'In a link or form, echoed once', 'Whoever opens the crafted link', 'Search pages that repeat the query'],
    ['DOM based', 'In the URL or browser state, handled by the page’s own JavaScript', 'Whoever opens the crafted link', 'location.hash written with innerHTML'],
    ['Script supply chain', 'In a third party or altered script file', 'Every visitor', 'British Airways card skimming (2018)']])}
''', kw=['XSS', 'cross site scripting', 'stored XSS', 'reflected XSS', 'DOM XSS', 'Samy worm', 'MySpace', 'British Airways', 'Magecart', 'CERT CA-2000-02', 'JavaScript', 'same origin'])

K.lesson('encoding', 'Output encoding: the right escape for each context', f'''
{talk('The main defence against XSS is output encoding, and the key idea is that the right encoding depends on where the text lands. Inside normal HTML text, the characters less than, greater than and ampersand must become entities such as <code>&amp;lt;</code>, so the browser shows them instead of opening a tag. Inside an HTML attribute the value must also be quoted and its quote characters encoded, or the attacker can close the attribute and add an event handler such as onmouseover. Inside a JavaScript string, HTML entities do not help, because the JavaScript parser does not decode them. Here the safe way is to produce a proper JavaScript string, for example with json.dumps, and also make the less than sign harmless so that a closing script tag inside the string cannot end the script block early. Inside a URL attribute such as href, encoding is not enough: a link to javascript:steal() is perfectly well encoded and still runs when clicked, so the scheme must be checked against an allow list of http and https. Getting all of this right by hand is hard, which is why modern template engines and frameworks encode automatically. Jinja2 with autoescape, Django templates, React and Angular all escape by default. XSS creeps back in through escape hatches with names that warn you, such as the safe filter, mark_safe, or dangerouslySetInnerHTML.')}
{run('xss_contexts')}
{table(['Context', 'Example', 'Encode with', 'Watch out for'], [
    ['HTML body', '&lt;p&gt;Hello NAME&lt;/p&gt;', 'html.escape: &amp; &lt; &gt; to entities', 'Template filters that turn escaping off'],
    ['HTML attribute', '&lt;input value="NAME"&gt;', 'html.escape(quote=True), always quote', 'Unquoted attributes, event handler attributes'],
    ['JavaScript string', 'var u = NAME', '<code>json.dumps</code>, plus <code>\\u003c</code> for &lt;', 'Closing script tags, template literals'],
    ['URL in href or src', '&lt;a href="URL"&gt;', 'Scheme allow list, then attribute encoding', 'javascript: and data: URLs'],
    ['URL query value', '/search?q=VALUE', 'urllib.parse.quote', 'Double decoding'],
    ['CSS', 'style="color: VALUE"', 'Avoid user input in CSS', 'expression() in old IE, url()']])}
{fxs(fx('Escaping rule for HTML text', '&amp; &rarr; <code>&amp;amp;</code>, &lt; &rarr; <code>&amp;lt;</code>, &gt; &rarr; <code>&amp;gt;</code>, " &rarr; <code>&amp;quot;</code>, \' &rarr; <code>&amp;#x27;</code>', 'Python html.escape does all five with quote=True. Escape &amp; first, or you double escape the others.', key=True))}
''', kw=['output encoding', 'escaping', 'html.escape', 'context', 'HTML attribute', 'JavaScript string', 'javascript: URL', 'autoescape', 'Jinja2', 'React', 'dangerouslySetInnerHTML', 'mark_safe'])

K.lesson('sanitise', 'Allowing some HTML, and DOM based XSS', f'''
{talk('Some sites must accept a little HTML, such as bold and italic in comments or formatted text from a rich editor. Encoding everything would break that, so the HTML has to be sanitised. Blocklists, which try to remove dangerous things such as the word script, fail again and again. Removing script once from scr-script-ipt leaves script behind. Payloads need no script tag at all: an image with a broken source and an onerror handler, an SVG with onload, or a link with a javascript URL all run code. Browsers also repair broken HTML in surprising ways, which has defeated many clever filters. The reliable approach is an allow list parser: parse the HTML properly, keep only known safe tags and attributes, encode all text, and drop everything else. Use a maintained library, such as DOMPurify in the browser or nh3 in Python, because the edge cases are endless. DOM based XSS needs its own attention because the server may never see the payload. The page’s own JavaScript reads from a source an attacker controls, such as location.hash, document.referrer or a message from another window, and writes it to a sink that parses HTML or runs code, such as innerHTML, document.write, eval or setTimeout with a string. The safe versions are textContent instead of innerHTML and real functions instead of strings. Browsers based on Chromium also support Trusted Types since 2020, which, when turned on by a CSP directive, makes the dangerous sinks refuse plain strings, so every write must go through a reviewed policy.')}
{run('sanitiser')}
{table(['Dangerous DOM sink', 'Safer alternative'], [
    ['element.innerHTML = text', 'element.textContent = text'],
    ['document.write(text)', 'createElement and textContent'],
    ['eval(text), new Function(text)', 'JSON.parse for data, real functions for code'],
    ['setTimeout("code", 100)', 'setTimeout(function, 100)'],
    ['a.href = userUrl', 'Check the URL scheme first'],
    ['jQuery $(userText)', 'Build elements explicitly, insert text with .text()']])}
{note('Sanitise once, at output, with a maintained library and its default safe settings. Sanitising on input and then editing the text later is a common way to reintroduce XSS.')}
''', kw=['HTML sanitiser', 'allow list', 'blocklist', 'DOMPurify', 'nh3', 'onerror', 'DOM XSS', 'source and sink', 'innerHTML', 'textContent', 'eval', 'Trusted Types'])

K.lesson('csp', 'Content Security Policy and Subresource Integrity', f'''
{talk('Content Security Policy is a response header that tells the browser which scripts, styles, images and frames a page may load and run. It was proposed at Mozilla in 2009 and first shipped in Firefox 4 in 2011, and CSP Level 3 is the current version. Its main job in security is to be a second line of defence against XSS: even if an attacker manages to inject a script tag, the browser will not run it unless the policy allows it. Early policies listed allowed hosts, but in 2016 a Google team led by Lukas Weichselbaum studied about 26000 real policies and found that almost 95 percent could be bypassed, mostly because they allowed unsafe-inline, which permits every inline script, or listed large hosts such as public CDNs that also serve scripts an attacker can abuse. They recommended strict CSP instead. The server generates a fresh random value, a nonce, for every response, puts it in the header and on each of its own script tags, and the browser runs only scripts with that nonce. The strict-dynamic keyword lets those trusted scripts load others, which keeps real sites working. Policies should be rolled out first with the Report-Only header, which logs violations without blocking. Subresource Integrity handles a different risk: a library loaded from another server being changed, as in the British Airways case. The script tag carries a hash of the expected file, such as integrity="sha384-…", and the browser refuses the file if its hash differs.')}
{viz('cycsp')}
{run('csp_check')}
{fxs(fx('Nonce guessing', 'P(guess) = 2<sup>&minus;b</sup> per try, b = nonce bits', 'A 128 bit random nonce: 2<sup>&minus;128</sup>. A fixed nonce reused on every page is worthless once seen.', key=True),
     fx('Hash source', "'sha256-' + base64(SHA-256(exact script text))", 'Any change, even one space, changes the hash and blocks the script.'),
     fx('SRI', 'integrity = "sha384-" + base64(SHA-384(file))', 'A changed library file fails the check and does not run.', key=True))}
{table(['Directive', 'What it controls', 'Strict choice'], [
    ['script-src', 'Where scripts may come from', "'nonce-RANDOM' 'strict-dynamic'"],
    ['object-src', 'Plugins such as Flash', "'none'"],
    ['base-uri', 'The base element, which changes relative URLs', "'none'"],
    ['frame-ancestors', 'Who may frame this page', "'self' or 'none'"],
    ['report-to / report-uri', 'Where to send violation reports', 'A logging endpoint'],
    ['require-trusted-types-for', 'Forces Trusted Types for DOM sinks', "'script'"]])}
''', kw=['Content Security Policy', 'CSP', 'nonce', 'strict-dynamic', 'unsafe-inline', 'Report-Only', 'CSP Level 3', 'Weichselbaum', 'Subresource Integrity', 'SRI', 'hash source', 'frame-ancestors'])

K.lesson('csrf', 'Cross site request forgery', f'''
{talk('Cross site request forgery, CSRF, abuses the fact that a browser attaches a site’s cookies to every request it sends to that site, no matter which page started the request. If you are logged in to your bank and visit an evil page, that page can contain a hidden form that posts a transfer to the bank, submitted automatically by a line of script. Your browser adds your bank cookie, and a bank that checks only the cookie performs the transfer. The attacker never sees your cookie or the bank’s reply, and does not need to, because the damage is the action itself. In 2008 William Zeller and Edward Felten at Princeton showed working CSRF attacks against ING Direct, where they could open accounts and move money, and against YouTube, The New York Times and MetaFilter. The classic defence is a CSRF token: a secret value the server puts in each of its forms and checks on submission. The evil page cannot read the bank’s pages, thanks to the same origin policy, so it cannot know the token. Tokens can be random values stored in the session, or HMAC values computed from the session id with a server key, so nothing extra has to be stored. The modern layer is the SameSite cookie attribute. With Lax, which Chrome made the default in 2020, cookies are not sent on cross site POST requests or background requests, which stops the classic attack. Checking the Origin header on state changing requests is a third, simple layer. All of them assume one rule: requests that change something must never use GET.')}
{viz('cycsrf')}
{run('csrf_token')}
{fxs(fx('HMAC CSRF token', 'token = HMAC(server key, session id)', 'Nothing to store: recompute on submit and compare with hmac.compare_digest.', key=True),
     fx('Guessing a token', 'P = 2<sup>&minus;b</sup> per try', 'A 128 bit token: no practical chance. A token of 6 digits: 1 in 10<sup>6</sup>, too weak.'))}
{attack([
    ['Hidden auto submitting form to a state changing URL', 'CSRF token checked on every POST, PUT and DELETE'],
    ['Cross site request carrying the session cookie', 'SameSite=Lax or Strict on session cookies'],
    ['State change through a GET link or image tag', 'Never change state with GET'],
    ['Request from an unexpected site', 'Check the Origin or Referer header on the server'],
    ['Stealing the token with XSS', 'Fix XSS first: any XSS defeats CSRF defences']])}
''', kw=['CSRF', 'cross site request forgery', 'CSRF token', 'synchroniser token', 'HMAC token', 'SameSite', 'Origin header', 'Zeller and Felten', 'ING Direct', 'GET versus POST'])

K.lesson('clickjacking', 'Clickjacking and framing', f'''
{talk('Clickjacking was named in 2008 by Robert Hansen and Jeremiah Grossman. The attacker loads the victim site in an invisible frame on top of an innocent looking page, and lines up a button on the real site, such as Delete account or Allow camera, under something the user wants to click, such as Play video. The user thinks they clicked the game, but the click lands on the real site, where they are logged in. Variants have tricked people into liking pages, changing privacy settings and approving payments. The fix is to tell the browser who may frame your pages. The old header X-Frame-Options, with values DENY or SAMEORIGIN, still works in all browsers. The modern way is the CSP directive frame-ancestors, which can list exact allowed parent origins. Sensitive actions should also ask for confirmation, such as typing a password or a code, which a single hidden click cannot provide.')}
{table(['Header', 'Value', 'Effect'], [
    ['X-Frame-Options', 'DENY', 'No site may frame the page'],
    ['X-Frame-Options', 'SAMEORIGIN', 'Only the same origin may frame it'],
    ['Content-Security-Policy', "frame-ancestors 'none'", 'Like DENY, the modern way'],
    ['Content-Security-Policy', 'frame-ancestors https://partner.example', 'Only that partner may frame it']])}
{note('Old JavaScript frame busting code, which tried to break out of frames, was bypassed in many ways and should not be relied on. Use the headers.')}
''', kw=['clickjacking', 'UI redressing', 'X-Frame-Options', 'frame-ancestors', 'iframe', 'Hansen', 'Grossman', 'frame busting'])

K.lesson('versus', 'XSS and CSRF compared', f'''
{talk('XSS and CSRF are often confused because both involve another site and a logged in user. The difference is where the attacker’s code runs. In XSS the attacker’s script runs inside the victim site, so it can read and do everything. In CSRF the attacker’s page stays on its own site and can only send blind requests that ride on the victim’s cookies. That is why XSS is more serious, and why an XSS bug defeats CSRF tokens: a script inside the site can simply read the token.')}
{versus('XSS versus CSRF versus clickjacking', ['', 'XSS', 'CSRF', 'Clickjacking'], [
    ['Attacker code runs', 'Inside the victim site', 'On the attacker’s site', 'On the attacker’s site'],
    ['Can read victim data', 'Yes', 'No, blind requests only', 'No'],
    ['Needs', 'An injection bug in the site', 'A state change checked only by cookie', 'A page that can be framed'],
    ['Main defence', 'Output encoding, sanitising, strict CSP', 'CSRF tokens, SameSite, no GET changes', 'frame-ancestors, X-Frame-Options'],
    ['Famous case', 'Samy worm 2005', 'ING Direct 2008', 'Facebook likejacking around 2010']],
    'Fix XSS first, because it breaks the other defences. Then add tokens and SameSite for CSRF, and framing headers for clickjacking.')}
''', kw=['comparison', 'XSS versus CSRF', 'clickjacking', 'defence in depth'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows not to click strange links while logged in to important sites. A college student can find and fix stored, reflected and DOM XSS in lab code, write a strict CSP and explain CSRF tokens. A professional reviews templates for escape hatches, deploys CSP with reporting, and tests with Burp Suite. Researchers study mutation XSS caused by browser parsing quirks, script gadgets in frameworks that bypass CSP, and new browser defences such as Trusted Types and sanitiser APIs.')}
{ladder(
    '<p>Be careful with links and pop ups while logged in, keep the browser updated, and log out of banking sites when done.</p>',
    '<p>Three kinds of XSS, context aware encoding, allow list sanitising, DOM sources and sinks, strict CSP with nonces, SRI, CSRF tokens and SameSite, framing headers.</p>',
    '<p>Review code for innerHTML, eval and template escape hatches, roll out CSP with Report-Only, enforce Trusted Types, and test with Burp Suite and DOM Invader.</p>',
    '<p>Mutation XSS from parser differences, script gadgets in JavaScript frameworks, formal models of browser security, the HTML Sanitizer API, and automatic detection of DOM XSS with taint tracking.</p>')}
{grow('Explain why a site must not show users’ text as code.',
      'Encode, sanitise and set CSP and CSRF defences in lab code.',
      'Audit real apps and keep defences working at scale.')}
''', kw=['beginner', 'expert', 'mutation XSS', 'script gadgets', 'DOM Invader', 'Sanitizer API'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>XSS</b>: untrusted text read as code in other users’ browsers, with the site’s origin. Stored, reflected, DOM based. Samy worm 2005, British Airways 2018.',
    '<b>Encoding</b>: depends on context. HTML text, attribute (quoted), JavaScript string (json.dumps), URL (scheme allow list). Frameworks escape by default.',
    '<b>Sanitising</b>: allow list parsers such as DOMPurify or nh3, never blocklists. DOM sinks: use textContent, not innerHTML. Trusted Types.',
    '<b>CSP</b>: strict policy with a fresh nonce and strict-dynamic, not unsafe-inline or broad host lists. Report-Only first. SRI hashes for third party files.',
    '<b>CSRF</b>: the browser sends cookies on cross site requests. Defend with tokens (random or HMAC of the session), SameSite=Lax, Origin checks, and no state change on GET.',
    '<b>Clickjacking</b>: hidden frames steal clicks. frame-ancestors or X-Frame-Options.'],
    'Next, Application Security 2.1: memory safety, from buffer overflows to stack canaries, ASLR and Rust.')}
{files('Three tasks: HTML escaping, a URL scheme check, and an HMAC CSRF token.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does an XSS attack let the attacker do?', ['Read the server’s disk', 'Run their own JavaScript inside the victim site in other users’ browsers', 'Crack passwords offline', 'Flood the network'], 1, 'Script in the page.', 'It runs with the site’s origin.')
K.quiz('e', 'Which kind of XSS is saved on the server and hits every visitor?', ['Reflected', 'Stored', 'DOM based', 'Blind'], 1, 'Stored.', 'The Samy worm was stored XSS.')
K.quiz('e', 'The main defence against XSS is', ['A firewall', 'Encoding output for the context it is placed in', 'Longer passwords', 'HTTPS'], 1, 'Encode at output.', 'Frameworks do this by default.')
K.quiz('e', 'CSRF makes the victim’s browser', ['Download malware', 'Send a request to a site where the victim is logged in, with their cookies', 'Show a pop up', 'Delete cookies'], 1, 'Borrowed browser.', 'The attacker never sees the cookie.')
K.quiz('m', 'Why does html.escape not make a javascript: link safe in href?', ['It does', 'The URL contains no special HTML characters, and the browser still runs it when clicked', 'href ignores escaping', 'It only works in Python 2'], 1, 'Scheme.', 'Allow only http and https.')
K.quiz('m', 'Why do blocklist XSS filters fail?', ['They are slow', 'Payloads need no script tag (onerror, onload, javascript: URLs) and nested tricks survive removal', 'They block too much', 'Browsers ignore them'], 1, 'Endless variants.', 'Use allow list sanitisers.')
K.quiz('m', 'Which DOM sink is safe for putting user text on a page?', ['innerHTML', 'textContent', 'document.write', 'eval'], 1, 'Text only.', 'textContent never parses HTML.')
K.quiz('m', "A CSP contains script-src 'self' 'unsafe-inline'. Against injected inline scripts it is", ['Strong', 'Useless, because unsafe-inline allows every inline script', 'Strong only on HTTPS', 'Only for images'], 1, 'unsafe-inline.', 'Use nonces instead.')
K.quiz('m', 'A CSRF token works because', ['It is encrypted', 'The attacker’s page cannot read the bank’s pages to learn it, due to the same origin policy', 'Cookies cannot be sent', 'It changes every second'], 1, 'Unreadable.', 'Any XSS on the site breaks this.')
K.quiz('h', 'What does strict-dynamic add to a nonce based CSP?', ['Allows all hosts', 'Scripts trusted by nonce may load further scripts, so host lists are not needed', 'Turns CSP off', 'Requires HTTPS'], 1, 'Trust propagates.', 'It keeps real sites working with strict CSP.')
K.quiz('h', 'Why is XSS more serious than CSRF?', ['It is not', 'XSS code runs inside the site and can read data and tokens, while CSRF sends blind requests', 'CSRF needs a password', 'XSS only affects admins'], 1, 'Inside versus outside.', 'XSS defeats CSRF tokens.')
K.quiz('h', 'What does Subresource Integrity protect against?', ['SQL injection', 'A third party script file being altered on its server or CDN', 'Weak passwords', 'Clickjacking'], 1, 'Hash check.', 'The browser refuses a file whose hash differs.')
K.quiz('h', 'Which header stops clickjacking?', ['Strict-Transport-Security', "Content-Security-Policy: frame-ancestors 'none'", 'X-Content-Type-Options', 'Set-Cookie'], 1, 'Framing.', 'X-Frame-Options DENY is the older form.')
K.quiz('x', 'In the style of an MIT 6.5660 question: a site sets SameSite=Lax on its session cookie. Which request still carries the cookie from evil.io?', ['A hidden auto submitting POST form', 'A top level GET navigation when the user clicks a link to the site', 'A background fetch()', 'An image load'], 1, 'Lax allows top level GET.', 'So GET requests must never change state.')
K.quiz('x', 'In the style of an IIT Kharagpur web security exam: Google’s 2016 study of real CSP deployments found about what share of policies bypassable?', ['5%', '50%', '95%', '0%'], 2, 'Almost all.', 'About 94.7%, mostly due to unsafe-inline and broad host lists.')

K.calc('e', 'The Samy worm reached 1000000 users in about 20 hours. Assuming steady doubling from 1, what doubling time in hours? Round to 2 decimals.', '1.0', '20 / log<sub>2</sub> 10<sup>6</sup>.', ['log<sub>2</sub> 10<sup>6</sup> = 19.93 doublings.', '20 / 19.93.', eq('about 1.0 hour')], check=round(20 / 19.931568569324174, 2))
K.calc('e', 'How many characters is html.escape("&lt;b&gt;")?', '9', '<code>&amp;lt;</code>b<code>&amp;gt;</code>', ['&lt; becomes <code>&amp;lt;</code> (4 characters).', 'b stays, &gt; becomes <code>&amp;gt;</code> (4 characters).', eq('4 + 1 + 4 = 9')], check=9)
K.calc('e', 'A CSP nonce is 16 random bytes. How many bits?', '128', '8 bits per byte.', ['16 bytes.', '8 bits each.', eq('128 bits')], check=128)
K.calc('m', 'How many base64 characters (with padding) encode a 16 byte nonce?', '24', '4 &times; &lceil;n/3&rceil;.', ['&lceil;16/3&rceil; = 6 groups.', '4 characters per group.', eq('24')], check=24)
K.calc('m', 'Of 26011 policies, 94.72% were bypassable. About how many? Round to a whole number.', '24638', 'Multiply.', ['26011 &times; 0.9472.', '= 24637.6.', eq('24638')], check=round(26011 * 0.9472))
K.calc('m', 'A CSRF token is 6 digits. An attacker gets 1000 tries. Chance of success?', '0.001', 'Tries / possibilities.', ['10<sup>6</sup> possible tokens.', '1000 / 10<sup>6</sup>.', eq('0.001, far too weak')], check=0.001)
K.calc('m', 'A stored XSS sits on a page with 50000 views a day, and 30% of viewers are logged in. Sessions exposed per day?', '15000', 'Multiply.', ['50000 views.', '30% logged in.', eq('15000')], check=15000)
K.calc('m', 'How many base64 characters encode a SHA-384 digest (48 bytes) in an SRI attribute?', '64', '48 / 3 &times; 4.', ['48 bytes = 16 groups of 3.', '4 characters per group.', eq('64')], check=64)
K.calc('h', 'A worm doubles every hour from 1 profile. Whole hours until it reaches at least 1000000?', '20', '&lceil;log<sub>2</sub> 10<sup>6</sup>&rceil;.', ['log<sub>2</sub> 10<sup>6</sup> = 19.93.', 'Round up to whole hours.', eq('20 hours')], check=20)
K.calc('h', 'Entropy of an 8 character token over 62 symbols? Round to 1 decimal.', '47.6', '8 log<sub>2</sub> 62.', ['log<sub>2</sub> 62 = 5.954.', '8 &times; 5.954.', eq('47.6 bits')], check=47.6)
K.calc('h', 'Of 1000 cross site requests, 700 are top level link clicks (GET), 200 are POST forms and 100 are fetch calls. With SameSite=Lax, how many carry the cookie?', '700', 'Only top level GET.', ['POST forms: no cookie.', 'Background fetch: no cookie.', eq('700')], check=700)
K.calc('h', 'How many base64 characters encode a SHA-256 hash in a CSP hash source?', '44', '4 &times; &lceil;32/3&rceil;.', ['32 bytes needs 11 groups of 3.', '11 &times; 4 = 44 (with one = of padding).', eq('44')], check=44)
K.calc('x', 'Each infected profile infects 3 new viewers per hour, so the count multiplies by 4 each hour from 1. Whole hours to reach 1000000?', '10', 'log<sub>4</sub> 10<sup>6</sup>.', ['4<sup>t</sup> &ge; 10<sup>6</sup>.', 't &ge; log<sub>4</sub> 10<sup>6</sup> = 9.97.', eq('10 hours')], check=10)
K.calc('x', 'An attacker can make 10<sup>9</sup> guesses of a 128 bit CSRF token. Probability of any success, to 2 significant figures?', '2.9e-30', '10<sup>9</sup> / 2<sup>128</sup>.', ['2<sup>128</sup> = 3.40 &times; 10<sup>38</sup>.', '10<sup>9</sup> / 3.40 &times; 10<sup>38</sup>.', eq('2.9 &times; 10<sup>&minus;30</sup>')], check=float('%.2g' % (1e9 / 2 ** 128)))

K.assign('escape_html', 'e', 'Escape text for HTML',
         '<p>Write <code>escape_html(text)</code> without using the html module. Replace &amp; with <code>&amp;amp;</code> first, then &lt; with <code>&amp;lt;</code>, &gt; with <code>&amp;gt;</code>, " with <code>&amp;quot;</code> and \' with <code>&amp;#x27;</code>.</p>',
         '''
def escape_html(text):
    # your code here
    pass
''', [('escape_html("<b>")', '&lt;b&gt;'), ('escape_html("a & b")', 'a &amp; b'), ('escape_html(\'"><script>\')', '&quot;&gt;&lt;script&gt;'), ('escape_html("it\'s")', 'it&#x27;s'), ('escape_html("&lt;")', '&amp;lt;')],
         '''
def escape_html(text):
    for ch, ent in (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), (\'"\', "&quot;"), ("\'", "&#x27;")):
        text = text.replace(ch, ent)
    return text
''', 'Do the ampersand first, or the &amp; inside <code>&amp;lt;</code> gets escaped again.', '<p>The last test shows why the order matters: text that already looks like an entity must be shown as typed, so its &amp; must become <code>&amp;amp;</code>.</p>')
K.assign('safe_href', 'm', 'A safe link target',
         '<p>Write <code>safe_href(url)</code> that returns the URL unchanged if its scheme (from <code>urllib.parse.urlsplit</code>, lower cased) is http or https, returns it unchanged if it is a relative link with no scheme that starts with "/", and returns "#" for anything else.</p>',
         '''
from urllib.parse import urlsplit

def safe_href(url):
    # your code here
    pass
''', [('safe_href("https://example.org/a")', 'https://example.org/a'), ('safe_href("javascript:steal()")', '#'), ('safe_href("JaVaScRiPt:steal()")', '#'), ('safe_href("/profile/7")', '/profile/7'), ('safe_href("data:text/html,<script>x</script>")', '#')],
         '''
from urllib.parse import urlsplit

def safe_href(url):
    scheme = urlsplit(url).scheme.lower()
    if scheme in ("http", "https"):
        return url
    if scheme == "" and url.startswith("/"):
        return url
    return "#"
''', 'Lower case the scheme: browsers accept JaVaScRiPt: too.', '<p>Allow lists beat blocklists here as well: data:, vbscript: and future schemes are all refused without being named.</p>')
K.assign('csrf_token', 'h', 'An HMAC CSRF token',
         '<p>Write <code>csrf_token(session_id, key)</code> that returns the first 32 hex characters of HMAC-SHA-256(key, session_id), and <code>csrf_ok(session_id, token, key)</code> that recomputes it and compares with <code>hmac.compare_digest</code>.</p>',
         '''
import hashlib, hmac

def csrf_token(session_id, key):
    # your code here
    pass

def csrf_ok(session_id, token, key):
    # your code here
    pass
''', [('csrf_token("8f3a91c2", b"k")', 'dd0dcb0628bbbe2dbaf20b6f459909de'), ('csrf_token("abc", b"server-key")', '47d19a41e6e236b0198edeec77d8bd90'), ('csrf_ok("abc", "47d19a41e6e236b0198edeec77d8bd90", b"server-key")', True), ('csrf_ok("abc", "00000000000000000000000000000000", b"server-key")', False), ('csrf_ok("other", "47d19a41e6e236b0198edeec77d8bd90", b"server-key")', False)],
         '''
import hashlib, hmac

def csrf_token(session_id, key):
    return hmac.new(key, session_id.encode(), hashlib.sha256).hexdigest()[:32]

def csrf_ok(session_id, token, key):
    return hmac.compare_digest(csrf_token(session_id, key), token)
''', 'hmac.new(key, message, hashlib.sha256).hexdigest() gives 64 hex characters, keep 32.', '<p>The last test shows the binding: a token from one session is useless in another, so a stolen token cannot be replayed by a different user.</p>')

K.must('XSS', 'Untrusted text read as code in the browser, with the site’s origin. Stored, reflected, DOM. CERT CA-2000-02. Samy worm 2005 (1 million in about 20 h). BA 2018.')
K.must('Encoding', 'By context: HTML text (&amp; &lt; &gt;), attribute (quote + encode quotes), JS string (json.dumps), URL (scheme allow list). Frameworks autoescape.')
K.must('Sanitising and DOM', 'Allow list parsers (DOMPurify, nh3), never blocklists. Sinks: innerHTML, document.write, eval. Use textContent. Trusted Types.')
K.must('CSP and SRI', "Strict CSP: fresh nonce + 'strict-dynamic', object-src 'none', base-uri 'none'. No unsafe-inline. Report-Only first. SRI: integrity hash on third party files.")
K.must('CSRF', 'Cookies ride on cross site requests. Tokens (random or HMAC of session), SameSite=Lax default since 2020, Origin check, never change state on GET.')
K.must('Clickjacking', "Invisible frames steal clicks (Hansen and Grossman 2008). frame-ancestors 'none' or X-Frame-Options DENY. Confirm sensitive actions.")

T = K.topic(
    slug='cy-xss', topic='cy-xss', step=(1, 'Attacking and defending the web', 'cy-a1', 'How the web works, the OWASP Top 10, and the injection, cross site and server side request attacks behind most web breaches.', 'Intermediate'),
    title='Cross site attacks: XSS, CSP, CSRF and clickjacking', short='XSS and CSRF', badge='1.3', minutes=80,
    lead='How attackers make websites run their code or act in their users’ names, and how to stop it: stored, reflected and DOM XSS with the Samy worm, output encoding for each context, allow list sanitising, strict Content Security Policy with nonces and Subresource Integrity, CSRF with HMAC tokens and SameSite cookies, and clickjacking with framing headers.',
    desc='XSS, cross site scripting, stored XSS, reflected XSS, DOM XSS, Samy worm, British Airways, Magecart, output encoding, html.escape, context aware escaping, javascript URL, sanitiser, DOMPurify, nh3, innerHTML, textContent, Trusted Types, Content Security Policy, CSP, nonce, strict-dynamic, unsafe-inline, Report-Only, Subresource Integrity, SRI, CSRF, cross site request forgery, CSRF token, SameSite, Origin header, clickjacking, X-Frame-Options, frame-ancestors',
    summary='XSS kinds and output encoding, sanitising and DOM sinks, strict CSP and SRI, CSRF tokens and SameSite, clickjacking.',
    keywords=['XSS', 'output encoding', 'sanitiser', 'DOM XSS', 'CSP', 'nonce', 'SRI', 'CSRF', 'SameSite', 'clickjacking'],
    recap='<p>Encode every output for its context, sanitise with allow lists, add a strict CSP, and protect every state change with tokens and SameSite. Fix XSS first, because it breaks everything else.</p>',
    added='2026-11-15')
