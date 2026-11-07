# 6.2 CSV, JSON, XML and settings files
# Model solutions. Try practice.py first.
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
# Why it works: The quoted city "Washington, DC" stays one field because DictReader understands CSV
# quoting. Splitting lines on commas yourself would break it.

import csv
import io


def total_by_city(csv_text):
    totals = {}
    for row in csv.DictReader(io.StringIO(csv_text)):
        totals[row["city"]] = totals.get(row["city"], 0.0) + float(row["amount"])
    return totals


# ================================================================== task 2: Write JSON with dates and sets
# Write dump_event(event) that returns a JSON string of the dict event with sorted keys. Dates must
# become "YYYY-MM-DD" strings and sets sorted lists. Anything else that JSON does not support must
# still raise TypeError. Use json.dumps with default= and sort_keys=True.
# Why it works: Web frameworks do this for you: Django REST framework and FastAPI turn dates,
# decimals and UUIDs into JSON with exactly this kind of default function.

import json
from datetime import date


def to_json(value):
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, set):
        return sorted(value)
    raise TypeError(f"{type(value).__name__} is not JSON serializable")


def dump_event(event):
    return json.dumps(event, default=to_json, sort_keys=True)


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
# Why it works: Raising your own ValueError hides which parser you used, so callers do not need to
# import ElementTree just to catch the error.

import xml.etree.ElementTree as ET


def cheap_books(xml_text, limit):
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as err:
        raise ValueError(f"not valid XML: {err}") from err
    found = []
    for book in root.iter("book"):
        price = book.findtext("price")
        if price is None:
            continue
        if float(price) <= limit:
            found.append((float(price), book.findtext("title")))
    return [title for price, title in sorted(found)]


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
