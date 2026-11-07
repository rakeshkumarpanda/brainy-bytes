# 1.4 Input, output and formatting text
# Example "spec" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

amount = 1234567.891
print(f"{amount:.2f}")       # 2 decimal places
print(f"{amount:,.2f}")      # thousands separator
print(f"{amount:_.0f}")      # underscore separator, no decimals
print(f"{amount:12.1f}|")    # width 12, right aligned (numbers default)
print(f"{'left':<10}|{'mid':^10}|{'right':>10}|")
print(f"{42:05d} {42:+d} {42:b} {255:x} {255:#X}")
print(f"{0.4567:.1%}  {1234.5:e}  {0.000123:.2e}")
print(f"{'Python':*^20}")
