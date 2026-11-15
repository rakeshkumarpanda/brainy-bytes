# Network and Systems 2.1: authentication. Checked against NIST SP 800-63B-4 (2025), RFC 4226 (HOTP) and RFC 6238
# (TOTP) test vectors, W3C WebAuthn Level 2, FIDO2 CTAP, RFC 4120 (Kerberos 5), RFC 6749 (OAuth 2.0), RFC 7636 (PKCE),
# OpenID Connect Core 1.0, SAML 2.0, RFC 7519 (JWT), RFC 8725 (JWT best practices), Medin (Kerberoasting, 2014).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-authn')
K = Kit()

K.code('password_policy', r'''
# Modern password rules (NIST SP 800-63B): length, a breached list, and rate limiting
import hashlib
import math

breached = {"password", "123456", "qwerty123", "iloveyou", "Summer2024!", "qwerty123qwerty"}     # tiny stand in for real lists
breached_sha1 = {hashlib.sha1(w.encode()).hexdigest().upper() for w in breached}

def k_anonymity_check(pw):
    # like the Have I Been Pwned range API: send only the first 5 hex chars, compare the rest locally
    h = hashlib.sha1(pw.encode()).hexdigest().upper()
    prefix, suffix = h[:5], h[5:]
    bucket = [x[5:] for x in breached_sha1 if x.startswith(prefix)]          # what the server would return
    return suffix in bucket, prefix

def check(pw, only_factor=True):
    need = 15 if only_factor else 8
    if len(pw) < need:
        return f"too short: {len(pw)} < {need}"
    hit, prefix = k_anonymity_check(pw)
    if hit:
        return f"found in a breach (sent only {prefix} to the checker)"
    return "ok"

for pw in ["Summer2024!", "Tr0ub4dor&3", "correct horse battery staple", "qwerty123qwerty"]:
    print(f"{pw!r:32} -> {check(pw)}")

# Online guessing: rate limits make even short PINs survive
for label, tries in (("10 tries then lock", 10), ("100 tries per day for a year", 36500)):
    print(f"6 digit PIN, {label}: chance of success {tries / 10 ** 6:.4%}")
print("bits in a 4 word passphrase from a 7776 word list:", round(4 * math.log2(7776), 1))
''', long=True)

K.code('totp', r'''
# One time passwords: HOTP (RFC 4226) and TOTP (RFC 6238), checked against the RFC test vectors
import hashlib
import hmac
import struct

def hotp(secret, counter, digits=6, algo=hashlib.sha1):
    mac = hmac.new(secret, struct.pack(">Q", counter), algo).digest()   # HMAC of the 8 byte counter
    offset = mac[-1] & 0x0F                                             # dynamic truncation
    code = int.from_bytes(mac[offset:offset + 4], "big") & 0x7FFFFFFF   # 31 bits
    return str(code % 10 ** digits).zfill(digits)

def totp(secret, unix_time, step=30, digits=6, algo=hashlib.sha1):
    return hotp(secret, unix_time // step, digits, algo)                # the counter is the time slot

key = b"12345678901234567890"
print("RFC 4226 HOTP, counter 0:", hotp(key, 0), "(expected 755224)")
print("RFC 4226 HOTP, counter 1:", hotp(key, 1), "(expected 287082)")
print("RFC 6238 TOTP SHA-1, t = 59:", totp(key, 59, digits=8), "(expected 94287082)")
key256 = b"12345678901234567890123456789012"
print("RFC 6238 TOTP SHA-256, t = 59:", totp(key256, 59, digits=8, algo=hashlib.sha256), "(expected 46119246)")

# The server accepts the current slot and one either side, to allow for clock drift
def verify(secret, code, now, window=1):
    return any(totp(secret, now + d * 30) == code for d in range(-window, window + 1))

now = 1_700_000_000
code = totp(key, now)
print("code", code, "accepted now:", verify(key, code, now), "| 25 s later:", verify(key, code, now + 25), "| 2 min later:", verify(key, code, now + 120))
print("chance a random guess hits one of 3 slots:", 3 / 10 ** 6)
''', long=True)

K.code('passkey', r'''
# Why passkeys stop phishing: the signature covers the website's origin, so a look alike site gets nothing useful
# Toy Schnorr signatures in a small group (from the zero knowledge chapter). Real passkeys use ECDSA P-256 or Ed25519.
import hashlib
import secrets

p = 1099511628443                        # toy safe prime, q = (p - 1) / 2 is prime
q = (p - 1) // 2
g = 4

def H(*parts):
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest(), "big") % q

# Registration: the authenticator makes a new key pair just for this site. The server keeps only the public key.
private = secrets.randbelow(q)
public = pow(g, private, p)
registered_origin = "https://bank.example"

def authenticator_sign(challenge, origin):
    # the browser, not the user, fills in the origin it is really talking to
    r = secrets.randbelow(q)
    t = pow(g, r, p)
    c = H(t, challenge, origin)
    return origin, t, (r + c * private) % q

def server_verify(challenge, response):
    origin, t, s = response
    if origin != registered_origin:
        return "rejected: signed for " + origin
    c = H(t, challenge, origin)
    return "accepted" if pow(g, s, p) == t * pow(public, c, p) % p else "rejected: bad signature"

challenge = secrets.token_hex(16)        # fresh random challenge from the real bank
print("user on the real site:", server_verify(challenge, authenticator_sign(challenge, "https://bank.example")))

# A phishing site relays the bank's challenge, but the browser signs the phishing origin
relayed = authenticator_sign(challenge, "https://bank-example.login.test")
print("phisher relays it:    ", server_verify(challenge, relayed))

# Changing the origin field after signing breaks the signature
origin, t, s = relayed
print("phisher edits origin: ", server_verify(challenge, ("https://bank.example", t, s)))
print("replay of an old login:", server_verify(secrets.token_hex(16), authenticator_sign(challenge, "https://bank.example")))
''', long=True)

