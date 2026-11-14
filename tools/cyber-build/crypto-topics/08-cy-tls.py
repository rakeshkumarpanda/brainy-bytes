# Cryptography 3.1: certificates, PKI and TLS 1.3. Checked against RFC 5280, RFC 6962, RFC 8446, RFC 8448 (the key
# schedule values were checked by running the program), RFC 8555, RFC 6797, RFC 8996, the CA/Browser Forum Baseline
# Requirements and ballot SC-081 (2025), and the BEAST, CRIME, Lucky Thirteen, Heartbleed, POODLE, FREAK, Logjam, DROWN
# and ROBOT papers and advisories.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-tls')
K = Kit()

K.code('x509_real', r'''
# Real X.509 certificates: make a small CA, issue a server certificate, and verify it (pip install cryptography)
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.x509.verification import PolicyBuilder, Store, VerificationError
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

now = datetime.datetime(2026, 11, 14, tzinfo=datetime.timezone.utc)

def name(text):
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, text)])

ca_key = ec.generate_private_key(ec.SECP256R1())
ca_cert = (x509.CertificateBuilder()
           .subject_name(name("Demo Root CA")).issuer_name(name("Demo Root CA"))
           .public_key(ca_key.public_key()).serial_number(x509.random_serial_number())
           .not_valid_before(now - datetime.timedelta(days=1)).not_valid_after(now + datetime.timedelta(days=3650))
           .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
           .add_extension(x509.KeyUsage(False, False, False, False, False, True, True, False, False), critical=True)
           .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()), critical=False)
           .sign(ca_key, hashes.SHA256()))

site_key = ec.generate_private_key(ec.SECP256R1())
site_cert = (x509.CertificateBuilder()
             .subject_name(name("shop.example")).issuer_name(ca_cert.subject)
             .public_key(site_key.public_key()).serial_number(x509.random_serial_number())
             .not_valid_before(now - datetime.timedelta(days=1)).not_valid_after(now + datetime.timedelta(days=90))
             .add_extension(x509.SubjectAlternativeName([x509.DNSName("shop.example")]), critical=False)
             .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
             .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
             .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()), critical=False)
             .sign(ca_key, hashes.SHA256()))

print("subject:", site_cert.subject.rfc4514_string(), "| issuer:", site_cert.issuer.rfc4514_string())
print("valid until:", site_cert.not_valid_after_utc.date(), "| signature hash:", site_cert.signature_hash_algorithm.name)

store = Store([ca_cert])
verifier = PolicyBuilder().store(store).time(now).build_server_verifier(x509.DNSName("shop.example"))
chain = verifier.verify(site_cert, [])
print("verified chain length:", len(chain))

wrong = PolicyBuilder().store(store).time(now).build_server_verifier(x509.DNSName("bank.example"))
try:
    wrong.verify(site_cert, [])
except VerificationError:
    print("bank.example rejected: the name does not match")
''')

K.code('chain_verify', r'''
# How a browser checks a certificate chain, with toy RSA keys and certificates as dictionaries
import hashlib
from datetime import date

def make_key(p, q, e=65537):
    n = p * q
    return {"n": n, "e": e, "d": pow(e, -1, (p - 1) * (q - 1))}

def digest(cert, n):
    text = repr(sorted((k, v) for k, v in cert.items() if k != "sig"))
    return int.from_bytes(hashlib.sha256(text.encode()).digest(), "big") % n

def sign(cert, issuer_key):
    cert["sig"] = pow(digest(cert, issuer_key["n"]), issuer_key["d"], issuer_key["n"])

root_key = make_key(1000000007, 998244353)              # toy primes, far too small for real use
mid_key = make_key(1000000009, 999999937)
site_key = make_key(1000000021, 999999929)

root = {"subject": "Toy Root CA", "issuer": "Toy Root CA", "ca": True, "key": (root_key["n"], 65537),
        "from": date(2020, 1, 1), "to": date(2035, 1, 1)}
mid = {"subject": "Toy Issuing CA", "issuer": "Toy Root CA", "ca": True, "key": (mid_key["n"], 65537),
       "from": date(2024, 1, 1), "to": date(2029, 1, 1)}
leaf = {"subject": "shop.example", "issuer": "Toy Issuing CA", "ca": False, "key": (site_key["n"], 65537),
        "names": ["shop.example", "www.shop.example"], "from": date(2026, 9, 1), "to": date(2026, 11, 30)}
sign(root, root_key)                                     # a root signs itself
sign(mid, root_key)
sign(leaf, mid_key)

trusted = {"Toy Root CA": root}                          # the browser's root store
revoked = set()

def check(chain, host, today):
    for cert, issuer in zip(chain, chain[1:] + [None]):
        issuer = issuer or trusted.get(cert["issuer"])
        if issuer is None:
            return "unknown issuer: " + cert["issuer"]
        n, e = issuer["key"]
        if pow(cert["sig"], e, n) != digest(cert, n):
            return "bad signature on " + cert["subject"]
        if not (cert["from"] <= today <= cert["to"]):
            return "expired or not yet valid: " + cert["subject"]
        if cert is not chain[0] and not cert["ca"]:
            return cert["subject"] + " is not allowed to issue certificates"
        if cert["subject"] in revoked:
            return "revoked: " + cert["subject"]
    if host not in chain[0]["names"]:
        return "name mismatch: certificate is not for " + host
    return "OK, chain trusted"

today = date(2026, 11, 14)
print("1.", check([leaf, mid], "shop.example", today))
print("2.", check([leaf, mid], "bank.example", today))
print("3.", check([leaf, mid], "shop.example", date(2026, 12, 25)))
leaf["names"].append("bank.example")                     # tampering breaks the signature
print("4.", check([leaf, mid], "bank.example", today))
leaf["names"].remove("bank.example")
revoked.add("shop.example")
print("5.", check([leaf, mid], "shop.example", today))
''', long=True)

