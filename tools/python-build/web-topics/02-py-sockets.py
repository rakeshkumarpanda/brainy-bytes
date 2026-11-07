# Web and APIs 1.2: sockets, TCP and UDP. Checked against RFC 9293 (TCP: three way handshake, sequence and
# acknowledgement numbers, FIN, retransmission), RFC 768 (UDP), RFC 791 and RFC 4632 (IPv4 and CIDR), RFC 3021 (/31
# links) and the Python 3.14 documentation of socket, struct, ipaddress, socketserver, selectors and asyncio streams.
# Programs that open network sockets cannot run in the page's Pyodide, so they use local() and show a real run.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, lc, leet, files, grow, leet_items

chapter('py-sockets')
K = Kit()

K.code('bytes_text', r'''
import struct

text = "héllo"
data = text.encode("utf-8")          # sockets send bytes, not str
print(data, len(text), "letters,", len(data), "bytes")
print(data.decode("utf-8"))

number = 258
print(number.to_bytes(4, "big"), number.to_bytes(4, "little"))
print(int.from_bytes(b"\x00\x00\x01\x02", "big"))

packed = struct.pack("!HI", 8080, 1_000_000)     # ! = network order (big endian), H = 2 bytes, I = 4 bytes
print(packed.hex(" "), "is", len(packed), "bytes")
print(struct.unpack("!HI", packed))
print(struct.calcsize("!HI"), struct.calcsize("HI"))    # without ! the computer may add padding bytes
''')
K.code('tcp_echo', r'''
import socket
import threading


def serve_one(server):
    conn, addr = server.accept()              # waits for a client, then gives a NEW socket for it
    with conn:
        print("server: connection from", addr[0])
        while True:
            data = conn.recv(1024)            # up to 1024 bytes, b"" means the client closed
            if not data:
                break
            print("server got", data)
            conn.sendall(data.upper())
    print("server: the client closed the connection")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # IPv4 and TCP
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 0))                 # port 0: the system picks a free port
server.listen()
port = server.getsockname()[1]
worker = threading.Thread(target=serve_one, args=(server,))
worker.start()

with socket.create_connection(("127.0.0.1", port), timeout=5) as client:
    for word in ["hello", "sockets"]:
        client.sendall(word.encode())
        reply = client.recv(1024)
        print("client got", reply)

worker.join()
server.close()
''', long=True)
K.code('errors_timeouts', r'''
import socket

# 1. Nobody listens on the port: the other side answers "refused" at once
probe = socket.socket()
probe.bind(("127.0.0.1", 0))
free_port = probe.getsockname()[1]
probe.close()
try:
    socket.create_connection(("127.0.0.1", free_port), timeout=2)
except ConnectionRefusedError as err:
    print("refused:", err.strerror)

# 2. The server accepts but never answers: a timeout stops the wait
server = socket.create_server(("127.0.0.1", 0))
port = server.getsockname()[1]
client = socket.create_connection(("127.0.0.1", port), timeout=0.5)
try:
    client.recv(1024)
except TimeoutError:
    print("timeout: no answer within 0.5 s")
client.close()

# 3. A second server on a port that is already taken
other = socket.socket()
try:
    other.bind(("127.0.0.1", port))
except OSError as err:
    print("bind failed:", err.strerror)
other.close()
server.close()
''', long=True)
K.code('stream_framing', r'''
import struct


def frame(text):
    data = text.encode("utf-8")
    return struct.pack("!I", len(data)) + data      # 4 bytes of length, then the message


stream = frame("hi") + frame("how are you?") + frame("bye")
print(len(stream), "bytes on the wire")

# TCP may cut the stream anywhere. Here it arrives in pieces of 5 bytes.
pieces = [stream[i:i + 5] for i in range(0, len(stream), 5)]
print(len(pieces), "pieces, the first is", pieces[0])

buffer = b""
for piece in pieces:
    buffer += piece
    while len(buffer) >= 4:
        size = struct.unpack("!I", buffer[:4])[0]
        if len(buffer) < 4 + size:
            break                                    # not complete yet, wait for more bytes
        message = buffer[4:4 + size].decode("utf-8")
        buffer = buffer[4 + size:]
        print("message:", message)
print("bytes left over:", len(buffer))
''')
K.code('udp_ping', r'''
import socket

receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # UDP
receiver.bind(("127.0.0.1", 0))
address = receiver.getsockname()

sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for number in range(3):
    sender.sendto(f"ping {number}".encode(), address)        # no connect, no handshake

receiver.settimeout(1)
for _ in range(3):
    data, from_address = receiver.recvfrom(1024)            # one whole datagram each time
    print("got", data.decode(), "from", from_address[0])
try:
    receiver.recvfrom(1024)
except TimeoutError:
    print("nothing more came, and UDP never says if something was lost")
sender.close()
receiver.close()
''')
K.code('many_clients', r'''
import asyncio


async def handle(reader, writer):
    name = (await reader.readline()).decode().strip()
    await asyncio.sleep(0.1)                 # slow work, but the other clients still run
    writer.write(f"hello {name}\n".encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def client(port, name):
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    writer.write(f"{name}\n".encode())
    await writer.drain()
    reply = await reader.readline()
    writer.close()
    await writer.wait_closed()
    return reply.decode().strip()


async def main():
    server = await asyncio.start_server(handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    loop = asyncio.get_running_loop()
    start = loop.time()
    replies = await asyncio.gather(*(client(port, name) for name in ["ann", "bob", "cy"]))
    print(replies)
    print("3 clients that need 0.1 s each took about", round(loop.time() - start, 1), "s in total")
    server.close()
    await server.wait_closed()


asyncio.run(main())
''', long=True)
K.code('ip_ports', r'''
import ipaddress

net = ipaddress.ip_network("192.168.1.0/24")
print(net.num_addresses, "addresses,", net.num_addresses - 2, "for computers")
print("netmask", net.netmask, "and broadcast", net.broadcast_address)
print(ipaddress.ip_address("192.168.1.77") in net)
print(ipaddress.ip_address("192.168.2.5") in net)
print([str(part) for part in net.subnets(new_prefix=26)])
print(ipaddress.ip_address("10.0.0.1").is_private, ipaddress.ip_address("8.8.8.8").is_private)
print(ipaddress.ip_address("::1"), "is IPv6 version", ipaddress.ip_address("::1").version)
print(int(ipaddress.ip_address("192.168.1.1")))     # an IPv4 address is just a 32 bit number

WELL_KNOWN = {22: "SSH", 53: "DNS", 80: "HTTP", 443: "HTTPS", 5432: "PostgreSQL", 6379: "Redis"}
for port, name in WELL_KNOWN.items():
    print(port, name)
''')

