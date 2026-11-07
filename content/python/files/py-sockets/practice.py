# 1.2 Sockets, TCP and UDP: under HTTP
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: Pack and split length prefixed messages
# Write pack(text) that returns the UTF-8 bytes of the text with a 4 byte big endian length in
# front. The length counts BYTES, not letters. Then write split_messages(chunks): chunks is a list
# of bytes objects as recv might return them, cut anywhere. Return the list of complete messages as
# text, and ignore an unfinished message at the end.
# Hint: Encode first and measure the bytes. Keep one buffer for all chunks, and in a while loop take
# out every complete message it holds.

def pack(text):
    return len(text).to_bytes(4, "big") + text.encode()


def split_messages(chunks):
    messages = []
    for chunk in chunks:
        messages.append(chunk[4:].decode(errors="replace"))
    return messages


def cut(data, size):
    return [data[i:i + size] for i in range(0, len(data), size)]


STREAM = b"\x00\x00\x00\x02hi\x00\x00\x00\x03bye\x00\x00\x00\x06h\xc3\xa9llo"


# ================================================================== task 2: Work with subnets
# Use the ipaddress module. Write usable_hosts(cidr): 232 − prefix − 2 addresses, but 2 for a /31 (a
# link between two routers) and 1 for a /32. Write same_subnet(ip1, ip2, prefix): True when both
# addresses are in the same network of that prefix length. Write split(cidr, parts): the list of
# equal smaller networks as text, and raise ValueError when parts is not a power of 2.
# Hint: ip_network(..., strict=False) builds the network that an address belongs to. A number is a
# power of 2 when n & (n − 1) is 0, and splitting into 2k parts adds k bits to the prefix.

def usable_hosts(cidr):
    prefix = int(cidr.split("/")[1])
    return 2 ** (32 - prefix)


def same_subnet(ip1, ip2, prefix):
    return ip1.split(".")[:3] == ip2.split(".")[:3]


def split(cidr, parts):
    return [cidr]


def split_error(cidr, parts):
    try:
        split(cidr, parts)
    except ValueError:
        return "ValueError"
    return "no error"


# ================================================================== task 3: Read exact sizes and lines from a socket
# FakeSocket acts like a TCP socket: recv(n) returns at most n bytes and often fewer, and b"" at the
# end. Write recv_exact(sock, n) that returns exactly n bytes, and raises ConnectionError if the
# data ends first. Then finish LineReader: read_line() returns the next line as text without the
# line end ("\n", and also "\r\n"), the last piece of text when it has no line end, and None when
# nothing is left. Bytes after a line must be kept for the next call.
# Hint: Loop on recv and ask only for the bytes still missing. In LineReader keep a buffer: read
# until it holds a new line or the socket is closed, then cut off one line and keep the rest.

class FakeSocket:
    """Acts like a TCP socket: recv(n) gives at most n bytes, and often fewer."""

    def __init__(self, data, piece=3):
        self.data = data
        self.piece = piece

    def recv(self, n):
        size = min(n, self.piece)
        chunk = self.data[:size]
        self.data = self.data[size:]
        return chunk


def recv_exact(sock, n):
    return sock.recv(n)


def exact_error(data, n):
    try:
        recv_exact(FakeSocket(data), n)
    except ConnectionError:
        return "ConnectionError"
    return "no error"


class LineReader:
    def __init__(self, sock):
        self.sock = sock

    def read_line(self):
        data = self.sock.recv(1024)
        if not data:
            return None
        return data.decode().strip()


def read_lines(data, piece):
    reader = LineReader(FakeSocket(data, piece))
    lines = []
    while True:
        line = reader.read_line()
        if line is None:
            return lines
        lines.append(line)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Pack and split length prefixed messages", [('pack("hi").hex()', '000000026869'), ('pack("héllo")[:4].hex()', '00000006'), ('split_messages([STREAM])', ['hi', 'bye', 'héllo']), ('split_messages(cut(STREAM, 3))', ['hi', 'bye', 'héllo']), ('split_messages(cut(STREAM, 1))', ['hi', 'bye', 'héllo']), ('split_messages(cut(STREAM[:-2], 4))', ['hi', 'bye'])]))
    results.append(check("Task 2: Work with subnets", [('usable_hosts("192.168.1.0/24")', 254), ('usable_hosts("10.0.0.0/30")', 2), ('usable_hosts("10.0.0.0/31")', 2), ('usable_hosts("10.0.0.1/32")', 1), ('same_subnet("192.168.1.10", "192.168.1.200", 24)', True), ('same_subnet("10.0.1.5", "10.0.2.5", 16)', True), ('same_subnet("10.0.1.5", "10.0.1.200", 25)', False), ('split("192.168.1.0/24", 4)', ['192.168.1.0/26', '192.168.1.64/26', '192.168.1.128/26', '192.168.1.192/26']), ('split_error("192.168.1.0/24", 3)', 'ValueError')]))
    results.append(check("Task 3: Read exact sizes and lines from a socket", [('recv_exact(FakeSocket(b"hello world"), 5).decode()', 'hello'), ('recv_exact(FakeSocket(b"abcdefgh", 2), 7).decode()', 'abcdefg'), ('exact_error(b"abc", 5)', 'ConnectionError'), ('read_lines(b"one\\ntwo\\nthree\\n", 4)', ['one', 'two', 'three']), ('read_lines(b"GET / HTTP/1.1\\r\\nHost: a\\r\\n\\r\\n", 5)', ['GET / HTTP/1.1', 'Host: a', '']), ('read_lines(b"no line end here", 3)', ['no line end here'])]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
