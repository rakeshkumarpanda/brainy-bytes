# 5.2 Modules and packages: import, the standard library and pip
# Example "stdlib" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from datetime import date, timedelta
from collections import Counter
import json, os.path, statistics, string

exam = date(2026, 12, 1)
print(exam.strftime("%A %d %B %Y"), (exam - date(2026, 11, 7)).days, "days to go")
print(exam + timedelta(weeks=2))
print(Counter("mississippi").most_common(2))
print(json.dumps({"name": "Asha", "marks": [90, 85]}))
print(os.path.join("data", "2026", "marks.csv"), os.path.splitext("photo.jpeg"))
print(statistics.median([3, 1, 4, 1, 5]), statistics.mode([3, 1, 4, 1, 5]))
print(string.ascii_lowercase[:5], string.digits)
