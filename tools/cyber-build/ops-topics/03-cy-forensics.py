# Security Operations 1.3: digital forensics. Checked against RFC 3227 Guidelines for Evidence Collection and Archiving
# (2002), NIST SP 800-86 Guide to Integrating Forensic Techniques into Incident Response (2006), ISO/IEC 27037:2012, the
# Microsoft FAT and NTFS documentation ($STANDARD_INFORMATION and $FILE_NAME times, FILETIME), Gary Kessler's file
# signature table, the Volatility Foundation documentation, the Plaso (log2timeline) documentation, section 63 of the
# Bharatiya Sakshya Adhiniyam 2023 and the Supreme Court of India in Anvar P.V. v. P.K. Basheer (2014) and Arjun
# Panditrao Khotkar v. Kailash Kushanrao Gorantyal (2020), and public reports on the BTK case (2005).
from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk, safe

chapter('cy-forensics')
K = Kit()

K.code('image_hash', r'''
# Proving a disk image never changed: hash it when it is made, and again every time it is used
import hashlib

# a pretend 4 KB disk image made of repeating text (a real one is a file of many gigabytes)
image = (b"Quarterly report draft. " * 200)[:4096]

def fingerprint(data):
    return hashlib.sha256(data).hexdigest()

at_seizure = fingerprint(image)
print("hash recorded at seizure:", at_seizure[:16], "...")

at_lab = fingerprint(image)
print("hash at the lab:         ", at_lab[:16], "...", "MATCH" if at_lab == at_seizure else "DIFFERENT")

# someone mounts the original without a write blocker and one byte changes
changed = bytearray(image)
changed[100] ^= 1                      # flip a single bit
after_mistake = fingerprint(bytes(changed))
print("hash after one bit flip: ", after_mistake[:16], "...", "MATCH" if after_mistake == at_seizure else "DIFFERENT")

same = sum(1 for a, b in zip(at_seizure, after_mistake) if a == b)
print(f"\nOnly 1 bit of 32768 changed, yet only {same} of 64 hex digits of the hash stayed the same.")
print("This is the avalanche effect, and it is why one hash can stand for a whole disk.")
''')

K.code('file_carve', r'''
# File carving: find files inside raw bytes by their magic numbers (start and end patterns)
SIGNATURES = {
    "jpeg": (bytes.fromhex("FFD8FF"), bytes.fromhex("FFD9")),
    "pdf": (b"%PDF", b"%%EOF"),
    "png": (bytes.fromhex("89504E470D0A1A0A"), b"IEND"),
}

raw = (bytes.fromhex("0013 7A00 41") + bytes.fromhex("FFD8FFE0104A46FFD9") + bytes.fromhex("0000 2E91 0005 0077")
       + b"%PDF-1\n%%EOF" + bytes.fromhex("003C 0000 1100") + bytes.fromhex("89504E470D0A1A0A"))
print(f"{len(raw)} raw bytes from unallocated space\n")

for kind, (head, foot) in SIGNATURES.items():
    start = raw.find(head)
    while start != -1:
        end = raw.find(foot, start + len(head))
        if end == -1:
            print(f"{kind:4}: header at offset {start}, no footer, partial file of {len(raw) - start} bytes")
        else:
            end += len(foot)                          # include the footer
            print(f"{kind:4}: header at offset {start}, footer ends at {end - 1}, carved {end - start} bytes")
        start = raw.find(head, start + 1)
''')

K.code('deleted_file', r'''
# Why deleted files can come back: a tiny FAT style file system.
# Deleting only marks the directory entry (first byte becomes 0xE5) and frees the clusters. The data stays.
CLUSTER = 8                      # bytes per cluster, tiny so we can print it
disk = bytearray(b"." * 64)      # 8 clusters of free space

directory = []                   # each entry: [name, first cluster, size]

def save(name, data, first):
    disk[first * CLUSTER: first * CLUSTER + len(data)] = data
    directory.append([name, first, len(data)])

def delete(name):
    for entry in directory:
        if entry[0] == name:
            entry[0] = "\xe5" + name[1:]           # FAT marks a deleted entry with 0xE5
    print(f"deleted {name}: the directory now shows {[e[0] for e in directory]!r}")

save("PLAN.TXT", b"Meet at gate 4 at 9pm", 1)
save("LIST.TXT", b"milk eggs", 5)
delete("PLAN.TXT")

print("\nThe disk bytes are untouched:")
print(disk.decode())

for name, first, size in directory:
    if name.startswith("\xe5"):
        data = disk[first * CLUSTER: first * CLUSTER + size]
        print(f"\nrecovered ?{name[1:]} from cluster {first}: {data.decode()!r}")
print("\nThe first letter of the name is lost, so tools show it as ? or _. On SSDs, TRIM often wipes the data soon after.")
''')

K.code('timeline', r'''
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
''')

