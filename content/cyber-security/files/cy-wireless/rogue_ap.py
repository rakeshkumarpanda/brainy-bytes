# 1.3 Wireless security: from WEP to WPA3
# Example "rogue_ap" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Spot rogue access points and evil twins in a list of beacons (a pretend Wi-Fi survey)
authorised = {                           # what IT installed: BSSID -> (SSID, security)
    "a0:00:00:00:00:01": ("CorpWiFi", "WPA3-Enterprise"),
    "a0:00:00:00:00:02": ("CorpWiFi", "WPA3-Enterprise"),
    "a0:00:00:00:00:10": ("CorpGuest", "WPA3-SAE"),
}
survey = [                               # (BSSID, SSID, security, signal in dBm)
    ("a0:00:00:00:00:01", "CorpWiFi", "WPA3-Enterprise", -60),
    ("de:ad:be:ef:00:01", "CorpWiFi", "WPA2-PSK", -38),        # same name, stronger, weaker security
    ("a0:00:00:00:00:10", "CorpGuest", "WPA3-SAE", -55),
    ("12:34:56:78:9a:bc", "Printer-Setup", "Open", -70),        # someone plugged in a device AP
    ("a0:00:00:00:00:02", "CorpWiFi", "WPA2-PSK", -58),         # a real AP that was misconfigured
]
our_ssids = {ssid for ssid, sec in authorised.values()}
for bssid, ssid, sec, dbm in survey:
    if bssid in authorised:
        want = authorised[bssid][1]
        verdict = "ok" if sec == want else f"MISCONFIGURED: {sec}, should be {want}"
    elif ssid in our_ssids:
        verdict = "EVIL TWIN: our network name from an unknown radio"
    else:
        verdict = "rogue or neighbour: check where it is"
    print(f"{bssid}  {ssid:14} {sec:16} {dbm:4} dBm -> {verdict}")
