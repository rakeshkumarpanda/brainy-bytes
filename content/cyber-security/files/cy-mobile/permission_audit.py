# 4.2 Mobile security: sandboxes, permissions, signing and the OWASP Mobile Top 10
# Example "permission_audit" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Read an Android style manifest and flag permissions that do not fit what the app says it does
import xml.etree.ElementTree as ET          # fine for this fixed text. For files from strangers use defusedxml

MANIFEST = """
<manifest package="com.example.torch">
  <uses-permission name="android.permission.CAMERA"/>
  <uses-permission name="android.permission.READ_CONTACTS"/>
  <uses-permission name="android.permission.READ_SMS"/>
  <uses-permission name="android.permission.ACCESS_FINE_LOCATION"/>
  <uses-permission name="android.permission.INTERNET"/>
</manifest>
"""

DANGEROUS = {"CAMERA", "READ_CONTACTS", "READ_SMS", "RECEIVE_SMS", "ACCESS_FINE_LOCATION",
             "RECORD_AUDIO", "READ_CALL_LOG", "READ_MEDIA_IMAGES"}
NEEDED = {"torch": {"CAMERA"}, "maps": {"ACCESS_FINE_LOCATION", "INTERNET"}, "chat": {"INTERNET", "CAMERA", "RECORD_AUDIO", "READ_CONTACTS"}}

def audit(xml, purpose):
    root = ET.fromstring(xml)
    perms = {p.get("name").split(".")[-1] for p in root.iter("uses-permission")}
    extra = sorted(p for p in perms if p in DANGEROUS and p not in NEEDED[purpose])
    return root.get("package"), sorted(perms), extra

pkg, perms, extra = audit(MANIFEST, "torch")
print("package:", pkg)
print("asks for:", ", ".join(perms))
print("dangerous and unexplained for a torch:", ", ".join(extra) if extra else "none")
print("risk score:", len(extra), "of", len(DANGEROUS), "dangerous permissions beyond its purpose")
