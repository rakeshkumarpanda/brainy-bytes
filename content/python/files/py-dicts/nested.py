# 3.4 Dictionaries: keys, values and hash tables
# Example "nested" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

student = {
    "name": "Asha",
    "marks": {"maths": 91, "physics": 84},
    "clubs": ["chess", "music"],
}
print(student["marks"]["maths"])
print(student["clubs"][-1])
student["marks"]["chemistry"] = 77
print(student)

import json
text = json.dumps(student)          # to JSON text (Web 2.2 uses this a lot)
print(text)
back = json.loads(text)
print(back == student)
