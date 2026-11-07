# 2.3 Context managers and the with statement
# Example "generator" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from contextlib import contextmanager


@contextmanager
def temporary(settings, key, value):
    old = settings.get(key)
    settings[key] = value                      # set up: like __enter__
    try:
        yield settings                         # the with body runs here
    finally:
        settings[key] = old                    # clean up: like __exit__, even after an error


config = {"mode": "live"}
with temporary(config, "mode", "test") as c:
    print("inside:", c["mode"])
print("after:", config["mode"])

try:
    with temporary(config, "mode", "debug"):
        raise RuntimeError("crash")
except RuntimeError:
    print("after a crash:", config["mode"])


@temporary(config, "mode", "audit")            # works as a decorator too
def report():
    return "report made in " + config["mode"] + " mode"


print(report(), "|", config["mode"])
