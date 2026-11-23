# 3.2 Ethereum and smart contract security: reentrancy, overflow, oracles and MEV
# Example "gas_fee" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Ethereum fees after EIP-1559 (August 2021): gas used times (base fee + tip). The base fee is burned.
GWEI = 1e-9                                   # 1 gwei = one billionth of an ether

def fee(gas_used, base_gwei, tip_gwei, eth_price):
    eth = gas_used * (base_gwei + tip_gwei) * GWEI
    burned = gas_used * base_gwei * GWEI
    return eth, burned, eth * eth_price

for what, gas in [("send ether", 21_000), ("token transfer", 65_000), ("swap on a pool", 150_000)]:
    eth, burned, usd = fee(gas, base_gwei=20, tip_gwei=2, eth_price=3000)
    print(f"{what:15s} {gas:7,d} gas: {eth:.6f} ETH (${usd:6.2f}), burned {burned:.6f}")

# the base fee rises by up to 12.5% after a full block and falls by up to 12.5% after an empty one
base = 20.0
for fullness in (1.0, 1.0, 1.0, 0.5, 0.0):
    base *= 1 + 0.125 * (fullness - 0.5) / 0.5
    print(f"block {fullness:.0%} full -> next base fee {base:.2f} gwei")

# why gas exists: a contract stuck in a loop stops when its gas runs out, and the sender still pays
limit, per_loop = 100_000, 300
print("an endless loop stops after", limit // per_loop, "rounds when 100,000 gas runs out")