K.code('kerberos', r'''
# Kerberos in miniature: a trusted KDC hands out tickets so passwords never cross the network
# Toy authenticated encryption from SHA-256 and HMAC. Real Kerberos uses AES (RFC 3962, RFC 8009).
import hashlib
import hmac
import json
import secrets

def stream(key, nonce, n):               # keystream: SHA-256 of key, nonce and a counter
    return b"".join(hashlib.sha256(key + nonce + i.to_bytes(4, "big")).digest() for i in range(n // 32 + 1))

def seal(key, obj):
    data = json.dumps(obj).encode()
    nonce = secrets.token_bytes(12)
    body = bytes(a ^ b for a, b in zip(data, stream(key, nonce, len(data))))
    return nonce + body + hmac.new(key, nonce + body, hashlib.sha256).digest()

def unseal(key, blob):
    nonce, body, tag = blob[:12], blob[12:-32], blob[-32:]
    if not hmac.compare_digest(tag, hmac.new(key, nonce + body, hashlib.sha256).digest()):
        raise ValueError("wrong key or tampered ticket")
    return json.loads(bytes(a ^ b for a, b in zip(body, stream(key, nonce, len(body)))))

def key_from_password(pw, salt):         # real Kerberos: PBKDF2 string to key
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 10000)

# Long term keys, known to the KDC only
asha_key = key_from_password("Correct-Horse-41", "EXAMPLE.ORGasha")
krbtgt_key = secrets.token_bytes(32)     # the KDC's own key. Stealing it allows "golden tickets".
files_key = secrets.token_bytes(32)      # the file server's key

# 1. AS exchange: Asha asks for a ticket granting ticket (TGT). No password is sent.
s1 = secrets.token_bytes(16).hex()
tgt = seal(krbtgt_key, {"user": "asha", "session": s1, "expires": 36000})
as_reply = seal(asha_key, {"session": s1})           # only someone with Asha's password can open this
s1_client = unseal(key_from_password("Correct-Horse-41", "EXAMPLE.ORGasha"), as_reply)["session"]
print("1. Asha opened the AS reply with her password: session key", s1_client[:8], "...")

# 2. TGS exchange: show the TGT and ask for a ticket to the file server
inside = unseal(krbtgt_key, tgt)                    # the KDC reads its own TGT
s2 = secrets.token_bytes(16).hex()
service_ticket = seal(files_key, {"user": inside["user"], "session": s2})
tgs_reply = seal(bytes.fromhex(inside["session"]), {"session": s2})
s2_client = unseal(bytes.fromhex(s1_client), tgs_reply)["session"]
print("2. Got a service ticket for the file server")

# 3. AP exchange: the file server opens the ticket with its own key, no call to the KDC needed
print("3. File server sees user:", unseal(files_key, service_ticket)["user"], "| shared session key matches:", unseal(files_key, service_ticket)["session"] == s2_client)

# A wrong password cannot open the AS reply
try:
    unseal(key_from_password("guess123", "EXAMPLE.ORGasha"), as_reply)
except ValueError as e:
    print("wrong password:", e)
''', long=True)

K.code('jwt_check', r'''
# JSON Web Tokens (RFC 7519): how they are signed and the checks a server must never skip
import base64
import hashlib
import hmac
import json

SECRET = b"server-side secret, 32+ random bytes in real life"

def b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def unb64(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))

def make(claims):
    header = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = b64(json.dumps(claims).encode())
    sig = b64(hmac.new(SECRET, f"{header}.{body}".encode(), hashlib.sha256).digest())
    return f"{header}.{body}.{sig}"

def verify(token, now):
    try:
        header, body, sig = token.split(".")
    except ValueError:
        return "rejected: not three parts"
    if json.loads(unb64(header)).get("alg") != "HS256":
        return "rejected: unexpected algorithm"         # never let the token choose, e.g. "none"
    good = b64(hmac.new(SECRET, f"{header}.{body}".encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(sig, good):
        return "rejected: bad signature"
    claims = json.loads(unb64(body))
    if claims["exp"] < now:
        return "rejected: expired"
    return f"accepted: user {claims['sub']}, role {claims['role']}"

now = 1_700_000_000
token = make({"sub": "asha", "role": "user", "exp": now + 900})
print("token:", token[:40], "...")
print("payload is only encoded, anyone can read it:", unb64(token.split(".")[1]).decode())
print("valid token:   ", verify(token, now))
h, b, s = token.split(".")
admin = b64(json.dumps({"sub": "asha", "role": "admin", "exp": now + 900}).encode())
print("role changed:  ", verify(f"{h}.{admin}.{s}", now))
none_header = b64(json.dumps({"alg": "none", "typ": "JWT"}).encode())
print("alg none trick:", verify(f"{none_header}.{admin}.", now))
print("after 15 min:  ", verify(token, now + 901))
''', long=True)