K.code('hidden_process', r'''
# Memory forensics in miniature: list walking versus scanning.
# Windows keeps running processes in a linked list. Rootkits unlink themselves (DKOM) so the list skips them.
# Scanning all of memory for the process structure's signature still finds them, as Volatility's psscan does.
memory = {
    0x1000: {"tag": "Proc", "pid": 4, "name": "System", "next": 0x2000},
    0x2000: {"tag": "Proc", "pid": 612, "name": "lsass.exe", "next": 0x3000},
    0x3000: {"tag": "Proc", "pid": 1880, "name": "explorer.exe", "next": 0x5000},
    0x4000: {"tag": "Proc", "pid": 6666, "name": "svch0st.exe", "next": 0x5000},   # unlinked: nobody points here
    0x5000: {"tag": "Proc", "pid": 2210, "name": "chrome.exe", "next": None},
    0x6000: {"tag": "Data", "text": "random heap bytes"},
}

def walk_list(head):
    found, addr = [], head
    while addr is not None:
        proc = memory[addr]
        found.append((proc["pid"], proc["name"]))
        addr = proc["next"]
    return found

def scan_memory():
    return [(m["pid"], m["name"]) for addr, m in sorted(memory.items()) if m["tag"] == "Proc"]

listed = walk_list(0x1000)
scanned = scan_memory()
print("pslist (walk the list):", [n for _, n in listed])
print("psscan (scan memory):  ", [n for _, n in scanned])
hidden = set(scanned) - set(listed)
print("\nIn the scan but not in the list:", hidden)
print("A process named svch0st.exe (zero, not o) hiding from the list is a strong sign of a rootkit.")
''')

K.code('volatility_order', r'''
# Plan a collection in the order of volatility from RFC 3227: most fragile first
ORDER = {
    "registers and cache": 1,
    "routing table, ARP cache, process table, kernel statistics, memory": 2,
    "temporary file systems": 3,
    "disk": 4,
    "remote logging and monitoring data": 5,
    "physical configuration and network topology": 6,
    "archival media (backups)": 7,
}
found_on_scene = ["disk", "archival media (backups)", "routing table, ARP cache, process table, kernel statistics, memory",
                  "remote logging and monitoring data", "temporary file systems"]

plan = sorted(found_on_scene, key=lambda item: ORDER[item])
for step, item in enumerate(plan, start=1):
    print(f"{step}. collect {item}")
print("\nWrite down the time, the tool and its version, and the hash of everything you collect.")
''')

K.lesson('idea', 'What digital forensics is: evidence that holds up', f'''
{talk('Digital forensics means finding, collecting, studying and presenting evidence from computers, phones, networks and cloud accounts, in a way that a court, a regulator or a company board can trust. It grew out of police work. The French criminologist Edmond Locard, in the early twentieth century, taught that every contact leaves a trace. A burglar leaves fingerprints and takes away dust. Computers are the same: an intruder who logs in, runs a program or copies a file leaves records in logs, in memory, in file system time stamps and in network devices. A famous example is the BTK serial killer in Kansas, who had escaped police for about thirty years. In 2005 he sent the police a floppy disk. Hidden details inside a Word document on it named a church and a user called Dennis, and that led quickly to Dennis Rader’s arrest. Forensics is also used every day for ordinary cases: an employee who took customer data before leaving, a fraud in accounts, or a ransomware attack where the company must know what data was taken. The work follows a few strict rules. Do not change the original. Work on verified copies. Record everything you do, with the time and the tool. Be able to repeat your steps and get the same result. And keep an unbroken record of who held the evidence, called the chain of custody.')}
{src('RFC 3227 Guidelines for Evidence Collection and Archiving (Brezinski and Killalea, 2002), NIST SP 800-86 (2006), ISO/IEC 27037:2012, Volatility Foundation documentation, Plaso documentation, Microsoft FAT and NTFS specifications, Bharatiya Sakshya Adhiniyam 2023 section 63, Supreme Court of India judgments in Anvar P.V. v. P.K. Basheer (2014) and Arjun Panditrao Khotkar (2020), FBI and press reports on the BTK case (2005).')}
{safe('Only examine devices and data you own or have written permission to examine. The programs here use small made up byte strings. For practice images, use the free test images published by NIST’s Computer Forensic Reference Data Sets.')}
{wwh('<b>Digital forensics</b> is the careful collection and study of digital evidence so that the findings can be trusted and repeated by others.',
     'After an incident, people need facts: how the attacker got in, what they touched, what was taken, and who did it. Courts and regulators accept only evidence that was handled properly.',
     'Collect in the order of volatility, make exact copies through write blockers, prove them unchanged with hashes, analyse the copies with tested tools, build a timeline, and write a clear report.')}
{steps('The forensic process (NIST SP 800-86)', [
    'Collection: identify the sources of evidence and collect them without changing them, most fragile first.',
    'Examination: process the data, for example recover deleted files and pull out logs and time stamps.',
    'Analysis: connect the findings into a story that answers the questions asked.',
    'Reporting: write what was done, what was found and how sure we are, so a non expert can follow it.'])}
''', kw=['digital forensics', 'Locard exchange principle', 'evidence', 'BTK case', 'metadata', 'NIST SP 800-86', 'ISO 27037', 'RFC 3227', 'repeatability'])

