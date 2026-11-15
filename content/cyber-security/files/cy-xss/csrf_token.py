# 1.3 Cross site attacks: XSS, CSP, CSRF and clickjacking
# Example "csrf_token" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

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