K.lesson('idea', 'Identification, authentication and authorisation', f'''
{talk('Every login answers three questions in order. Identification is the claim: I am asha. Authentication is the proof: here is something only asha should have. Authorisation, covered in the next chapter, decides what asha may then do. Proofs come in three kinds, called factors: something you know, such as a password or PIN, something you have, such as a phone or security key, and something you are, such as a fingerprint or face. Using two different kinds is multi factor authentication. Passwords are the oldest method in computing. MIT’s Compatible Time Sharing System used them in 1961, and in 1962 a researcher printed the system’s whole password file to get more computer time, perhaps the first password breach. Stolen and reused passwords remain one of the most common ways attackers get in, because people reuse them across sites and fall for phishing pages. This chapter follows the path from passwords to one time codes, to passkeys that cannot be phished, and then to the systems that let one login reach many services: Kerberos inside companies, and OAuth, OpenID Connect and SAML on the web.')}
{src('NIST SP 800-63B-4, Digital Identity Guidelines: Authentication (2025), RFC 4226 (HOTP, 2005), RFC 6238 (TOTP, 2011), W3C Web Authentication Level 2 (2021), FIDO Alliance CTAP 2.1, RFC 4120 (Kerberos V5), RFC 6749 (OAuth 2.0), RFC 7636 (PKCE), OpenID Connect Core 1.0 (2014), OASIS SAML 2.0 (2005), RFC 7519 (JWT), RFC 8725 (JWT best current practices).')}
{wwh('<b>Authentication</b> verifies a claimed identity using one or more factors: knowledge, possession or inherence. It is different from identification (the claim) and authorisation (the permissions).',
     'Every other control assumes the system knows who is asking. Weak authentication lets an attacker become a real user, and most monitoring then sees normal activity.',
     'Check a secret against a stored verifier (a slow salted hash), a code from a shared key (TOTP), a signature from a private key (passkeys), or a trusted third party’s statement (Kerberos tickets, OpenID Connect tokens, SAML assertions).')}
{table(['Factor', 'Examples', 'Main risks'], [
    ['Something you know', 'Password, PIN, pass phrase', 'Guessing, reuse, phishing, breaches'],
    ['Something you have', 'Phone app, security key, smart card, SMS', 'Theft, SIM swap, relay through phishing'],
    ['Something you are', 'Fingerprint, face, iris, voice', 'Cannot be changed if leaked, false accepts, spoofing'],
    ['Context signals', 'Location, device, time, behaviour', 'Used to adjust risk, not as a factor on its own']])}
''', kw=['authentication', 'identification', 'authorisation', 'factors', 'something you know', 'something you have', 'something you are', 'multi factor authentication', 'MFA', 'CTSS'])

K.lesson('passwords', 'Passwords done right', f'''
{talk('Password advice changed a lot in the last decade, mostly because of evidence about how people behave. Old rules forced a capital letter, a digit and a symbol, and a change every 90 days. People responded with predictable patterns such as Summer2024 followed by an exclamation mark, then Autumn2024. NIST’s guidance, SP 800-63B, now says the opposite: favour length over complexity, allow all characters including spaces, do not force periodic changes unless there is a sign of compromise, and check new passwords against lists of breached and common passwords. The 2025 revision asks for at least 15 characters when a password is the only factor, and at least 8 when it is part of multi factor login. A clever way to check breach lists without revealing the password is k anonymity: the Have I Been Pwned service receives only the first five hex characters of the password’s SHA-1 hash and returns every breached hash with that prefix, and the check finishes on the user’s own device. On the server, passwords must be stored with a slow salted hash such as Argon2id, scrypt or bcrypt, covered in the hashing chapter, and login attempts must be rate limited. Rate limits matter enormously: a six digit PIN with ten tries is nearly impossible to guess online. Password managers make long unique passwords practical, and credential stuffing, where attackers try passwords leaked from one site on many others, only works when passwords are reused.')}
{run('password_policy')}
{wwh('<b>Password policy</b>: rules for choosing, checking, storing and limiting attempts on passwords.',
     'Passwords remain the most common first factor, and reuse plus phishing make them the most common way in.',
     'Require length (15 or more alone, 8 or more with MFA), block breached and common passwords, never force pointless changes, hash with Argon2id or bcrypt, rate limit and lock out gradually, and encourage password managers.')}
{fxs(fx('Online guessing', 'P(success) = guesses allowed / size of the space', '6 digit PIN with 10 tries: 10 / 10<sup>6</sup> = 0.001%. 100 tries a day for a year: 3.65%.', key=True),
     fx('Pass phrase strength', 'bits = words &times; log<sub>2</sub>(list size)', '4 words from the 7776 word Diceware list: 4 &times; 12.92 = 51.7 bits. 6 words: 77.5 bits.', key=True),
     fx('k anonymity check', 'send SHA-1(password)[0:5], compare the other 35 hex characters locally', 'The server sees one of 16<sup>5</sup> = 1048576 buckets, each holding hundreds of real breached hashes.'))}
{table(['Old rule', 'Modern guidance (NIST SP 800-63B)', 'Why'], [
    ['Must contain upper, lower, digit, symbol', 'No composition rules, allow all characters', 'Rules create predictable patterns'],
    ['Change every 90 days', 'Change only on evidence of compromise', 'Forced changes lead to small, guessable edits'],
    ['Password hints and security questions', 'Not allowed', 'Answers are often public or guessable'],
    ['8 characters is enough', '15 or more alone, 8 or more with MFA', 'Length grows the space fastest'],
    ['Nothing about breaches', 'Block passwords found in breach lists', 'Attackers try those first']])}
''', kw=['password policy', 'NIST SP 800-63B', 'length over complexity', 'breached passwords', 'k anonymity', 'Have I Been Pwned', 'credential stuffing', 'password manager', 'rate limiting', 'Diceware', 'pass phrase'])

