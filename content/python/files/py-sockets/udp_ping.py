# 1.2 Sockets, TCP and UDP: under HTTP
# Example "udp_ping" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