WHY_NET = 'It opens real network sockets, and the Python inside this page has no network sockets.'

K.lesson('idea', 'What a socket is', f'''
{src('RFC 9293 (TCP), RFC 768 (UDP), RFC 791 and RFC 4632 (IPv4 and CIDR) and the Python 3.14 documentation of socket, struct, ipaddress and asyncio streams.')}
{wwh('A <b>socket</b> is one end of a network connection inside your program. You give it an address (an IP address and a port), and then you can send and receive bytes through it. Python has the socket module for this, and every web library, from requests to Django, uses sockets underneath.',
     'Two programs on different computers have no shared memory. They need a way to move bytes across the network to the right program, in the right order, even when the network loses or delays packets.',
     'The operating system does the hard part. The IP address finds the computer, the <b>port</b> finds the program on it, and the protocol decides the rules: <b>TCP</b> gives a reliable, ordered stream of bytes, <b>UDP</b> sends single packets fast with no promises. Your program only calls connect, send and recv.')}
{viz('pysock')}
{versus('Ways to move bytes between programs', ['', 'TCP socket', 'UDP socket', 'Unix domain socket', 'QUIC'], [
    ['Setup', 'Three way handshake', 'None', 'None, a file path on one computer', 'One round trip, with TLS built in'],
    ['Delivery', 'Every byte, in order, no duplicates', 'May lose, repeat or reorder packets', 'Reliable', 'Reliable, per stream'],
    ['Message borders', 'No: a stream of bytes', 'Yes: one datagram is one message', 'Stream or datagram, you choose', 'Streams inside one connection'],
    ['Good for', 'HTTP/1 and HTTP/2, databases, SSH, email', 'DNS, video calls, games, metrics', 'Programs on the same computer, such as Docker or PostgreSQL', 'HTTP/3'],
    ['In Python', 'socket.SOCK_STREAM, asyncio streams', 'socket.SOCK_DGRAM', 'socket.AF_UNIX', 'aioquic library']],
    'Use TCP unless you have a clear reason not to. Most of the time a higher level library such as requests is even better, and sockets are what you learn to understand it.')}
''', kw=['socket', 'IP address', 'port', 'TCP', 'UDP', 'stream', 'datagram', 'Unix domain socket', 'QUIC', 'handshake'])

K.lesson('bytes', 'Bytes: what really travels', f'''
{run('bytes_text')}
{table(['struct code', 'C type', 'Bytes', 'Range'], [
    ['B', 'unsigned char', '1', '0 to 255'],
    ['H', 'unsigned short', '2', '0 to 65,535 (a port number fits here)'],
    ['I', 'unsigned int', '4', '0 to about 4.29 billion (an IPv4 address fits here)'],
    ['Q', 'unsigned long long', '8', '0 to about 1.8 &times; 10<sup>19</sup>'],
    ['h, i, q', 'signed versions', '2, 4, 8', 'Negative numbers too'],
    ['!', 'byte order mark', '', 'Network order: the most important byte first (big endian), no padding']])}
{note('A socket only knows bytes. Turn text into bytes with .encode("utf-8") before sending and back with .decode("utf-8") after receiving. "é" is one letter but 2 bytes, so always measure the length of the bytes, never of the text.', 'exam')}
{scene('a network game sends positions', '<p>A game sends the x and y position of a player 30 times a second. As text, "1023,887" is 8 bytes and the receiver must split and convert it. With struct.pack("!HH", 1023, 887) it is always exactly 4 bytes, and struct.unpack gives the two numbers back at once. Fixed size binary data is smaller and faster to read, which is why real network protocols use it for their headers.</p>')}
''', kw=['bytes', 'str', 'encode', 'decode', 'UTF-8', 'struct', 'pack', 'unpack', 'big endian', 'network byte order', 'to_bytes', 'from_bytes'])

K.lesson('tcp', 'A TCP client and server', f'''
{local('tcp_echo', WHY_NET)}
{steps('The life of a TCP server and client', [
    'Server: <code>socket(AF_INET, SOCK_STREAM)</code> makes an IPv4 TCP socket. <code>bind((host, port))</code> claims a port. <code>listen()</code> starts accepting connections.',
    'Server: <code>accept()</code> waits for a client. It returns a NEW socket for that one client plus the client address. The listening socket keeps listening for others.',
    'Client: <code>socket.create_connection((host, port), timeout=5)</code> finds the address, makes the socket and connects in one call.',
    'Both: <code>sendall(data)</code> sends every byte (plain send() may send only part of it). <code>recv(n)</code> returns between 1 and n bytes, or b"" when the other side has closed.',
    'Both: <code>close()</code>, or a with block that closes for you. Always set a timeout, so a dead network cannot make your program wait for ever.'])}
{local('errors_timeouts', WHY_NET)}
{table(['Error', 'When', 'What to do'], [
    ['ConnectionRefusedError', 'Nothing listens on that port', 'Check the host and port, is the server running'],
    ['TimeoutError (socket.timeout)', 'No answer within the timeout', 'Retry later or give up with a clear message'],
    ['ConnectionResetError', 'The other side crashed or closed hard', 'Reconnect, and send again only if that is safe'],
    ['OSError: Address already in use', 'Another program, or your old one, has the port', 'Pick another port, or wait. SO_REUSEADDR helps after a restart'],
    ['socket.gaierror', 'The host name could not be found (DNS)', 'Check the spelling and the network']])}
{note('Host "127.0.0.1" (localhost) only accepts connections from the same computer. "0.0.0.0" accepts them from every network card, so other computers can connect. Use 127.0.0.1 while you learn.', 'warn')}
''', kw=['socket', 'bind', 'listen', 'accept', 'connect', 'create_connection', 'create_server', 'send', 'sendall', 'recv', 'close', 'timeout', 'ConnectionRefusedError', 'SO_REUSEADDR', 'localhost'])