K.lesson('mfa', 'One time codes and multi factor authentication', f'''
{talk('Multi factor authentication asks for a second proof of a different kind, so a stolen password alone is not enough. The most common second factor is a one time code. HOTP, defined in RFC 4226 in 2005, computes an HMAC of a shared secret key and a counter, then cuts it down to six digits by a step called dynamic truncation. TOTP, RFC 6238 from 2011, uses the number of 30 second slots since 1970 as the counter, so the code changes every half minute. Authenticator apps and servers share the secret once, usually through a QR code, and then compute the same codes independently. SMS codes are weaker: attackers can take over a phone number by convincing a mobile carrier to move it to their SIM card, a SIM swap, which hijacked Twitter’s chief executive’s own account in 2019, and NIST classes SMS as a restricted authenticator. Push notifications that ask “Is this you?” are convenient but suffer from fatigue attacks, where attackers send prompts until a tired user approves, as happened at Uber in 2022. Number matching helps. But all of these share one weakness: a phishing page can ask the user for the code and relay it to the real site within seconds. Only phishing resistant methods, covered next, stop that.')}
{viz('cytotp')}
{run('totp')}
{wwh('<b>TOTP</b>: code = Truncate(HMAC(K, floor(t / 30))) mod 10<sup>digits</sup>. <b>HOTP</b> uses a counter instead of time.',
     'It blocks attacks that use only a stolen or guessed password, works offline on the phone, and needs no extra hardware.',
     'HMAC the 8 byte counter, take offset = last byte &amp; 0x0F, read 4 bytes there, clear the top bit, take the remainder mod 10<sup>6</sup>. Servers accept one slot either side for clock drift and block reuse of a code.')}
{fxs(fx('HOTP', 'HOTP(K, C) = (DT(HMAC-SHA-1(K, C)) &amp; 0x7FFFFFFF) mod 10<sup>d</sup>', 'RFC 4226 key "12345678901234567890": C = 0 gives 755224, C = 1 gives 287082.', key=True),
     fx('TOTP', 'T = floor((t &minus; T<sub>0</sub>) / X), X = 30 s, then HOTP(K, T)', 'RFC 6238 SHA-256 at t = 59: T = 1, code 46119246 (8 digits).', key=True),
     fx('Guessing a code', 'P = window slots &times; tries / 10<sup>d</sup>', '3 slots, 1 try, 6 digits: 3 in a million. With 5 tries before lockout: 15 in a million.'))}
{table(['Second factor', 'Stops password reuse', 'Stops real time phishing', 'Main weakness'], [
    ['SMS code', 'Yes', 'No', 'SIM swap, interception'],
    ['Authenticator app (TOTP)', 'Yes', 'No', 'Relay through a fake page'],
    ['Push approval', 'Yes', 'No', 'Fatigue attacks'],
    ['Push with number matching', 'Yes', 'No (a fake page can show the number)', 'Relay still possible'],
    ['Passkey or security key (FIDO2)', 'Yes', 'Yes', 'Account recovery paths, lost devices']])}
''', kw=['MFA', 'one time password', 'HOTP', 'TOTP', 'RFC 4226', 'RFC 6238', 'dynamic truncation', 'authenticator app', 'SMS', 'SIM swap', 'push notification', 'MFA fatigue', 'number matching', 'Uber 2022'])

K.lesson('passkeys', 'Passkeys: phishing resistant login', f'''
{talk('Passkeys replace a shared secret with a key pair. When you register with a site, your device creates a new private key that never leaves it, usually protected by a secure chip, and sends the site only the public key. To log in, the site sends a random challenge, and your device signs it after you unlock it with a fingerprint, face or PIN. The site checks the signature with the stored public key. A breach of the site leaks only public keys, which are useless to attackers. The key to phishing resistance is that the browser includes the origin it is really talking to, such as https colon slash slash bank.example, in the data that is signed, and the private key is tied to the site it was created for. A look alike phishing domain cannot get a valid signature for the real bank, however convincing the page looks, and the user cannot be tricked into making one. The standards are FIDO2 from the FIDO Alliance, founded in 2013, and the W3C’s Web Authentication API, a Recommendation since 2019. In 2022 Apple, Google and Microsoft announced passkeys that sync across a user’s devices. Google reported in 2018 that after moving its employees to security keys, none of its more than 85000 staff had their work accounts phished.')}
{viz('cyphish')}
{run('passkey')}
{wwh('<b>A passkey</b> is a FIDO2 / WebAuthn credential: a per site key pair, with the private key held by the user’s device and the public key stored by the site.',
     'It removes shared secrets from servers, stops credential stuffing, and is phishing resistant because signatures are bound to the real origin.',
     'Registration: the authenticator makes (sk, pk) for this relying party and returns pk. Login: the site sends a challenge, the browser builds client data with the challenge and origin, and the authenticator signs it after user verification.')}
{steps('A WebAuthn login', [
    'The site sends a fresh random challenge and its relying party ID (bank.example).',
    'The browser checks the page’s real origin matches that ID and builds client data: challenge, origin, type.',
    'The authenticator asks for a fingerprint, face or PIN, then signs the authenticator data and a hash of the client data.',
    'The site checks the signature with the stored public key, the challenge, the origin and a counter or flags.',
    'A phishing domain fails at step 2 or the site rejects the origin at step 4.'])}
{note('Passkeys move the weak point to account recovery. If a lost passkey can be reset by email or SMS alone, attackers will target that path. Offer several passkeys or a recovery key, and protect recovery as strongly as login.', 'warn')}
''', kw=['passkey', 'FIDO2', 'WebAuthn', 'CTAP', 'security key', 'public key authentication', 'challenge response', 'origin binding', 'phishing resistant', 'relying party', 'account recovery'])