K.lesson('collect', 'Collecting evidence: order of volatility, write blockers and hashes', f'''
{talk('Some evidence disappears in nanoseconds, some lasts for years. RFC 3227, written in 2002, lists the order to collect it: first CPU registers and cache, then memory with the routing table, the ARP cache, the list of processes and the network connections, then temporary files, then the disk, then remote logs, then the physical setup, and last of all backups and archives. In practice the first two are captured together by dumping the memory of the running machine to an external drive with a tool such as WinPmem on Windows or LiME on Linux. That is why responders today usually do not pull the plug straight away, as the animation shows. Pulling the plug loses running malware, open network connections and the keys that unlock encrypted disks. Next the disk is copied bit for bit into an image file. The copy is made through a write blocker, a small device or software switch that lets the computer read the disk but never write to it, because even plugging a disk into a normal computer can change some bytes. Then the image is hashed with SHA-256, and the hash is written on the evidence form. Anyone can later hash the image again. If the hash is the same, the image is the same, down to every single bit. Older cases used MD5 and SHA-1, which are now broken for collisions, so SHA-256 is the safe choice today, and some labs record two hashes.')}
{viz('cyvolatility')}
{run('volatility_order')}
{run('image_hash')}
{fxs(fx('Imaging time', 't = size / speed', '500 GB at 200 MB per second: 2500 seconds &asymp; 41.7 minutes. Verifying reads it again, so double it.', key=True),
     fx('Chance of a random SHA-256 match', 'P &asymp; n<sup>2</sup> / 2<sup>257</sup> for n items', 'Even for 2<sup>32</sup> files, P &asymp; 2<sup>&minus;193</sup>. A matching hash means the same data.', key=True))}
{note('Photograph the scene and the screen before touching anything, and note what is running. If the disk is encrypted and the machine is unlocked, capture memory and a logical copy of the files before it locks.', 'warn')}
''', kw=['order of volatility', 'RFC 3227', 'memory capture', 'WinPmem', 'LiME', 'pull the plug', 'write blocker', 'disk image', 'bit for bit copy', 'SHA-256', 'MD5', 'hash verification'])

K.lesson('disk', 'Disk forensics: deleted files, slack space and carving', f'''
{talk('When you delete a file, the computer usually does not erase it. It is faster to just mark the space as free and remove the name from the folder list. On the old FAT file system, the first letter of the file name is replaced with the byte E5 in hexadecimal, and the file’s clusters are marked free. The bytes stay on the disk until a new file happens to be written on top of them. That is why deleted files can often be recovered, as the program below shows. Two other hiding places matter. Slack space is the unused end of the last cluster of a file. If clusters are 4096 bytes and a file is 10000 bytes, it needs three clusters, and the last 2288 bytes may still hold pieces of an older file. Unallocated space is all the clusters marked free, full of old data. If the file system itself is damaged or formatted, the names and folders are gone, but files can still be found by carving: scanning raw bytes for the magic numbers that start and end each file type, such as FF D8 FF for a JPEG photo or %PDF for a PDF. Real carvers such as PhotoRec, Foremost and Scalpel do this across whole disks. Two modern changes make recovery harder. Solid state drives use a command called TRIM that tells the drive which blocks are free, and the drive often wipes them soon after. And full disk encryption, such as BitLocker or FileVault, makes the raw bytes unreadable without the key.')}
{run('deleted_file')}
{viz('cycarve')}
{run('file_carve')}
{table(['File type', 'Header (hex)', 'Footer', 'Note'], [
    ['JPEG', 'FF D8 FF', 'FF D9', 'Photos from almost every camera and phone'],
    ['PNG', '89 50 4E 47 0D 0A 1A 0A', 'IEND chunk', 'Screenshots and web images'],
    ['PDF', '25 50 44 46 (%PDF)', '%%EOF', 'May have several %%EOF after edits'],
    ['ZIP, DOCX, XLSX', '50 4B 03 04 (PK)', 'End of central directory', 'Office files are ZIP files inside'],
    ['Windows program', '4D 5A (MZ)', 'None fixed', 'Executables and DLLs']])}
{fxs(fx('Slack space', 'slack = clusters &times; cluster size &minus; file size', '10000 bytes in 4096 byte clusters: 3 &times; 4096 &minus; 10000 = 2288 bytes.', key=True),
     fx('False header hits', 'expected = positions / 2<sup>8k</sup> for a k byte magic number', 'A 4 byte pattern in 1 TB of random data appears about 233 times by chance, so carvers also check structure.', key=True))}
''', kw=['deleted file recovery', 'FAT', '0xE5', 'cluster', 'slack space', 'unallocated space', 'file carving', 'magic number', 'file signature', 'PhotoRec', 'Foremost', 'Scalpel', 'TRIM', 'SSD', 'full disk encryption'])

