# 1.4 Exceptions in depth, copying and serialisation
# Example "customcopy" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import copy


class Document:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages
        self.cache = {"rendered": True}

    def __copy__(self):                        # used by copy.copy
        new = Document(self.title, self.pages)
        new.cache = {}                         # never share a cache
        return new

    def __deepcopy__(self, memo):              # used by copy.deepcopy
        new = Document(self.title, copy.deepcopy(self.pages, memo))
        new.cache = {}
        return new


doc = Document("Notes", ["p1", "p2"])
s = copy.copy(doc)
d = copy.deepcopy(doc)
print(s.pages is doc.pages, d.pages is doc.pages, s.cache, d.cache)
