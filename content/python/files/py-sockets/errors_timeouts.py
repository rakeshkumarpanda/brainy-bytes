# 1.2 Sockets, TCP and UDP: under HTTP
# Example "errors_timeouts" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
