# 1.4 Exceptions in depth, copying and serialisation
# Example "warn" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import warnings


def old_area(w, h):
    warnings.warn("old_area is deprecated, use area", DeprecationWarning, stacklevel=2)
    return w * h


with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")            # show every warning, even repeated ones
    print(old_area(3, 4))
    print(len(caught), caught[0].category.__name__, str(caught[0].message))

warnings.simplefilter("error")                 # turn warnings into exceptions
try:
    old_area(1, 1)
except DeprecationWarning as err:
    print("now an error:", err)
