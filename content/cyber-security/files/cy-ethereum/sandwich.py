# 3.2 Ethereum and smart contract security: reentrancy, overflow, oracles and MEV
# Example "sandwich" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A sandwich attack and how the victim's slippage limit caps it
def buy(usdc, eth, amount):
    return eth - usdc * eth / (usdc + amount * 0.997)

def sandwich(slippage, victim=20_000, gas=30):
    X, Y = 200_000.0, 100.0
    fair = buy(X, Y, victim)
    min_out = fair * (1 - slippage)
    lo, hi = 0.0, 400_000.0
    for _ in range(60):                             # the biggest front run that still lets the victim trade
        a = (lo + hi) / 2
        e = buy(X, Y, a)
        if buy(X + a, Y - e, victim) >= min_out:
            lo = a
        else:
            hi = a
    a = lo
    e = buy(X, Y, a)
    x1, y1 = X + a, Y - e
    got = buy(x1, y1, victim)
    x2, y2 = x1 + victim, y1 - got
    sold = x2 - x2 * y2 / (y2 + e * 0.997)
    return fair, got, sold - a - gas

for s in (0.005, 0.02, 0.05, 0.10):
    fair, got, profit = sandwich(s)
    verdict = "attack" if profit > 0 else "not worth it"
    print(f"slippage {s:5.1%}: victim gets {got:.3f} of {fair:.3f} ETH, bot profit {profit:9.2f} -> {verdict}")