K.code('ssl_context', r'''
# Safe TLS settings in Python's standard ssl module (no network needed to inspect them)
import ssl

ctx = ssl.create_default_context()        # the right starting point for a client
print("checks the server name:", ctx.check_hostname)
print("requires a valid certificate:", ctx.verify_mode == ssl.CERT_REQUIRED)
print("oldest version allowed:", ctx.minimum_version.name)

ctx.minimum_version = ssl.TLSVersion.TLSv1_3   # only when every server you talk to supports TLS 1.3
print("after hardening:", ctx.minimum_version.name)

# The dangerous pattern seen in many tutorials. It turns off every check above.
bad = ssl.create_default_context()
bad.check_hostname = False
bad.verify_mode = ssl.CERT_NONE
print("bad context verifies certificates:", bad.verify_mode != ssl.CERT_NONE, "-> any man in the middle wins")

print("OpenSSL in use:", ssl.OPENSSL_VERSION.split()[0], ssl.OPENSSL_VERSION.split()[1])
print("TLS 1.3 supported:", ssl.HAS_TLSv1_3)
''')

K.code('ct_merkle', r'''
# Certificate Transparency: a public append only log built as a Merkle tree (RFC 6962 hashing)
import hashlib

def leaf_hash(entry):
    return hashlib.sha256(b"\x00" + entry).digest()      # 0x00 marks a leaf

def node_hash(left, right):
    return hashlib.sha256(b"\x01" + left + right).digest()   # 0x01 marks an inner node

def root(hashes):
    if len(hashes) == 1:
        return hashes[0]
    k = 1
    while k * 2 < len(hashes):                          # largest power of two below the size
        k = k * 2
    return node_hash(root(hashes[:k]), root(hashes[k:]))

def proof(hashes, index):                               # the sibling hashes from the leaf up to the root
    if len(hashes) == 1:
        return []
    k = 1
    while k * 2 < len(hashes):
        k = k * 2
    if index < k:
        return proof(hashes[:k], index) + [("R", root(hashes[k:]))]
    return proof(hashes[k:], index - k) + [("L", root(hashes[:k]))]

def verify(entry, path, expected_root):
    h = leaf_hash(entry)
    for side, sibling in path:
        h = node_hash(h, sibling) if side == "R" else node_hash(sibling, h)
    return h == expected_root

certs = [f"certificate {i} for site{i}.example".encode() for i in range(7)]
hashes = [leaf_hash(c) for c in certs]
signed_root = root(hashes)                              # the log signs this and publishes it
print("log of", len(certs), "certificates, root", signed_root.hex()[:16], "...")

path = proof(hashes, 5)
print("inclusion proof for certificate 5 has", len(path), "hashes (about log2 of the log size)")
print("certificate 5 is in the log:", verify(certs[5], path, signed_root))
print("a forged certificate passes:", verify(b"certificate 5 for evil.example", path, signed_root))
print("a log of 1 billion entries needs about", (10 ** 9).bit_length(), "hashes per proof")
''', long=True)

K.code('tls_keyschedule', r'''
# The TLS 1.3 key schedule (RFC 8446, section 7.1), checked against the RFC 8448 example handshake
import hashlib
import hmac

def hkdf_extract(salt, ikm):
    return hmac.new(salt, ikm, hashlib.sha256).digest()

def hkdf_expand_label(secret, label, context, length):
    full = b"tls13 " + label
    info = length.to_bytes(2, "big") + bytes([len(full)]) + full + bytes([len(context)]) + context
    out, block, i = b"", b"", 1
    while len(out) < length:
        block = hmac.new(secret, block + info + bytes([i]), hashlib.sha256).digest()
        out, i = out + block, i + 1
    return out[:length]

def derive_secret(secret, label, messages):
    return hkdf_expand_label(secret, label, hashlib.sha256(messages).digest(), 32)

zeros = bytes(32)
early = hkdf_extract(zeros, zeros)                        # no pre shared key
print("early secret:    ", early.hex()[:16], "...")
print("matches RFC 8448:", early.hex() == "33ad0a1c607ec03b09e6cd9893680ce210adf300aa1f2660e1b22e10f170f92a")

derived = derive_secret(early, b"derived", b"")
print("derived:         ", derived.hex()[:16], "...")
print("matches RFC 8448:", derived.hex() == "6f2615a108c702c5678f54fc9dbab69716c076189c48250cebeac3576c3611ba")

ecdhe = bytes.fromhex("8bd4054fb55b9d63fdfbacf9f04b9f0d35e6d63f537563efd46272900f89492d")   # X25519 result in RFC 8448
handshake = hkdf_extract(derived, ecdhe)
print("handshake secret:", handshake.hex()[:16], "...")
print("matches RFC 8448:", handshake.hex() == "1dc826e93606aa6fdc0aadc12f741b01046aa6b99f691ed221a9f0ca043fbeac")

master = hkdf_extract(derive_secret(handshake, b"derived", b""), zeros)
print("master secret:   ", master.hex()[:16], "...")
print("every traffic key comes from these three steps, so it depends on the fresh ECDHE value")
''', long=True)

