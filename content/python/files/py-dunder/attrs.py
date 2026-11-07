# 1.1 Special methods and operator overloading
# Example "attrs" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Config:
    def __init__(self, **values):
        self.__dict__["values"] = values       # avoid our own __setattr__ here

    def __getattr__(self, name):               # only called when normal lookup FAILS
        if name in self.values:
            return self.values[name]
        raise AttributeError(f"no setting called {name!r}")

    def __setattr__(self, name, value):        # called for EVERY attribute assignment
        if name == "port" and not 0 < value < 65536:
            raise ValueError("port must be 1 to 65535")
        self.values[name] = value


cfg = Config(host="localhost", port=8000)
print(cfg.host, cfg.port)
cfg.port = 8080
print(cfg.values)
try:
    cfg.port = 99999
except ValueError as err:
    print("ValueError:", err)
try:
    cfg.timeout
except AttributeError as err:
    print("AttributeError:", err)
