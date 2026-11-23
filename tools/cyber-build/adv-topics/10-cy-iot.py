# Advanced 4.3: IoT and industrial control security. Checked against Antonakakis et al., "Understanding the Mirai
# Botnet" (USENIX Security 2017), KrebsOnSecurity and Dyn reports on the October 2016 attacks, the OWASP IoT Top 10
# (2018), the UK Product Security and Telecommunications Infrastructure regime (in force 29 April 2024), the EU Cyber
# Resilience Act (2024), California SB-327 (2020), Miller and Valasek's remote Jeep Cherokee research (2015, recall of
# 1.4 million vehicles), the Verkada camera breach (March 2021), NIST SP 800-82 Revision 3 (2023), IEC 62443, the
# Modbus Application Protocol and Modbus/TCP Security specifications, Langner and Symantec analyses of Stuxnet
# (2010 to 2013), the E-ISAC and SANS report on the Ukrainian grid attack of 23 December 2015, analyses of
# Industroyer (2016) and Triton/Trisis (2017), the Colonial Pipeline incident (May 2021) and NPCIL's statement on
# the Kudankulam malware (October 2019).
import math

from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq, scene
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk, attack, safe

chapter('cy-iot')
K = Kit()

K.code('botnet_growth', r'''
# How fast does a worm fill the weak devices? A simple epidemic model of Mirai style spread
def spread(n_devices, weak_share, probes_per_round, rounds=12):
    weak = n_devices * weak_share
    infected = 1.0
    history = [infected]
    for _ in range(rounds):
        # each bot probes random addresses, a probe succeeds if it hits a weak device not yet infected
        new = infected * probes_per_round * (weak - infected) / n_devices
        infected = min(weak, infected + new)
        history.append(infected)
    return history

for share in (0.6, 0.2, 0.02):
    h = spread(100_000, share, probes_per_round=3)
    print(f"{share:4.0%} default passwords: " + "  ".join(f"{x:7.0f}" for x in h[::2]))

bots = 600_000
for upload_mbps in (1, 5):
    print(f"{bots:,} bots at {upload_mbps} Mbit/s each = {bots * upload_mbps / 1e6:.1f} Tbit/s of attack traffic")
''')

K.code('default_creds', r'''
# Audit your own device inventory for factory passwords (a defender's check, on a made up list)
DEFAULTS = {("admin", "admin"), ("root", "root"), ("admin", "1234"), ("root", "xc3511"),
            ("admin", "password"), ("user", "user"), ("root", "vizxv"), ("support", "support")}

inventory = [
    {"name": "lobby camera", "user": "admin", "password": "admin", "firmware": "2019.04", "telnet": True},
    {"name": "warehouse DVR", "user": "root", "password": "xc3511", "firmware": "2016.11", "telnet": True},
    {"name": "office router", "user": "admin", "password": "T7#qL9!vRm2", "firmware": "2026.09", "telnet": False},
    {"name": "smart TV", "user": "user", "password": "b4Kp!xw8", "firmware": "2025.12", "telnet": False},
]

for d in inventory:
    problems = []
    if (d["user"], d["password"]) in DEFAULTS:
        problems.append("factory password")
    if d["telnet"]:
        problems.append("telnet open (port 23)")
    if int(d["firmware"][:4]) < 2024:
        problems.append(f"old firmware {d['firmware']}")
    print(f"{d['name']:15s} {'; '.join(problems) if problems else 'ok'}")

print("\nThe real Mirai tried about 60 such pairs, including root / xc3511 used by many DVRs and cameras.")
''')

K.code('modbus_frame', r'''
# Reading a Modbus TCP frame byte by byte (a parser, as monitoring tools use, on a made up frame)
import struct

FUNCTIONS = {1: "read coils", 3: "read holding registers", 5: "write single coil",
             6: "write single register", 15: "write multiple coils", 16: "write multiple registers"}

def parse(frame):
    tid, proto, length, unit, func = struct.unpack(">HHHBB", frame[:8])
    body = frame[8:]
    out = {"transaction": tid, "protocol": proto, "length": length, "unit": unit,
           "function": f"{func:02d} {FUNCTIONS.get(func, 'unknown')}"}
    if func in (5, 6):
        addr, value = struct.unpack(">HH", body[:4])
        out["address"] = hex(addr)
        out["value"] = hex(value)
    return out

frame = bytes.fromhex("002A 0000 0006 01 05 0010 FF00".replace(" ", ""))
for k, v in parse(frame).items():
    print(f"{k:12s} {v}")

print("\nNo field holds a user name, password or signature. Any device that can reach port 502")
print("can send this. That is why plants allow writes only from known operator stations.")
''')

K.code('zone_rules', r'''
# Purdue levels and a firewall policy: which flows are allowed between zones?
LEVEL = {"internet": 5, "office_pc": 4, "erp": 4, "dmz_historian": 3.5, "dmz_jump": 3.5,
         "site_historian": 3, "hmi": 2, "scada": 2, "plc": 1}

ALLOW = {("office_pc", "dmz_historian"), ("erp", "dmz_historian"), ("site_historian", "dmz_historian"),
         ("office_pc", "dmz_jump"), ("dmz_jump", "hmi"), ("hmi", "plc"), ("scada", "plc")}

def allowed(src, dst):
    return (src, dst) in ALLOW

def check(path):
    for a, b in zip(path, path[1:]):
        if not allowed(a, b):
            return f"blocked at {a} -> {b}"
        if LEVEL[a] >= 4 and LEVEL[b] <= 3:
            return f"rule error: {a} (level {LEVEL[a]}) talks straight to {b} (level {LEVEL[b]})"
    return "path open"

for path in [["office_pc", "site_historian", "hmi", "plc"],
             ["office_pc", "dmz_historian", "plc"],
             ["office_pc", "dmz_jump", "hmi", "plc"],
             ["internet", "plc"]]:
    print(" -> ".join(path), ":", check(path))

print("\nThe jump host path is open by design, so it needs MFA, recording and approval for each session.")
''')

