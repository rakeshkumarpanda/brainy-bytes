# 3.3 Logging and debugging
# Example "loggers" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import logging
import os
import sys
import tempfile

log_path = os.path.join(tempfile.mkdtemp(), "app.log")

logger = logging.getLogger("shop.cart")        # in a module: logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False                       # do not also pass records to the root logger

console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.WARNING)              # the screen shows only problems
console.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))

file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.DEBUG)           # the file keeps everything
file_handler.setFormatter(logging.Formatter("%(levelname)-8s %(funcName)s:%(lineno)d %(message)s"))

logger.addHandler(console)
logger.addHandler(file_handler)


def checkout(total):
    logger.debug("checkout started with total %s", total)
    if total > 1000:
        logger.warning("large order: %s", total)
    logger.info("order saved")


checkout(1500)
file_handler.close()
print("--- app.log ---")
with open(log_path) as f:
    print(f.read().strip())
print(logging.getLogger("shop").name, logger.parent.name, logger.parent.parent.name)