K.lesson('idea', 'Why we need PKI', f'''
{talk('Public key cryptography has a gap that the maths alone cannot fill. When your browser receives a public key from shop dot example, how does it know the key really belongs to that shop and not to someone in the middle of the network? The answer the internet settled on is the public key infrastructure, PKI for short. A small number of certificate authorities, CAs, check who owns a domain and then sign a certificate, a document that binds a name to a public key. Browsers and operating systems ship a list of about 150 trusted root authorities. The model goes back to the X.509 standard of 1988 and to Netscape’s SSL in the mid 1990s. It has failed in public several times. In 2011 the Dutch authority DigiNotar was hacked, and a fake certificate for Google was used to spy on users in Iran. DigiNotar was removed from every browser and went bankrupt within weeks. Those failures led to the defences in this chapter: Certificate Transparency logs, shorter certificate lifetimes, and TLS 1.3, which hides certificates and removes old weak options.')}
{src('RFC 5280 (X.509 profile), RFC 6962 and RFC 9162 (Certificate Transparency), RFC 8446 (TLS 1.3), RFC 8448 (example handshakes), RFC 8555 (ACME), RFC 6797 (HSTS), RFC 8996 (deprecating TLS 1.0 and 1.1), CA/Browser Forum Baseline Requirements and ballot SC-081 (2025).')}
{wwh('<b>PKI</b> (public key infrastructure) is the system of certificate authorities, certificates, root stores and revocation that ties public keys to names such as domain names.',
     'Without it, a man in the middle could hand you his own public key and read everything. Encryption without authentication protects only against passive listeners.',
     'A CA checks that you control a domain, then signs a certificate containing your name and public key. Browsers trust a set of root CAs and verify a chain of signatures from your certificate up to one of them.')}
{table(['Version', 'Year', 'Status'], [
    ['SSL 2.0 and 3.0', '1995, 1996', 'Broken (DROWN, POODLE). Forbidden'],
    ['TLS 1.0 and 1.1', '1999, 2006', 'Deprecated by RFC 8996 in 2021'],
    ['TLS 1.2', '2008', 'Still common. Safe with AEAD suites and ECDHE'],
    ['TLS 1.3', '2018', 'Current. Faster, simpler, encrypted handshake'],
    ['QUIC with TLS 1.3', '2021', 'HTTP/3 transport, joins the transport and TLS handshakes']])}
''', kw=['PKI', 'public key infrastructure', 'certificate authority', 'CA', 'root store', 'X.509', 'SSL', 'DigiNotar', 'TLS versions'])

K.lesson('certs', 'X.509 certificates', f'''
{talk('A certificate is a structured document, encoded in a format called ASN.1 DER, and usually shown as a block of base64 text between BEGIN CERTIFICATE lines. Its core fields are short. The subject is who the certificate is for. The issuer is the authority that signed it. Not Before and Not After give the validity period. The subject public key is the key being vouched for. Then come extensions, and they matter more than the old fields. Subject Alternative Name lists the domain names the certificate is valid for, and browsers ignore the old common name field. Basic Constraints says whether the certificate belongs to a CA that may sign other certificates. Key Usage and Extended Key Usage say what the key may do, such as server authentication. Finally the issuer’s signature covers all of it. Certificates are also getting shorter lived. In 2025 the CA and Browser Forum voted to cut the maximum lifetime of public TLS certificates step by step from 398 days to 47 days by 2029, which pushes everyone towards automatic renewal with the ACME protocol, as Let’s Encrypt has done since 2015.')}
{wwh('An <b>X.509 certificate</b> binds a subject (such as a domain name) to a public key, for a validity period, signed by an issuer. Extensions limit what it can be used for.',
     'It lets a browser trust a public key it has never seen, by trusting the CA that signed it. Its fields decide which names and uses are allowed.',
     'The CA fills in the fields, hashes the to be signed part with SHA-256, and signs the hash with its private key (RSA or ECDSA). Anyone can check the signature with the CA’s public key.')}
{local('x509_real', 'It needs the cryptography package: python3 -m pip install cryptography.')}
{table(['Field or extension', 'Meaning', 'Example'], [
    ['Subject, Issuer', 'Who it is for, who signed it', 'CN=shop.example, CN=Example Issuing CA'],
    ['Validity', 'Not Before, Not After', '90 days for Let’s Encrypt, at most 47 days from 2029'],
    ['Subject Alternative Name', 'Names the certificate covers', 'shop.example, *.shop.example'],
    ['Basic Constraints', 'CA or not, path length', 'CA:TRUE, pathlen:0 for an issuing CA'],
    ['Key Usage, Extended Key Usage', 'What the key may do', 'digitalSignature, serverAuth'],
    ['Authority Information Access', 'Where to fetch the issuer and OCSP', 'URLs'],
    ['SCT list', 'Proof of Certificate Transparency logging', 'Two or more log signatures']])}
{note('A wildcard *.shop.example matches a.shop.example but not shop.example itself and not a.b.shop.example. Exam questions and real bugs both come from forgetting this.', 'exam')}
''', kw=['X.509', 'certificate', 'ASN.1', 'DER', 'PEM', 'subject alternative name', 'basic constraints', 'key usage', 'wildcard', 'ACME', 'Let us Encrypt', 'certificate lifetime'])

K.lesson('chain', 'Chains of trust and how browsers verify them', f'''
{talk('Root CA keys are too valuable to use every day. They sit in offline hardware security modules, often in guarded rooms, and are switched on only to sign a few intermediate certificates. The intermediates sign the certificates of websites. So a website sends its own certificate and the intermediate, and the browser builds a chain up to a root that is already in its store. Then it checks, for every link, that the signature is valid, that the certificate is within its dates, and that every certificate above the leaf is really allowed to act as a CA. For the leaf, it checks that the name typed in the address bar appears in the Subject Alternative Name list. It also checks that the certificate has not been revoked. Each of these checks has failed in real software. In 2014 Apple’s goto fail bug skipped signature checks in iOS and macOS. In 2020, the CurveBall bug in Windows let attackers forge chains with a custom elliptic curve. And countless apps have disabled checking entirely to silence errors during development, then shipped that way.')}
{viz('cychain')}
{run('chain_verify')}
{steps('What the browser checks, in order', [
    'Build a path from the leaf through intermediates to a root in the local trust store.',
    'Verify each signature with the public key of the certificate above it.',
    'Check every certificate is within its validity dates.',
    'Check that every issuer has Basic Constraints CA = true and respects path length and name constraints.',
    'Check the host name against the leaf’s Subject Alternative Name list, and the Extended Key Usage allows serverAuth.',
    'Check revocation (stapled OCSP or CRL data) and Certificate Transparency proofs.'])}
{run('ssl_context')}
{note('Never set verify_mode = CERT_NONE or check_hostname = False, and never pass verify=False to requests, outside a throw away lab. Fix the trust store instead, or add your own CA for internal services.', 'warn')}
''', kw=['chain of trust', 'root CA', 'intermediate CA', 'certificate verification', 'trust store', 'goto fail', 'CurveBall', 'verify=False', 'ssl module'])

