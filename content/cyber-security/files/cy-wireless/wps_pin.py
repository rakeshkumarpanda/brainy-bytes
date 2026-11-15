# 1.3 Wireless security: from WEP to WPA3
# Example "wps_pin" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Why WPS PINs fall in hours: the router checks the two halves of the PIN separately (Viehbock, 2011)
def checksum(pin7):                      # the last digit of a WPS PIN is a checksum of the first 7
    accum = 0
    while pin7:
        accum += 3 * (pin7 % 10)
        pin7 //= 10
        accum += pin7 % 10
        pin7 //= 10
    return (10 - accum % 10) % 10

print("PIN 1234567 + checksum ->", f"1234567{checksum(1234567)}")
print("naive guesses for 8 digits:", 10 ** 8)
print("but the 8th digit is a checksum:", 10 ** 7)
print("and the halves are confirmed separately:", 10 ** 4, "+", 10 ** 3, "=", 10 ** 4 + 10 ** 3)
seconds_per_try = 1.5
print(f"at {seconds_per_try} s per try, worst case: {(10 ** 4 + 10 ** 3) * seconds_per_try / 3600:.1f} hours")
print("defence: turn WPS PIN mode off, or use routers that lock out after failures")