K.lesson('time', 'Time stamps and timelines', f'''
{talk('Time is the backbone of every investigation. File systems keep several time stamps for each file, often called MAC times: when the content was last Modified, when it was last Accessed, and when the file record was Changed or the file was Created, depending on the system. NTFS, the Windows file system, keeps two sets: one in a part called $STANDARD_INFORMATION, which normal programs can change, and one in $FILE_NAME, which is much harder to change. Attackers sometimes use a trick called timestomping, giving a malicious file a fake old date so it hides among old files. When the $STANDARD_INFORMATION date is earlier than the $FILE_NAME date, or the fraction of a second is exactly zero, an examiner gets suspicious. Windows stores times as a number called FILETIME, which counts 100 nanosecond steps since 1 January 1601. Linux and most logs use Unix time, the seconds since 1 January 1970. Converting between them, and from local time to UTC, is a daily job, and a mistake of one hour from daylight saving or of five and a half hours from Indian time can ruin a timeline. The goal is a super timeline: every event from every source, in one list, in UTC, sorted by time. The free tool Plaso, also called log2timeline, builds one from hundreds of kinds of logs and files, and the story of the attack usually jumps out, as in the animation.')}
{viz('cytimeline')}
{run('timeline')}
{fxs(fx('Windows FILETIME to Unix time', 'unix = FILETIME / 10<sup>7</sup> &minus; 11644473600', '132539328000000000 / 10<sup>7</sup> &minus; 11644473600 = 1609459200, which is 1 January 2021 00:00 UTC.', key=True),
     fx('Indian time to UTC', 'UTC = IST &minus; 5 h 30 min', '10:00 IST is 04:30 UTC.', key=True))}
{note('Clocks drift and can be set wrong on purpose. Compare each device’s clock with a trusted time when you collect it, and record the difference so you can correct its time stamps.')}
''', kw=['time stamps', 'MAC times', 'NTFS', '$STANDARD_INFORMATION', '$FILE_NAME', 'timestomping', 'FILETIME', 'Unix time', 'UTC', 'IST', 'super timeline', 'Plaso', 'log2timeline'])

K.lesson('memory', 'Memory and artefact forensics', f'''
{talk('Memory forensics studies a copy of a computer’s RAM. It matters more every year, because a lot of modern malware never writes a file to disk. It lives only in memory, so a disk image would miss it. From a memory image, an examiner can list running processes, open network connections, loaded program libraries, command lines that were typed, and sometimes passwords and encryption keys. The best known free tool is the Volatility Framework, first released in 2007 by Aaron Walters, now in its third version. One clever trick shows its power. Windows keeps its running processes in a linked list. A rootkit can hide by unlinking itself from the list, a technique called direct kernel object manipulation. Tools that walk the list, such as Task Manager, no longer see it. But Volatility’s psscan ignores the list and scans all of memory for the pattern of a process structure, so the hidden process shows up, as the program below shows. Beyond memory, operating systems leave many useful artefacts. On Windows, Prefetch files show which programs ran and when, the registry Run keys show what starts at boot, the Amcache and ShimCache list programs that were present, and browser history shows websites visited. On Linux, bash history, auth.log and cron files tell a similar story. Phones and cloud accounts have their own artefacts, and cloud forensics often relies on the provider’s audit logs, because you cannot take the provider’s disks.')}
{run('hidden_process')}
{table(['Artefact', 'System', 'What it shows'], [
    ['Prefetch files', 'Windows', 'Programs run, how many times, last run times'],
    ['Registry Run keys, services', 'Windows', 'Programs set to start automatically (persistence)'],
    ['Event logs 4624, 4688, 7045', 'Windows', 'Logons, new processes, new services'],
    ['bash_history, auth.log, cron', 'Linux', 'Commands typed, logins and sudo, scheduled jobs'],
    ['Browser history and downloads', 'Any', 'Sites visited, files downloaded'],
    ['Cloud audit logs', 'AWS, Azure, Google Cloud', 'Who changed what, from where']])}
{deep('Why scanning beats walking', '<p>Walking a list trusts every pointer in it, so one changed pointer hides an entry. Scanning trusts nothing: it checks every position for the expected pattern, such as the tag and the shape of a process structure. Scanning also finds processes that have exited but whose memory has not yet been reused. The cost is speed and some false hits, so examiners compare both views and look at the differences.</p>')}
''', kw=['memory forensics', 'RAM', 'fileless malware', 'Volatility', 'pslist', 'psscan', 'DKOM', 'rootkit', 'Prefetch', 'registry Run keys', 'Amcache', 'ShimCache', 'bash_history', 'cloud forensics'])

K.lesson('custody', 'Chain of custody, reports and the law', f'''
{talk('Evidence is only useful if others can trust it. The chain of custody is a written record of every person who held the evidence, when, where and why, from the moment it was seized to the moment it reaches court. Each hand over is signed, and the hash is checked again, as the animation shows. A gap in the chain, or a hash that no longer matches, lets the other side argue that the evidence was changed. In India, electronic records used in court must come with a certificate. For years this was section 65B of the Indian Evidence Act, and the Supreme Court said in Anvar P.V. versus P.K. Basheer in 2014, and again in Arjun Panditrao Khotkar in 2020, that the certificate is required. From 1 July 2024 the Bharatiya Sakshya Adhiniyam replaced the old Act, and section 63 now covers electronic records. The final product of forensic work is the report. A good report says what questions were asked, what evidence was collected and how, which tools and versions were used, what was found, what it means, and how sure the examiner is. It separates facts from opinions, and it is written so that a judge or a manager who is not technical can follow it. The examiner must be ready to explain every step and to have another expert repeat it and get the same result.')}
{viz('cycustody')}
{table(['Rule', 'Why it matters'], [
    ['Never work on the original', 'Any change gives the other side a reason to doubt everything'],
    ['Hash at collection and at every use', 'Proves the copy is exactly the original'],
    ['Record every hand over', 'No gaps in who held the evidence'],
    ['Use tested tools and note versions', 'Another expert can repeat the work'],
    ['Separate facts from opinions in the report', 'The reader knows what is proven and what is judged']])}
''', kw=['chain of custody', 'evidence form', 'hash verification', 'section 65B', 'Bharatiya Sakshya Adhiniyam', 'section 63', 'Anvar v Basheer', 'expert report', 'admissibility'])

