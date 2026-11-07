# 1.2 Sockets, TCP and UDP: under HTTP
# Example "tcp_echo" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

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
