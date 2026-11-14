# 2.2 Networks for security: layers, addresses, subnets, TCP and DNS
# Example "handshake" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Sequence and acknowledgement numbers in a TCP connection
client_isn = 1000      # initial sequence numbers, random in real systems
server_isn = 5000
data_len = 120

print("1. client -> server  SYN      seq =", client_isn)
print("2. server -> client  SYN-ACK  seq =", server_isn, " ack =", client_isn + 1)
print("3. client -> server  ACK      seq =", client_isn + 1, " ack =", server_isn + 1)
print("4. client -> server  data     seq =", client_isn + 1, " length =", data_len)
print("5. server -> client  ACK      ack =", client_isn + 1 + data_len)

# A SYN flood: many SYNs, no final ACK. Each half open connection waits in a queue.
queue_size = 128
syn_per_second = 500
print("queue full after", round(queue_size / syn_per_second, 3), "seconds without SYN cookies")