K.lesson('revoke', 'Revocation and Certificate Transparency', f'''
{talk('What happens when a private key is stolen while its certificate still has months to run? The CA can revoke the certificate, but browsers must find out. The first method was a certificate revocation list, a signed list of revoked serial numbers that grew to many megabytes. Then came OCSP, where the browser asks the CA about one certificate, which is slow and tells the CA which sites you visit. OCSP stapling lets the server fetch a fresh signed answer and send it in the handshake. In practice browsers often ignored revocation failures, so the industry is moving to short lifetimes and compressed lists that browsers download in the background, such as Firefox’s CRLite. In 2024 Let’s Encrypt announced it would end OCSP and rely on revocation lists. The second problem is that any trusted CA can issue a certificate for any name. Certificate Transparency, designed at Google by Ben Laurie and Adam Langley after the DigiNotar breach, requires every public certificate to be recorded in public append only logs built as Merkle trees. Browsers refuse certificates without proof of logging, and domain owners watch the logs for certificates they never asked for.')}
{wwh('<b>Revocation</b> marks a certificate as untrusted before it expires (CRL, OCSP, stapling). <b>Certificate Transparency</b> (CT) puts every public certificate in public Merkle tree logs.',
     'Revocation limits the damage of stolen keys. CT makes it impossible for a CA, hacked or dishonest, to issue a certificate in secret.',
     'The CA submits a certificate to logs and gets back signed promises (SCTs) to include it. The log publishes signed tree heads, and anyone can request inclusion and consistency proofs of a few dozen hashes.')}
{viz('cyctlog')}
{run('ct_merkle')}
{fxs(fx('RFC 6962 hashing', 'leaf = SHA-256(0x00 &#8214; entry), node = SHA-256(0x01 &#8214; left &#8214; right)', 'The prefixes stop an attacker presenting an inner node as a leaf (a second preimage trick).', key=True),
     fx('Proof size', 'about &lceil;log<sub>2</sub> n&rceil; hashes', '8 entries: 3 hashes. 1 million: 20. 1 billion: 30.', key=True))}
''', kw=['revocation', 'CRL', 'OCSP', 'OCSP stapling', 'CRLite', 'Certificate Transparency', 'CT log', 'Merkle tree', 'SCT', 'inclusion proof'])

K.lesson('tls13', 'The TLS 1.3 handshake', f'''
{talk('TLS 1.3, published as RFC 8446 in August 2018 after four years and 28 drafts, is a deep clean of the protocol. Everything known to be fragile was removed: RSA key transport, static Diffie-Hellman, CBC mode ciphers, RC4, SHA-1 signatures, compression and renegotiation. What remains is a short list of five cipher suites, all authenticated encryption, and key exchange that is always ephemeral Diffie-Hellman, so forward secrecy is guaranteed. The handshake is also faster. The client guesses which group the server will accept and sends its key share in the very first message, so the server can answer with its own share and start encrypting at once. Data flows after one round trip instead of two. Everything after the ServerHello is encrypted, including the certificate, which used to travel in plain view. The server proves its identity by signing the whole handshake transcript with its certificate key, in a message called CertificateVerify. A returning client can even send data in its first message, called 0-RTT, but that early data can be replayed by an attacker, so servers must only accept it for requests that are safe to repeat.')}
{viz('cytls13')}
{wwh('<b>TLS 1.3</b> is the current Transport Layer Security protocol. It runs an authenticated ephemeral (EC)DHE handshake and then protects records with AES-GCM or ChaCha20-Poly1305.',
     'It secures HTTPS, email transport, VPNs and APIs. Version 1.3 cut a round trip, encrypted the handshake, and removed the options behind a decade of attacks.',
     'ClientHello with key shares, ServerHello with the server share, then encrypted EncryptedExtensions, Certificate, CertificateVerify and Finished messages. Keys come from HKDF over the ECDHE secret and the transcript hash.')}
{table(['TLS 1.2', 'TLS 1.3'], [
    ['2 round trips before data', '1 round trip (0 with resumption)'],
    ['RSA key transport or (EC)DHE', 'Always ephemeral (EC)DHE, forward secrecy'],
    ['CBC, RC4, AEAD suites, dozens of combinations', '5 AEAD suites only'],
    ['Certificate sent in clear', 'Certificate encrypted'],
    ['Downgrade attacks (FREAK, Logjam)', 'Downgrade sentinel in ServerHello random, transcript signed'],
    ['Renegotiation, compression', 'Removed']])}
{note('ServerHello.random ends with the bytes 44 4F 57 4E 47 52 44 01 ("DOWNGRD" and 01) when a TLS 1.3 server is forced to speak TLS 1.2. A TLS 1.3 client that sees this aborts, which defeats version downgrade attacks.', 'tip')}
''', kw=['TLS 1.3', 'handshake', 'ClientHello', 'ServerHello', 'key share', 'CertificateVerify', 'Finished', '0-RTT', 'replay', 'cipher suites', 'downgrade'])

K.lesson('keys', 'The TLS 1.3 key schedule', f'''
{talk('In TLS 1.3, every key comes from one carefully designed chain of HKDF steps, called the key schedule. It starts with an early secret, which is just zeros unless a pre shared key is used. A derived value from it becomes the salt for mixing in the fresh Diffie-Hellman result, which gives the handshake secret. From that come the keys that encrypt the rest of the handshake, separately for each direction. Another derive and extract step gives the master secret, and from it the application traffic keys. Every derivation also mixes in a hash of all handshake messages so far, called the transcript hash, so keys are bound to exactly what both sides saw. The labels, such as c hs traffic for client handshake traffic, keep each key separate. The design was checked by cryptographers with formal tools such as Tamarin and ProVerif before the standard was finished, a first for TLS. The program implements the schedule in a few lines with Python’s standard library and checks it against the example handshake published in RFC 8448.')}
{run('tls_keyschedule')}
{fxs(fx('HKDF-Expand-Label', 'HKDF-Expand(secret, length &#8214; "tls13 " + label &#8214; context, length)', 'Labels such as "derived", "c hs traffic", "s ap traffic" separate every key.', key=True),
     fx('Key schedule', 'early = Extract(0, PSK), handshake = Extract(Derive(early), ECDHE), master = Extract(Derive(handshake), 0)', 'Traffic secrets = Derive-Secret(stage secret, label, transcript hash).', key=True),
     fx('Record nonce', 'nonce = write_iv XOR sequence number (12 bytes)', 'Each record gets a unique nonce without sending it, so AES-GCM nonces never repeat.'))}
''', kw=['key schedule', 'HKDF-Expand-Label', 'early secret', 'handshake secret', 'master secret', 'transcript hash', 'RFC 8448', 'formal verification'])