K.code('sensor_anomaly', r'''
# Watching the process itself: flag readings that do not fit what the physics says should happen
import statistics

level = [40, 41, 40, 42, 41, 40, 41, 42, 41, 40, 47, 55, 63, 71, 79]   # tank level %, one reading a minute
valve_cmd = [0] * 15                                                  # the HMI says the inlet valve is shut

window = level[:10]
mean, sd = statistics.mean(window), statistics.pstdev(window)
print(f"normal level {mean:.1f} +/- {sd:.2f}")
for t in range(10, len(level)):
    z = (level[t] - mean) / sd
    rise = level[t] - level[t - 1]
    flags = []
    if abs(z) > 3:
        flags.append(f"z score {z:.1f}")
    if rise > 3 and valve_cmd[t] == 0:
        flags.append("level rising while the valve is commanded shut")
    print(f"minute {t:2d}: level {level[t]:3d}%  {'; '.join(flags) if flags else 'normal'}")

print("\nA change in the physical process that no operator ordered is the strongest sign of tampering,")
print("even when the network traffic looks normal.")
''')

# ------------------------------------------------------------------------------------------------ lessons
K.lesson('idea', 'Computers in everything: IoT and industrial systems', f'''
{talk('Look around your home. A Wi-Fi router, a smart TV, maybe a doorbell camera, a smart speaker, a fitness band, perhaps a smart electricity meter. Each one is a small computer on the internet, and together they are called the Internet of Things, IoT. There are well over fifteen billion of them worldwide. Behind the scenes there is a second, older family: industrial control systems, the computers that run power stations, water treatment plants, oil pipelines, factories and railway signals. Both families share a problem. They were often built by companies focused on features and price, not security, they stay in service for many years, often more than ten for industrial equipment, and many are hard or impossible to update. When they are attacked, the damage can be physical, not only lost data: a power cut, a flooded tank, a car that brakes by itself. In 2015 the researchers Charlie Miller and Chris Valasek showed they could control a Jeep Cherokee’s brakes and steering over the mobile network from miles away, and the maker recalled 1.4 million vehicles. In 2021 hackers got into the cloud account of the camera company Verkada using a password found exposed online, and could watch about 150,000 cameras in hospitals, schools and prisons. This chapter starts with consumer IoT and the Mirai botnet, then moves into factories and power grids, where the rules of security change.')}
{src('Antonakakis et al. (2017), OWASP IoT Top 10 (2018), UK PSTI regime (2024), EU Cyber Resilience Act (2024), Miller and Valasek (2015), Verkada (2021), NIST SP 800-82 Rev. 3, IEC 62443, Modbus specifications, Stuxnet analyses, E-ISAC and SANS (2016), Industroyer and Triton analyses, Colonial Pipeline (2021), NPCIL (2019).')}
{wwh('<b>IoT security</b> protects connected everyday devices. <b>Industrial control system (ICS) or operational technology (OT) security</b> protects the computers that control physical processes, such as PLCs, SCADA systems and safety systems.',
     'These devices are many, cheap, long lived and hard to patch, and attacks on them can cause physical harm, from botnets that take down websites to power cuts and explosions.',
     'Unique passwords and automatic updates for devices, network segmentation, allow lists for industrial commands, independent safety systems, monitoring of both the network and the physical process, and laws that set minimum standards.')}
{table(['Where', 'Example devices', 'Worst realistic outcome'], [
    ['Home', 'Routers, cameras, smart locks, baby monitors', 'Spying, joining a botnet, opening a door'],
    ['Health', 'Infusion pumps, pacemakers, hospital networks', 'Wrong dose, delayed treatment'],
    ['Vehicles', 'Connected cars, EV chargers', 'Remote control of a car, charging network outages'],
    ['Industry and utilities', 'PLCs, SCADA, safety controllers', 'Power cuts, floods, toxic releases, explosions']])}
{scene('Around you', '<p>Every traffic signal at a big junction is run by a controller in a roadside box. If someone could change its timing from the internet, they could turn every light green at once. Engineers design these so that a hardware safety circuit refuses conflicting greens, whatever the software says. That idea, a safety layer that does not trust the computer, runs through this whole chapter.</p>')}
''', kw=['IoT', 'Internet of Things', 'industrial control systems', 'ICS', 'operational technology', 'OT', 'SCADA', 'PLC', 'Jeep Cherokee hack', 'Miller Valasek', 'Verkada', 'physical consequences'])

