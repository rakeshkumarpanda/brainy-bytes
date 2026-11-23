# 4.4 API security: BOLA, rate limits, mass assignment and the OWASP API Top 10
# Example "mass_assign" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

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