K.lesson('framing', 'TCP is a stream: framing messages', f'''
{run('stream_framing')}
{table(['Framing method', 'How the receiver finds the end', 'Used by'], [
    ['Length prefix', 'Read a fixed size length first, then exactly that many bytes', 'PostgreSQL, Kafka, gRPC, WebSocket frames'],
    ['End marker', 'Read until a special byte sequence, such as a new line', 'SMTP email, Redis, HTTP headers (end with an empty line)'],
    ['Fixed size', 'Every message has the same size', 'Simple sensor data, some games'],
    ['Close the connection', 'The message ends when the sender closes', 'HTTP/1.0 without Content-Length']])}
{note('A very common bug: the sender calls sendall twice and the receiver expects two recv calls to return the two messages. On a fast local test it often works, and then it fails on a real network. recv only promises "some bytes", so always loop until you have a whole message.', 'warn')}
{deep('Why TCP cuts the stream', '<p>TCP puts your bytes into segments that fit the network. A segment is at most the MSS (usually 1,460 bytes on Ethernet). Nagle&#39;s algorithm may join small writes into one segment, and the receiver may read two segments at once. So the borders you see in recv have nothing to do with the borders of your sendall calls.</p>')}
''', kw=['stream', 'message boundary', 'framing', 'length prefix', 'delimiter', 'buffer', 'partial recv', 'MSS', 'Nagle'])

K.lesson('udp', 'UDP: single packets, no promises', f'''
{local('udp_ping', WHY_NET)}
{versus('TCP compared with UDP', ['', 'TCP', 'UDP'], [
    ['Connection', 'connect and accept first', 'None, just sendto an address'],
    ['Lost packets', 'Sent again automatically', 'Gone, the program must notice'],
    ['Order', 'Always the order they were sent', 'Can arrive in any order'],
    ['Message borders', 'Not kept', 'Kept: one sendto is one recvfrom'],
    ['Header size', '20 to 60 bytes', '8 bytes'],
    ['Speed of the first message', 'After one round trip', 'At once'],
    ['Python calls', 'connect, sendall, recv', 'sendto, recvfrom']],
    'TCP is better when every byte matters, such as files, web pages and payments. UDP is better when old data is useless anyway, such as the position of a player a second ago, or when one small question needs one small answer, such as DNS.')}
{note('A UDP datagram larger than the path allows (about 1,472 bytes of data on normal Ethernet) gets split by IP, and if one piece is lost the whole datagram is lost. Keep UDP messages small.', 'tip')}
''', kw=['UDP', 'SOCK_DGRAM', 'sendto', 'recvfrom', 'datagram', 'packet loss', 'DNS', 'TCP vs UDP'])

K.lesson('many', 'Serving many clients at once', f'''
{local('many_clients', WHY_NET)}
{versus('How a server can talk to many clients', ['', 'One at a time', 'A thread per client', 'selectors', 'asyncio'], [
    ['Idea', 'accept, serve, then accept the next', 'Each accepted socket gets its own thread', 'One loop asks the OS which sockets are ready', 'Coroutines that wait with await, on one event loop'],
    ['Many slow clients', 'Everyone else waits', 'Fine up to a few thousand', 'Fine, tens of thousands', 'Fine, tens of thousands'],
    ['Code', 'Very simple', 'Simple, but shared data needs locks', 'Hard to write by hand', 'Looks like normal code with async and await'],
    ['In Python', 'socket', 'socketserver.ThreadingTCPServer', 'selectors.DefaultSelector', 'asyncio.start_server']],
    'For new network code use asyncio, or a framework built on it. Threads are fine for small tools, and the one at a time server is only for learning.')}
{steps('What asyncio does in the example', [
    'asyncio.start_server opens a listening socket and calls handle() for every new client.',
    'When handle() reaches await asyncio.sleep(0.1) or await reader.readline(), it pauses and the event loop runs another client.',
    'So the three clients wait at the same time, and the whole run takes about 0.1 s instead of 0.3 s.',
    'Under the hood the event loop uses selectors (epoll on Linux, kqueue on macOS) to learn which sockets have data.'])}
''', kw=['concurrency', 'threading', 'socketserver', 'ThreadingTCPServer', 'selectors', 'epoll', 'asyncio', 'start_server', 'open_connection', 'event loop'])

K.lesson('addresses', 'IP addresses, ports and layers', f'''
{run('ip_ports')}
{table(['Layer', 'Job', 'Example', 'In Python'], [
    ['Application', 'What the program means', 'HTTP, DNS, SMTP, your own protocol', 'requests, http.server, your code'],
    ['Transport', 'Which program, and how reliable', 'TCP, UDP (ports)', 'socket.SOCK_STREAM, socket.SOCK_DGRAM'],
    ['Internet', 'Which computer, and the route there', 'IPv4, IPv6 (IP addresses)', 'socket.AF_INET, socket.AF_INET6, ipaddress'],
    ['Link', 'The next hop on the local network', 'Ethernet, Wi-Fi (MAC addresses)', 'The operating system does it']])}
{note('A /24 network has 2<sup>32 &minus; 24</sup> = 256 addresses. The first is the network address and the last is the broadcast address, so 254 are left for computers. Ports go from 0 to 65,535, and ports below 1024 usually need admin rights.', 'exam')}
''', kw=['IP address', 'IPv4', 'IPv6', 'CIDR', 'subnet', 'netmask', 'broadcast', 'ipaddress', 'port', 'well known ports', 'layers', 'TCP/IP model'])