K.lesson('mirai', 'Default passwords and the Mirai botnet', f'''
{talk('In September 2016 the security journalist Brian Krebs’s website was hit by one of the largest floods of traffic ever seen, about 620 gigabits per second. Days later the French hosting company OVH saw nearly a terabit per second. Then on 21 October 2016 the same kind of attack hit Dyn, a company that runs DNS for many big websites, and Twitter, Netflix, Reddit and GitHub became unreachable for many people across the United States and Europe. The weapon was a botnet called Mirai, made of hundreds of thousands of cameras, video recorders and routers. Mirai did not use any clever exploit. It scanned the internet for devices with the telnet port open and tried a list of about sixty factory usernames and passwords, such as admin and admin, or root and xc3511, a password shared by many cheap video recorders. Researchers later counted about 600,000 infected devices at its peak. Its authors, three young men from the United States, released the source code online, and copies are still active. The animation shows why the share of devices on default passwords matters so much: with 60 percent the worm spreads like a fire, with 2 percent it barely moves. That is why the UK banned universal default passwords for new consumer devices from 29 April 2024, why California required unique passwords from 2020, and why the EU’s Cyber Resilience Act will require security updates for connected products.')}
{viz('cymirai')}
{run('botnet_growth')}
{run('default_creds')}
{fxs(fx('Epidemic growth of a worm', 'I<sub>t+1</sub> = I<sub>t</sub> + I<sub>t</sub> &times; k &times; (W &minus; I<sub>t</sub>) / N', 'k probes per bot, W weak devices out of N. Fast at first, then slows as weak devices run out.', key=True),
     fx('Botnet attack size', 'traffic = bots &times; upload speed per bot', '600,000 &times; 1 Mbit/s = 0.6 Tbit/s.', key=True),
     fx('Effect of unique passwords', 'W = N &times; share on defaults', 'From 60% to 2% shrinks the target pool 30 times.'))}
''', kw=['Mirai', 'botnet', 'DDoS', 'default password', 'telnet', 'Krebs', 'OVH', 'Dyn', 'October 2016', 'epidemic model', 'UK PSTI', 'California SB-327', 'Cyber Resilience Act'])

K.lesson('design', 'Building safer devices: the OWASP IoT Top 10', f'''
{talk('What should a well made connected device do? The OWASP IoT Top 10, published in 2018, lists the commonest failures, and the first one is the Mirai problem: weak, guessable or hard coded passwords. Next come insecure network services left running, like telnet, insecure web and cloud interfaces, and the lack of a secure update mechanism. A device that cannot be updated safely will carry every bug it shipped with for its whole life. Good devices check that every firmware update is signed by the maker before installing it, use secure boot so that only signed software can start, store keys in a secure element chip, turn off debugging ports such as UART and JTAG in production, encrypt their traffic, and collect only the data they need. Makers should publish how long the device will get security updates and give researchers a way to report bugs. As a buyer you can help too: choose brands that promise updates, change any default password straight away, keep devices updated, put them on a separate guest network away from your laptops, and switch off features such as remote access or UPnP that you do not use.')}
{table(['OWASP IoT Top 10 (2018)', 'What it means', 'Good practice'], [
    ['I1 Weak, guessable or hard coded passwords', 'admin and admin, or a password built into the firmware', 'A unique password per device, forced change at setup'],
    ['I2 Insecure network services', 'Telnet, open debug services', 'Turn off everything not needed, close ports'],
    ['I3 Insecure ecosystem interfaces', 'Weak web, mobile app or cloud APIs', 'Authentication and authorisation on every call'],
    ['I4 Lack of secure update mechanism', 'No updates, or unsigned updates', 'Signed, automatic updates over TLS'],
    ['I5 Use of insecure or outdated components', 'Old libraries and kernels', 'Track components with an SBOM and patch them'],
    ['I6 Insufficient privacy protection', 'Collecting too much personal data', 'Collect less, store it safely'],
    ['I7 Insecure data transfer and storage', 'Plain text traffic and files', 'Encrypt in transit and at rest'],
    ['I8 Lack of device management', 'No way to see or fix devices in a fleet', 'Inventory, monitoring, remote update'],
    ['I9 Insecure default settings', 'Everything open out of the box', 'Secure by default'],
    ['I10 Lack of physical hardening', 'Debug ports, easy to open', 'Disable UART and JTAG, tamper evidence']])}
{steps('Making a smart home safer, today', ['Change every default password to a unique one, kept in a password manager.',
       'Turn on automatic updates, and replace devices that no longer get them.',
       'Put IoT devices on a separate guest network.',
       'Switch off UPnP and remote access features you do not use.',
       'Check the router’s list of connected devices now and then.'])}
''', kw=['OWASP IoT Top 10', 'hard coded password', 'secure update', 'firmware signing', 'secure boot', 'secure element', 'UART', 'JTAG', 'SBOM', 'guest network', 'UPnP', 'secure by default'])