K.lesson('sso', 'Single sign on: Kerberos, SAML, OAuth and OpenID Connect', f'''
{talk('Single sign on lets a user log in once and use many services. Inside companies the classic system is Kerberos, designed at MIT for Project Athena in the 1980s and the basis of Microsoft Active Directory since Windows 2000. A trusted Key Distribution Centre shares a key with every user and service. After one login the user holds a ticket granting ticket and exchanges it for tickets to individual services, so passwords never cross the network. Two famous attacks show its limits: Kerberoasting, described by Tim Medin in 2014, requests service tickets that are encrypted with service account passwords and guesses them offline, and a stolen krbtgt key lets attackers forge golden tickets. On the web, SAML 2.0, from 2005, sends signed XML assertions from an identity provider to business applications. OAuth 2.0, RFC 6749 from 2012, is about authorisation: it lets an app act for a user on an API with an access token, without ever seeing the password. Because OAuth on its own does not say who the user is, OpenID Connect, finished in 2014, adds an ID token, usually a signed JSON Web Token, for login. Public clients such as phone apps must use PKCE so a stolen authorisation code is useless. Many breaches come from small verification mistakes, such as accepting a token signed with the “none” algorithm, so libraries must pin the expected algorithm and check every claim.')}
{viz('cykerberos')}
{run('kerberos')}
{run('jwt_check')}
{table(['Protocol', 'Year', 'Main use', 'Token', 'Classic pitfall'], [
    ['Kerberos 5', '1993, RFC 4120 in 2005', 'Company networks, Active Directory', 'Tickets encrypted with service keys', 'Kerberoasting, golden tickets, clock skew'],
    ['SAML 2.0', '2005', 'Enterprise web SSO', 'Signed XML assertion', 'XML signature wrapping, golden SAML (used in the SolarWinds intrusion)'],
    ['OAuth 2.0', '2012', 'Delegated API access', 'Access token (often opaque or JWT)', 'Using it as login, open redirects, missing PKCE'],
    ['OpenID Connect', '2014', 'Login with an identity provider', 'ID token (signed JWT)', 'Not checking audience, issuer, nonce or expiry'],
    ['JWT', 'RFC 7519, 2015', 'Signed claims', 'header.payload.signature', 'alg none, key confusion, secrets in the payload']])}
{fxs(fx('JWT', 'token = base64url(header) . base64url(payload) . base64url(Sign(key, header.payload))', 'The payload is only encoded, so anyone can read it. The signature stops changes, as the program shows.', key=True),
     fx('PKCE', 'code_challenge = base64url(SHA-256(code_verifier))', 'The app keeps the random verifier, so a stolen authorisation code cannot be exchanged without it.'))}
''', kw=['single sign on', 'SSO', 'Kerberos', 'KDC', 'TGT', 'service ticket', 'Active Directory', 'Kerberoasting', 'golden ticket', 'SAML', 'golden SAML', 'OAuth 2.0', 'access token', 'OpenID Connect', 'ID token', 'JWT', 'alg none', 'PKCE'])

K.lesson('biometrics', 'Biometrics and their error rates', f'''
{talk('Biometric systems measure a body feature, compare it with a stored template, and accept if the match score passes a threshold. No match is perfect, so there are always two kinds of error. A false accept lets the wrong person in, and its rate is the FAR. A false reject turns away the right person, the FRR. Moving the threshold trades one for the other, and the point where they are equal is the equal error rate, a common single number for comparing systems. Apple, for example, states about a 1 in 50000 chance that a random person could unlock a phone with Touch ID and about 1 in 1000000 for Face ID. Biometrics have special risks. You cannot change your fingerprint if a template leaks, so templates should stay on the device in a secure chip, as phones do. Sensors can be fooled by fakes, so liveness detection matters. And laws such as India’s Digital Personal Data Protection Act 2023, Europe’s GDPR and Illinois’ BIPA treat biometric data as especially sensitive. On phones, biometrics usually unlock a local key, such as a passkey, rather than being sent to a server.')}
{fxs(fx('False accept rate', 'FAR = impostor attempts accepted / impostor attempts', '3 accepts in 10000 impostor tries: FAR = 0.03%.', key=True),
     fx('False reject rate', 'FRR = genuine attempts rejected / genuine attempts', '50 rejects in 2000 genuine tries: FRR = 2.5%.', key=True),
     fx('Equal error rate', 'EER = the rate at the threshold where FAR = FRR', 'Lower is better. Raising the threshold lowers FAR and raises FRR.'),
     fx('Expected false accepts', 'E = attempts &times; FAR', 'A thief trying 5 random fingers against FAR 1/50000: 5/50000 = 0.01%.'))}
{note('A biometric is an identifier, not a secret: your face is in photos and your fingerprints are on every glass. Treat it as a convenient way to unlock a key held on the device, combined with a PIN fallback and attempt limits.', 'tip')}
''', kw=['biometrics', 'FAR', 'FRR', 'false accept rate', 'false reject rate', 'equal error rate', 'EER', 'liveness detection', 'Touch ID', 'Face ID', 'template', 'DPDP Act', 'BIPA'])

