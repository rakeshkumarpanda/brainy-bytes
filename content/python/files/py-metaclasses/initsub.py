# 1.5 Metaprogramming: type, class hooks and metaclasses
# Example "initsub" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Plugin:
    registry = {}

    def __init_subclass__(cls, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        key = name or cls.__name__.lower()
        Plugin.registry[key] = cls             # every child registers itself


class CsvExport(Plugin, name="csv"):
    def run(self, rows):
        lines = []
        for row in rows:
            lines.append(",".join(str(x) for x in row))
        return "\n".join(lines)


class JsonExport(Plugin, name="json"):
    def run(self, rows):
        return str(rows)


class Pdf(Plugin):                             # no name given, so the key is "pdf"
    def run(self, rows):
        return "PDF with " + str(len(rows)) + " rows"


print(sorted(Plugin.registry))
chosen = Plugin.registry["csv"]()              # pick a class by a string
print(chosen.run([[1, 2], [3, 4]]))
print(Plugin.registry["pdf"]().run([[1], [2], [3]]))
