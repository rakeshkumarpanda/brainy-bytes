# 6.2 CSV, JSON, XML and settings files
# Example "csv_files" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import csv
import io
import os
import tempfile

path = os.path.join(tempfile.mkdtemp(), "people.csv")
rows = [
    {"name": "Ann", "city": "Paris", "age": 31},
    {"name": "Smith, Bo", "city": "Rome", "age": 25},
]
with open(path, "w", newline="", encoding="utf-8") as f:   # newline="" is required for csv
    writer = csv.DictWriter(f, fieldnames=["name", "city", "age"])
    writer.writeheader()
    writer.writerows(rows)

with open(path, newline="", encoding="utf-8") as f:
    print(repr(f.read()))                      # the real text in the file

with open(path, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row["name"], int(row["age"]) + 1)    # every value comes back as a string

text = "id;price\n1;2,50\n2;3,10\n"           # European style: ; between fields, comma decimals
for row in csv.reader(io.StringIO(text), delimiter=";"):
    print(row)
print(csv.Sniffer().sniff(text).delimiter)
