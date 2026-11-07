# 1.2 Extended arguments, closures and decorators
# Example "factory" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from functools import wraps


def repeat(times):                       # 1. the factory takes the settings
    def decorate(func):                  # 2. the real decorator takes the function
        @wraps(func)
        def wrapper(*args, **kwargs):    # 3. the wrapper takes the call's arguments
            results = []
            for i in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorate


@repeat(3)                               # wave = repeat(3)(wave)
def wave(name):
    return "hi " + name


print(wave("Asha"))


def retry(attempts):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except ConnectionError as err:
                    print("attempt", attempt, "failed:", err)
            raise ConnectionError("gave up after " + str(attempts) + " attempts")
        return wrapper
    return decorate


tries = {"n": 0}


@retry(3)
def fetch():
    tries["n"] += 1
    if tries["n"] < 3:                   # fails twice, then works
        raise ConnectionError("timeout")
    return "data"


print(fetch())