K.lesson('maths', 'The maths: windows, round trips and loss', f'''
{fxs(fx('Addresses in a network', 'addresses = 2<sup>32 &minus; prefix</sup>, usable = addresses &minus; 2', '/24: 256 addresses, 254 usable. /20: 4,096 addresses.', key=True),
     fx('Data in one packet', 'MSS = MTU &minus; IP header &minus; TCP header', '1,500 &minus; 20 &minus; 20 = 1,460 bytes of your data.'),
     fx('Window limit on speed', 'throughput &le; window / RTT', 'A 64 KB window with RTT 100 ms: 65,535 &times; 8 / 0.1 &asymp; 5.2 Mbit/s, however fast the line is.', key=True),
     fx('Window needed', 'window = bandwidth &times; RTT (the bandwidth delay product)', '100 Mbit/s and 50 ms: 100,000,000 &times; 0.05 / 8 = 625,000 bytes.'),
     fx('TCP with loss (Mathis formula)', 'throughput &asymp; (MSS / RTT) &times; 1.22 / &radic;p', 'MSS 1,460 B, RTT 100 ms, loss p = 0.0001: about 14.2 Mbit/s.', key=True),
     fx('Chance of at least one loss', 'P = 1 &minus; (1 &minus; p)<sup>n</sup>', '100 packets with p = 0.01: 1 &minus; 0.99<sup>100</sup> &asymp; 0.634.'))}
{steps('Worked example: why a fast line can still be slow', [
    'A server is 100 ms away (RTT) on a 1 Gbit/s line. The receive window is 64 KB.',
    'TCP may only have one window of data on the way before it waits for an ACK, so each RTT moves at most 65,535 bytes.',
    'That is 65,535 &times; 8 / 0.1 &asymp; 5.2 Mbit/s, about 0.5 % of the line.',
    'To fill the line the window must be bandwidth &times; RTT = 1,000,000,000 &times; 0.1 / 8 = 12.5 MB. Modern systems grow the window with window scaling.',
    eq('throughput &le; window / RTT')])}
''', kw=['MTU', 'MSS', 'window', 'RTT', 'bandwidth delay product', 'throughput', 'Mathis formula', 'packet loss', 'subnet size'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Know that a socket is an IP address plus a port, that text must become bytes, and the difference between TCP and UDP.</p>',
    '<p>Write a TCP client and server with timeouts and error handling, use struct for binary data, and frame messages with a length prefix.</p>',
    '<p>Serve many clients with asyncio or selectors, compute subnets with ipaddress, and reason about windows, RTT and loss.</p>',
    '<p>Tune TCP options (TCP_NODELAY, keep alive, buffer sizes), understand TIME_WAIT, congestion control and QUIC, and design binary protocols that can change over time.</p>')}
{grow('Send and receive bytes.', 'Write reliable clients and servers.', 'Tune and design network protocols.')}
{deep('TIME_WAIT and SO_REUSEADDR', '<p>After a TCP connection closes, the side that closed first keeps the address in the TIME_WAIT state for up to a few minutes, so late packets from the old connection cannot be confused with a new one. If you restart a server quickly, bind can fail with "Address already in use". Setting SO_REUSEADDR before bind allows the restart. socket.create_server sets it for you on Linux and macOS.</p>')}
''', kw=['beginner', 'expert', 'TCP_NODELAY', 'keep alive', 'TIME_WAIT', 'congestion control', 'protocol design'])

lc(190, 'Reverse Bits', 'reverse-bits', 'e', 'Take the last bit, push it in from the right', 'Byte order and bit order matter on the wire. Take the lowest bit of n 32 times and add it to the result from the other end.', r'''
def reverse_bits(n):
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result
''', [('reverse_bits(43261596)', 964176192), ('reverse_bits(4294967293)', 3221225471)])
lc(1971, 'Find if Path Exists in Graph', 'find-if-path-exists-in-graph', 'e', 'Breadth first search from the source', 'Can a packet get from one computer to another? Keep a set of visited computers and a queue of computers to visit.', r'''
from collections import deque


def valid_path(n, edges, source, destination):
    links = {node: [] for node in range(n)}
    for a, b in edges:
        links[a].append(b)
        links[b].append(a)
    seen = {source}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        if node == destination:
            return True
        for other in links[node]:
            if other not in seen:
                seen.add(other)
                queue.append(other)
    return False
''', [('valid_path(3, [[0, 1], [1, 2], [2, 0]], 0, 2)', True), ('valid_path(6, [[0, 1], [0, 2], [3, 5], [5, 4], [4, 3]], 0, 5)', False)])
lc(2073, 'Time Needed to Buy Tickets', 'time-needed-to-buy-tickets', 'e', 'Count what each person buys before k is done', 'A queue served in turns, like a server that sends one piece to each client in turn. People before k buy at most tickets[k], people after k at most tickets[k] minus 1.', r'''
def time_required_to_buy(tickets, k):
    total = 0
    for i, wanted in enumerate(tickets):
        if i <= k:
            total += min(wanted, tickets[k])
        else:
            total += min(wanted, tickets[k] - 1)
    return total
''', [('time_required_to_buy([2, 3, 2], 2)', 6), ('time_required_to_buy([5, 1, 1, 1], 0)', 8)])
lc(743, 'Network Delay Time', 'network-delay-time', 'm', 'Dijkstra with a heap', 'A signal spreads from computer k over links with delays. Dijkstra finds the fastest time to each computer, and the answer is the slowest of those.', r'''
import heapq


def network_delay_time(times, n, k):
    links = {node: [] for node in range(1, n + 1)}
    for a, b, delay in times:
        links[a].append((b, delay))
    best = {}
    heap = [(0, k)]
    while heap:
        time, node = heapq.heappop(heap)
        if node in best:
            continue
        best[node] = time
        for other, delay in links[node]:
            if other not in best:
                heapq.heappush(heap, (time + delay, other))
    return max(best.values()) if len(best) == n else -1
''', [('network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2)', 2), ('network_delay_time([[1, 2, 1]], 2, 1)', 1), ('network_delay_time([[1, 2, 1]], 2, 2)', -1)])
lc(1319, 'Number of Operations to Make Network Connected', 'number-of-operations-to-make-network-connected', 'm', 'Union find counts the groups', 'You need at least n minus 1 cables. If there are enough, the answer is the number of separate groups minus 1.', r'''
def make_connected(n, connections):
    if len(connections) < n - 1:
        return -1
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    groups = n
    for a, b in connections:
        root_a, root_b = find(a), find(b)
        if root_a != root_b:
            parent[root_a] = root_b
            groups -= 1
    return groups - 1
