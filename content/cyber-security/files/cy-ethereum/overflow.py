# 3.2 Ethereum and smart contract security: reentrancy, overflow, oracles and MEV
# Example "overflow" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Fixed width integers: what Solidity before 0.8 did silently, and what 0.8 does now
def unchecked(x, bits=256):
    return x % (2 ** bits)                         # wrap around, no error

def checked(x, bits=256):
    if not 0 <= x < 2 ** bits:
        raise OverflowError("Panic(0x11): arithmetic overflow or underflow")
    return x

print("uint8   0 - 1   unchecked =", unchecked(0 - 1, 8))
print("uint8 250 + 10  unchecked =", unchecked(250 + 10, 8))
try:
    checked(0 - 1, 8)
except OverflowError as e:
    print("uint8   0 - 1   checked   ->", e)

# BeautyChain batchTransfer (April 2018): total = count * value, then check sender balance >= total
count = 2
value = 2 ** 255                                   # chosen by the attacker
total = unchecked(count * value)                   # 2 * 2^255 = 2^256, which wraps to 0
print("\nBeautyChain total to deduct:", total)
print("balance check 'balance >= total' passes with any balance, yet each receiver gets", value)
print("that is about 5.8 x 10^76 tokens created from nothing")
