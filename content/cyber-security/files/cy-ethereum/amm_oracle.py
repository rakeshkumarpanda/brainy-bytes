# 3.2 Ethereum and smart contract security: reentrancy, overflow, oracles and MEV
# Example "amm_oracle" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A flash loan pumps a constant product pool, and a lending app that trusts the spot price pays for it
def swap(r_in, r_out, amount, fee=0.003):
    amount_after_fee = amount * (1 - fee)
    return r_out - r_in * r_out / (r_in + amount_after_fee)

def attack(loan, oracle):
    usdc, eth = 200_000.0, 100.0                 # pool reserves, price 2,000
    got_eth = swap(usdc, eth, loan)
    usdc, eth = usdc + loan, eth - got_eth
    spot = usdc / eth
    price = spot if oracle == "spot" else 2000 * (1 - 12 / 1800) + spot * 12 / 1800
    borrowed = 0.75 * 10 * price                 # 10 ETH deposited as collateral, 75% loan to value
    usdc_back = swap(eth, usdc, got_eth)
    profit = borrowed + usdc_back - loan * 1.0009 - 10 * 2000
    return spot, price, borrowed, profit

for loan in (100_000, 200_000, 400_000):
    for oracle in ("spot", "twap"):
        spot, price, borrowed, profit = attack(loan, oracle)
        print(f"loan {loan:7,d} oracle {oracle:4s}: pool price {spot:8,.0f}, oracle {price:8,.0f}, "
              f"borrowed {borrowed:9,.0f}, attacker profit {profit:10,.0f}")