''', [('make_connected(4, [[0, 1], [0, 2], [1, 2]])', 1), ('make_connected(6, [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3]])', 2), ('make_connected(6, [[0, 1], [0, 2], [0, 3], [1, 2]])', -1)])
lc(1514, 'Path with Maximum Probability', 'path-with-maximum-probability', 'm', 'Dijkstra on the largest product', 'Each link delivers a packet with some probability. Use a heap of negative probabilities so the most likely path comes out first.', r'''
import heapq


def max_probability(n, edges, succ_prob, start, end):
    links = {node: [] for node in range(n)}
    for (a, b), p in zip(edges, succ_prob):
        links[a].append((b, p))
        links[b].append((a, p))
    done = set()
    heap = [(-1.0, start)]
    while heap:
        neg_p, node = heapq.heappop(heap)
        if node == end:
            return -neg_p
        if node in done:
            continue
        done.add(node)
        for other, p in links[node]:
            if other not in done:
                heapq.heappush(heap, (neg_p * p, other))
    return 0.0
''', [('max_probability(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.2], 0, 2)', 0.25), ('max_probability(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.3], 0, 2)', 0.3), ('max_probability(3, [[0, 1]], [0.5], 0, 2)', 0.0)])
lc(787, 'Cheapest Flights Within K Stops', 'cheapest-flights-within-k-stops', 'm', 'Bellman Ford for k + 1 rounds', 'Like a packet with a hop limit (TTL). Each round allows one more flight. Copy the prices first so one round uses only one more flight.', r'''
def find_cheapest_price(n, flights, src, dst, k):
    INF = float("inf")
    price = [INF] * n
    price[src] = 0
    for _ in range(k + 1):
        new_price = price[:]
        for a, b, cost in flights:
            if price[a] + cost < new_price[b]:
                new_price[b] = price[a] + cost
        price = new_price
    return price[dst] if price[dst] < INF else -1
''', [('find_cheapest_price(4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1)', 700), ('find_cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1)', 200), ('find_cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0)', 500)])
lc(1615, 'Maximal Network Rank', 'maximal-network-rank', 'm', 'Degrees of both cities, minus 1 if they are linked', 'The rank of two cities is the number of roads touching either one. Try every pair and do not count a shared road twice.', r'''
def maximal_network_rank(n, roads):
    degree = [0] * n
    linked = set()
    for a, b in roads:
        degree[a] += 1
        degree[b] += 1
        linked.add((a, b))
        linked.add((b, a))
    best = 0
    for a in range(n):
        for b in range(a + 1, n):
            rank = degree[a] + degree[b] - (1 if (a, b) in linked else 0)
            best = max(best, rank)
    return best
''', [('maximal_network_rank(4, [[0, 1], [0, 3], [1, 2], [1, 3]])', 4), ('maximal_network_rank(5, [[0, 1], [0, 3], [1, 2], [1, 3], [2, 3], [2, 4]])', 5), ('maximal_network_rank(8, [[0, 1], [1, 2], [2, 3], [2, 4], [5, 6], [5, 7]])', 5)])
lc(1192, 'Critical Connections in a Network', 'critical-connections-in-a-network', 'h', 'Tarjan: discovery time and lowest reachable time', 'A cable is critical if cutting it splits the network. In a depth first search, the link to a child is critical when the child cannot reach back above itself.', r'''
def critical_connections(n, connections):
    links = {node: [] for node in range(n)}
    for a, b in connections:
        links[a].append(b)
        links[b].append(a)
    order = [-1] * n
    low = [0] * n
    found = []
    counter = 0
    for root in range(n):
        if order[root] != -1:
            continue
        order[root] = low[root] = counter
        counter += 1
        stack = [(root, -1, iter(links[root]))]
        while stack:
            node, parent, children = stack[-1]
            moved = False
            for child in children:
                if child == parent:
                    continue
                if order[child] == -1:
                    order[child] = low[child] = counter
                    counter += 1
                    stack.append((child, node, iter(links[child])))
                    moved = True
                    break
                low[node] = min(low[node], order[child])
            if moved:
                continue
            stack.pop()
            if parent != -1:
                low[parent] = min(low[parent], low[node])
                if low[node] > order[parent]:
                    found.append(sorted([parent, node]))
    return sorted(found)
''', [('critical_connections(4, [[0, 1], [1, 2], [2, 0], [1, 3]])', [[1, 3]]), ('critical_connections(2, [[0, 1]])', [[0, 1]]), ('critical_connections(5, [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4]])', [[2, 3], [3, 4]])])
lc(1579, 'Remove Max Number of Edges to Keep Graph Fully Traversable', 'remove-max-number-of-edges-to-keep-graph-fully-traversable', 'h', 'Two union finds, shared edges first', 'Use the edges both Alice and Bob can use first, then each person&#39;s own edges. Every edge that joins nothing new can be removed.', r'''
class Groups:
    def __init__(self, n):
        self.parent = list(range(n + 1))
        self.count = n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def join(self, a, b):
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False
        self.parent[root_a] = root_b
        self.count -= 1
        return True


def max_num_edges_to_remove(n, edges):
    alice, bob = Groups(n), Groups(n)
    used = 0
    for kind, a, b in edges:
        if kind == 3:
            joined_a = alice.join(a, b)
            joined_b = bob.join(a, b)
            if joined_a or joined_b:
                used += 1
    for kind, a, b in edges:
        if kind == 1 and alice.join(a, b):
            used += 1
        elif kind == 2 and bob.join(a, b):
            used += 1
    if alice.count != 1 or bob.count != 1:
        return -1
    return len(edges) - used