K.lesson('ics', 'Industrial control systems: when safety comes first', f'''
{talk('Industrial control systems look very different from office IT. At the bottom are the physical things: pumps, valves, motors, breakers and sensors. Above them sit programmable logic controllers, PLCs, small rugged computers that read sensors and switch outputs many times a second, following simple logic written by engineers. Above those are SCADA systems, supervisory control and data acquisition, and HMIs, human machine interfaces, the screens where operators watch the plant and give commands. A historian database records every reading. And separate from all of these is the safety instrumented system, an independent controller with its own sensors whose only job is to shut the process down safely if something dangerous happens. In office IT the priority is usually confidentiality, then integrity, then availability. In a plant the order flips. Safety comes first, then availability, because stopping a furnace or a grid can itself be dangerous and expensive, then integrity, and confidentiality last. That changes everything. You cannot just reboot a PLC to install a patch, because the process it controls might run for months without stopping, and a plant may run the same controller for twenty years. Scanning a network aggressively can crash old controllers. So industrial security leans on separation, careful monitoring and safety systems that do not trust the computers.')}
{versus('Office IT and industrial OT', ['', 'Office IT', 'Industrial OT'], [
    ['Top priority', 'Confidentiality of data', 'Safety of people, then availability'],
    ['Lifetime', '3 to 5 years', '15 to 30 years'],
    ['Patching', 'Monthly, automatic', 'Planned outages, sometimes once a year or never'],
    ['Downtime', 'Annoying', 'Lost production, blackouts, danger'],
    ['Protocols', 'Modern, encrypted (HTTPS, TLS)', 'Old, often no authentication (Modbus, DNP3, Profinet)'],
    ['Scanning', 'Routine', 'Can crash fragile controllers, done passively or with care'],
    ['Standards', 'ISO 27001, NIST CSF', 'IEC 62443, NIST SP 800-82']],
    'Treat the plant network as a separate world with its own rules, and design so that even a fully hacked control system cannot cause a disaster, because an independent safety layer will stop it.')}
''', kw=['PLC', 'SCADA', 'HMI', 'historian', 'safety instrumented system', 'SIS', 'AIC triad', 'availability first', 'IEC 62443', 'NIST SP 800-82', 'patching in OT', 'legacy systems'])

K.lesson('protocols', 'Industrial protocols with no passwords: Modbus and friends', f'''
{talk('Many industrial protocols were designed in the 1970s and 1980s for wires that ran only inside a factory, where everyone on the network was trusted. Modbus, created by the company Modicon in 1979, is the classic example and is still everywhere. A Modbus command is just a few bytes: who it is for, a function code such as read registers or write a coil, an address and a value. There is no username, no password and no signature. Any device that can reach a PLC on Modbus TCP port 502 can tell it to open a valve, and the PLC will obey. The animation walks through such a frame byte by byte on a toy water tank, and shows the two defences that matter most. An industrial firewall that understands Modbus can allow write commands only from the operator’s HMI and drop everything else. And an independent safety system with its own sensor and valve can stop the tank overflowing whatever the PLC does. Newer versions add security, such as Modbus TCP Security, which wraps the protocol in TLS with certificates and roles, and DNP3 Secure Authentication for power grids, but old equipment lives for decades, so plants must protect insecure protocols for a long time to come.')}
{viz('cymodbus')}
{run('modbus_frame')}
{table(['Protocol', 'Used in', 'Built in security', 'Secure version'], [
    ['Modbus', 'Factories, water, buildings', 'None', 'Modbus TCP Security (TLS)'],
    ['DNP3', 'Electricity and water utilities', 'None originally', 'DNP3 Secure Authentication'],
    ['IEC 61850', 'Electrical substations', 'Limited', 'IEC 62351 security extensions'],
    ['Profinet and EtherNet/IP', 'Factory automation', 'Very limited', 'Newer security profiles, not yet common'],
    ['OPC UA', 'Modern plant data exchange', 'Designed in: signing, encryption, users', 'Use the secure modes, not "None"']])}
''', kw=['Modbus', 'Modicon', 'Modbus TCP', 'port 502', 'function code', 'write coil', 'DNP3', 'IEC 61850', 'Profinet', 'OPC UA', 'industrial firewall', 'deep packet inspection', 'Modbus TCP Security'])

K.lesson('purdue', 'The Purdue model and network segmentation', f'''
{talk('Because old protocols cannot defend themselves, the main protection in a plant is keeping attackers away from them. The Purdue model, from a reference architecture developed at Purdue University in the 1990s, gives a shared way to draw this. It stacks the plant in levels: level 0 is the physical process, level 1 the controllers, level 2 the HMIs and SCADA, level 3 site operations, then an industrial DMZ at level 3.5, level 4 the business network with email and ERP, and level 5 the internet. The rule is that traffic should not jump levels, and that the business network should never talk straight to the control network. Data the business needs, such as production figures, is copied to servers in the DMZ, and engineers who must reach the plant from outside go through a jump host in the DMZ with multi factor authentication and recorded sessions. The most sensitive sites go further and use data diodes, hardware that physically lets signals travel in only one direction, out of the plant. The international standard IEC 62443 turns this into zones and conduits, each zone with a required security level. The animation shows why it matters. On a flat network a phishing email on one office PC can lead all the way to the breakers, which is close to what happened in Ukraine in 2015. With a DMZ, the same breach stays in the office.')}
{viz('cypurdue')}
{run('zone_rules')}
{fxs(fx('Attack path through independent layers', 'P(reach the plant) = p<sub>1</sub> &times; p<sub>2</sub> &times; &hellip; &times; p<sub>k</sub>', 'Three layers each beaten with probability 0.3: 0.3<sup>3</sup> = 0.027.', key=True),
     fx('Data diode', 'traffic in = 0, by physics', 'A fibre with a transmitter on one side and only a receiver on the other.'))}
''', kw=['Purdue model', 'PERA', 'levels', 'industrial DMZ', 'segmentation', 'jump host', 'data diode', 'unidirectional gateway', 'IEC 62443', 'zones and conduits', 'flat network'])

