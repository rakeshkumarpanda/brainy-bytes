# 6.2 CSV, JSON, XML and settings files
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: Add up a CSV by city
# Write total_by_city(csv_text). The text has a header line city,amount and one sale per line.
# Return a dict from city to the total amount as a float, in the order cities first appear. Read it
# with csv.DictReader(io.StringIO(csv_text)). Remember that every value is a string.
# Hint: Start each total at 0.0 and add float(row["amount"]). The starter joins strings: "10.5" +
# "2" gives "10.52".

import csv
import io


def total_by_city(csv_text):
    totals = {}
    for row in csv.DictReader(io.StringIO(csv_text)):
        totals[row["city"]] = totals.get(row["city"], "") + row["amount"]
    return totals


# ================================================================== task 2: Write JSON with dates and sets
# Write dump_event(event) that returns a JSON string of the dict event with sorted keys. Dates must
# become "YYYY-MM-DD" strings and sets sorted lists. Anything else that JSON does not support must
# still raise TypeError. Use json.dumps with default= and sort_keys=True.
# Hint: default= gets each object json does not know. Return something it does know (a string, a
# list), or raise TypeError.

import json
from datetime import date


def dump_event(event):
    return json.dumps(event, sort_keys=True)


def error_of(event):
    try:
        dump_event(event)
    except TypeError:
        return "TypeError"
    return "no error"


# ================================================================== task 3: Pick cheap books out of XML
# Write cheap_books(xml_text, limit). The XML has a root with book elements that each have a title
# and usually a price. Return the titles of books whose price is at most limit, sorted by price and
# then by title. Skip books without a price. If the text is not valid XML, raise ValueError
# (ElementTree raises ET.ParseError).
# Hint: findtext("price") gives None when there is no price. Sort (price, title) tuples so equal
# prices fall back to the title. Turn ET.ParseError into ValueError with raise ... from.

import xml.etree.ElementTree as ET


def cheap_books(xml_text, limit):
    root = ET.fromstring(xml_text)
    return [b.findtext("title") for b in root.iter("book")]


def error_of(xml_text):
    try:
        cheap_books(xml_text, 10)
    except ValueError:
        return "ValueError"
    except Exception as err:
        return type(err).__name__
    return "no error"


SHOP = """<shop>
  <book><title>B</title><price>9.5</price></book>
  <book><title>A</title><price>9.5</price></book>
  <book><title>C</title><price>30</price></book>
  <book><title>D</title></book>
  <book><title>E</title><price>4</price></book>
</shop>"""


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Add up a CSV by city", [('total_by_city("city,amount\\nParis,10.5\\nRome,4\\nParis,2\\n")', {'Paris': 12.5, 'Rome': 4.0}), ('total_by_city("city,amount\\n")', {}), ('total_by_city(\'city,amount\\n"Washington, DC",3\\n\')', {'Washington, DC': 3.0})]))
    results.append(check("Task 2: Write JSON with dates and sets", [('dump_event({"name": "launch", "day": date(2026, 11, 7)})', '{"day": "2026-11-07", "name": "launch"}'), ('dump_event({"tags": {"b", "a"}, "n": 1})', '{"n": 1, "tags": ["a", "b"]}'), ('dump_event({})', '{}'), ('error_of({"x": object()})', 'TypeError')]))
    results.append(check("Task 3: Pick cheap books out of XML", [('cheap_books(SHOP, 10)', ['E', 'A', 'B']), ('cheap_books(SHOP, 1)', []), ('cheap_books(SHOP, 100)', ['E', 'A', 'B', 'C']), ('error_of("<shop><book>")', 'ValueError')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