''', [('max_num_edges_to_remove(4, [[3, 1, 2], [3, 2, 3], [1, 1, 3], [1, 2, 4], [1, 1, 2], [2, 3, 4]])', 2), ('max_num_edges_to_remove(4, [[3, 1, 2], [3, 2, 3], [1, 1, 4], [2, 1, 4]])', 0), ('max_num_edges_to_remove(4, [[3, 2, 3], [1, 1, 2], [2, 3, 4]])', -1)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Networks are graphs: computers are nodes and cables are edges. These problems practise the graph ideas that real routing uses, such as reachability, shortest delay, groups of connected computers and links whose failure splits a network, plus bit work like byte order.</p>'), kw=['LeetCode', 'graph', 'BFS', 'Dijkstra', 'Bellman Ford', 'union find', 'Tarjan', 'bridges', 'bits'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A socket is one end of a connection: an IP address finds the computer, a port finds the program. Sockets send and receive bytes, so encode text first.',
    'TCP server: socket, bind, listen, accept (a new socket per client). Client: create_connection. Use sendall, loop on recv, and always set a timeout.',
    'TCP is a reliable stream with no message borders, so frame messages with a length prefix (struct.pack("!I", n)) or an end marker.',
    'UDP sends single datagrams with sendto and recvfrom: fast, keeps borders, but may lose or reorder them.',
    'Serve many clients with asyncio (start_server, open_connection). Speed is limited by window / RTT and by packet loss.'],
    'Next: calling real web APIs with the requests library.')}
{files('Three tasks: pack and split length prefixed messages, work with subnets using ipaddress, and read exact sizes and lines from a socket that returns small pieces.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does a port number choose?', ['The computer', 'The program on the computer', 'The cable', 'The website name'], 1, 'The IP address already found the computer.', 'For example port 443 for an HTTPS server and 5432 for PostgreSQL.')
K.quiz('e', 'What does a socket send and receive in Python?', ['str', 'bytes', 'dict', 'JSON objects'], 1, 'Encode before sending.', 'Use .encode("utf-8") and .decode("utf-8") to change between text and bytes.')
K.quiz('e', 'Which protocol sends lost data again automatically?', ['UDP', 'TCP', 'Both', 'Neither'], 1, 'The reliable one.', 'UDP leaves this to the program.')
K.quiz('m', 'What does accept() return on a TCP server?', ['The data from the client', 'A new socket for this client and the client address', 'True or False', 'The port number'], 1, 'One socket per client.', 'The listening socket stays open and can accept the next client.')
K.quiz('m', 'conn.recv(1024) returns b"". What does it mean?', ['No data yet, try again', 'The other side closed the connection', 'An error happened', '1024 bytes were lost'], 1, 'Empty bytes.', 'A blocking recv waits for data, so an empty result can only mean the end of the stream.')
K.quiz('m', 'A client calls sendall(b"ab") and then sendall(b"cd"). What may the server get from recv(1024)?', ['Always b"ab" first, then b"cd"', 'b"abcd", or b"a" then b"bcd", or other cuts', 'Only b"cd"', 'An error'], 1, 'TCP is a stream.', 'That is why messages need framing.')
K.quiz('m', 'Why use sendall() and not send()?', ['sendall is faster', 'send may send only part of the data and returns how much it sent', 'send only works for UDP', 'There is no difference'], 1, 'Read the return value of send.', 'sendall loops for you until every byte is sent or an error happens.')
K.quiz('m', 'What does struct.pack("!I", 5) give?', ['b"5"', 'Four bytes 00 00 00 05', 'Five bytes', 'The text "!I5"'], 1, 'I is 4 bytes, ! is big endian.', 'The most important byte comes first in network order.')
K.quiz('m', 'How many addresses are in the network 10.0.0.0/22?', ['22', '256', '1024', '4096'], 2, '2 to the power of (32 minus 22).', '2<sup>10</sup> = 1024 addresses, 1022 for computers.')
K.quiz('h', 'A server must be reachable from other computers. Which host should it bind to?', ['127.0.0.1', '0.0.0.0 (or the address of one network card)', 'localhost', '255.255.255.255'], 1, 'Every network card.', '127.0.0.1 only accepts connections from the same computer.')
K.quiz('h', 'A server restarts and bind fails with "Address already in use", though no server runs. Why?', ['The port is broken', 'Old connections are in TIME_WAIT, set SO_REUSEADDR before bind', 'The firewall', 'Python keeps a lock file'], 1, 'TCP waits a little after closing.', 'socket.create_server sets SO_REUSEADDR for you on Linux and macOS.')
K.quiz('x', 'In the style of a Stanford CS 144 exam: a link has 1 Gbit/s and RTT 100 ms, and the TCP window is fixed at 64 KB. Roughly what throughput can one connection reach?', ['1 Gbit/s', 'About 5.2 Mbit/s', 'About 100 Mbit/s', 'About 64 Mbit/s'], 1, 'window / RTT.', '65,535 &times; 8 / 0.1 &asymp; 5.2 Mbit/s. Window scaling fixes this on modern systems.')
K.quiz('x', 'In the style of a CMU 15-441 exam: by the Mathis formula, if the loss rate p becomes 4 times larger, what happens to TCP throughput?', ['It stays the same', 'It halves', 'It becomes 4 times smaller', 'It doubles'], 1, 'Throughput goes with 1 / &radic;p.', '&radic;4 = 2, so the throughput is divided by 2.')

K.calc('e', 'MTU 1500 bytes, IPv4 header 20 bytes, TCP header 20 bytes. How many bytes of your data fit in one packet?', '1460', 'MTU minus both headers.', ['The MTU is the whole packet: 1500 bytes.', 'Take away both headers: 1500 &minus; 20 &minus; 20.', eq('1460 bytes')], check=1500 - 20 - 20)
K.calc('e', 'How many addresses can computers use in a /24 network?', '254', '256 minus network and broadcast.', ['2<sup>8</sup> = 256.', '256 &minus; 2.', eq('254')], check=2 ** 8 - 2)
K.calc('e', 'How many bytes does struct.pack("!HI", 8080, 7) make?', '6', 'H is 2 bytes, I is 4.', ['2 + 4.', 'No padding with !.', eq('6')], check=__import__('struct').calcsize('!HI'))
K.calc('m', 'RTT is 80 ms. A new TCP connection does the handshake and then one request and its answer. How many ms before the answer arrives?', '160', 'Handshake 1 RTT, request and answer 1 RTT.', ['2 round trips.', '2 &times; 80.', eq('160 ms')], check=2 * 80)
K.calc('m', 'How many addresses are in a /20 network?', '4096', '2<sup>32 &minus; 20</sup>.', ['32 &minus; 20 = 12.', '2<sup>12</sup>.', eq('4096')], check=2 ** 12)
K.calc('m', 'Window 65,535 bytes, RTT 100 ms. What is the most throughput in Mbit/s (2 decimals)?', '5.24', 'window &times; 8 / RTT.', ['65,535 &times; 8 = 524,280 bits.', '524,280 / 0.1 = 5,242,800 bit/s.', eq('5.24 Mbit/s')], check=65535 * 8 / 0.1 / 1e6, tol=0.01)
K.calc('m', 'How many bytes must the TCP window be to fill 100 Mbit/s at RTT 50 ms?', '625000', 'bandwidth &times; RTT / 8.', ['100,000,000 &times; 0.05 = 5,000,000 bits.', '5,000,000 / 8.', eq('625,000 bytes')], check=100_000_000 * 0.05 / 8)
K.calc('m', 'What percent of a 1500 byte packet are the 40 bytes of IP and TCP headers (2 decimals)?', '2.67', '40 / 1500 &times; 100.', ['40 / 1500 = 0.02667.', 'Times 100.', eq('2.67 %')], check=40 / 1500 * 100, tol=0.01)
K.calc('h', 'Mathis formula: MSS 1460 bytes, RTT 0.1 s, loss p = 0.0001. Throughput in Mbit/s (1 decimal)?', '14.2', '(MSS &times; 8 / RTT) &times; 1.22 / &radic;p.', ['1460 &times; 8 / 0.1 = 116,800 bit/s.', '1.22 / &radic;0.0001 = 1.22 / 0.01 = 122.', '116,800 &times; 122 = 14,249,600 bit/s.', eq('&asymp; 14.2 Mbit/s')], check=1460 * 8 / 0.1 * 1.22 / 0.0001 ** 0.5 / 1e6, tol=0.06)
K.calc('x', 'In the style of an MIT 6.829 exam: each packet is lost with probability 0.01. What is the chance that at least one of 100 packets is lost (3 decimals)?', '0.634', '1 &minus; (1 &minus; p)<sup>n</sup>.', ['No loss in one packet: 0.99.', 'No loss in all 100: 0.99<sup>100</sup> &asymp; 0.366.', '1 &minus; 0.366.', eq('&asymp; 0.634')], check=1 - 0.99 ** 100, tol=0.001)

K.assign('frames', 'e', 'Pack and split length prefixed messages',
         '<p>Write <code>pack(text)</code> that returns the UTF-8 bytes of the text with a 4 byte big endian length in front. The length counts BYTES, not letters. Then write <code>split_messages(chunks)</code>: chunks is a list of bytes objects as recv might return them, cut anywhere. Return the list of complete messages as text, and ignore an unfinished message at the end.</p>',
         '''