K.lesson('cases', 'Real attacks on industry: Stuxnet to Colonial Pipeline', f'''
{talk('A handful of incidents shaped this whole field. Stuxnet, discovered in 2010, was a worm built to sabotage Iran’s uranium enrichment plant at Natanz. It spread on USB drives into a network with no internet connection, used four previously unknown Windows bugs, found Siemens controllers driving centrifuges, and made them spin too fast and then too slow while replaying normal readings to the operators. Analysts estimate it destroyed around a thousand centrifuges, and it showed the world that code could break machines. On 23 December 2015 attackers who had entered three Ukrainian power companies through phishing emails months earlier used the companies’ own control software to open breakers, cutting power to about 225,000 customers, and then wiped computers and disabled backup power to slow recovery. A year later a malware called Industroyer, which spoke grid protocols directly, caused a blackout in part of Kyiv. In 2017 the Triton malware, also called Trisis, targeted the safety instrumented system of a petrochemical plant in Saudi Arabia. It was found only because a bug in it tripped the plant safely. In May 2021 ransomware hit the office IT of Colonial Pipeline in the United States. The control systems were not infected, but the company shut the pipeline for several days because it could not bill or track fuel safely, causing fuel shortages on the east coast. And in 2019 the operator of India’s Kudankulam nuclear plant confirmed malware on an administrative network, while stating the control systems were isolated and unaffected.')}
{table(['Incident', 'Year', 'Way in', 'Effect', 'Lesson'], [
    ['Stuxnet', '2010', 'USB drives, four zero day bugs', 'Centrifuges damaged, readings faked', 'Air gaps leak, watch the physical process'],
    ['Ukraine grid', '2015', 'Phishing, stolen credentials, remote access tools', 'About 225,000 customers without power', 'Segment, protect remote access, plan manual operation'],
    ['Industroyer', '2016', 'Malware speaking grid protocols', 'Blackout in part of Kyiv', 'Monitor protocol commands'],
    ['Triton or Trisis', '2017', 'Into the safety controller’s network', 'Plant tripped, safety system targeted', 'Isolate safety systems, keep their key switch in RUN'],
    ['Colonial Pipeline', '2021', 'Ransomware via an old VPN password without MFA', 'Pipeline shut for days', 'IT outages hit OT too, MFA on remote access'],
    ['Kudankulam', '2019', 'Malware on an administrative network', 'Control systems reported unaffected', 'Separation between IT and plant works']])}
{run('sensor_anomaly')}
''', kw=['Stuxnet', 'Natanz', 'Siemens', 'zero day', 'Ukraine power grid attack', 'BlackEnergy', 'Industroyer', 'CrashOverride', 'Triton', 'Trisis', 'safety system attack', 'Colonial Pipeline', 'Kudankulam', 'process anomaly detection'])

