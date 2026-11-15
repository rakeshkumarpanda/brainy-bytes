# 1.1 Logging, monitoring and the SIEM
# Example "impossible_travel" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Impossible travel: two logins by the same user, too far apart to fly between in the time given
import math

def distance_km(lat1, lon1, lat2, lon2):
    """Great circle distance with the haversine formula. Earth radius 6371 km."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    d_lat = p2 - p1
    d_lon = math.radians(lon2 - lon1)
    h = math.sin(d_lat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(d_lon / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))

CITY = {"Mumbai": (19.0760, 72.8777), "Delhi": (28.6139, 77.2090), "London": (51.5074, -0.1278)}
MAX_SPEED = 900          # km per hour, roughly a passenger jet

# (user, hour of the day, city where the IP address is located)
logins = [
    ("meena", 9.0, "Mumbai"),
    ("meena", 12.5, "Delhi"),     # a morning flight: possible
    ("meena", 13.0, "London"),    # half an hour later: impossible
]

for (u1, t1, c1), (u2, t2, c2) in zip(logins, logins[1:]):
    km = distance_km(*CITY[c1], *CITY[c2])
    hours = t2 - t1
    speed = km / hours
    verdict = "IMPOSSIBLE, alert" if speed > MAX_SPEED else "possible"
    print(f"{u1}: {c1} -> {c2}  {km:7.1f} km in {hours:.1f} h = {speed:8.1f} km/h  {verdict}")

print("\nBefore alerting, check for a VPN or a company proxy. They make a user appear in another city.")
