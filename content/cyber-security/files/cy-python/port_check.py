# 2.3 Python for security: bytes, hashes, logs, packets and safe code
# Example "port_check" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Is a TCP port open? Checked only on this computer (127.0.0.1), never on someone else's.
import socket

def is_open(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    result = s.connect_ex((host, port))      # 0 means the handshake worked
    s.close()
    return result == 0

server = socket.socket()
server.bind(("127.0.0.1", 0))                 # port 0: let the OS pick a free port
server.listen()
open_port = server.getsockname()[1]

spare = socket.socket()
spare.bind(("127.0.0.1", 0))
closed_port = spare.getsockname()[1]
spare.close()                                 # nothing listens here any more

print("port with a listener open:", is_open("127.0.0.1", open_port))
print("port with no listener open:", is_open("127.0.0.1", closed_port))
server.close()
