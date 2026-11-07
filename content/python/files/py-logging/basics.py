# 3.3 Logging and debugging
# Example "basics" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, force=True,
                    format="%(levelname)s %(name)s: %(message)s")

logging.debug("hidden: DEBUG is below INFO")
logging.info("app started")
logging.warning("disk is 91% full")
logging.error("could not save the file")
logging.critical("database is down")
print(logging.getLevelName(logging.WARNING), logging.WARNING, logging.getLogger().level)
