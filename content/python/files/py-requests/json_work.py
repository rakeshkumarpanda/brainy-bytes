# 2.1 Calling web APIs with requests
# Example "json_work" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import json
from datetime import datetime

answer = """
{"city": "Pune", "updated": "2026-11-07T09:30:00+05:30",
 "days": [{"date": "2026-11-07", "max": 31.5, "min": 19.0, "rain": null},
          {"date": "2026-11-08", "max": 29.0, "min": 18.5, "rain": 2.4},
          {"date": "2026-11-09", "max": 27.5, "min": 17.0}]}
"""
data = json.loads(answer)                     # the same as response.json() in requests
print(type(data).__name__, list(data))
print(data["city"], "has", len(data["days"]), "days")

updated = datetime.fromisoformat(data["updated"])
print("updated", updated.strftime("%d %b %Y %H:%M"), "offset", updated.utcoffset())

for day in data["days"]:
    rain = day.get("rain") or 0.0            # a missing key and null both become 0.0
    print(day["date"], f"{day['min']} to {day['max']} C, rain {rain} mm")

hottest = max(data["days"], key=lambda day: day["max"])
print("hottest day:", hottest["date"])
print(json.dumps({"city": data["city"], "hottest": hottest["max"]}, indent=2))
print(json.dumps({"name": "café"}), json.dumps({"name": "café"}, ensure_ascii=False))
