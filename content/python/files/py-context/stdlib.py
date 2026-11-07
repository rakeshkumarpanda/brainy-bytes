# 2.3 Context managers and the with statement
# Example "stdlib" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import io
import os
import tempfile
import threading
from contextlib import redirect_stdout, chdir, closing, nullcontext
from decimal import Decimal, localcontext

buffer = io.StringIO()
with redirect_stdout(buffer):                  # capture print output
    print("this goes into the buffer")
print("captured:", repr(buffer.getvalue()))

start = os.getcwd()
with tempfile.TemporaryDirectory() as folder:  # deleted when the block ends
    with chdir(folder):                        # Python 3.11 and later
        print("inside a temp folder:", os.getcwd() != start)
    print("back home:", os.getcwd() == start)
print("folder deleted:", not os.path.exists(folder))

with localcontext() as ctx:
    ctx.prec = 4
    print(Decimal(1) / Decimal(7))
print(Decimal(1) / Decimal(7))

lock = threading.Lock()
with lock:                                     # acquire, then always release
    print("locked:", lock.locked())
print("locked:", lock.locked())


class Connection:
    def close(self):
        print("connection closed")


with closing(Connection()):                    # calls .close() at the end
    print("using the connection")

with nullcontext("no set up needed") as value: # a stand in that does nothing
    print(value)
