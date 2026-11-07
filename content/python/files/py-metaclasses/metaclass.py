# 1.5 Metaprogramming: type, class hooks and metaclasses
# Example "metaclass" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class CheckMeta(type):
    def __new__(mcs, name, bases, namespace):
        public = sorted(k for k in namespace if not k.startswith("__"))
        print("building class", name, "with", public)
        if bases and "run" not in namespace:   # every child must have run()
            raise TypeError(name + " must define run()")
        namespace["kind"] = name.lower()       # add an attribute to every class
        return super().__new__(mcs, name, bases, namespace)


class Job(metaclass=CheckMeta):
    pass


class Backup(Job):                             # the metaclass is inherited
    def run(self):
        return "backing up"


print(Backup().run(), Backup.kind, type(Backup).__name__)
try:
    class Broken(Job):
        def start(self):
            pass
except TypeError as err:
    print("TypeError:", err)
