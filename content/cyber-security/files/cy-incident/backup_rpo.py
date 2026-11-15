# 1.2 Incident response: from the first alert to lessons learned
# Example "backup_rpo" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Backups against ransomware: data lost (recovery point) and time to restore (recovery time)
INCIDENT_HOUR = 15.5        # 15:30
DATA_TB = 4                 # size of the file server
RESTORE_MB_PER_S = 400      # restore speed

def last_backup(every):
    """Backups run at 0, every, 2 * every, ... Return the last one before the incident."""
    t = 0
    while t + every <= INCIDENT_HOUR:
        t += every
    return t

restore_hours = DATA_TB * 1_000_000 / RESTORE_MB_PER_S / 3600
print(f"Restoring {DATA_TB} TB at {RESTORE_MB_PER_S} MB/s takes {restore_hours:.2f} hours (the recovery time)\n")
for every in [24, 12, 4, 1]:
    t = last_backup(every)
    print(f"backup every {every:2} h: last good copy at {t:5.1f} h, work lost = {INCIDENT_HOUR - t:4.1f} h")

def check_32110(copies):
    """copies: list of (kind of storage, off site?, offline or immutable?, last restore test passed?)"""
    kinds = {c[0] for c in copies}
    rules = {
        "3 copies": len(copies) >= 3,
        "2 kinds of storage": len(kinds) >= 2,
        "1 off site": any(c[1] for c in copies),
        "1 offline or immutable": any(c[2] for c in copies),
        "0 restore errors": all(c[3] for c in copies),
    }
    return rules

plan = [("disk", False, False, True), ("disk", False, False, True), ("cloud", True, False, True)]
print()
for rule, ok in check_32110(plan).items():
    print(f"{rule:24} {'yes' if ok else 'NO, fix this'}")