def pack(text):
    return len(text).to_bytes(4, "big") + text.encode()


def split_messages(chunks):
    messages = []
    for chunk in chunks:
        messages.append(chunk[4:].decode(errors="replace"))
    return messages


def cut(data, size):
    return [data[i:i + size] for i in range(0, len(data), size)]


STREAM = b"\\x00\\x00\\x00\\x02hi\\x00\\x00\\x00\\x03bye\\x00\\x00\\x00\\x06h\\xc3\\xa9llo"
''', [('pack("hi").hex()', '000000026869'), ('pack("héllo")[:4].hex()', '00000006'), ('split_messages([STREAM])', ['hi', 'bye', 'héllo']), ('split_messages(cut(STREAM, 3))', ['hi', 'bye', 'héllo']), ('split_messages(cut(STREAM, 1))', ['hi', 'bye', 'héllo']), ('split_messages(cut(STREAM[:-2], 4))', ['hi', 'bye'])],
         '''
import struct


def pack(text):
    data = text.encode("utf-8")
    return struct.pack("!I", len(data)) + data


def split_messages(chunks):
    messages = []
    buffer = b""
    for chunk in chunks:
        buffer += chunk
        while len(buffer) >= 4:
            size = struct.unpack("!I", buffer[:4])[0]
            if len(buffer) < 4 + size:
                break
            messages.append(buffer[4:4 + size].decode("utf-8"))
            buffer = buffer[4 + size:]
    return messages


def cut(data, size):
    return [data[i:i + size] for i in range(0, len(data), size)]


STREAM = b"\\x00\\x00\\x00\\x02hi\\x00\\x00\\x00\\x03bye\\x00\\x00\\x00\\x06h\\xc3\\xa9llo"
''', 'Encode first and measure the bytes. Keep one buffer for all chunks, and in a while loop take out every complete message it holds.', '<p>Real protocols such as PostgreSQL and Kafka read messages exactly like this. They also refuse a length that is too big, so a bad client cannot make the server reserve gigabytes of memory.</p>')
K.assign('subnets', 'm', 'Work with subnets',
         '<p>Use the ipaddress module. Write <code>usable_hosts(cidr)</code>: 2<sup>32 &minus; prefix</sup> &minus; 2 addresses, but 2 for a /31 (a link between two routers) and 1 for a /32. Write <code>same_subnet(ip1, ip2, prefix)</code>: True when both addresses are in the same network of that prefix length. Write <code>split(cidr, parts)</code>: the list of equal smaller networks as text, and raise ValueError when parts is not a power of 2.</p>',
         '''
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
''', [('usable_hosts("192.168.1.0/24")', 254), ('usable_hosts("10.0.0.0/30")', 2), ('usable_hosts("10.0.0.0/31")', 2), ('usable_hosts("10.0.0.1/32")', 1), ('same_subnet("192.168.1.10", "192.168.1.200", 24)', True), ('same_subnet("10.0.1.5", "10.0.2.5", 16)', True), ('same_subnet("10.0.1.5", "10.0.1.200", 25)', False), ('split("192.168.1.0/24", 4)', ['192.168.1.0/26', '192.168.1.64/26', '192.168.1.128/26', '192.168.1.192/26']), ('split_error("192.168.1.0/24", 3)', 'ValueError')],
         '''
