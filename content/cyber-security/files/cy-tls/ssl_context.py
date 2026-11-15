# 1.1 Certificates, PKI and TLS 1.3
# Example "ssl_context" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

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