K.lesson('defend', 'Defending plants: monitor, separate and fail safe', f'''
{talk('Defending industrial systems uses a different rhythm from office security. First, know what you have. Many plants do not have a complete list of their controllers, firmware versions and network links, and you cannot protect what you cannot see. Passive monitoring tools listen to a copy of the network traffic without sending anything, so they cannot crash fragile devices, and they learn which device normally talks to which, using which commands. A new device, a write command from an unusual computer, or a firmware download outside a maintenance window raises an alert. Second, watch the process itself. If a tank level rises while every screen says the valve is shut, something is wrong, whatever the network says, which is the lesson of Stuxnet. Third, keep remote access tight, with a jump host, multi factor authentication and approval for each session, because remote access was the door in Ukraine and at Colonial. Fourth, patch in planned maintenance windows and use compensating controls, such as stricter firewall rules, for devices that cannot be patched. Fifth, keep the safety instrumented system truly independent, with physical key switches that must be turned before its program can be changed. Finally, practise: plants should be able to run manually for a while and should rehearse recovery from a cyber incident just as they rehearse fire drills.')}
{steps('An OT security programme in order', ['Build an asset inventory: every controller, HMI, firmware version and network link.',
       'Draw zones and conduits (IEC 62443) and put a DMZ between IT and OT.',
       'Lock down remote access: jump host, MFA, approval and recording.',
       'Deploy passive network monitoring and alerts on new devices and write commands.',
       'Monitor the physical process for changes nobody ordered.',
       'Patch in maintenance windows and add compensating controls for the rest.',
       'Keep safety systems independent, with key switches in RUN.',
       'Exercise manual operation and incident recovery every year.'])}
{safe('Never scan or probe industrial or utility systems you do not own, even if they appear on the internet. Doing so can break real equipment and is a crime. Practise with simulators and virtual labs such as GRFICSv2, or with a cheap PLC trainer kit on your own desk.')}
''', kw=['asset inventory', 'passive monitoring', 'OT network monitoring', 'anomaly detection', 'remote access', 'jump host', 'maintenance window', 'compensating controls', 'safety key switch', 'manual operation', 'incident exercises', 'GRFICS'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner changes default passwords and updates home devices. A student explains Mirai, the Purdue model and why Modbus is unsafe. A professional builds OT security programmes with IEC 62443 and monitoring. Experts analyse industrial malware, design safety and security together, and protect national infrastructure.')}
{ladder(
    '<p>Smart devices are small computers. Change their passwords, keep them updated, and remember that factories and power stations use computers too, which need extra protection because they control real machines.</p>',
    '<p>Mirai and default passwords, worm growth, OWASP IoT Top 10, PLC, SCADA, HMI and SIS, safety first priorities, Modbus frames with no authentication, Purdue levels and DMZs.</p>',
    '<p>Run IEC 62443 risk assessments, design zones and conduits, deploy passive monitoring, manage remote access and patching in OT, and coordinate with safety engineers.</p>',
    '<p>Reverse engineer industrial malware, design secure by design controllers and protocols, research cyber physical anomaly detection, and work on national infrastructure resilience.</p>')}
{grow('Secure your own smart devices.',
      'Explain how IoT and industrial attacks work and what stops them.',
      'Design and run security for plants and device fleets.')}
''', kw=['beginner', 'expert', 'critical infrastructure', 'cyber physical systems'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>IoT</b>: billions of small, long lived, hard to patch computers. Jeep 2015, Verkada 2021.',
    '<b>Mirai</b>: about 60 default passwords, about 600,000 devices, Krebs, OVH and Dyn attacks in 2016. Worm growth I + I k (W &minus; I)/N. UK default password ban from April 2024.',
    '<b>Safer devices</b>: OWASP IoT Top 10, unique passwords, signed updates, secure boot, no debug ports, guest networks.',
    '<b>ICS</b>: PLC, SCADA, HMI, historian, independent safety system. Safety and availability first. IEC 62443, NIST SP 800-82.',
    '<b>Protocols</b>: Modbus (1979, port 502) has no authentication. Industrial firewalls, OPC UA secure modes, Modbus TCP Security.',
    '<b>Purdue</b>: levels 0 to 5, DMZ at 3.5, no direct IT to OT, jump hosts, data diodes.',
    '<b>Incidents</b>: Stuxnet 2010, Ukraine 2015, Industroyer 2016, Triton 2017, Colonial 2021, Kudankulam 2019. Watch the process, protect remote access.'],
    'Advanced 4.4: API security, because the apps, devices and clouds in this step all talk to each other through APIs.')}
{files('Three tasks: find default credentials, parse a Modbus function code, and check a zone path.')}
''', kw=['summary', 'recap'])

# ------------------------------------------------------------------------------------------------ quiz
K.quiz('e', 'What is the first thing to do with a new smart camera?', ['Put it on the internet', 'Change the default password to a unique one and update it', 'Turn on telnet', 'Share its password'], 1, 'Mirai’s door.', 'Default passwords are how Mirai built its botnet.')
K.quiz('e', 'What did the Mirai botnet use to break into devices?', ['A new zero day', 'A list of factory usernames and passwords', 'Phishing emails', 'Bluetooth'], 1, 'admin and admin.', 'About 60 default pairs were enough.')
K.quiz('e', 'In a factory, which goal usually comes first?', ['Confidentiality', 'Safety of people, then availability', 'Speed', 'Cost'], 1, 'Physical processes.', 'Stopping or breaking a process can hurt people.')
K.quiz('e', 'Where should smart home devices sit on your home network?', ['On the same network as your work laptop', 'On a separate guest network', 'Directly on the internet', 'Nowhere'], 1, 'Separation.', 'A hacked device then cannot reach your laptops easily.')
K.quiz('m', 'What does a PLC do?', ['Sends emails', 'Reads sensors and switches outputs to control machines', 'Stores web pages', 'Runs the office network'], 1, 'Programmable logic controller.', 'It follows simple logic many times a second.')
K.quiz('m', 'Why is Modbus risky on a network attackers can reach?', ['It is slow', 'Commands carry no username, password or signature', 'It is encrypted', 'It uses too many ports'], 1, 'Designed for closed networks.', 'Any device reaching port 502 can send commands.')
K.quiz('m', 'In the Purdue model, which level holds the industrial DMZ?', ['Level 0', 'Level 2', 'Level 3.5', 'Level 5'], 2, 'Between business and operations.', 'It brokers data so IT never talks straight to OT.')
K.quiz('m', 'What is a data diode?', ['A fast router', 'Hardware that lets data travel in only one direction', 'An antivirus', 'A kind of PLC'], 1, 'One way by physics.', 'Data can leave the plant but nothing can come in.')
K.quiz('m', 'What is the job of a safety instrumented system?', ['Display graphs', 'Independently shut the process down safely when something dangerous happens', 'Send billing data', 'Run the HMI'], 1, 'Last line of defence.', 'It does not trust the control system.')
K.quiz('h', 'How did Stuxnet hide its sabotage from operators?', ['It turned the screens off', 'It replayed normal readings while changing centrifuge speeds', 'It encrypted the plant', 'It did not hide'], 1, 'Fake normal.', 'This is why watching the physical process matters.')
K.quiz('h', 'What was unusual about the Triton malware of 2017?', ['It stole credit cards', 'It targeted a plant’s safety instrumented system', 'It was a phishing kit', 'It mined cryptocurrency'], 1, 'The last line of defence.', 'A bug in it tripped the plant safely and exposed it.')
K.quiz('h', 'Why did Colonial Pipeline stop the pipeline in 2021 though OT was not infected?', ['A court ordered it', 'Ransomware on IT systems meant it could not run billing and operations safely', 'A flood', 'The PLCs failed'], 1, 'IT and OT depend on each other.', 'The shutdown was a precaution.')
K.quiz('h', 'Why do OT teams prefer passive network monitoring?', ['It is cheaper', 'It only listens, so it cannot crash fragile controllers', 'It blocks all traffic', 'It needs no sensors'], 1, 'Do not touch.', 'Active scans can upset old devices.')
K.quiz('x', 'In the style of a Georgia Tech CPS security question: three independent defence layers, each beaten with probability 0.3. P(attacker passes all three)?', ['0.9', '0.3', '0.027', '0.09'], 2, 'Multiply.', '0.3 &times; 0.3 &times; 0.3 = 0.027.')
K.quiz('x', 'In the style of an IIT Kharagpur SCADA exam: in a Modbus TCP frame, function code 05 means', ['Read coils', 'Write single coil', 'Read holding registers', 'Write multiple registers'], 1, 'A single output.', '05 switches one coil on (FF00) or off (0000).')

# ------------------------------------------------------------------------------------------------ problems
K.calc('e', '600,000 bots each send 1 Mbit/s. Attack size in Tbit/s?', '0.6', 'Multiply, then convert.', ['600,000 Mbit/s.', '1 Tbit/s = 1,000,000 Mbit/s.', eq('0.6 Tbit/s')], check=600000 / 1e6)
K.calc('e', '120 devices, 60% on default passwords. How many weak devices?', '72', 'N &times; share.', ['120 &times; 0.6.', 'Whole devices.', eq('72')], check=120 * 0.6)
K.calc('e', 'Three layers each beaten with probability 0.3. P(all three beaten)?', '0.027', 'Multiply.', ['0.3 &times; 0.3 = 0.09.', '&times; 0.3.', eq('0.027')], check=round(0.3 ** 3, 3))
K.calc('m', 'Worm step: I = 10 bots, k = 3 probes each, W = 600 weak of N = 1,000. New infections this round?', '17.7', 'I k (W &minus; I) / N.', ['10 &times; 3 = 30 probes.', '30 &times; 590 / 1000.', eq('17.7')], check=10 * 3 * (600 - 10) / 1000)
K.calc('m', 'Weak share falls from 60% to 2%. By what factor does the pool of targets shrink?', '30', '0.6 / 0.02.', ['Ratio of shares.', '60 / 2.', eq('30 times')], check=round(0.6 / 0.02))
K.calc('m', 'A Modbus TCP header is 7 bytes and a write single coil body is 5 bytes. Total frame length?', '12', '7 + 5.', ['Header: transaction, protocol, length, unit.', 'Body: function, address (2), value (2).', eq('12 bytes')], check=12)
K.calc('m', 'Modbus coil value FF00 in hex. Decimal?', '65280', '255 &times; 256.', ['FF = 255, 00 = 0.', '255 &times; 256 + 0.', eq('65,280')], check=0xFF00)
K.calc('h', 'Tank level readings have mean 40.8 and standard deviation 0.75. A reading of 47: z score? Round to 2 decimals.', '8.27', '(x &minus; mean) / sd.', ['47 &minus; 40.8 = 6.2.', '6.2 / 0.75.', eq('&asymp; 8.27')], check=round((47 - 40.8) / 0.75, 2))
K.calc('h', 'A plant patches its PLCs once a year. A fix comes out at a random time. Average wait in months until it is installed?', '6', 'Uniform over 12 months.', ['The fix arrives anywhere in the year.', 'Mean of uniform(0, 12).', eq('6 months')], check=6)
K.calc('h', 'Ukraine 2015: about 225,000 customers lost power for about 3 hours. Customer hours lost?', '675000', 'Multiply.', ['225,000 &times; 3.', 'Customer hours.', eq('675,000')], check=225000 * 3)
K.calc('x', 'An IDS sees 2,000 Modbus writes a day, 1 of them malicious. It flags 99% of bad writes and 0.5% of good ones. P(malicious | flagged)? Round to 3 decimals.', '0.09', 'Bayes.', ['True alerts: 0.99.', 'False alerts: 1,999 &times; 0.005 = 9.995.', eq('0.99 / 10.985 &asymp; 0.090')], check=round(0.99 / (0.99 + 1999 * 0.005), 3))

# ------------------------------------------------------------------------------------------------ assignments
K.assign('find_defaults', 'e', 'Find devices with factory passwords',
         '<p>devices is a list of (name, user, password) tuples and defaults is a set of (user, password) pairs. Write <code>weak(devices, defaults)</code> that returns the sorted list of names whose login is in defaults.</p>',
         '''
def weak(devices, defaults):
    # your code here
    pass
''', [('weak([("cam", "admin", "admin"), ("dvr", "root", "xc3511"), ("tv", "u", "Qx!9")], {("admin", "admin"), ("root", "xc3511")})', ['cam', 'dvr']), ('weak([], {("a", "b")})', []), ('weak([("x", "admin", "Admin")], {("admin", "admin")})', [])],
         '''
def weak(devices, defaults):
    return sorted(name for name, user, pw in devices if (user, pw) in defaults)
''', 'Unpack each tuple and test (user, pw) in defaults.', '<p>The third test matters: passwords are case sensitive, so "Admin" is not "admin". Real audits also try common variants, because attackers do.</p>')
K.assign('modbus_func', 'm', 'Name a Modbus function code',
         '<p>Write <code>func_name(frame_hex)</code>. frame_hex is a Modbus TCP frame as a hex string (spaces allowed). The function code is byte 8 (index 7). Return <code>"read"</code> for codes 1, 2, 3, 4, <code>"write"</code> for 5, 6, 15, 16, and <code>"other"</code> otherwise.</p>',
         '''
def func_name(frame_hex):
    # your code here
    pass
''', [('func_name("002A 0000 0006 01 05 0010 FF00")', 'write'), ('func_name("0001 0000 0006 01 03 0000 000A")', 'read'), ('func_name("0001 0000 0002 01 2B")', 'other')],
         '''
def func_name(frame_hex):
    data = bytes.fromhex(frame_hex.replace(" ", ""))
    code = data[7]
    if code in (1, 2, 3, 4):
        return "read"
    if code in (5, 6, 15, 16):
        return "write"
    return "other"
''', 'bytes.fromhex turns the string into bytes. data[7] is the function code as an integer.', '<p>Industrial firewalls and monitors make exactly this decision on every packet: reads are usually fine from many places, writes only from the operator stations.</p>')
K.assign('zone_path', 'h', 'Is there an allowed path into the plant?',
         '<p>allow is a set of (from, to) pairs. Write <code>reachable(allow, start, goal)</code> that returns True if goal can be reached from start by following allowed pairs (breadth first search).</p>',
         '''
from collections import deque

def reachable(allow, start, goal):
    # your code here
    pass
''', [('reachable({("office", "dmz"), ("dmz", "hmi"), ("hmi", "plc")}, "office", "plc")', True),
      ('reachable({("office", "dmz"), ("hmi", "plc")}, "office", "plc")', False),
      ('reachable(set(), "plc", "plc")', True)],
         '''
from collections import deque

def reachable(allow, start, goal):
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == goal:
            return True
        for a, b in allow:
            if a == node and b not in seen:
                seen.add(b)
                queue.append(b)
    return False
''', 'Keep a queue and a seen set. For each node, add every allowed next hop you have not visited.', '<p>Auditors run this kind of search over real firewall rules to find forgotten paths from the office network into control systems.</p>')

K.must('IoT and OT', 'Small, long lived, hard to patch computers in homes, cars, hospitals and plants. Attacks can cause physical harm. Jeep 2015 (1.4 million recalled), Verkada 2021.')
K.must('Mirai', 'About 60 default telnet passwords, about 600,000 bots, Krebs (about 620 Gbit/s), OVH, Dyn on 21 October 2016. Worm growth I k (W &minus; I)/N. UK ban on default passwords from 29 April 2024, EU Cyber Resilience Act.')
K.must('Safer devices', 'OWASP IoT Top 10: I1 weak passwords, I2 network services, I3 interfaces, I4 updates, I5 components, I6 privacy, I7 data, I8 management, I9 defaults, I10 physical. Signed updates, secure boot, guest networks.')
K.must('ICS basics', 'Levels: sensors and actuators, PLCs, HMI and SCADA, historian, independent safety instrumented system. Safety and availability first. IEC 62443, NIST SP 800-82 Rev. 3.')
K.must('Protocols', 'Modbus (Modicon 1979, TCP port 502) and DNP3 have no authentication. Function 05 writes a coil. Industrial firewalls, OPC UA secure modes, Modbus TCP Security, DNP3 SA.')
K.must('Purdue and segmentation', 'Levels 0 to 5, DMZ at 3.5, no direct IT to OT, jump host with MFA, data diodes, zones and conduits.')
K.must('Incidents', 'Stuxnet (2010, faked readings), Ukraine (23 December 2015, about 225,000 customers), Industroyer (2016), Triton (2017, safety system), Colonial (2021, IT ransomware stopped OT), Kudankulam (2019, admin network only).')

T = K.topic(
    slug='cy-iot', topic='cy-iot', step=(4, 'Beyond the web', 'cy-a4', 'Security for people, phones, connected devices, industrial systems and the APIs that link them.', 'Advanced'),
    title='IoT and industrial control security: Mirai, Modbus, Purdue and Stuxnet', short='IoT and ICS security', badge='4.3', minutes=85,
    lead='How connected gadgets and the computers that run factories and power grids are attacked and protected: default passwords and the Mirai botnet, safer device design, PLCs, SCADA and safety systems, Modbus with no passwords, the Purdue model and segmentation, and the incidents from Stuxnet to Colonial Pipeline.',
    desc='IoT security, Internet of Things, Mirai, botnet, DDoS, default password, telnet, OWASP IoT Top 10, firmware update, secure boot, industrial control systems, ICS, OT, SCADA, PLC, HMI, historian, safety instrumented system, Modbus, DNP3, OPC UA, Purdue model, DMZ, data diode, IEC 62443, NIST SP 800-82, Stuxnet, Ukraine power grid, Industroyer, Triton, Colonial Pipeline, Kudankulam, Jeep Cherokee, Verkada',
    summary='IoT risks and Mirai, OWASP IoT Top 10, ICS components and priorities, Modbus without authentication, the Purdue model and segmentation, major industrial incidents, and OT defence.',
    keywords=['IoT', 'Mirai', 'default password', 'ICS', 'SCADA', 'PLC', 'Modbus', 'Purdue model', 'Stuxnet', 'safety system'],
    recap='<p>Give every device a unique password and signed updates, keep the office and the plant on separate networks, allow only known writers to controllers, and let an independent safety system have the last word.</p>',
    added='2026-11-22')
