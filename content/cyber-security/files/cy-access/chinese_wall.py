# 2.2 Access control models: from the access matrix to RBAC and ABAC
# Example "chinese_wall" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The Chinese Wall model (Brewer and Nash, 1989): what you may see depends on what you have already seen
conflict_classes = {
    "banks": {"Bank A", "Bank B", "Bank C"},
    "oil": {"Oil X", "Oil Y"},
}
history = {"consultant": set()}          # companies whose data this person has already opened

def company_class(company):
    return next(name for name, members in conflict_classes.items() if company in members)

def may_read(person, company):
    cls = conflict_classes[company_class(company)]
    seen_rivals = (history[person] & cls) - {company}
    return not seen_rivals               # allowed unless a competitor in the same class was already seen

for company in ["Bank A", "Oil X", "Bank A", "Bank B", "Oil Y"]:
    ok = may_read("consultant", company)
    if ok:
        history["consultant"].add(company)
    print(f"open {company:7}: {'allowed' if ok else 'BLOCKED (conflict of interest)'}  seen so far: {sorted(history['consultant'])}")