K.lesson('attacks', 'A history of TLS attacks', f'''
{talk('Almost every weakness removed in TLS 1.3 was found by a real attack. In 2011 BEAST used predictable CBC initial vectors in TLS 1.0 to recover cookies. In 2012 CRIME used compression: the size of compressed data leaked whether a guess matched a secret. Lucky Thirteen in 2013 used tiny timing differences in CBC padding checks. In April 2014, Heartbleed, a missing length check in OpenSSL’s heartbeat feature, let anyone read up to 64 kilobytes of server memory per request, including private keys, and affected a large part of the web. Later in 2014, POODLE broke SSL 3.0. In 2015 FREAK and Logjam tricked servers into using deliberately weak export grade keys from 1990s US export rules. DROWN in 2016 used servers that still supported SSL 2.0 to break modern connections. ROBOT in 2017 revived Bleichenbacher’s padding oracle. Several of these were protocol design flaws, and others were implementation bugs in one library. The lessons: remove options you do not need, keep libraries updated, and test your servers with tools such as testssl.sh or the SSL Labs scanner.')}
{table(['Attack', 'Year', 'Cause', 'Fixed by'], [
    ['BEAST', '2011', 'Predictable CBC IV in TLS 1.0', 'TLS 1.1+, AEAD'],
    ['CRIME, BREACH', '2012, 2013', 'Compression length leaks', 'No TLS compression, careful HTTP compression'],
    ['Lucky Thirteen', '2013', 'CBC padding timing', 'AEAD only in TLS 1.3'],
    ['Heartbleed', '2014', 'OpenSSL missing bounds check', 'Patch, revoke and reissue keys'],
    ['POODLE', '2014', 'SSL 3.0 padding', 'Disable SSL 3.0'],
    ['FREAK, Logjam', '2015', 'Export grade RSA and DH', 'Remove export suites, 2048 bit groups'],
    ['DROWN', '2016', 'SSL 2.0 on the same key', 'Disable SSL 2.0 everywhere'],
    ['ROBOT', '2017', 'RSA PKCS #1 v1.5 padding oracle', 'No RSA key transport (TLS 1.3)']])}
{safe('Use testssl.sh, nmap’s ssl-enum-ciphers script or the SSL Labs test only on servers you own or are authorised to test.')}
''', kw=['BEAST', 'CRIME', 'BREACH', 'Lucky Thirteen', 'Heartbleed', 'POODLE', 'FREAK', 'Logjam', 'DROWN', 'ROBOT', 'testssl.sh', 'SSL Labs'])

