# 3.3 Logging and debugging
# Example "config" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import logging
import logging.config

CONFIG = {
    "version": 1,
    "formatters": {
        "short": {"format": "%(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "screen": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "short",
            "level": "INFO",
        },
    },
    "loggers": {
        "shop": {"level": "DEBUG", "handlers": ["screen"], "propagate": False},
    },
}
logging.config.dictConfig(CONFIG)

cart = logging.getLogger("shop.cart")
cart.info("child loggers use the handlers of their parent")
cart.debug("the handler level still filters this one out")
print(cart.getEffectiveLevel(), cart.handlers, cart.parent.name)
