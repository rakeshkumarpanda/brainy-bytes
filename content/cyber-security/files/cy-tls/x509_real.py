# 1.1 Certificates, PKI and TLS 1.3
# Example "x509_real" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

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
