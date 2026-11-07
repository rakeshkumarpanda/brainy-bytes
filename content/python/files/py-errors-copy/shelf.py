# 1.4 Exceptions in depth, copying and serialisation
# Example "shelf" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import shelve, os, tempfile

path = os.path.join(tempfile.mkdtemp(), "contacts")

with shelve.open(path) as db:                  # a dict that lives on disk
    db["asha"] = {"phone": "98100", "tags": ["family"]}
    db["ravi"] = {"phone": "98200", "tags": []}

with shelve.open(path) as db:                  # open again later: still there
    print(sorted(db.keys()))
    print(db["asha"]["phone"])
    entry = db["ravi"]
    entry["tags"].append("work")               # change a copy...
    db["ravi"] = entry                         # ...and store it back
    print(db["ravi"]["tags"], "ravi" in db, len(db))