K.lesson('versus', 'Kinds of forensics compared', f'''
{talk('Forensics splits into fields by where the evidence lives. Each needs its own tools and has its own limits. A real investigation usually combines several of them, for example memory and disk from the infected laptop, logs from the SIEM, and audit logs from the cloud.')}
{versus('Where the evidence lives', ['', 'Disk', 'Memory', 'Network', 'Mobile', 'Cloud'], [
    ['Best for', 'Files, deleted data, history', 'Running and fileless malware, keys', 'What crossed the wire, data theft', 'Messages, location, apps', 'Changes to accounts and services'],
    ['Main tools', 'FTK Imager, Autopsy, Sleuth Kit', 'Volatility, WinPmem, LiME', 'Wireshark, Zeek, full packet capture', 'Cellebrite, adb backups', 'CloudTrail, Azure and Google audit logs'],
    ['Lasts', 'Until overwritten', 'Until power off', 'Only if captured at the time', 'Varies, often encrypted', 'As long as logs are kept'],
    ['Hard part', 'Encryption, SSD TRIM', 'Must capture live', 'Encryption (TLS), volume', 'Locked devices, encryption', 'No access to provider hardware']],
    'Capture memory first on a live machine, image the disk, pull the logs from the SIEM and the cloud, and join it all on one timeline.')}
''', kw=['comparison', 'disk forensics', 'memory forensics', 'network forensics', 'mobile forensics', 'cloud forensics', 'Autopsy', 'Sleuth Kit', 'FTK Imager', 'Zeek'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows that computers keep traces and that evidence must not be changed. A student can hash images, carve files, read time stamps and build timelines. A professional examiner collects evidence on site, analyses memory and disks, and writes reports that hold up in court. Experts research new artefacts, defeat anti forensic tricks, and give testimony in difficult cases.')}
{ladder(
    '<p>Every action on a computer leaves a small trace. Detectives collect those traces carefully, never change them, and write down who looked after them.</p>',
    '<p>Order of volatility, write blockers, SHA-256 verification, FAT deletion and slack space, carving by magic numbers, MAC times and timestomping, FILETIME, memory lists versus scans, chain of custody.</p>',
    '<p>Live response and memory capture, Autopsy and Volatility analysis, super timelines with Plaso, mobile and cloud acquisition, expert reports and courtroom testimony under section 63 of the Bharatiya Sakshya Adhiniyam.</p>',
    '<p>New artefacts in each OS release, anti forensics and its detection, forensics of encrypted and TRIM enabled storage, memory analysis of virtual machines and containers, and the statistics of evidence strength.</p>')}
{grow('Explain why evidence must be handled carefully and never changed.',
      'Hash, carve and build timelines from raw data.',
      'Run a full investigation and defend the report.')}
''', kw=['beginner', 'expert', 'anti forensics', 'expert witness'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Forensics</b>: collect, examine, analyse, report (NIST SP 800-86). Locard: every contact leaves a trace. BTK caught by document metadata in 2005.',
    '<b>Collection</b>: RFC 3227 order of volatility, capture memory before the disk, write blockers, bit for bit images, SHA-256 at every step.',
    '<b>Disk</b>: deleting only marks space free (FAT 0xE5). Slack = clusters &times; size &minus; file size. Carving by magic numbers (FF D8 FF, %PDF, PK). TRIM and encryption make it harder.',
    '<b>Time</b>: MAC times, NTFS $SI versus $FN shows timestomping, FILETIME / 10<sup>7</sup> &minus; 11644473600 = Unix time, always UTC. Plaso super timelines.',
    '<b>Memory</b>: fileless malware lives only in RAM. Volatility pslist walks the list, psscan scans memory and finds DKOM hidden processes. Windows and Linux artefacts.',
    '<b>Custody and law</b>: unbroken signed record with hash checks. India: certificate under section 63 of the Bharatiya Sakshya Adhiniyam 2023 (formerly 65B). Clear, repeatable reports.'],
    'Security Operations 2.1: threat intelligence, learning about attackers before they arrive.')}
{files('Three tasks: order evidence by volatility, find magic numbers in raw bytes, and carve JPEG files.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does a write blocker do?', ['Speeds up copying', 'Lets a computer read a disk but never write to it', 'Encrypts the disk', 'Deletes old files'], 1, 'Read only.', 'Even plugging a disk in normally can change bytes.')
K.quiz('e', 'When you delete a file on a FAT disk, what usually happens to its data?', ['It is erased at once', 'It stays on disk until something overwrites it', 'It moves to the cloud', 'It is encrypted'], 1, 'Marked free.', 'Only the directory entry is marked with 0xE5.')
K.quiz('e', 'Why is a disk image hashed with SHA-256?', ['To compress it', 'To prove later that the copy has not changed by a single bit', 'To hide it', 'To make it smaller'], 1, 'Fingerprint.', 'Any change gives a completely different hash.')
K.quiz('e', 'Which should be collected first from a running computer?', ['Backups', 'The disk', 'Memory', 'Printed documents'], 2, 'Most fragile first.', 'RAM is lost when power goes.')
K.quiz('m', 'What does file carving rely on?', ['File names', 'Magic numbers at the start and end of each file type', 'The recycle bin', 'Passwords'], 1, 'Signatures.', 'FF D8 FF starts a JPEG, for example.')
K.quiz('m', 'A file’s $STANDARD_INFORMATION created time is 2019 but its $FILE_NAME created time is today. What does that suggest?', ['A normal copy', 'Timestomping: someone faked the date', 'A broken disk', 'Daylight saving'], 1, 'Two clocks disagree.', '$SI is easy to change, $FN is not.')
K.quiz('m', 'Why can Volatility’s psscan find a process that pslist misses?', ['It is faster', 'It scans all memory for process structures instead of trusting the linked list', 'It reads the disk', 'It asks the user'], 1, 'Scan, do not walk.', 'Rootkits unlink themselves from the list (DKOM).')
K.quiz('m', 'Why does SSD TRIM make deleted file recovery harder?', ['It encrypts data', 'The drive learns which blocks are free and often wipes them soon after', 'It renames files', 'It slows the disk'], 1, 'Background wiping.', 'On hard disks, freed data can sit for years.')
K.quiz('m', 'In India, what law now governs electronic evidence certificates (formerly section 65B)?', ['IT Act section 43', 'Section 63 of the Bharatiya Sakshya Adhiniyam 2023', 'GDPR', 'Copyright Act'], 1, 'New evidence law.', 'In force from 1 July 2024.')
K.quiz('h', 'A 10000 byte file uses 4096 byte clusters. How much slack space is in its last cluster?', ['96 bytes', '2288 bytes', '4096 bytes', '0 bytes'], 1, '3 clusters.', '3 &times; 4096 &minus; 10000 = 2288.')
K.quiz('h', 'What is a strong reason not to pull the plug on a live, unlocked, encrypted laptop?', ['It may break', 'The disk key in memory is lost and the disk becomes unreadable', 'It voids warranty', 'It changes the hash of backups'], 1, 'Keys in RAM.', 'Capture memory and a logical copy first.')
K.quiz('h', 'Why do modern labs prefer SHA-256 to MD5 for evidence hashes?', ['MD5 is slower', 'MD5 collisions can be made on purpose, so two different files could share a hash', 'SHA-256 is shorter', 'Courts ban MD5'], 1, 'Collisions.', 'SHA-256 has no known practical collision.')
K.quiz('h', 'What does FILETIME 116444736000000000 convert to in Unix time?', ['1970', '0', '1601', '116444736'], 1, 'The offset itself.', '116444736000000000 / 10<sup>7</sup> = 11644473600, minus 11644473600 = 0, which is 1 January 1970.')
K.quiz('x', 'In the style of a CMU forensics exam: a carver searches 1 TB of random bytes for a 4 byte header. About how many false hits?', ['0', 'About 233', 'About 1 million', 'Exactly 1'], 1, '10<sup>12</sup> / 2<sup>32</sup>.', 'That is why carvers validate structure after the header.')
K.quiz('x', 'In the style of an IIT Kanpur forensics question: the generic work to find any collision in an n bit hash is about', ['2<sup>n</sup>', '2<sup>n/2</sup>', 'n<sup>2</sup>', '2n'], 1, 'Birthday bound.', 'For MD5 (128 bits) that is 2<sup>64</sup>, and real attacks are far cheaper than that.')

K.calc('e', 'Image a 500 GB disk at 200 MB per second. Minutes needed? Round to 2 decimals.', '41.67', 'Size over speed.', ['500 GB = 500000 MB.', '500000 / 200 = 2500 seconds.', eq('2500 / 60 &asymp; 41.67 minutes')], check=round(500000 / 200 / 60, 2))
K.calc('e', 'How many hex characters are in a SHA-256 hash?', '64', '4 bits per hex digit.', ['SHA-256 gives 256 bits.', 'Each hex digit holds 4 bits.', eq('256 / 4 = 64')], check=64)
K.calc('e', 'FAT marks deleted entries with byte 0xE5. What is that in decimal?', '229', '14 &times; 16 + 5.', ['E = 14.', '14 &times; 16 = 224.', eq('224 + 5 = 229')], check=229)
K.calc('m', 'A JPEG header starts at offset 5 and its footer ends at offset 13. How many bytes is the carved file?', '9', 'Inclusive count.', ['End minus start = 8.', 'Both ends are included.', eq('13 &minus; 5 + 1 = 9 bytes')], check=9)
K.calc('m', 'A 10000 byte file on 4096 byte clusters. Slack space in bytes?', '2288', 'Round up the clusters.', ['10000 / 4096 = 2.44, so 3 clusters.', '3 &times; 4096 = 12288.', eq('12288 &minus; 10000 = 2288')], check=2288)
K.calc('m', 'Convert FILETIME 132539328000000000 to Unix seconds.', '1609459200', 'Divide, then subtract.', ['132539328000000000 / 10<sup>7</sup> = 13253932800.', 'Subtract 11644473600.', eq('1609459200 (1 January 2021 UTC)')], check=1609459200)
K.calc('m', 'An event happened at 10:00 IST. What is the UTC time, as decimal hours?', '4.5', 'Subtract 5.5.', ['IST = UTC + 5:30.', '10:00 &minus; 5:30 = 04:30.', eq('4.5')], check=4.5)
K.calc('m', 'pslist shows 41 processes. psscan shows 43, one of which exited normally. How many are hidden?', '1', 'Compare views.', ['43 &minus; 41 = 2 extra in the scan.', 'One of them simply exited.', eq('1 hidden process')], check=1)
K.calc('h', 'Image and then verify a 2 TB disk at 250 MB per second (two full reads). Hours? Round to 2 decimals.', '4.44', 'Two passes.', ['2 TB = 2000000 MB, one read = 8000 seconds.', 'Two reads = 16000 seconds.', eq('16000 / 3600 &asymp; 4.44 hours')], check=round(2 * 2e6 / 250 / 3600, 2))
K.calc('h', 'Expected chance matches of a 4 byte header in 10<sup>12</sup> random byte positions? Round to 2 decimals.', '232.83', 'positions / 2<sup>32</sup>.', ['A given 4 bytes match with p = 2<sup>&minus;32</sup>.', '10<sup>12</sup> &times; 2<sup>&minus;32</sup>.', eq('&asymp; 232.83')], check=round(1e12 / 2 ** 32, 2))
K.calc('h', 'Birthday bound: with n = 2<sup>32</sup> files and a 256 bit hash, P &asymp; n<sup>2</sup> / 2<sup>257</sup>. What is log<sub>2</sub> P?', '-193', 'Add and subtract exponents.', ['n<sup>2</sup> = 2<sup>64</sup>.', '2<sup>64</sup> / 2<sup>257</sup> = 2<sup>64 &minus; 257</sup>.', eq('log<sub>2</sub> P = &minus;193')], check=-193)
K.calc('h', 'A disk has 8 clusters of 8 bytes. A deleted file starts at cluster 1 with size 21. Which byte offset does it end at (last byte)?', '28', 'Start offset plus size minus 1.', ['Start offset = 1 &times; 8 = 8.', 'It covers 21 bytes.', eq('8 + 21 &minus; 1 = 28')], check=28)
K.calc('x', 'Generic collision work for MD5 is 2<sup>n/2</sup> with n = 128. What is the exponent?', '64', 'Half the bits.', ['Birthday bound for n bits: 2<sup>n/2</sup>.', 'n = 128.', eq('2<sup>64</sup>')], check=64)
K.calc('x', 'One bit of a 4096 byte image is flipped. What fraction of the bits changed? Give it as 1 in how many?', '32768', 'Bits in the image.', ['4096 bytes &times; 8 = 32768 bits.', 'One bit changed.', eq('1 in 32768, yet the hash changes completely')], check=32768)

K.assign('order_volatility', 'e', 'Order evidence by volatility',
         '<p>Write <code>order_volatility(items)</code>. Use this ranking, most fragile first: "memory" 1, "temp files" 2, "disk" 3, "remote logs" 4, "backups" 5. Return the items sorted by rank.</p>',
         '''
def order_volatility(items):
    # your code here
    pass
''', [('order_volatility(["disk", "memory"])', ['memory', 'disk']), ('order_volatility(["backups", "remote logs", "temp files", "disk", "memory"])', ['memory', 'temp files', 'disk', 'remote logs', 'backups']), ('order_volatility([])', [])],
         '''
def order_volatility(items):
    rank = {"memory": 1, "temp files": 2, "disk": 3, "remote logs": 4, "backups": 5}
    return sorted(items, key=lambda item: rank[item])
''', 'A dictionary of ranks and sorted with a key.', '<p>The full RFC 3227 list has more levels, but the idea is the same: what vanishes soonest is collected first.</p>')
K.assign('find_magic', 'm', 'Find magic numbers in raw bytes',
         '<p>Write <code>find_magic(data)</code> that returns a list of <code>(offset, kind)</code> for every place where a header starts, sorted by offset. Headers: "jpeg" is bytes FF D8 FF, "png" is 89 50 4E 47, "pdf" is b"%PDF", "zip" is b"PK" followed by bytes 03 04.</p>',
         '''
def find_magic(data):
    # your code here
    pass
''', [('find_magic(bytes.fromhex("00FFD8FF00"))', [(1, 'jpeg')]), ('find_magic(b"xx%PDF-1.7 PK\\x03\\x04")', [(2, 'pdf'), (11, 'zip')]), ('find_magic(bytes.fromhex("89504E47") + bytes.fromhex("FFD8FF"))', [(0, 'png'), (4, 'jpeg')]), ('find_magic(b"nothing here")', [])],
         '''
def find_magic(data):
    headers = {
        "jpeg": bytes.fromhex("FFD8FF"),
        "png": bytes.fromhex("89504E47"),
        "pdf": b"%PDF",
        "zip": b"PK\\x03\\x04",
    }
    found = []
    for kind, head in headers.items():
        start = data.find(head)
        while start != -1:
            found.append((start, kind))
            start = data.find(head, start + 1)
    return sorted(found)
''', 'Use bytes.find in a loop for each header, starting one past the last hit, then sort.', '<p>Real tools also check what follows the header, such as a valid JPEG segment marker, to cut false hits.</p>')
K.assign('carve_jpegs', 'h', 'Carve JPEG files',
         '<p>Write <code>carve_jpegs(data)</code> that returns a list of carved files, each written as an upper case hex string with <code>.hex().upper()</code>. Each file starts at a JPEG header FF D8 FF and ends at the first FF D9 after it, both included. A header with no footer after it is skipped. After a carve, keep searching after the footer.</p>',
         '''
def carve_jpegs(data):
    # your code here
    pass
''', [('carve_jpegs(bytes.fromhex("00FFD8FFE011FFD900"))', ["FFD8FFE011FFD9"]), ('carve_jpegs(bytes.fromhex("FFD8FF01FFD9AAFFD8FF02FFD9"))', ["FFD8FF01FFD9", "FFD8FF02FFD9"]), ('carve_jpegs(bytes.fromhex("FFD8FF0102"))', []), ('carve_jpegs(b"")', [])],
         '''
def carve_jpegs(data):
    head = bytes.fromhex("FFD8FF")
    foot = bytes.fromhex("FFD9")
    results = []
    start = data.find(head)
    while start != -1:
        end = data.find(foot, start + len(head))
        if end == -1:
            break
        results.append(data[start:end + len(foot)].hex().upper())
        start = data.find(head, end + len(foot))
    return results
''', 'Find a header, then the first footer after it, slice, and search again after the footer.', '<p>Real JPEGs can hold a small preview JPEG inside them, with its own header and footer, so good carvers parse the segments instead of stopping at the first FF D9.</p>')

K.must('Forensics', 'Collect, examine, analyse, report (NIST SP 800-86). Locard: every contact leaves a trace. Never touch the original, work on verified copies, record every step, be repeatable. BTK 2005 metadata.')
K.must('Collection', 'RFC 3227 order: registers, memory, temp, disk, remote logs, physical, archives. Capture RAM live (WinPmem, LiME). Write blocker, bit for bit image, SHA-256 (MD5 and SHA-1 have collisions).')
K.must('Disk', 'Delete marks space free (FAT 0xE5). Slack = clusters &times; size &minus; file size. Carving: FF D8 FF / FF D9, %PDF / %%EOF, 89 50 4E 47, PK 03 04. False hits = N / 2<sup>8k</sup>. TRIM, encryption.')
K.must('Time', 'MAC times. NTFS $SI (easy to change) versus $FN, timestomping. Unix = FILETIME / 10<sup>7</sup> &minus; 11644473600. UTC = IST &minus; 5:30. Plaso super timeline.')
K.must('Memory', 'Fileless malware. Volatility: pslist walks the list, psscan scans and finds DKOM hidden processes. Artefacts: Prefetch, Run keys, 4688, 7045, bash_history, auth.log, cloud audit logs.')
K.must('Custody', 'Signed record of every hand over, hash re-checked. India: certificate under BSA 2023 section 63 (was Evidence Act 65B, Anvar v Basheer 2014). Reports separate facts from opinions.')

T = K.topic(
    slug='cy-forensics', topic='cy-forensics', step=(1, 'Detect, respond and investigate', 'cy-o1', 'How defenders watch logs and raise alerts, handle an incident step by step, and collect digital evidence that holds up.', 'Intermediate'),
    title='Digital forensics: collecting and reading evidence', short='Digital forensics', badge='1.3', minutes=75,
    lead='How investigators find out what really happened, in a way others can trust: the order of volatility, write blockers and hash verification, recovering deleted files and carving by magic numbers, time stamps and timestomping, memory forensics that finds hidden processes, and the chain of custody and Indian evidence law.',
    desc='digital forensics, Locard, NIST SP 800-86, RFC 3227, order of volatility, memory capture, write blocker, disk image, SHA-256, hash verification, deleted file recovery, FAT 0xE5, slack space, unallocated space, file carving, magic numbers, PhotoRec, TRIM, MAC times, NTFS, timestomping, FILETIME, Unix time, super timeline, Plaso, memory forensics, Volatility, pslist, psscan, DKOM, rootkit, Prefetch, chain of custody, section 65B, Bharatiya Sakshya Adhiniyam, section 63, expert report',
    summary='Order of volatility, imaging and hashes, deleted files and carving, timelines and timestomping, memory forensics, chain of custody.',
    keywords=['forensics', 'order of volatility', 'write blocker', 'hash', 'file carving', 'timestomping', 'timeline', 'Volatility', 'chain of custody', 'section 63'],
    recap='<p>Collect the most fragile evidence first, copy without changing, prove it with hashes, let raw bytes and time stamps tell the story, and keep a record that anyone can check.</p>',
    added='2026-11-15')
