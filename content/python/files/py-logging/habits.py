# 3.3 Logging and debugging
# Example "habits" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import io
import logging

stream = io.StringIO()
logger = logging.getLogger("payments")
logger.setLevel(logging.INFO)
logger.propagate = False
handler = logging.StreamHandler(stream)
handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
logger.addHandler(handler)


class Report:
    def __str__(self):
        print("  (the slow __str__ ran)")
        return "big report"


logger.debug(f"report: {Report()}")            # an f-string is built first, even if dropped
logger.debug("report: %s", Report())           # %s with arguments: never built, DEBUG is off
logger.info("report: %s", Report())            # built now, because INFO passes
try:
    1 / 0
except ZeroDivisionError:
    logger.exception("could not split the bill")   # ERROR level plus the traceback

lines = stream.getvalue().splitlines()
print(lines[0])
print(lines[1])
print(lines[2])
print(lines[-1])
print(logger.isEnabledFor(logging.DEBUG))
