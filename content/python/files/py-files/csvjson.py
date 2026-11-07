# 5.3 Files: reading, writing, modes, paths and streams
# Example "csvjson" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import csv, json, os, tempfile
os.chdir(tempfile.mkdtemp())

rows = [{"name": "Asha", "city": "Pune", "mark": 88}, {"name": "Ravi, Jr", "city": "Delhi", "mark": 72}]
with open("students.csv", "w", newline="", encoding="utf-8") as f:   # newline="" for csv
    writer = csv.DictWriter(f, fieldnames=["name", "city", "mark"])
    writer.writeheader()
    writer.writerows(rows)
print(open("students.csv", encoding="utf-8").read())

with open("students.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row["name"], int(row["mark"]) + 5)

with open("students.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2)
with open("students.json", encoding="utf-8") as f:
    back = json.load(f)
print(back == rows, back[1]["name"])