K.lesson('deploy', 'Deploying TLS well', f'''
{talk('Getting TLS right on a real site is mostly configuration. Use certificates from an ACME authority such as Let’s Encrypt, renewed automatically, because outages from expired certificates are still common, even at large companies. Enable TLS 1.3 and TLS 1.2 only, with ECDHE key exchange and AEAD ciphers. Send the HTTP Strict Transport Security header, so browsers always use HTTPS for your domain and an attacker cannot strip the connection back to plain HTTP. For the strongest protection, add your domain to the browser HSTS preload list. Staple OCSP if your CA supports it. For service to service traffic inside a company, use mutual TLS, where the client also presents a certificate, often issued automatically by a service mesh. Certificate pinning, where an app accepts only specific keys, can stop rogue CAs, but browsers abandoned HTTP public key pinning around 2018, because mistakes locked sites out of their own users. Finally, plan for the quantum transition: modern browsers and servers already negotiate the hybrid group X25519MLKEM768, which combines X25519 with the post quantum ML-KEM.')}
{steps('A good HTTPS setup', [
    'Automate certificates with ACME (certbot, Caddy, cert-manager) and monitor expiry.',
    'Allow TLS 1.2 and 1.3 only, ECDHE plus AES-GCM or ChaCha20-Poly1305.',
    'Redirect HTTP to HTTPS and send <code>Strict-Transport-Security: max-age=63072000&#59; includeSubDomains&#59; preload</code>.',
    'Enable OCSP stapling where supported, and watch CT logs for your domains (for example with crt.sh).',
    'Use mutual TLS for internal services, and prefer the hybrid X25519MLKEM768 group where available.',
    'Scan regularly with testssl.sh or SSL Labs and fix anything below an A grade.'])}
{fxs(fx('Latency before the first request byte', 'TCP + TLS 1.2: 3 RTT, TCP + TLS 1.3: 2 RTT, QUIC: 1 RTT, QUIC 0-RTT: 0 RTT', 'With an 80 ms round trip, TLS 1.3 over TCP waits 160 ms, QUIC 80 ms.', key=True))}
''', kw=['deployment', 'HSTS', 'preload', 'ACME', 'certbot', 'mutual TLS', 'mTLS', 'certificate pinning', 'HPKP', 'X25519MLKEM768', 'QUIC', 'crt.sh'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('TLS is something every developer uses and few understand fully. A beginner learns that the padlock means the connection is encrypted and that the site’s certificate was checked, and that a certificate warning should never be clicked through. A college student can read a certificate, explain the chain of trust, describe the TLS 1.3 handshake and its key schedule, and configure a server with HSTS and modern ciphers. A masters student studies authenticated key exchange proofs, the formal analysis of TLS 1.3 that found and fixed problems in drafts, attacks on implementations through state machine bugs, and the economics and policy of the CA system, including root programs and distrust decisions such as Symantec’s in 2018. At the research level, people verify TLS implementations formally, as in Project Everest’s miTLS and EverCrypt, design Encrypted Client Hello to hide even the site name, measure the deployment of post quantum hybrids, and propose replacements for parts of the CA system, such as Merkle tree certificates.')}
{ladder(
    '<p>The padlock means the connection is encrypted and the site proved its identity with a certificate from a trusted authority. Never click through a certificate warning.</p>',
    '<p>Read certificate fields, verify a chain step by step, explain revocation and CT, trace the TLS 1.3 handshake and key schedule, and configure HTTPS with ACME, HSTS and modern suites.</p>',
    '<p>Authenticated key exchange models and the TLS 1.3 proofs, state machine attacks, downgrade resistance, 0-RTT replay, PKI governance (root programs, distrust of Symantec), and mutual TLS at scale.</p>',
    '<p>Verified implementations (Project Everest), Encrypted Client Hello, post quantum and hybrid key exchange in TLS, Merkle tree certificates and other proposals to change the CA model.</p>')}
{grow('Explain what the padlock means and why warnings matter.',
      'Verify chains, trace TLS 1.3 and configure a secure server.',
      'Analyse TLS security proofs, PKI governance and post quantum migration.')}
''', kw=['beginner', 'expert', 'formal analysis', 'Project Everest', 'Encrypted Client Hello', 'ECH', 'Symantec distrust', 'Merkle tree certificates'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>PKI</b> binds names to keys: CAs sign X.509 certificates, browsers trust about 150 roots. DigiNotar (2011) showed what a hacked CA can do.',
    '<b>Certificates</b>: subject, issuer, validity, public key, SAN, Basic Constraints, Key Usage, all signed by the issuer. Lifetimes fall to 47 days by 2029.',
    '<b>Chain checks</b>: path to a trusted root, every signature, dates, CA flags, host name in SAN, revocation. Never disable verification.',
    '<b>Revocation</b>: CRL, OCSP, stapling, CRLite, short lifetimes. <b>CT</b>: public Merkle logs, proofs of about log<sub>2</sub> n hashes.',
    '<b>TLS 1.3</b>: 1-RTT, always ephemeral (EC)DHE, five AEAD suites, encrypted certificate, CertificateVerify signs the transcript. 0-RTT data can be replayed.',
    '<b>Key schedule</b>: HKDF from early to handshake to master secret, labels and transcript hashes bind every key.',
    '<b>Attacks</b>: BEAST, CRIME, Lucky Thirteen, Heartbleed, POODLE, FREAK, Logjam, DROWN, ROBOT, each removed or fixed.',
    '<b>Deploy</b>: ACME automation, TLS 1.2 and 1.3 only, HSTS with preload, mTLS inside, hybrid X25519MLKEM768 for quantum safety.'],
    'Cryptography 3.2 explains that quantum threat and the new NIST standards: ML-KEM, ML-DSA and SLH-DSA, with the lattice maths behind them.')}
{files('Three tasks: count days to expiry, match host names with wildcards, and compute a CT Merkle root.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does a TLS certificate bind together?', ['A password and a user', 'A name (such as a domain) and a public key', 'Two private keys', 'An IP address and a MAC address'], 1, 'Identity and key.', 'The CA signs a statement that this public key belongs to this name.')
K.quiz('e', 'Which certificate does the website NOT send in the handshake?', ['Its own leaf certificate', 'The intermediate', 'The root', 'It sends all three'], 2, 'Already in the browser.', 'The root must already be in the browser’s trust store, or the chain is not trusted.')
K.quiz('e', 'How many round trips does a full TLS 1.3 handshake take before the client sends data?', ['0', '1', '2', '3'], 1, 'Key share in the first message.', 'The client sends its key share in ClientHello, so data follows after one round trip.')
K.quiz('e', 'Which extension lists the domain names a certificate covers?', ['Basic Constraints', 'Subject Alternative Name', 'Key Usage', 'Issuer'], 1, 'SAN.', 'Browsers check the host name only against the Subject Alternative Name list.')
K.quiz('m', 'Does *.shop.example match a.b.shop.example?', ['Yes', 'No, a wildcard covers exactly one label', 'Only on Tuesdays', 'Only with HSTS'], 1, 'One label.', 'The * stands for one label, so a.shop.example matches but a.b.shop.example and shop.example do not.')
K.quiz('m', 'Which key exchange is removed in TLS 1.3?', ['ECDHE', 'DHE', 'RSA key transport', 'X25519'], 2, 'No forward secrecy.', 'TLS 1.3 only allows ephemeral (EC)DHE and PSK modes.')
K.quiz('m', 'Why is 0-RTT data risky?', ['It is not encrypted', 'An attacker can replay it', 'It uses RSA', 'It skips the certificate check on every connection'], 1, 'Replay.', 'Early data has no fresh server input, so it can be resent. Only accept it for safe, repeatable requests.')
K.quiz('m', 'What does Certificate Transparency prevent?', ['Expired certificates', 'Certificates issued in secret by a CA without anyone being able to see them', 'Weak ciphers', 'Phishing pages'], 1, 'Public logs.', 'Browsers require proof of logging, and domain owners watch the logs.')
K.quiz('m', 'What does the HSTS header do?', ['Speeds up TLS', 'Tells browsers to always use HTTPS for the domain, stopping downgrade to plain HTTP', 'Revokes certificates', 'Enables 0-RTT'], 1, 'Strict transport.', 'After the first visit the browser refuses plain HTTP for that domain for max-age seconds.')
K.quiz('h', 'In TLS 1.3, what proves to the client that the server holds the certificate’s private key?', ['Finished', 'CertificateVerify, a signature over the handshake transcript', 'ServerHello random', 'The SCT list'], 1, 'Signature.', 'CertificateVerify signs the transcript hash with the certificate key, binding the key exchange to the identity.')
K.quiz('h', 'Heartbleed (2014) was', ['A protocol design flaw in TLS', 'A missing bounds check in OpenSSL’s heartbeat code that leaked up to 64 KB of memory per request', 'A weak cipher', 'A CA breach'], 1, 'Implementation bug.', 'Servers had to patch, revoke and reissue certificates because private keys could have leaked.')
K.quiz('h', 'Why does RFC 6962 hash leaves with a 0x00 prefix and inner nodes with 0x01?', ['For speed', 'So an inner node can never be presented as a leaf (a second preimage trick)', 'It is required by SHA-256', 'For compression'], 1, 'Domain separation.', 'Without the prefixes, the concatenation of two child hashes could be passed off as a leaf entry.')
K.quiz('h', 'The ServerHello random ends with "DOWNGRD 01". What should a TLS 1.3 client do?', ['Continue with TLS 1.2', 'Abort the handshake, because someone forced a version downgrade', 'Retry with SSL 3.0', 'Ignore it'], 1, 'Sentinel.', 'A TLS 1.3 capable server sets this only when negotiating TLS 1.2, so a 1.3 client knows it was downgraded.')
K.quiz('x', 'In the style of an MIT 6.858 question: an app sets verify=False because of a certificate error in testing and ships it. What can a coffee shop Wi-Fi attacker do?', ['Nothing, TLS still encrypts', 'Present any certificate and read and change all traffic as a man in the middle', 'Only see domain names', 'Only slow it down'], 1, 'No authentication.', 'Encryption to an unauthenticated key is encryption to the attacker. The fix is a correct trust store or pinning.')
K.quiz('x', 'In the style of a Stanford CS 255 exam: why does every TLS 1.3 key derivation include the transcript hash?', ['For speed', 'To bind keys to the exact messages both sides saw, so tampering or downgrades produce different keys and the Finished check fails', 'To compress records', 'Because HKDF needs a salt'], 1, 'Binding.', 'Any change to an earlier message changes the transcript hash and hence all later keys.')

K.calc('e', 'How many round trips does TLS 1.3 resumption with 0-RTT need before the client sends data?', '0', 'Data rides in the first flight.', ['The PSK gives early keys at once.', 'The request goes with ClientHello.', eq('0 RTT')], check=0)
K.calc('e', 'How many round trips does a full TLS 1.2 handshake need before data?', '2', 'One more than TLS 1.3.', ['Hello exchange, then key exchange and Finished.', 'TLS 1.3 merged them.', eq('2 RTT')], check=2)
K.calc('e', 'How many cipher suites does RFC 8446 define for TLS 1.3?', '5', 'All AEAD.', ['AES-128-GCM, AES-256-GCM, ChaCha20-Poly1305,', 'AES-128-CCM and AES-128-CCM-8.', eq('5 suites')], check=5)
K.calc('m', 'A CT log holds 8 certificates. How many hashes are in an inclusion proof?', '3', 'log<sub>2</sub> 8.', ['One sibling per level.', '8 leaves give 3 levels.', eq('3 hashes')], check=3)
K.calc('m', 'A CT log holds 1,000,000 certificates. How many hashes are in an inclusion proof, at most?', '20', '&lceil;log<sub>2</sub> 10<sup>6</sup>&rceil;.', ['2<sup>19</sup> = 524,288 &lt; 10<sup>6</sup>.', '2<sup>20</sup> = 1,048,576 &ge; 10<sup>6</sup>.', eq('20 hashes')], check=(10 ** 6 - 1).bit_length())
K.calc('m', 'Round trip time is 80 ms. How long before the first request byte with TCP and TLS 1.3?', '160', 'TCP 1 RTT + TLS 1 RTT.', ['TCP handshake: 80 ms.', 'TLS 1.3: 80 ms.', eq('160 ms')], check=2 * 80, unit='ms')
K.calc('m', 'Same 80 ms round trip, TCP with TLS 1.2. How long before the first request byte?', '240', 'TCP 1 RTT + TLS 2 RTT.', ['80 + 2 &times; 80.', 'TLS 1.3 saves 80 ms per new connection.', eq('240 ms')], check=3 * 80, unit='ms')
K.calc('m', 'From March 2029, what is the maximum lifetime in days of a public TLS certificate (CA/Browser Forum ballot SC-081)?', '47', 'Stepped down from 398.', ['200 days from 2026, 100 from 2027.', '47 from 2029.', eq('47 days')], check=47, unit='days')
K.calc('h', 'How many signatures does a browser verify for a chain of leaf plus one intermediate up to a trusted root?', '2', 'One per link.', ['Leaf checked with the intermediate’s key.', 'Intermediate checked with the root’s key. The root is trusted as is.', eq('2 signatures')], check=2)
K.calc('h', 'With QUIC (HTTP/3) and an 80 ms round trip, how long before the first request byte on a new connection?', '80', 'Transport and TLS handshakes are combined.', ['QUIC carries the TLS 1.3 messages in its first packets.', 'One round trip in total.', eq('80 ms')], check=80, unit='ms')
K.calc('h', 'How many bytes is the TLS 1.3 per record nonce for AES-GCM?', '12', 'write_iv XOR sequence number.', ['The IV is 96 bits.', '96 / 8 = 12.', eq('12 bytes')], check=96 // 8)
K.calc('x', 'In the style of a CMU 18-631 question: Heartbleed’s payload length field was 16 bits. What is the largest number of bytes one request could ask for?', '65535', '2<sup>16</sup> &minus; 1.', ['A 16 bit unsigned field holds 0 to 65,535.', 'OpenSSL copied that many bytes without checking the real length.', eq('65,535 bytes, about 64 KB')], check=2 ** 16 - 1)
K.calc('x', 'HSTS max-age = 63072000 seconds. How many days is that?', '730', 'Divide by 86,400.', ['63,072,000 / 86,400.', '= 730 days, two years.', eq('730 days')], check=63072000 // 86400, unit='days')

K.assign('days_left', 'e', 'Days until a certificate expires',
         '<p>Write <code>days_left(not_after, today)</code> where both are strings like "2026-11-30". Return the number of days from today to not_after (negative if already expired). Use datetime.date.fromisoformat.</p>',
         '''
from datetime import date

def days_left(not_after, today):
    # your code here
    pass
''', [('days_left("2026-11-30", "2026-11-14")', 16), ('days_left("2026-10-30", "2026-11-14")', -15), ('days_left("2027-02-12", "2026-11-14")', 90)],
         '''
from datetime import date

def days_left(not_after, today):
    end = date.fromisoformat(not_after)
    now = date.fromisoformat(today)
    return (end - now).days
''', 'Turn both strings into date objects, subtract, and read .days.', '<p>Monitoring tools run exactly this check every day and alert when fewer than about 20 days remain, so automated renewal failures are noticed in time.</p>')
K.assign('name_matches', 'm', 'Host name matching with wildcards',
         '<p>Write <code>name_matches(host, names)</code> that returns True if host matches any entry in names. Matching ignores case. A wildcard entry like "*.shop.example" matches exactly one extra label on the left: a.shop.example yes, shop.example no, a.b.shop.example no.</p>',
         '''
def name_matches(host, names):
    # your code here
    pass
''', [('name_matches("shop.example", ["shop.example"])', True), ('name_matches("WWW.Shop.Example", ["*.shop.example"])', True),
      ('name_matches("shop.example", ["*.shop.example"])', False), ('name_matches("a.b.shop.example", ["*.shop.example"])', False),
      ('name_matches("bank.example", ["shop.example", "*.shop.example"])', False)],
         '''
def name_matches(host, names):
    host = host.lower()
    for name in names:
        name = name.lower()
        if name == host:
            return True
        if name.startswith("*."):
            rest = name[2:]
            if host.endswith("." + rest) and "." not in host[:-len(rest) - 1]:
                return True
    return False
''', 'For a wildcard, check that host ends with "." + rest and that the part before it has no dot.', '<p>RFC 6125 and the CA/Browser Forum rules allow the wildcard only as the whole left most label, which is what this check enforces.</p>')
K.assign('ct_root', 'm', 'A Certificate Transparency Merkle root',
         '<p>Write <code>ct_root(entries)</code> for a list of byte strings. Hash leaves as SHA-256(0x00 + entry), inner nodes as SHA-256(0x01 + left + right), and split a list of size n at the largest power of two below n (RFC 6962). Return the root as a hex string.</p>',
         '''
import hashlib

def ct_root(entries):
    # your code here
    pass
''', [('ct_root([b"a"])', __import__('hashlib').sha256(b"\x00a").hexdigest()),
      ('ct_root([b"a", b"b"])', __import__('hashlib').sha256(b"\x01" + __import__('hashlib').sha256(b"\x00a").digest() + __import__('hashlib').sha256(b"\x00b").digest()).hexdigest()),
      ('len(ct_root([b"x"] * 7))', 64)],
         '''
import hashlib

def ct_root(entries):
    def tree(items):
        if len(items) == 1:
            return hashlib.sha256(b"\\x00" + items[0]).digest()
        k = 1
        while k * 2 < len(items):
            k = k * 2
        return hashlib.sha256(b"\\x01" + tree(items[:k]) + tree(items[k:])).digest()
    return tree(entries).hex()
''', 'Write a helper that returns raw bytes for a list, recurse on items[:k] and items[k:], and call .hex() only at the end.', '<p>Splitting at the largest power of two below n keeps the tree append only: adding entries never changes the shape of the part already built.</p>')

K.must('PKI', 'CAs sign certificates binding names to keys. About 150 roots in browsers. DigiNotar 2011. Lifetimes down to 47 days by 2029.')
K.must('Certificate', 'Subject, issuer, validity, key, SAN, Basic Constraints, Key Usage, EKU, signature. Wildcard = one label.')
K.must('Verify', 'Path to trusted root, signatures, dates, CA flags, host in SAN, revocation, CT. Never verify=False.')
K.must('TLS 1.3', '1-RTT, (EC)DHE only, 5 AEAD suites, encrypted certificate, CertificateVerify, Finished, 0-RTT replayable, DOWNGRD sentinel.')
K.must('Keys and logs', 'HKDF schedule early, handshake, master with transcript hashes. CT leaf 0x00, node 0x01, proof log<sub>2</sub> n.')
K.must('Deploy', 'ACME auto renewal, TLS 1.2 and 1.3 only, HSTS preload, OCSP stapling or CRLite, mTLS inside, X25519MLKEM768.')

T = K.topic(
    slug='cy-tls', topic='cy-tls', step=(3, 'Applied and modern cryptography', 'cy-c3', 'Certificates and TLS 1.3, the move to post quantum cryptography, and advanced tools: secret sharing, zero knowledge proofs and homomorphic encryption.', 'Advanced'),
    title='Certificates, PKI and TLS 1.3', short='PKI and TLS', badge='1.1', minutes=85,
    lead='How the web proves who you are talking to: the PKI model, X.509 certificates and their extensions, chains of trust and how browsers check them, revocation and Certificate Transparency with Merkle proofs, the TLS 1.3 handshake and key schedule checked against RFC 8448, a history of TLS attacks, and a checklist for deploying HTTPS well.',
    desc='PKI, certificate authority, X.509, ASN.1, subject alternative name, basic constraints, wildcard, chain of trust, root store, certificate verification, revocation, CRL, OCSP stapling, CRLite, Certificate Transparency, Merkle tree, SCT, TLS 1.3, handshake, ClientHello, key share, CertificateVerify, 0-RTT, key schedule, HKDF-Expand-Label, RFC 8448, BEAST, CRIME, Heartbleed, POODLE, FREAK, Logjam, DROWN, ROBOT, HSTS, ACME, Let us Encrypt, mutual TLS, certificate pinning, QUIC, X25519MLKEM768',
    summary='PKI, X.509, chain verification, revocation and CT, the TLS 1.3 handshake and key schedule, TLS attacks, HTTPS deployment.',
    keywords=['PKI', 'X.509', 'certificate chain', 'revocation', 'Certificate Transparency', 'TLS 1.3', 'key schedule', 'Heartbleed', 'HSTS', 'ACME'],
    recap='<p>Encryption is only as good as the check on who holds the other key. Certificates, public logs and a short, signed TLS 1.3 handshake make that check work at internet scale.</p>',
    added='2026-11-14')
