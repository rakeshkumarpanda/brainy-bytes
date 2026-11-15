# 1.3 Digital forensics: collecting and reading evidence
# Example "timeline" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A small super timeline: merge events from several sources, sort by time, and spot timestomping.
events = [
    ("2026-11-14 10:03:40", "web log", "GET /uploads/shell.php?cmd=whoami"),
    ("2026-11-14 09:58:11", "file system", "shell.php created in /var/www/uploads"),
    ("2026-11-14 10:31:50", "firewall", "2.1 GB sent to 203.0.113.80:443"),
    ("2026-11-14 09:58:10", "web log", "POST /upload.php from 198.51.100.23"),
    ("2026-11-14 10:20:15", "auth.log", "sudo by www-data FAILED"),
    ("2026-11-14 10:03:41", "EDR", "www-data started /bin/sh"),
]
for when, source, what in sorted(events):        # ISO dates sort correctly as text
    print(f"{when}  {source:11}  {what}")

# NTFS keeps two sets of times per file. Tools that fake dates usually change only $STANDARD_INFORMATION.
files = [
    # name, $STANDARD_INFORMATION created, $FILE_NAME created
    ("report.docx", "2026-11-02 09:15:22.4817", "2026-11-02 09:15:22.4817"),
    ("backup.php", "2019-03-01 00:00:00.0000", "2026-11-14 10:06:02.1934"),
]
print()
for name, si, fn in files:
    reasons = []
    if si < fn:
        reasons.append("$SI created is earlier than $FN created")
    if si.endswith(".0000"):
        reasons.append("fraction of a second is exactly zero")
    print(f"{name:12} {'SUSPICIOUS: ' + ' and '.join(reasons) if reasons else 'looks normal'}")
