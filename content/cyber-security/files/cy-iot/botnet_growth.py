# 4.3 IoT and industrial control security: Mirai, Modbus, Purdue and Stuxnet
# Example "botnet_growth" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# How fast does a worm fill the weak devices? A simple epidemic model of Mirai style spread
def spread(n_devices, weak_share, probes_per_round, rounds=12):
    weak = n_devices * weak_share
    infected = 1.0
    history = [infected]
    for _ in range(rounds):
        # each bot probes random addresses, a probe succeeds if it hits a weak device not yet infected
        new = infected * probes_per_round * (weak - infected) / n_devices
        infected = min(weak, infected + new)
        history.append(infected)
    return history

for share in (0.6, 0.2, 0.02):
    h = spread(100_000, share, probes_per_round=3)
    print(f"{share:4.0%} default passwords: " + "  ".join(f"{x:7.0f}" for x in h[::2]))

bots = 600_000
for upload_mbps in (1, 5):
    print(f"{bots:,} bots at {upload_mbps} Mbit/s each = {bots * upload_mbps / 1e6:.1f} Tbit/s of attack traffic")