K.lesson('versus', 'Authentication methods compared', f'''
{talk('When comparing methods, ask three questions: can it be guessed, can it be stolen in a breach, and can it be phished. Passwords fail all three unless managed well. One time codes stop guessing and breach reuse but can be phished. Passkeys and security keys resist all three, which is why governments and large companies now ask for phishing resistant MFA. Kerberos, SAML and OpenID Connect are not factors themselves but ways to carry the result of one strong login to many services.')}
{versus('Login methods side by side', ['', 'Password', 'SMS code', 'TOTP app', 'Push', 'Passkey'], [
    ['Resists guessing', 'Only if long and rate limited', 'Yes', 'Yes', 'Yes', 'Yes'],
    ['Server breach leaks it', 'Hashes, crackable if weak', 'No long term secret', 'Shared secret on server', 'No', 'Only public keys'],
    ['Resists phishing relay', 'No', 'No', 'No', 'No', 'Yes, origin bound'],
    ['Other risks', 'Reuse, stuffing', 'SIM swap', 'Seed theft', 'Fatigue', 'Recovery paths'],
    ['NIST 800-63B view', 'Allowed with rules', 'Restricted', 'Allowed', 'Allowed', 'Phishing resistant']],
    'Move users to passkeys, keep TOTP as a fallback rather than SMS, and protect account recovery as strongly as login.')}
''', kw=['comparison', 'password', 'SMS', 'TOTP', 'push', 'passkey', 'phishing resistant MFA'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner uses a password manager, turns on two step login and prefers passkeys. A college student can implement TOTP from the RFC, explain why SMS and push can be phished, set password policy by NIST, and describe Kerberos, OAuth and OpenID Connect flows. A masters student studies protocol details and attacks: OAuth redirect and mix up attacks, SAML signature wrapping, Kerberos delegation abuse, JWT key confusion, WebAuthn attestation and the security of account recovery. Researchers work on formal verification of authentication protocols, usable security studies of how people actually log in, password hardening services that resist offline cracking, and post quantum signatures for passkeys.')}
{ladder(
    '<p>Use long unique passwords in a manager, turn on MFA, prefer passkeys, and never type a code into a page you reached from an email link.</p>',
    '<p>NIST password rules and k anonymity checks, HOTP and TOTP maths, why codes can be relayed, WebAuthn origin binding, Kerberos tickets, OAuth versus OpenID Connect, JWT checks, FAR and FRR.</p>',
    '<p>OAuth mix up and redirect attacks, PKCE, SAML wrapping, Kerberos delegation and golden tickets, JWT key confusion, attestation, risk based authentication and recovery design.</p>',
    '<p>Formal proofs of OAuth and FIDO2, usable security research, password hardening (PHE), threshold and post quantum authenticators, and continuous behavioural authentication.</p>')}
{grow('Set up strong logins for yourself and explain each factor.',
      'Implement TOTP and JWT checks and trace Kerberos and OAuth flows.',
      'Find and fix subtle protocol and recovery flaws.')}
''', kw=['beginner', 'expert', 'OAuth mix up', 'SAML wrapping', 'Kerberos delegation', 'attestation', 'formal verification'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Three steps</b>: identify, authenticate, authorise. Factors: know, have, are. MFA uses two kinds.',
    '<b>Passwords</b>: length over complexity (15 or more alone), block breached ones (k anonymity), no forced changes, Argon2id or bcrypt, rate limits.',
    '<b>TOTP</b>: HMAC(K, floor(t/30)), dynamic truncation, mod 10<sup>6</sup>. RFC vectors 755224 and 46119246. SMS, codes and push can be relayed.',
    '<b>Passkeys</b>: per site key pairs, challenge signed with the origin. Phishing resistant, breaches leak only public keys. Protect recovery.',
    '<b>Kerberos</b>: KDC, TGT, service tickets, no password on the wire. Kerberoasting and golden tickets.',
    '<b>Web SSO</b>: SAML assertions, OAuth for API access, OpenID Connect ID tokens for login, PKCE for apps. Pin JWT algorithms, check every claim.',
    '<b>Biometrics</b>: FAR, FRR, EER trade off by threshold. Keep templates on the device, use them to unlock a key.'],
    'Next, Network and Systems 2.2: access control models, from Bell-LaPadula to RBAC and ABAC.')}
{files('Three tasks: online guessing odds with lockout, HOTP from RFC 4226, and a JWT verifier that pins the algorithm and checks expiry.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Which pair is two factor authentication?', ['Password and PIN', 'Password and a code from an authenticator app', 'Two passwords', 'User name and password'], 1, 'Different kinds.', 'Know plus have. A password and a PIN are both things you know.')
K.quiz('e', 'What does modern NIST guidance say about forced password changes every 90 days?', ['Required', 'Do not force them unless there is evidence of compromise', 'Change daily', 'Change yearly'], 1, 'Evidence based.', 'Forced changes produce small predictable edits.')
K.quiz('e', 'Why do passkeys stop phishing?', ['They are long', 'The browser signs the challenge together with the real site origin, so a fake site gets no valid signature', 'They expire quickly', 'They use SMS'], 1, 'Origin.', 'The user cannot be tricked into signing for the wrong site.')
K.quiz('e', 'Authentication answers', ['What may this user do?', 'Is this really the claimed user?', 'Where is the user?', 'Which server is busy?'], 1, 'Proof.', 'Authorisation comes after and decides permissions.')
K.quiz('m', 'Why is SMS a weak second factor?', ['Codes are short', 'Phone numbers can be moved to an attacker’s SIM, and codes can be phished', 'SMS is slow', 'It needs internet'], 1, 'SIM swap.', 'NIST lists SMS as a restricted authenticator.')
K.quiz('m', 'TOTP codes change every 30 seconds because', ['The phone battery', 'The counter is floor(Unix time / 30)', 'Servers reboot', 'HMAC is slow'], 1, 'Time slots.', 'Both sides compute the same slot number from their clocks.')
K.quiz('m', 'Credential stuffing works because', ['Passwords are short', 'People reuse the same password on many sites', 'MFA is broken', 'Hashes are fast'], 1, 'Reuse.', 'Passwords leaked from one site are tried on others. Unique passwords and MFA stop it.')
K.quiz('m', 'OAuth 2.0 on its own is designed for', ['Logging users in', 'Letting an app access an API on a user’s behalf', 'Encrypting disks', 'Firewall rules'], 1, 'Delegation.', 'OpenID Connect adds the ID token that says who the user is.')
K.quiz('m', 'What can anyone do with a JWT they intercept?', ['Nothing', 'Read its payload, because it is only base64url encoded', 'Change it freely', 'Decrypt the signature key'], 1, 'Encoded, not encrypted.', 'Never put secrets in a JWT payload. The signature prevents changes, not reading.')
K.quiz('h', 'What is Kerberoasting?', ['Overheating a KDC', 'Requesting service tickets and guessing the service account password offline from them', 'Replaying TGTs', 'Stealing smart cards'], 1, 'Offline.', 'Long random service passwords or managed service accounts stop it.')
K.quiz('h', 'Why must a JWT verifier pin the expected algorithm?', ['For speed', 'Otherwise an attacker can set alg to none or switch to a key confusion attack', 'Algorithms expire', 'To compress tokens'], 1, 'RFC 8725.', 'The token must not choose how it is checked.')
K.quiz('h', 'Raising a biometric threshold usually', ['Raises FAR and FRR', 'Lowers FAR and raises FRR', 'Lowers both', 'Changes nothing'], 1, 'Trade off.', 'Stricter matching rejects more impostors and more real users.')
K.quiz('h', 'What does PKCE protect in OAuth?', ['The password', 'The authorisation code, which is useless without the secret code verifier', 'The refresh token', 'TLS'], 1, 'RFC 7636.', 'An app that intercepts the code cannot redeem it.')
K.quiz('x', 'In the style of an MIT 6.858 question: number matching stops push fatigue but not a real time phishing proxy. Why?', ['It does', 'The proxy page shows the real number from the bank’s login page, and the user types it into the app as asked', 'Numbers are short', 'Apps are offline'], 1, 'Relay.', 'Only origin bound methods (FIDO2) break the relay, because the browser, not the user, reports the origin.')
K.quiz('x', 'In the style of an IIT Bombay security exam: in Kerberos, why does the AS reply encrypt the session key with the user’s long term key, and the TGT with krbtgt?', ['For speed', 'Only the real user can open the session key, and only the KDC can read or change the TGT', 'To save bandwidth', 'Because of TLS'], 1, 'Two audiences.', 'Each part is readable only by the party that needs it, which is the whole design of tickets.')

K.calc('e', 'A 6 digit PIN allows 10 tries before lockout. What is the chance of guessing it, in millionths?', '10', '10 / 10<sup>6</sup>.', ['10<sup>6</sup> possible PINs.', '10 tries.', eq('10 in a million')], check=10)
K.calc('e', 'How many different 6 digit codes are there?', '1000000', '10<sup>6</sup>.', ['Each digit 0 to 9.', '10<sup>6</sup>.', eq('1000000')], check=10 ** 6)
K.calc('e', 'Unix time t = 59 with 30 second slots. What is the TOTP counter T?', '1', 'floor(59 / 30).', ['59 / 30 = 1.97.', 'Round down.', eq('T = 1')], check=59 // 30)
K.calc('m', 'Unix time 1234567890. What is the TOTP counter T?', '41152263', 'floor(t / 30).', ['1234567890 / 30 = 41152263.0.', 'Round down.', eq('T = 41152263')], check=1234567890 // 30)
K.calc('m', 'Dynamic truncation: the last HMAC byte is 0x5A. What is the offset?', '10', '0x5A &amp; 0x0F.', ['0x5A = 0101 1010.', 'Low 4 bits 1010 = 10.', eq('offset 10')], check=0x5A & 0x0F)
K.calc('m', 'A Diceware pass phrase of 6 words from 7776 words has how many bits? Round to a whole number.', '78', '6 &times; log<sub>2</sub> 7776.', ['log<sub>2</sub> 7776 = 12.925.', '&times; 6 = 77.5.', eq('about 78 bits')], check=round(6 * __import__('math').log2(7776)))
K.calc('m', 'How many k anonymity buckets do 5 hex characters give?', '1048576', '16<sup>5</sup>.', ['Each hex character has 16 values.', '16<sup>5</sup> = 2<sup>20</sup>.', eq('1048576')], check=16 ** 5)
K.calc('m', 'A server accepts the TOTP slot before, now and after, and allows 5 tries. Chance a random guesser wins, in millionths, with 6 digits?', '15', '3 &times; 5 / 10<sup>6</sup>.', ['3 valid codes at any time.', '5 tries.', eq('15 in a million')], check=3 * 5)
K.calc('h', 'An impostor test: 3 accepts out of 10000 tries. What is the FAR in hundredths of a percent?', '3', '3 / 10000 = 0.03%.', ['3 / 10000 = 0.0003.', '= 0.03% = 3 hundredths of a percent.', eq('0.03%')], check=3)
K.calc('h', 'A genuine user test: 50 rejects out of 2000 tries. What is the FRR in percent?', '2.5', '50 / 2000.', ['50 / 2000 = 0.025.', '= 2.5%.', eq('FRR = 2.5%')], check=round(50 / 2000 * 100, 1))
K.calc('h', '100 online guesses a day for a year against a 6 digit PIN. Chance of success in percent?', '3.65', '36500 / 10<sup>6</sup>.', ['365 &times; 100 = 36500.', '36500 / 10<sup>6</sup> = 0.0365.', eq('3.65%')], check=round(36500 / 10 ** 6 * 100, 2))
K.calc('h', 'Kerberos allows 5 minutes of clock skew. How many seconds is that?', '300', '5 &times; 60.', ['Authenticators older than this are rejected.', '5 &times; 60.', eq('300 s')], check=5 * 60)
K.calc('x', 'A thief tries 5 fingers against a sensor with FAR 1 in 50000. What is the chance of a false accept, in millionths? Round to a whole number.', '100', '5 / 50000.', ['5 / 50000 = 0.0001.', '= 100 in a million.', eq('100')], check=round(5 / 50000 * 10 ** 6))
K.calc('x', 'An 8 digit TOTP truncates a 31 bit number. How many bits of that number can a code hold at most? Round down to a whole number.', '26', 'log<sub>2</sub>(10<sup>8</sup>).', ['10<sup>8</sup> codes.', 'log<sub>2</sub> 10<sup>8</sup> = 26.6.', eq('26 bits')], check=int(__import__('math').log2(10 ** 8)))

K.assign('guess_odds', 'e', 'Online guessing odds',
         '<p>Write <code>guess_odds(tries, digits)</code> that returns the chance of guessing a random numeric code of the given length within the number of tries: tries / 10<sup>digits</sup>, but never more than 1.</p>',
         '''
def guess_odds(tries, digits):
    # your code here
    pass
''', [('guess_odds(10, 6)', 1e-05), ('guess_odds(3, 4)', 0.0003), ('guess_odds(2000, 3)', 1)],
         '''
def guess_odds(tries, digits):
    return min(1, tries / 10 ** digits)
''', 'Divide, then cap with min(1, ...).', '<p>Lockouts turn a tiny 4 digit space into a strong control. Offline, the same space falls in microseconds.</p>')
K.assign('hotp', 'm', 'HOTP from RFC 4226',
         '<p>Write <code>hotp(secret, counter, digits)</code>. <code>secret</code> is a text string. Compute HMAC-SHA-1 of the counter as 8 big endian bytes, take offset = last byte &amp; 0x0F, read 4 bytes from there as a big endian number, clear the top bit (&amp; 0x7FFFFFFF), take the remainder mod 10<sup>digits</sup>, and return it as a string padded with zeros.</p>',
         '''
import hashlib
import hmac
import struct

def hotp(secret, counter, digits):
    # your code here
    pass
''', [('hotp("12345678901234567890", 0, 6)', '755224'), ('hotp("12345678901234567890", 1, 6)', '287082'), ('hotp("12345678901234567890", 9, 6)', '520489')],
         '''
import hashlib
import hmac
import struct

def hotp(secret, counter, digits):
    mac = hmac.new(secret.encode(), struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = mac[-1] & 0x0F
    code = int.from_bytes(mac[offset:offset + 4], "big") & 0x7FFFFFFF
    return str(code % 10 ** digits).zfill(digits)
''', 'struct.pack(">Q", counter) gives 8 big endian bytes. int.from_bytes(..., "big") reads the 4 bytes.', '<p>These are the RFC 4226 test values. TOTP is the same function with counter = Unix time // 30.</p>')
K.assign('jwt_verify', 'h', 'A safe JWT verifier',
         '<p>Write <code>jwt_verify(token, secret, now)</code> for HS256 tokens. Split into header, payload and signature. Return None if the header’s alg is not "HS256", if the base64url HMAC-SHA-256 of "header.payload" with <code>secret</code> (text) does not equal the signature (use <code>hmac.compare_digest</code>), or if the payload’s exp is less than now. Otherwise return the payload’s sub.</p>',
         '''
import base64
import hashlib
import hmac
import json

def jwt_verify(token, secret, now):
    # your code here
    pass
''', [('jwt_verify("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhc2hhIiwiZXhwIjoyMDAwfQ.5bD7oiqVcBUVub0e5wzgVySQX-Ssuo2FG6iyXMKsOg4", "k3y", 1500)', 'asha'),
      ('jwt_verify("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyYXZpIiwiZXhwIjoxMDAwfQ.DdSAkRRs5h6rdcwu7AG77uA5vM-L9RkEeQHE9hPtb1Y", "k3y", 1500)', None),
      ('jwt_verify("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhc2hhIiwiZXhwIjoyMDAwfQ.sYpIBzuiHElL370LtCS2tMuKywvLyzYL6XCeLC4h2R4", "k3y", 1500)', None),
      ('jwt_verify("eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJldmUiLCJleHAiOjIwMDB9.", "k3y", 1500)', None)],
         '''
import base64
import hashlib
import hmac
import json

def b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def unb64(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))

def jwt_verify(token, secret, now):
    header, payload, sig = token.split(".")
    if json.loads(unb64(header)).get("alg") != "HS256":
        return None
    good = b64(hmac.new(secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(sig, good):
        return None
    claims = json.loads(unb64(payload))
    if claims["exp"] < now:
        return None
    return claims["sub"]
''', 'Add back the "=" padding before base64url decoding. Check alg first, then the signature, then exp.', '<p>The four tests are a valid token, an expired one, one signed with a different key, and an alg none forgery. Real verifiers also check iss, aud and nbf.</p>')

K.must('Basics', 'Identify, authenticate, authorise. Factors: know, have, are. MFA = two kinds. Passwords since CTSS 1961.')
K.must('Passwords', 'NIST 800-63B: length (15 alone, 8 with MFA), no composition rules, no forced changes, block breached (k anonymity, 16<sup>5</sup> buckets), rate limit.')
K.must('OTP', 'HOTP = DT(HMAC-SHA1(K, C)) &amp; 0x7FFFFFFF mod 10<sup>6</sup> (RFC 4226). TOTP C = floor(t/30) (RFC 6238). SMS restricted, push fatigue.')
K.must('Passkeys', 'FIDO2 / WebAuthn. Per site key pair, sign challenge + origin. Phishing resistant, breach leaks only public keys. Guard recovery.')
K.must('SSO', 'Kerberos: KDC, TGT, tickets, 5 min skew, Kerberoasting, golden ticket. SAML 2.0. OAuth 2.0 (access), OIDC (ID token), PKCE.')
K.must('JWT and biometrics', 'header.payload.sig, payload readable. Pin alg, check exp, iss, aud. FAR, FRR, EER, keep templates on device.')

T = K.topic(
    slug='cy-authn', topic='cy-authn', step=(2, 'Identity and access', 'cy-s2', 'How systems prove who you are, from passwords and MFA to passkeys and Kerberos, and how they decide what you may do.', 'Intermediate'),
    title='Authentication: passwords, MFA, passkeys and single sign on', short='Authentication', badge='2.1', minutes=85,
    lead='How systems prove who you are: factors, NIST password rules with breach checks by k anonymity, HOTP and TOTP built from the RFCs, why SMS, codes and push can be phished, passkeys and origin binding, Kerberos tickets and Kerberoasting, SAML, OAuth, OpenID Connect and JWT pitfalls, and biometric error rates.',
    desc='authentication, identification, authorisation, factors, MFA, two factor, password policy, NIST SP 800-63B, breached passwords, k anonymity, credential stuffing, password manager, HOTP, TOTP, RFC 4226, RFC 6238, authenticator app, SMS, SIM swap, push fatigue, number matching, passkey, FIDO2, WebAuthn, phishing resistant, Kerberos, KDC, TGT, Kerberoasting, golden ticket, Active Directory, SAML, OAuth 2.0, OpenID Connect, ID token, PKCE, JWT, alg none, biometrics, FAR, FRR, equal error rate',
    summary='factors, password rules, TOTP, phishing and passkeys, Kerberos, SAML, OAuth and OpenID Connect, JWT, biometrics.',
    keywords=['authentication', 'MFA', 'TOTP', 'passkey', 'WebAuthn', 'Kerberos', 'OAuth', 'OpenID Connect', 'JWT', 'biometrics'],
    recap='<p>Strong authentication means proofs that cannot be guessed, reused after a breach or phished. Passkeys meet all three, and single sign on carries one strong login to many services.</p>',
    added='2026-11-15')