import ipaddress


def usable_hosts(cidr):
    prefix = ipaddress.ip_network(cidr).prefixlen
    if prefix == 32:
        return 1
    if prefix == 31:
        return 2
    return 2 ** (32 - prefix) - 2


def same_subnet(ip1, ip2, prefix):
    network = ipaddress.ip_network(f"{ip1}/{prefix}", strict=False)
    return ipaddress.ip_address(ip2) in network


def split(cidr, parts):
    if parts < 1 or parts & (parts - 1) != 0:
        raise ValueError(f"{parts} is not a power of 2")
    network = ipaddress.ip_network(cidr)
    extra_bits = parts.bit_length() - 1
    return [str(part) for part in network.subnets(prefixlen_diff=extra_bits)]


def split_error(cidr, parts):
    try:
        split(cidr, parts)
    except ValueError:
        return "ValueError"
    return "no error"
''', 'ip_network(..., strict=False) builds the network that an address belongs to. A number is a power of 2 when n &amp; (n &minus; 1) is 0, and splitting into 2<sup>k</sup> parts adds k bits to the prefix.', '<p>Cloud providers ask for exactly these numbers when you make a virtual network: how big it is, how to split it into subnets, and which addresses can talk directly.</p>')
K.assign('recvall', 'h', 'Read exact sizes and lines from a socket',
         '<p>FakeSocket acts like a TCP socket: recv(n) returns at most n bytes and often fewer, and b"" at the end. Write <code>recv_exact(sock, n)</code> that returns exactly n bytes, and raises ConnectionError if the data ends first. Then finish <code>LineReader</code>: read_line() returns the next line as text without the line end ("&#92;n", and also "&#92;r&#92;n"), the last piece of text when it has no line end, and None when nothing is left. Bytes after a line must be kept for the next call.</p>',
         '''
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
''', [('recv_exact(FakeSocket(b"hello world"), 5).decode()', 'hello'), ('recv_exact(FakeSocket(b"abcdefgh", 2), 7).decode()', 'abcdefg'), ('exact_error(b"abc", 5)', 'ConnectionError'), ('read_lines(b"one\\ntwo\\nthree\\n", 4)', ['one', 'two', 'three']), ('read_lines(b"GET / HTTP/1.1\\r\\nHost: a\\r\\n\\r\\n", 5)', ['GET / HTTP/1.1', 'Host: a', '']), ('read_lines(b"no line end here", 3)', ['no line end here'])],
         '''
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
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError(f"closed after {len(data)} of {n} bytes")
        data += chunk
    return data


def exact_error(data, n):
    try:
        recv_exact(FakeSocket(data), n)
    except ConnectionError:
        return "ConnectionError"
    return "no error"


class LineReader:
    def __init__(self, sock):
        self.sock = sock
        self.buffer = b""
        self.closed = False

    def read_line(self):
        while b"\\n" not in self.buffer and not self.closed:
            chunk = self.sock.recv(1024)
            if chunk:
                self.buffer += chunk
            else:
                self.closed = True
        if b"\\n" in self.buffer:
            line, _, self.buffer = self.buffer.partition(b"\\n")
            return line.rstrip(b"\\r").decode()
        if self.buffer:
            line = self.buffer
            self.buffer = b""
            return line.decode()
        return None


def read_lines(data, piece):
    reader = LineReader(FakeSocket(data, piece))
    lines = []
    while True:
        line = reader.read_line()
        if line is None:
            return lines
        lines.append(line)
''', 'Loop on recv and ask only for the bytes still missing. In LineReader keep a buffer: read until it holds a new line or the socket is closed, then cut off one line and keep the rest.', '<p>asyncio has the same tools built in: reader.readexactly(n) and reader.readline(). Now you know what they do inside.</p>')

K.must('Sockets', 'socket(AF_INET, SOCK_STREAM) for TCP, SOCK_DGRAM for UDP. An address is (host, port). Ports 0 to 65,535. 127.0.0.1 local only, 0.0.0.0 every network card.')
K.must('TCP calls', 'Server: bind, listen, accept (new socket per client). Client: create_connection(addr, timeout). sendall, recv(n) gives 1 to n bytes, b"" means closed.')
K.must('Framing', 'TCP keeps no message borders. Length prefix with struct.pack("!I", n), or an end marker such as a new line. Loop until a message is complete.')
K.must('UDP', 'sendto and recvfrom, no handshake, borders kept, may lose or reorder. Used for DNS, games, video. 8 byte header.')
K.must('Numbers', 'MSS = MTU &minus; 40. throughput &le; window / RTT. window = bandwidth &times; RTT. /n network has 2<sup>32 &minus; n</sup> addresses.')

T = K.topic(
    slug='py-sockets', topic='py-sockets', step=(1, 'How the web works: HTTP, REST and sockets', 'py-w1', 'See what really travels between a program and a server: HTTP requests and responses, REST design, and the sockets underneath.', 'Intermediate'),
    title='Sockets, TCP and UDP: under HTTP', short='Sockets', badge='1.2', minutes=90,
    lead='Go one level below HTTP. Write a TCP client and server with the socket module, see why TCP needs message framing, send UDP datagrams, serve many clients with asyncio, and work with IP addresses and subnets.',
    desc='Bytes, encode and decode, struct and network byte order, TCP sockets (bind, listen, accept, create_connection, sendall, recv), errors and timeouts, the TCP stream and message framing, UDP with sendto and recvfrom, serving many clients with threads, selectors and asyncio, IP addresses, ports, subnets with ipaddress, and the maths of windows, RTT and packet loss.',
    summary='TCP and UDP sockets, bytes and struct, message framing, many clients with asyncio, IP addresses and subnets.',
    keywords=['socket', 'TCP', 'UDP', 'bytes', 'struct', 'framing', 'asyncio', 'ipaddress', 'subnet', 'port'],
    recap='<p>The operating system moves the bytes, your program only sends and receives them. TCP gives a reliable stream that you must cut into messages yourself, UDP gives fast single packets with no promises.</p>',
    added='2026-11-07', leet=leet_items())
