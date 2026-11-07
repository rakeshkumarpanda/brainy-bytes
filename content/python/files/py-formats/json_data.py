# 6.2 CSV, JSON, XML and settings files
# Example "json_data" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import json
from datetime import date

order = {"id": 7, "paid": True, "items": ("tea", "cake"), "note": None, 2: "two"}
text = json.dumps(order)
print(text)
back = json.loads(text)
print(back, back == order)
print(json.dumps({"b": 1, "a": [1, 2]}, indent=2, sort_keys=True))
print(json.dumps({"city": "Zürich"}), json.dumps({"city": "Zürich"}, ensure_ascii=False))


def to_json(value):
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, set):
        return sorted(value)
    raise TypeError(f"cannot turn {type(value).__name__} into JSON")


print(json.dumps({"day": date(2026, 11, 7), "tags": {"b", "a"}}, default=to_json))


def from_json(d):
    if "day" in d:
        d["day"] = date.fromisoformat(d["day"])
    return d


print(json.loads('{"day": "2026-11-07"}', object_hook=from_json))

try:
    json.loads("{'single': 'quotes'}")
except json.JSONDecodeError as err:
    print("JSONDecodeError:", err.msg, "at position", err.pos)
