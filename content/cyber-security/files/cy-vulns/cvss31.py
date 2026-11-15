# 3.2 Vulnerabilities: CVE, CVSS, patching and hardening
# Example "cvss31" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# CVSS v3.1 base score, exactly as the FIRST specification defines it
import math

W = {
    "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},
    "AC": {"L": 0.77, "H": 0.44},
    "UI": {"N": 0.85, "R": 0.62},
    "CIA": {"H": 0.56, "L": 0.22, "N": 0.0},
}

def roundup(x):                          # the spec's Roundup: smallest one decimal number >= x, without float noise
    i = round(x * 100000)
    return i / 100000.0 if i % 10000 == 0 else (math.floor(i / 10000) + 1) / 10.0

def score(vector):
    m = dict(part.split(":") for part in vector.split("/")[1:])
    changed = m["S"] == "C"
    pr = {"N": 0.85, "L": 0.68 if changed else 0.62, "H": 0.5 if changed else 0.27}[m["PR"]]
    iss = 1 - (1 - W["CIA"][m["C"]]) * (1 - W["CIA"][m["I"]]) * (1 - W["CIA"][m["A"]])
    impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15 if changed else 6.42 * iss
    exploit = 8.22 * W["AV"][m["AV"]] * W["AC"][m["AC"]] * pr * W["UI"][m["UI"]]
    if impact <= 0:
        return 0.0, round(iss, 4), round(impact, 4), round(exploit, 4)
    base = roundup(min(1.08 * (impact + exploit), 10)) if changed else roundup(min(impact + exploit, 10))
    return base, round(iss, 4), round(impact, 4), round(exploit, 4)

def severity(s):
    return "None" if s == 0 else "Low" if s < 4 else "Medium" if s < 7 else "High" if s < 9 else "Critical"

examples = {
    "Log4Shell CVE-2021-44228": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
    "Heartbleed CVE-2014-0160": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
    "typical remote code execution": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
    "local privilege escalation": "CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H",
    "reflected XSS (needs a click)": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
}
for name, vec in examples.items():
    base, iss, imp, exp = score(vec)
    print(f"{name:31} {base:4} {severity(base):8} (ISS {iss}, impact {imp}, exploitability {exp})")
