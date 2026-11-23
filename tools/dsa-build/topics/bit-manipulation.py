# Bit manipulation: binary numbers, AND OR XOR NOT, shifts, masks, famous tricks, subsets as bitmasks,
# and bits in everyday systems (file permissions, colours, network masks).
from kit4 import Topic

t = Topic()

# ---------------------------------------------------------------- lesson programs
t.code('to_binary', py=r'''
def to_binary(n):
    if n == 0:
        return "0"
    bits = ""
    while n > 0:
        bits = str(n % 2) + bits    # the remainder is the next bit, read from the right
        n = n // 2                  # move on to the rest of the number
    return bits


def to_decimal(bits):
    value = 0
    for b in bits:
        value = value * 2 + int(b)  # make room on the right, then drop the bit in
    return value


for n in [13, 200, 255]:
    b = to_binary(n)
    print(n, "->", b, "->", to_decimal(b))
''', js=r'''
function toBinary(n) {
  if (n === 0) return "0";
  let bits = "";
  while (n > 0) {
    bits = String(n % 2) + bits;    // the remainder is the next bit, read from the right
    n = Math.floor(n / 2);          // move on to the rest of the number
  }
  return bits;
}

function toDecimal(bits) {
  let value = 0;
  for (const b of bits) {
    value = value * 2 + Number(b);  // make room on the right, then drop the bit in
  }
  return value;
}

for (const n of [13, 200, 255]) {
  const b = toBinary(n);
  console.log(n, "->", b, "->", toDecimal(b));
}
''', java=r'''
public class ToBinary {
    static String toBinary(int n) {
        if (n == 0) return "0";
        String bits = "";
        while (n > 0) {
            bits = (n % 2) + bits;          // the remainder is the next bit, read from the right
            n = n / 2;                      // move on to the rest of the number
        }
        return bits;
    }

    static int toDecimal(String bits) {
        int value = 0;
        for (char b : bits.toCharArray()) {
            value = value * 2 + (b - '0');  // make room on the right, then drop the bit in
        }
        return value;
    }

    public static void main(String[] args) {
        for (int n : new int[]{13, 200, 255}) {
            String b = toBinary(n);
            System.out.println(n + " -> " + b + " -> " + toDecimal(b));
        }
    }
}
''', ts=r'''
function toBinary(n: number): string {
  if (n === 0) return "0";
  let bits = "";
  while (n > 0) {
    bits = String(n % 2) + bits;    // the remainder is the next bit, read from the right
    n = Math.floor(n / 2);          // move on to the rest of the number
  }
  return bits;
}

function toDecimal(bits: string): number {
  let value = 0;
  for (const b of bits) {
    value = value * 2 + Number(b);  // make room on the right, then drop the bit in
  }
  return value;
}

for (const n of [13, 200, 255]) {
  const b: string = toBinary(n);
  console.log(n, "->", b, "->", toDecimal(b));
}
''')

t.code('bit_ops', py=r'''
a, b = 12, 10                        # 1100 and 1010 in binary


def show(x):
    return format(x, "04b")          # four binary digits with leading zeros


print("a & b =", a & b, show(a & b))  # AND: 1 only where both are 1
print("a | b =", a | b, show(a | b))  # OR: 1 where at least one is 1
print("a ^ b =", a ^ b, show(a ^ b))  # XOR: 1 where they differ
print("~a =", ~a)                     # NOT flips every bit, which gives -(a + 1)
''', js=r'''
const a = 12, b = 10;                // 1100 and 1010 in binary

function show(x) {
  return x.toString(2).padStart(4, "0");  // four binary digits with leading zeros
}

console.log("a & b =", a & b, show(a & b));  // AND: 1 only where both are 1
console.log("a | b =", a | b, show(a | b));  // OR: 1 where at least one is 1
console.log("a ^ b =", a ^ b, show(a ^ b));  // XOR: 1 where they differ
console.log("~a =", ~a);                     // NOT flips every bit, which gives -(a + 1)
''', java=r'''
public class BitOps {
    static String show(int x) {
        return String.format("%4s", Integer.toBinaryString(x)).replace(' ', '0');  // four binary digits
    }

    public static void main(String[] args) {
        int a = 12, b = 10;                  // 1100 and 1010 in binary
        System.out.println("a & b = " + (a & b) + " " + show(a & b));  // AND: 1 only where both are 1
        System.out.println("a | b = " + (a | b) + " " + show(a | b));  // OR: 1 where at least one is 1
        System.out.println("a ^ b = " + (a ^ b) + " " + show(a ^ b));  // XOR: 1 where they differ
        System.out.println("~a = " + (~a));                            // NOT flips every bit, which gives -(a + 1)
    }
}
''', ts=r'''
const a: number = 12, b: number = 10;  // 1100 and 1010 in binary

function show(x: number): string {
  return x.toString(2).padStart(4, "0");  // four binary digits with leading zeros
}

console.log("a & b =", a & b, show(a & b));  // AND: 1 only where both are 1
console.log("a | b =", a | b, show(a | b));  // OR: 1 where at least one is 1
console.log("a ^ b =", a ^ b, show(a ^ b));  // XOR: 1 where they differ
console.log("~a =", ~a);                     // NOT flips every bit, which gives -(a + 1)
''')

t.code('shifts', py=r'''
print("5 << 1 =", 5 << 1)      # every bit moves one place left: times 2
print("5 << 3 =", 5 << 3)      # three places left: times 2 * 2 * 2 = 8
print("40 >> 2 =", 40 >> 2)    # two places right: divide by 4, drop the remainder
print("-16 >> 2 =", -16 >> 2)  # an arithmetic shift keeps the sign
print("7 >> 1 =", 7 >> 1)      # the rightmost 1 falls off the edge
''', js=r'''
console.log("5 << 1 =", 5 << 1);      // every bit moves one place left: times 2
console.log("5 << 3 =", 5 << 3);      // three places left: times 2 * 2 * 2 = 8
console.log("40 >> 2 =", 40 >> 2);    // two places right: divide by 4, drop the remainder
console.log("-16 >> 2 =", -16 >> 2);  // an arithmetic shift keeps the sign
console.log("7 >> 1 =", 7 >> 1);      // the rightmost 1 falls off the edge
''', java=r'''
public class Shifts {
    public static void main(String[] args) {
        System.out.println("5 << 1 = " + (5 << 1));      // every bit moves one place left: times 2
        System.out.println("5 << 3 = " + (5 << 3));      // three places left: times 2 * 2 * 2 = 8
        System.out.println("40 >> 2 = " + (40 >> 2));    // two places right: divide by 4, drop the remainder
        System.out.println("-16 >> 2 = " + (-16 >> 2));  // an arithmetic shift keeps the sign
        System.out.println("7 >> 1 = " + (7 >> 1));      // the rightmost 1 falls off the edge
    }
}
''', ts=r'''
const shiftsDemo: Array<[string, number]> = [
  ["5 << 1 =", 5 << 1],      // every bit moves one place left: times 2
  ["5 << 3 =", 5 << 3],      // three places left: times 2 * 2 * 2 = 8
  ["40 >> 2 =", 40 >> 2],    // two places right: divide by 4, drop the remainder
  ["-16 >> 2 =", -16 >> 2],  // an arithmetic shift keeps the sign
  ["7 >> 1 =", 7 >> 1],      // the rightmost 1 falls off the edge
];
for (const [label, value] of shiftsDemo) {
  console.log(label, value);
}
''')

t.code('masks', py=r'''
n = 10                                # 1010 in binary

print("bit 1 is", (n >> 1) & 1)       # check: slide bit 1 to the end, keep only it
print("bit 2 is", (n >> 2) & 1)
print("set bit 2:", n | (1 << 2))     # OR with a mask turns a bit on
print("clear bit 1:", n & ~(1 << 1))  # AND with the flipped mask turns a bit off
print("toggle bit 0:", n ^ (1 << 0))  # XOR with a mask flips a bit
''', js=r'''
const n = 10;                                  // 1010 in binary

console.log("bit 1 is", (n >> 1) & 1);         // check: slide bit 1 to the end, keep only it
console.log("bit 2 is", (n >> 2) & 1);
console.log("set bit 2:", n | (1 << 2));       // OR with a mask turns a bit on
console.log("clear bit 1:", n & ~(1 << 1));    // AND with the flipped mask turns a bit off
console.log("toggle bit 0:", n ^ (1 << 0));    // XOR with a mask flips a bit
''', java=r'''
public class Masks {
    public static void main(String[] args) {
        int n = 10;                                          // 1010 in binary
        System.out.println("bit 1 is " + ((n >> 1) & 1));    // check: slide bit 1 to the end, keep only it
        System.out.println("bit 2 is " + ((n >> 2) & 1));
        System.out.println("set bit 2: " + (n | (1 << 2)));  // OR with a mask turns a bit on
        System.out.println("clear bit 1: " + (n & ~(1 << 1)));  // AND with the flipped mask turns a bit off
        System.out.println("toggle bit 0: " + (n ^ (1 << 0)));  // XOR with a mask flips a bit
    }
}
''', ts=r'''
const n: number = 10;                          // 1010 in binary

console.log("bit 1 is", (n >> 1) & 1);         // check: slide bit 1 to the end, keep only it
console.log("bit 2 is", (n >> 2) & 1);
console.log("set bit 2:", n | (1 << 2));       // OR with a mask turns a bit on
console.log("clear bit 1:", n & ~(1 << 1));    // AND with the flipped mask turns a bit off
console.log("toggle bit 0:", n ^ (1 << 0));    // XOR with a mask flips a bit
''')

t.code('tricks', py=r'''
def count_ones(n):
    count = 0
    while n:
        n = n & (n - 1)              # wipes out the lowest 1 bit
        count += 1
    return count


def power_of_two(n):
    return n > 0 and n & (n - 1) == 0  # exactly one 1 bit


for n in [12, 16, 255]:
    print(n, "has", count_ones(n), "ones, power of two:", "yes" if power_of_two(n) else "no")

print("lowest set bit of 12:", 12 & -12)  # keeps only the lowest 1 bit

x, y = 3, 9
x = x ^ y                            # the XOR swap needs no spare variable
y = x ^ y
x = x ^ y
print("swapped:", x, y)
''', js=r'''
function countOnes(n) {
  let count = 0;
  while (n !== 0) {
    n = n & (n - 1);                 // wipes out the lowest 1 bit
    count++;
  }
  return count;
}

function powerOfTwo(n) {
  return n > 0 && (n & (n - 1)) === 0;  // exactly one 1 bit
}

for (const n of [12, 16, 255]) {
  console.log(n, "has", countOnes(n), "ones, power of two:", powerOfTwo(n) ? "yes" : "no");
}

console.log("lowest set bit of 12:", 12 & -12);  // keeps only the lowest 1 bit

let x = 3, y = 9;
x = x ^ y;                           // the XOR swap needs no spare variable
y = x ^ y;
x = x ^ y;
console.log("swapped:", x, y);
''', java=r'''
public class Tricks {
    static int countOnes(int n) {
        int count = 0;
        while (n != 0) {
            n = n & (n - 1);                 // wipes out the lowest 1 bit
            count++;
        }
        return count;
    }

    static boolean powerOfTwo(int n) {
        return n > 0 && (n & (n - 1)) == 0;  // exactly one 1 bit
    }

    public static void main(String[] args) {
        for (int n : new int[]{12, 16, 255}) {
            System.out.println(n + " has " + countOnes(n) + " ones, power of two: " + (powerOfTwo(n) ? "yes" : "no"));
        }
        System.out.println("lowest set bit of 12: " + (12 & -12));  // keeps only the lowest 1 bit
        int x = 3, y = 9;
        x = x ^ y;                           // the XOR swap needs no spare variable
        y = x ^ y;
        x = x ^ y;
        System.out.println("swapped: " + x + " " + y);
    }
}
''', ts=r'''
function countOnes(n: number): number {
  let count = 0;
  while (n !== 0) {
    n = n & (n - 1);                 // wipes out the lowest 1 bit
    count++;
  }
  return count;
}

function powerOfTwo(n: number): boolean {
  return n > 0 && (n & (n - 1)) === 0;  // exactly one 1 bit
}

for (const n of [12, 16, 255]) {
  console.log(n, "has", countOnes(n), "ones, power of two:", powerOfTwo(n) ? "yes" : "no");
}

console.log("lowest set bit of 12:", 12 & -12);  // keeps only the lowest 1 bit

let x: number = 3, y: number = 9;
x = x ^ y;                           // the XOR swap needs no spare variable
y = x ^ y;
x = x ^ y;
console.log("swapped:", x, y);
''')

t.code('subsets_mask', py=r'''
items = ["a", "b", "c"]
n = len(items)
for mask in range(1 << n):                 # 0 to 2^n - 1, one number per subset
    picked = [items[i] for i in range(n) if mask & (1 << i)]  # bit i says "take item i"
    print(format(mask, "03b"), "{" + ", ".join(picked) + "}")
''', js=r'''
const items = ["a", "b", "c"];
const n = items.length;
for (let mask = 0; mask < (1 << n); mask++) {    // 0 to 2^n - 1, one number per subset
  const picked = [];
  for (let i = 0; i < n; i++) {
    if (mask & (1 << i)) picked.push(items[i]);  // bit i says "take item i"
  }
  console.log(mask.toString(2).padStart(3, "0"), "{" + picked.join(", ") + "}");
}
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class SubsetsMask {
    public static void main(String[] args) {
        String[] items = {"a", "b", "c"};
        int n = items.length;
        for (int mask = 0; mask < (1 << n); mask++) {        // 0 to 2^n - 1, one number per subset
            List<String> picked = new ArrayList<>();
            for (int i = 0; i < n; i++) {
                if ((mask & (1 << i)) != 0) picked.add(items[i]);  // bit i says "take item i"
            }
            String bits = String.format("%3s", Integer.toBinaryString(mask)).replace(' ', '0');
            System.out.println(bits + " {" + String.join(", ", picked) + "}");
        }
    }
}
''', ts=r'''
const items: string[] = ["a", "b", "c"];
const n: number = items.length;
for (let mask = 0; mask < (1 << n); mask++) {    // 0 to 2^n - 1, one number per subset
  const picked: string[] = [];
  for (let i = 0; i < n; i++) {
    if (mask & (1 << i)) picked.push(items[i]);  // bit i says "take item i"
  }
  console.log(mask.toString(2).padStart(3, "0"), "{" + picked.join(", ") + "}");
}
''')

t.code('real_bits', py=r'''
READ, WRITE, RUN = 4, 2, 1             # one bit each: 100, 010, 001
owner = READ | WRITE                   # 6, the "6" in chmod 644
print("owner can write:", "yes" if owner & WRITE else "no")
print("owner can run:", "yes" if owner & RUN else "no")

color = 0xFF8800                       # orange, packed as red, green, blue bytes
r = (color >> 16) & 0xFF
g = (color >> 8) & 0xFF
b = color & 0xFF
print("rgb", r, g, b)
print("packed again:", (r << 16) | (g << 8) | b == color)

ip = [192, 168, 1, 77]
mask = [255, 255, 255, 0]              # a /24 network
net = [ip[i] & mask[i] for i in range(4)]
print("network", ".".join(str(x) for x in net))
''', js=r'''
const READ = 4, WRITE = 2, RUN = 1;    // one bit each: 100, 010, 001
const owner = READ | WRITE;            // 6, the "6" in chmod 644
console.log("owner can write:", owner & WRITE ? "yes" : "no");
console.log("owner can run:", owner & RUN ? "yes" : "no");

const color = 0xFF8800;                // orange, packed as red, green, blue bytes
const r = (color >> 16) & 0xFF;
const g = (color >> 8) & 0xFF;
const b = color & 0xFF;
console.log("rgb", r, g, b);
console.log("packed again:", ((r << 16) | (g << 8) | b) === color ? "True" : "False");

const ip = [192, 168, 1, 77];
const mask = [255, 255, 255, 0];       // a /24 network
const net = ip.map((x, i) => x & mask[i]);
console.log("network", net.join("."));
''', java=r'''
public class RealBits {
    public static void main(String[] args) {
        final int READ = 4, WRITE = 2, RUN = 1;      // one bit each: 100, 010, 001
        int owner = READ | WRITE;                    // 6, the "6" in chmod 644
        System.out.println("owner can write: " + ((owner & WRITE) != 0 ? "yes" : "no"));
        System.out.println("owner can run: " + ((owner & RUN) != 0 ? "yes" : "no"));

        int color = 0xFF8800;                        // orange, packed as red, green, blue bytes
        int r = (color >> 16) & 0xFF;
        int g = (color >> 8) & 0xFF;
        int b = color & 0xFF;
        System.out.println("rgb " + r + " " + g + " " + b);
        System.out.println("packed again: " + (((r << 16) | (g << 8) | b) == color ? "True" : "False"));

        int[] ip = {192, 168, 1, 77};
        int[] mask = {255, 255, 255, 0};             // a /24 network
        StringBuilder net = new StringBuilder();
        for (int i = 0; i < 4; i++) {
            if (i > 0) net.append('.');
            net.append(ip[i] & mask[i]);
        }
        System.out.println("network " + net);
    }
}
''', ts=r'''
const READ = 4, WRITE = 2, RUN = 1;    // one bit each: 100, 010, 001
const owner: number = READ | WRITE;    // 6, the "6" in chmod 644
console.log("owner can write:", owner & WRITE ? "yes" : "no");
console.log("owner can run:", owner & RUN ? "yes" : "no");

const color: number = 0xFF8800;        // orange, packed as red, green, blue bytes
const r: number = (color >> 16) & 0xFF;
const g: number = (color >> 8) & 0xFF;
const b: number = color & 0xFF;
console.log("rgb", r, g, b);
console.log("packed again:", ((r << 16) | (g << 8) | b) === color ? "True" : "False");

const ip: number[] = [192, 168, 1, 77];
const mask: number[] = [255, 255, 255, 0];  // a /24 network
const net: number[] = ip.map((x, i) => x & mask[i]);
console.log("network", net.join("."));
''')

# ---------------------------------------------------------------- LeetCode practice programs
t.code('p_single', py=r'''
def single_number(nums):
    result = 0
    for x in nums:
        result ^= x          # pairs cancel, x ^ x = 0, so only the loner is left
    return result


print(single_number([2, 2, 1]), single_number([4, 1, 2, 1, 2]), single_number([1]))
''', js=r'''
function singleNumber(nums) {
  let result = 0;
  for (const x of nums) {
    result ^= x;             // pairs cancel, x ^ x = 0, so only the loner is left
  }
  return result;
}

console.log(singleNumber([2, 2, 1]), singleNumber([4, 1, 2, 1, 2]), singleNumber([1]));
''', java=r'''
public class SingleNumber {
    static int singleNumber(int[] nums) {
        int result = 0;
        for (int x : nums) {
            result ^= x;     // pairs cancel, x ^ x = 0, so only the loner is left
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println(singleNumber(new int[]{2, 2, 1}) + " " + singleNumber(new int[]{4, 1, 2, 1, 2}) + " " + singleNumber(new int[]{1}));
    }
}
''', ts=r'''
function singleNumber(nums: number[]): number {
  let result = 0;
  for (const x of nums) {
    result ^= x;             // pairs cancel, x ^ x = 0, so only the loner is left
  }
  return result;
}

console.log(singleNumber([2, 2, 1]), singleNumber([4, 1, 2, 1, 2]), singleNumber([1]));
''')

t.code('p_power_two', py=r'''
def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0   # a power of two has exactly one 1 bit


print(" ".join("yes" if is_power_of_two(n) else "no" for n in [1, 16, 3, 0, -16]))
''', js=r'''
function isPowerOfTwo(n) {
  return n > 0 && (n & (n - 1)) === 0;  // a power of two has exactly one 1 bit
}

console.log([1, 16, 3, 0, -16].map(n => (isPowerOfTwo(n) ? "yes" : "no")).join(" "));
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class PowerOfTwo {
    static boolean isPowerOfTwo(int n) {
        return n > 0 && (n & (n - 1)) == 0;  // a power of two has exactly one 1 bit
    }

    public static void main(String[] args) {
        List<String> out = new ArrayList<>();
        for (int n : new int[]{1, 16, 3, 0, -16}) out.add(isPowerOfTwo(n) ? "yes" : "no");
        System.out.println(String.join(" ", out));
    }
}
''', ts=r'''
function isPowerOfTwo(n: number): boolean {
  return n > 0 && (n & (n - 1)) === 0;  // a power of two has exactly one 1 bit
}

console.log([1, 16, 3, 0, -16].map(n => (isPowerOfTwo(n) ? "yes" : "no")).join(" "));
''')

t.code('p_ones', py=r'''
def hamming_weight(n):
    count = 0
    while n:
        n &= n - 1           # each round removes exactly one 1 bit
        count += 1
    return count


print(hamming_weight(11), hamming_weight(128), hamming_weight(2147483645))
''', js=r'''
function hammingWeight(n) {
  let count = 0;
  while (n !== 0) {
    n &= n - 1;              // each round removes exactly one 1 bit
    count++;
  }
  return count;
}

console.log(hammingWeight(11), hammingWeight(128), hammingWeight(2147483645));
''', java=r'''
public class NumberOfOneBits {
    static int hammingWeight(int n) {
        int count = 0;
        while (n != 0) {
            n &= n - 1;      // each round removes exactly one 1 bit
            count++;
        }
        return count;
    }

    public static void main(String[] args) {
        System.out.println(hammingWeight(11) + " " + hammingWeight(128) + " " + hammingWeight(2147483645));
    }
}
''', ts=r'''
function hammingWeight(n: number): number {
  let count = 0;
  while (n !== 0) {
    n &= n - 1;              // each round removes exactly one 1 bit
    count++;
  }
  return count;
}

console.log(hammingWeight(11), hammingWeight(128), hammingWeight(2147483645));
''')

t.code('p_hamming', py=r'''
def hamming_distance(x, y):
    diff = x ^ y             # 1 exactly where the two numbers differ
    count = 0
    while diff:
        diff &= diff - 1
        count += 1
    return count


print(hamming_distance(1, 4), hamming_distance(3, 1), hamming_distance(93, 73))
''', js=r'''
function hammingDistance(x, y) {
  let diff = x ^ y;          // 1 exactly where the two numbers differ
  let count = 0;
  while (diff !== 0) {
    diff &= diff - 1;
    count++;
  }
  return count;
}

console.log(hammingDistance(1, 4), hammingDistance(3, 1), hammingDistance(93, 73));
''', java=r'''
public class HammingDistance {
    static int hammingDistance(int x, int y) {
        int diff = x ^ y;    // 1 exactly where the two numbers differ
        int count = 0;
        while (diff != 0) {
            diff &= diff - 1;
            count++;
        }
        return count;
    }

    public static void main(String[] args) {
        System.out.println(hammingDistance(1, 4) + " " + hammingDistance(3, 1) + " " + hammingDistance(93, 73));
    }
}
''', ts=r'''
function hammingDistance(x: number, y: number): number {
  let diff = x ^ y;          // 1 exactly where the two numbers differ
  let count = 0;
  while (diff !== 0) {
    diff &= diff - 1;
    count++;
  }
  return count;
}

console.log(hammingDistance(1, 4), hammingDistance(3, 1), hammingDistance(93, 73));
''')

t.code('p_count_bits', py=r'''
def count_bits(n):
    ans = [0] * (n + 1)
    for i in range(1, n + 1):
        ans[i] = ans[i >> 1] + (i & 1)   # i has the bits of i // 2, plus its last bit
    return ans


print(" ".join(str(x) for x in count_bits(5)))
print(" ".join(str(x) for x in count_bits(8)))
''', js=r'''
function countBits(n) {
  const ans = new Array(n + 1).fill(0);
  for (let i = 1; i <= n; i++) {
    ans[i] = ans[i >> 1] + (i & 1);      // i has the bits of i / 2, plus its last bit
  }
  return ans;
}

console.log(countBits(5).join(" "));
console.log(countBits(8).join(" "));
''', java=r'''
public class CountingBits {
    static int[] countBits(int n) {
        int[] ans = new int[n + 1];
        for (int i = 1; i <= n; i++) {
            ans[i] = ans[i >> 1] + (i & 1);  // i has the bits of i / 2, plus its last bit
        }
        return ans;
    }

    static String join(int[] a) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < a.length; i++) sb.append(i > 0 ? " " : "").append(a[i]);
        return sb.toString();
    }

    public static void main(String[] args) {
        System.out.println(join(countBits(5)));
        System.out.println(join(countBits(8)));
    }
}
''', ts=r'''
function countBits(n: number): number[] {
  const ans: number[] = new Array(n + 1).fill(0);
  for (let i = 1; i <= n; i++) {
    ans[i] = ans[i >> 1] + (i & 1);      // i has the bits of i / 2, plus its last bit
  }
  return ans;
}

console.log(countBits(5).join(" "));
console.log(countBits(8).join(" "));
''')

t.code('p_subsets', py=r'''
def subsets(nums):
    n = len(nums)
    out = []
    for mask in range(1 << n):           # every number from 0 to 2^n - 1 is one subset
        out.append([nums[i] for i in range(n) if mask >> i & 1])
    return out


print(" ".join("[" + ",".join(str(x) for x in s) + "]" for s in subsets([1, 2, 3])))
''', js=r'''
function subsets(nums) {
  const n = nums.length, out = [];
  for (let mask = 0; mask < (1 << n); mask++) {  // every number from 0 to 2^n - 1 is one subset
    const s = [];
    for (let i = 0; i < n; i++) if ((mask >> i) & 1) s.push(nums[i]);
    out.push(s);
  }
  return out;
}

console.log(subsets([1, 2, 3]).map(s => "[" + s.join(",") + "]").join(" "));
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class Subsets {
    static List<List<Integer>> subsets(int[] nums) {
        int n = nums.length;
        List<List<Integer>> out = new ArrayList<>();
        for (int mask = 0; mask < (1 << n); mask++) {  // every number from 0 to 2^n - 1 is one subset
            List<Integer> s = new ArrayList<>();
            for (int i = 0; i < n; i++) if (((mask >> i) & 1) == 1) s.add(nums[i]);
            out.add(s);
        }
        return out;
    }

    public static void main(String[] args) {
        List<String> parts = new ArrayList<>();
        for (List<Integer> s : subsets(new int[]{1, 2, 3})) {
            List<String> xs = new ArrayList<>();
            for (int x : s) xs.add(String.valueOf(x));
            parts.add("[" + String.join(",", xs) + "]");
        }
        System.out.println(String.join(" ", parts));
    }
}
''', ts=r'''
function subsets(nums: number[]): number[][] {
  const n = nums.length, out: number[][] = [];
  for (let mask = 0; mask < (1 << n); mask++) {  // every number from 0 to 2^n - 1 is one subset
    const s: number[] = [];
    for (let i = 0; i < n; i++) if ((mask >> i) & 1) s.push(nums[i]);
    out.push(s);
  }
  return out;
}

console.log(subsets([1, 2, 3]).map(s => "[" + s.join(",") + "]").join(" "));
''')

t.code('p_gray', py=r'''
def gray_code(n):
    return [i ^ (i >> 1) for i in range(1 << n)]   # neighbours differ in exactly one bit


print(" ".join(str(x) for x in gray_code(2)))
print(" ".join(str(x) for x in gray_code(3)))
''', js=r'''
function grayCode(n) {
  const out = [];
  for (let i = 0; i < (1 << n); i++) out.push(i ^ (i >> 1));  // neighbours differ in exactly one bit
  return out;
}

console.log(grayCode(2).join(" "));
console.log(grayCode(3).join(" "));
''', java=r'''
import java.util.ArrayList;
import java.util.List;

public class GrayCode {
    static List<Integer> grayCode(int n) {
        List<Integer> out = new ArrayList<>();
        for (int i = 0; i < (1 << n); i++) out.add(i ^ (i >> 1));  // neighbours differ in exactly one bit
        return out;
    }

    static String join(List<Integer> a) {
        List<String> s = new ArrayList<>();
        for (int x : a) s.add(String.valueOf(x));
        return String.join(" ", s);
    }

    public static void main(String[] args) {
        System.out.println(join(grayCode(2)));
        System.out.println(join(grayCode(3)));
    }
}
''', ts=r'''
function grayCode(n: number): number[] {
  const out: number[] = [];
  for (let i = 0; i < (1 << n); i++) out.push(i ^ (i >> 1));  // neighbours differ in exactly one bit
  return out;
}

console.log(grayCode(2).join(" "));
console.log(grayCode(3).join(" "));
''')

t.code('p_max_xor', py=r'''
def find_maximum_xor(nums):
    best = 0
    mask = 0
    for bit in range(30, -1, -1):            # decide the answer one bit at a time, from the top
        mask |= 1 << bit
        prefixes = {x & mask for x in nums}  # the top bits of every number
        want = best | (1 << bit)             # can this bit be 1 as well?
        if any((want ^ p) in prefixes for p in prefixes):  # a ^ b = want means a ^ want = b
            best = want
    return best


print(find_maximum_xor([3, 10, 5, 25, 2, 8]))
print(find_maximum_xor([14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70]))
''', js=r'''
function findMaximumXOR(nums) {
  let best = 0, mask = 0;
  for (let bit = 30; bit >= 0; bit--) {      // decide the answer one bit at a time, from the top
    mask |= 1 << bit;
    const prefixes = new Set(nums.map(x => x & mask));  // the top bits of every number
    const want = best | (1 << bit);          // can this bit be 1 as well?
    for (const p of prefixes) {
      if (prefixes.has(want ^ p)) { best = want; break; }  // a ^ b = want means a ^ want = b
    }
  }
  return best;
}

console.log(findMaximumXOR([3, 10, 5, 25, 2, 8]));
console.log(findMaximumXOR([14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70]));
''', java=r'''
import java.util.HashSet;
import java.util.Set;

public class MaximumXor {
    static int findMaximumXOR(int[] nums) {
        int best = 0, mask = 0;
        for (int bit = 30; bit >= 0; bit--) {        // decide the answer one bit at a time, from the top
            mask |= 1 << bit;
            Set<Integer> prefixes = new HashSet<>();
            for (int x : nums) prefixes.add(x & mask);  // the top bits of every number
            int want = best | (1 << bit);            // can this bit be 1 as well?
            for (int p : prefixes) {
                if (prefixes.contains(want ^ p)) { best = want; break; }  // a ^ b = want means a ^ want = b
            }
        }
        return best;
    }

    public static void main(String[] args) {
        System.out.println(findMaximumXOR(new int[]{3, 10, 5, 25, 2, 8}));
        System.out.println(findMaximumXOR(new int[]{14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70}));
    }
}
''', ts=r'''
function findMaximumXOR(nums: number[]): number {
  let best = 0, mask = 0;
  for (let bit = 30; bit >= 0; bit--) {      // decide the answer one bit at a time, from the top
    mask |= 1 << bit;
    const prefixes = new Set<number>(nums.map(x => x & mask));  // the top bits of every number
    const want = best | (1 << bit);          // can this bit be 1 as well?
    for (const p of prefixes) {
      if (prefixes.has(want ^ p)) { best = want; break; }  // a ^ b = want means a ^ want = b
    }
  }
  return best;
}

console.log(findMaximumXOR([3, 10, 5, 25, 2, 8]));
console.log(findMaximumXOR([14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70]));
''')

t.leet(136, 'e', 'p_single',
       statement='<p>Every number in the list appears twice except one. Find the one that appears only once, in linear time and with constant extra memory.</p>',
       example='[2, 2, 1]        →  1\n[4, 1, 2, 1, 2]  →  4\n[1]              →  1',
       hint='What is x ^ x, and what is x ^ 0?',
       approach='<p>XOR every number into one total. Equal numbers cancel because <code>x ^ x = 0</code>, and the order does not matter because XOR is commutative and associative. Only the single number survives, because <code>x ^ 0 = x</code>.</p>',
       time='O(n)', space='O(1)')
t.leet(231, 'e', 'p_power_two',
       statement='<p>Given an integer n, say whether it is a power of two, such as 1, 2, 4, 8 and 16.</p>',
       example='1  → yes    16 → yes    3 → no\n0  → no     -16 → no',
       hint='Write a few powers of two in binary. How many 1 bits do they have?',
       approach='<p>A power of two has exactly one 1 bit. Subtracting 1 turns that bit off and every bit below it on, so <code>n &amp; (n - 1)</code> is zero only for powers of two. Zero and negative numbers are never powers of two, so check <code>n &gt; 0</code> first.</p>',
       time='O(1)', space='O(1)')
t.leet(191, 'm', 'p_ones',
       statement='<p>Count how many 1 bits an unsigned integer has. This count is called the Hamming weight or the population count.</p>',
       example='11 (1011)          →  3\n128 (10000000)     →  1\n2147483645         →  30',
       hint='n &amp; (n - 1) removes the lowest 1 bit. Count how many times you can do it.',
       approach='<p>Brian Kernighan\'s trick: each <code>n &amp;= n - 1</code> wipes out exactly one 1 bit, so the loop runs once per 1 bit instead of once per bit. Python has <code>bin(n).count("1")</code> and <code>int.bit_count()</code>, Java has <code>Integer.bitCount</code>.</p>',
       time='O(number of 1 bits)', space='O(1)')
t.leet(461, 'm', 'p_hamming',
       statement='<p>The Hamming distance between two integers is the number of bit positions where they differ. Return it for x and y.</p>',
       example='x = 1 (0001), y = 4 (0100)  →  2\nx = 3, y = 1                →  1',
       hint='Which operator marks exactly the places where two bits differ?',
       approach='<p>XOR puts a 1 exactly where the bits differ. Count the 1 bits of <code>x ^ y</code> with Kernighan\'s loop. The same idea measures how many bits flipped when data is sent over a noisy cable.</p>',
       time='O(1) for 32 bit numbers', space='O(1)')
t.leet(338, 'h', 'p_count_bits',
       statement='<p>For every i from 0 to n, return how many 1 bits i has, as a list of n + 1 numbers. Try to do it in one pass without counting each number from scratch.</p>',
       example='n = 5  →  0 1 1 2 1 2',
       hint='i >> 1 is i without its last bit, and you already know its answer.',
       approach='<p>Dynamic programming over bits. Shifting i right drops its last bit, and that smaller number was already solved. So <code>ans[i] = ans[i &gt;&gt; 1] + (i &amp; 1)</code>. Each answer costs one step.</p>',
       time='O(n)', space='O(n) for the answer')
t.leet(78, 'h', 'p_subsets',
       statement='<p>Return every subset of a list of distinct numbers. The order of the subsets does not matter.</p>',
       example='[1, 2, 3]  →  [] [1] [2] [1,2] [3] [1,3] [2,3] [1,2,3]',
       hint='With n items there are 2^n subsets, and also 2^n numbers from 0 to 2^n - 1.',
       approach='<p>Let bit i of a number decide whether item i is in the subset. Counting from 0 to 2^n - 1 then visits every yes or no pattern exactly once. The Backtracking chapter solves the same problem with a recursive take it or leave it choice.</p>',
       time='O(n · 2^n)', space='O(n · 2^n) for the answer')
t.leet(89, 'x', 'p_gray',
       statement='<p>Return an n bit Gray code sequence: all 2^n numbers, starting at 0, where every two neighbours differ in exactly one bit.</p>',
       example='n = 2  →  0 1 3 2\nn = 3  →  0 1 3 2 6 7 5 4',
       hint='Try i ^ (i >> 1) for i = 0, 1, 2, 3 and look at the bits.',
       approach='<p>The i-th Gray code is <code>i ^ (i &gt;&gt; 1)</code>. Moving from i to i + 1 changes a run of low bits, and the XOR with the shifted copy cancels all of that run except one bit. Rotary encoders in car steering columns and old radio dials use Gray code so a half turned knob is never misread by more than one step.</p>',
       time='O(2^n)', space='O(2^n) for the answer')
t.leet(421, 'x', 'p_max_xor',
       statement='<p>Given a list of non negative integers, return the largest value of <code>a ^ b</code> over any two of them.</p>',
       example='[3, 10, 5, 25, 2, 8]  →  28   (5 ^ 25)',
       hint='Build the answer from the highest bit down. For each bit, ask whether some pair can make it 1 while keeping the bits already chosen.',
       approach='<p>Greedy on bits. Keep the best answer so far and try to add the next lower bit. Collect the top bits of every number in a set. If <code>a ^ b = want</code> then <code>a ^ want = b</code>, so one set lookup per prefix tells whether the bit can be 1. A binary trie of the numbers gives the same answer and is shown in the Tries lesson of the Trees chapter.</p>',
       time='O(31 · n)', space='O(n)')

# ---------------------------------------------------------------- lessons
PARTS = [
    dict(id='binary', emoji='💡', title='Binary: counting with light switches', html='''
<p>A computer stores everything as tiny switches that are either <b>off (0)</b> or <b>on (1)</b>. One switch is a <b>bit</b>. Eight bits make a <b>byte</b>. With only two digits, each place is worth twice the place to its right: 1, 2, 4, 8, 16 and so on, just as each place in normal numbers is worth ten times the next.</p>
<div class="tw"><table class="jt"><tr><th>Place value</th><th>128</th><th>64</th><th>32</th><th>16</th><th>8</th><th>4</th><th>2</th><th>1</th><th>Total</th></tr>
<tr><td>13</td><td>0</td><td>0</td><td>0</td><td>0</td><td>1</td><td>1</td><td>0</td><td>1</td><td>8 + 4 + 1 = 13</td></tr>
<tr><td>200</td><td>1</td><td>1</td><td>0</td><td>0</td><td>1</td><td>0</td><td>0</td><td>0</td><td>128 + 64 + 8 = 200</td></tr></table></div>
<p>To turn a number into binary, keep dividing by 2. Each remainder is the next bit from the right. To turn binary back, read the bits from the left and do <code>value = value × 2 + bit</code>.</p>
<div class="viz" data-viz="pk" data-pk="binary"></div>
<div class="c3" data-k="to_binary" data-label="Decimal to binary and back"></div>
<div class="grid2">
<div class="box"><h4>🔢 How big can it get</h4><p>n bits can count from 0 to 2<sup>n</sup> − 1. A byte holds 0 to 255. A 32 bit int holds about 4.3 billion patterns, which is why old systems ran out of IPv4 addresses.</p></div>
<div class="box"><h4>➖ Negative numbers</h4><p>Java, JavaScript bit operators and most CPUs use <b>two's complement</b>: to make −x, flip every bit of x and add 1. The top bit then works as the sign. Python integers have no fixed width but behave as if they had endless sign bits.</p></div>
</div>
<div class="rule">Hex is just binary in groups of four: each hex digit is exactly four bits. 0xFF is 1111 1111, which is 255.</div>
'''),
    dict(id='operators', emoji='🔀', title='AND, OR, XOR and NOT', html='''
<p>Bitwise operators work on every pair of bits in the same place, all at once. Picture two rows of light switches lined up, and a rule that decides each result switch.</p>
<div class="tw"><table class="jt"><tr><th>a</th><th>b</th><th>a &amp; b (AND)</th><th>a | b (OR)</th><th>a ^ b (XOR)</th></tr>
<tr><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr><tr><td>0</td><td>1</td><td>0</td><td>1</td><td>1</td></tr>
<tr><td>1</td><td>0</td><td>0</td><td>1</td><td>1</td></tr><tr><td>1</td><td>1</td><td>1</td><td>1</td><td>0</td></tr></table></div>
<p><b>AND</b> is strict: both must agree on 1. <b>OR</b> is generous: one 1 is enough. <b>XOR</b> (exclusive or) asks "are they different". <b>NOT</b> (<code>~</code>) flips every bit, and in two's complement <code>~x</code> equals <code>−x − 1</code>.</p>
<div class="viz" data-viz="pk" data-pk="bitops"></div>
<div class="c3" data-k="bit_ops" data-label="The four bitwise operators"></div>
<div class="grid2">
<div class="box"><h4>✨ XOR superpowers</h4><p><code>x ^ x = 0</code>, <code>x ^ 0 = x</code>, and the order never matters. That is why XOR finds a lonely number among pairs and why simple ciphers use it: XOR with a key hides the data, and XOR with the same key again brings it back.</p></div>
<div class="box"><h4>⚠️ Not the same as and, or</h4><p><code>&amp;&amp;</code>, <code>||</code> and Python's <code>and</code>, <code>or</code> work on true or false and can skip the right side. <code>&amp;</code> and <code>|</code> always work bit by bit on numbers.</p></div>
</div>
<div class="warn">Precedence trap: in Java, JavaScript and C, <code>x &amp; 1 == 0</code> means <code>x &amp; (1 == 0)</code>. Always write <code>(x &amp; 1) == 0</code>.</div>
'''),
    dict(id='shifts', emoji='⏩', title='Shifts: sliding every bit', html='''
<p>A <b>left shift</b> <code>x &lt;&lt; k</code> slides every bit k places to the left and fills the gap with zeros. Each place left doubles the value, so <code>x &lt;&lt; k</code> is <code>x × 2<sup>k</sup></code>. A <b>right shift</b> <code>x &gt;&gt; k</code> slides bits to the right and the rightmost bits fall off, which is <code>x ÷ 2<sup>k</sup></code> rounded down.</p>
<div class="viz" data-viz="pk" data-pk="shift"></div>
<div class="c3" data-k="shifts" data-label="Left and right shifts"></div>
<div class="tw"><table class="jt"><tr><th>Shift</th><th>Python</th><th>JavaScript</th><th>Java</th></tr>
<tr><td>Left</td><td><code>&lt;&lt;</code>, grows forever</td><td><code>&lt;&lt;</code> on 32 bits</td><td><code>&lt;&lt;</code> on 32 or 64 bits</td></tr>
<tr><td>Right, keeps the sign</td><td><code>&gt;&gt;</code></td><td><code>&gt;&gt;</code></td><td><code>&gt;&gt;</code></td></tr>
<tr><td>Right, fills with zeros</td><td>none, mask first</td><td><code>&gt;&gt;&gt;</code></td><td><code>&gt;&gt;&gt;</code></td></tr></table></div>
<div class="exam">In Java and JavaScript a 32 bit shift uses only the low 5 bits of k, so <code>1 &lt;&lt; 32</code> is 1, not 0. In JavaScript every bit operator first turns the number into a 32 bit signed int, so <code>2 ** 31 | 0</code> is negative. Use BigInt for wider values.</div>
'''),
    dict(id='masks', emoji='🎭', title='Masks: check, set, clear and toggle one bit', html='''
<p>A <b>mask</b> is a number with 1s only where you want to act. <code>1 &lt;&lt; k</code> is a mask with a single 1 at position k (counted from 0 on the right). With one mask and one operator you can do four jobs.</p>
<div class="tw"><table class="jt"><tr><th>Job</th><th>Code</th><th>Why it works</th></tr>
<tr><td>Check bit k</td><td><code>(n &gt;&gt; k) &amp; 1</code></td><td>slide bit k to the end and keep only it</td></tr>
<tr><td>Set bit k</td><td><code>n | (1 &lt;&lt; k)</code></td><td>OR with 1 is always 1</td></tr>
<tr><td>Clear bit k</td><td><code>n &amp; ~(1 &lt;&lt; k)</code></td><td>AND with 0 is always 0</td></tr>
<tr><td>Toggle bit k</td><td><code>n ^ (1 &lt;&lt; k)</code></td><td>XOR with 1 flips</td></tr></table></div>
<div class="viz" data-viz="pk" data-pk="mask"></div>
<div class="c3" data-k="masks" data-label="Working on one bit at a time"></div>
<p>Masks pack many yes or no flags into one number. A game can store which of 32 achievements you unlocked in a single int, and a database can test a whole set of options with one AND.</p>
'''),
    dict(id='tricks', emoji='🪄', title='Famous bit tricks', html='''
<p>A few one line tricks show up again and again in interviews and in fast code. The star of the show is <code>n &amp; (n − 1)</code>. Subtracting 1 turns the lowest 1 bit off and every 0 below it on, so the AND wipes out exactly that lowest 1 bit.</p>
<div class="tw"><table class="jt"><tr><th>Trick</th><th>Code</th><th>Example with 12 (1100)</th></tr>
<tr><td>Remove the lowest 1 bit</td><td><code>n &amp; (n − 1)</code></td><td>1000 = 8</td></tr>
<tr><td>Keep only the lowest 1 bit</td><td><code>n &amp; −n</code></td><td>0100 = 4</td></tr>
<tr><td>Is it a power of two</td><td><code>n &gt; 0 and n &amp; (n − 1) == 0</code></td><td>no</td></tr>
<tr><td>Is it odd</td><td><code>n &amp; 1</code></td><td>0, so even</td></tr>
<tr><td>Swap without a spare</td><td><code>x ^= y, y ^= x, x ^= y</code></td><td>works, but a temp variable is clearer</td></tr></table></div>
<div class="viz" data-viz="pk" data-pk="kernighan"></div>
<div class="c3" data-k="tricks" data-label="Counting ones, powers of two and the XOR swap"></div>
<div class="box"><h4>🌳 Where <code>n &amp; −n</code> lives</h4><p>The Fenwick tree in the Arrays chapter jumps from index i to <code>i + (i &amp; −i)</code>. That single trick gives it O(log n) prefix sums.</p></div>
'''),
    dict(id='subsets', emoji='🎒', title='Subsets as bitmasks', html='''
<p>Packing for a trip with 3 items: for each item you either take it or leave it. That is 2 × 2 × 2 = 8 choices, the same as the 8 numbers from 0 to 7. If bit i is 1, item i goes in the bag. Counting from 0 to 2<sup>n</sup> − 1 visits every possible bag exactly once.</p>
<div class="viz" data-viz="pk" data-pk="subsets"></div>
<div class="c3" data-k="subsets_mask" data-label="Every subset from a counter"></div>
<div class="grid2">
<div class="box"><h4>📈 It grows fast</h4><p>2<sup>n</sup> doubles with every item. 20 items give about a million subsets, which is fine. 40 items give a trillion, which is not.</p></div>
<div class="box"><h4>🧭 Bitmask dynamic programming</h4><p>The travelling salesman for up to about 20 cities stores "which cities are visited" as a mask. The Dynamic programming part 2 chapter builds it.</p></div>
</div>
'''),
    dict(id='real-bits', emoji='🛰️', title='Bits in everyday systems', html='''
<p>Bits are not only an interview topic. They run quietly inside the tools you use every day.</p>
<div class="grid2">
<div class="box"><h4>🔐 File permissions</h4><p>On Linux and macOS, <code>chmod 755</code> is three groups of three bits: read is 4, write is 2, run is 1. 7 = 4 + 2 + 1 gives the owner everything, 5 = 4 + 1 lets everyone else read and run but not write.</p></div>
<div class="box"><h4>🎨 Colours</h4><p>The web colour <code>#FF8800</code> packs red, green and blue into one 24 bit number. Shifting right by 16 and masking with 0xFF pulls the red byte back out.</p></div>
<div class="box"><h4>🌐 Networks</h4><p>A router ANDs your IP address with the subnet mask to find your network. 192.168.1.77 AND 255.255.255.0 is 192.168.1.0, so it knows the device is on the home network.</p></div>
<div class="box"><h4>🚩 Feature flags</h4><p>Operating systems and game engines pass options as OR-ed flags, such as <code>O_CREAT | O_WRONLY</code> when opening a file in C.</p></div>
</div>
<div class="viz" data-viz="pk" data-pk="perm"></div>
<div class="c3" data-k="real_bits" data-label="Permissions, colours and network masks"></div>
'''),
    dict(id='leetcode', emoji='🏆', title='LeetCode problems in this chapter', html='''
<p>Each problem below is solved in the Practice section with code in Python, JavaScript, Java and TypeScript that you can run line by line. Where the site already has a Python solution in another subject, the problem links to that file as well.</p>
<div class="tw"><table class="jt lc-table"><tr><th>LeetCode</th><th>Level here</th><th>The bit idea</th></tr>
<tr><td><a href="#lc136">136. Single Number</a></td><td>Easy</td><td>XOR cancels pairs</td></tr>
<tr><td><a href="#lc231">231. Power of Two</a></td><td>Easy</td><td><code>n &amp; (n − 1)</code></td></tr>
<tr><td><a href="#lc191">191. Number of 1 Bits</a></td><td>Medium</td><td>Kernighan's loop</td></tr>
<tr><td><a href="#lc461">461. Hamming Distance</a></td><td>Medium</td><td>XOR, then count</td></tr>
<tr><td><a href="#lc338">338. Counting Bits</a></td><td>Hard</td><td>reuse the answer for i &gt;&gt; 1</td></tr>
<tr><td><a href="#lc78">78. Subsets</a></td><td>Hard</td><td>a counter as a bag of choices</td></tr>
<tr><td><a href="#lc89">89. Gray Code</a></td><td>Expert</td><td><code>i ^ (i &gt;&gt; 1)</code></td></tr>
<tr><td><a href="#lc421">421. Maximum XOR of Two Numbers</a></td><td>Expert</td><td>greedy from the top bit</td></tr></table></div>
'''),
]

# ---------------------------------------------------------------- playful animations
VIZ_JS = r'''
(() => {
  const D = PK.defs;
  const bin = (v, n) => (v >>> 0).toString(2).padStart(n, '0').slice(-n);
  const bitsCls = (n, f) => { const c = {}; for (let b = 0; b < n; b++) { const x = f(b); if (x) c[b] = x; } return c; };

  D.binary = el => PK.widget(el, {
    title: 'Watch a number turn into bits', sub: 'Type any whole number from 0 to 255. Pip keeps dividing by 2 and collects the remainders.',
    inputs: [{ k: 'n', label: 'Number', type: 'num', val: 13, min: 0, max: 255 }],
    random: () => ({ n: Math.floor(Math.random() * 256) }),
    check: v => (Number.isInteger(v.n) && v.n >= 0 && v.n <= 255) ? '' : 'Please give me a whole number from 0 to 255. Bigger numbers need more than one byte.',
    frames: ({ n }) => {
      const F = [], rem = [];
      let x = n;
      F.push({ mood: 'think', msg: `Let us turn <b>${n}</b> into binary. Each step divides by 2, and the remainder becomes the next bit from the right.`, layers: [{ t: 'note', html: `Start with <b>${n}</b>` }] });
      if (x === 0) rem.push(0);
      while (x > 0) {
        const r = x % 2, q = Math.floor(x / 2);
        rem.unshift(r);
        F.push({ mood: 'work', msg: `${x} divided by 2 is ${q}, remainder <b>${r}</b>. ${r ? 'Odd number, so this bit is on.' : 'Even number, so this bit is off.'}`,
          vars: { n: x, 'n // 2': q, remainder: r },
          layers: [{ t: 'row', label: 'Bits collected so far, newest on the left', cells: rem.slice(), cls: { 0: r ? 'yes' : 'cur' }, idx: false }] });
        x = q;
      }
      F.push({ mood: 'happy', fx: 'burst', msg: `Done. <b>${n}</b> is <b>${rem.join('')}</b> in binary. Each lit switch adds its place value.`,
        layers: [{ t: 'bits', label: 'The byte', v: n, n: 8, cls: bitsCls(8, b => (n >> b) & 1 ? 'yes' : '') },
                 { t: 'note', html: (n ? [7, 6, 5, 4, 3, 2, 1, 0].filter(b => (n >> b) & 1).map(b => 2 ** b).join(' + ') : '0') + ` = <b>${n}</b>` }] });
      return F;
    }
  });

  D.bitops = el => PK.widget(el, {
    title: 'Bit by bit: AND, OR and XOR', sub: 'Pick two numbers from 0 to 255 and an operator. Pip compares one column of switches at a time.',
    inputs: [{ k: 'a', label: 'a', type: 'num', val: 12, min: 0, max: 255 }, { k: 'b', label: 'b', type: 'num', val: 10, min: 0, max: 255 },
             { k: 'op', label: 'Operator', type: 'seg', val: '&', opts: [['&', 'AND &'], ['|', 'OR |'], ['^', 'XOR ^']] }],
    random: () => ({ a: Math.floor(Math.random() * 256), b: Math.floor(Math.random() * 256) }),
    check: v => [v.a, v.b].every(x => Number.isInteger(x) && x >= 0 && x <= 255) ? '' : 'Both numbers must be whole numbers from 0 to 255.',
    frames: ({ a, b, op }) => {
      const f = { '&': (x, y) => x & y, '|': (x, y) => x | y, '^': (x, y) => x ^ y }[op];
      const rule = { '&': 'AND gives 1 only when both bits are 1.', '|': 'OR gives 1 when at least one bit is 1.', '^': 'XOR gives 1 when the bits are different.' }[op];
      const F = [{ mood: 'think', msg: `${rule} Let us go column by column from the left.`, layers: [{ t: 'bits', name: 'a', v: a, n: 8 }, { t: 'bits', name: 'b', v: b, n: 8 }, { t: 'bits', name: 'a ' + op + ' b', v: 0, n: 8 }] }];
      let res = 0;
      for (let k = 7; k >= 0; k--) {
        const x = (a >> k) & 1, y = (b >> k) & 1, r = f(x, y);
        res |= r << k;
        const mask = res >> k << k;
        F.push({ mood: r ? 'happy' : 'look', msg: `Column worth ${2 ** k}: ${x} ${op} ${y} = <b>${r}</b>. ${r ? 'The result switch turns on.' : 'The result switch stays off.'}`,
          layers: [{ t: 'bits', name: 'a', v: a, n: 8, cls: { [k]: 'look' } }, { t: 'bits', name: 'b', v: b, n: 8, cls: { [k]: 'look' } },
                   { t: 'bits', name: 'a ' + op + ' b', v: mask, n: 8, cls: { [k]: r ? 'yes' : 'no' } }] });
      }
      F.push({ mood: 'wow', fx: 'burst', msg: `${a} ${op} ${b} = <b>${res}</b>, which is ${bin(res, 8)} in binary. All eight columns were really done at once by the CPU, in a single step.`,
        layers: [{ t: 'bits', name: 'a', v: a, n: 8 }, { t: 'bits', name: 'b', v: b, n: 8 }, { t: 'bits', name: 'a ' + op + ' b', v: res, n: 8, cls: bitsCls(8, q => (res >> q) & 1 ? 'yes' : '') }] });
      return F;
    }
  });

  D.shift = el => PK.widget(el, {
    title: 'Slide the switches', sub: 'Shift a number left or right one place at a time and watch the value double or halve.',
    inputs: [{ k: 'n', label: 'Number', type: 'num', val: 13, min: 0, max: 255 }, { k: 'k', label: 'Places', type: 'num', val: 3, min: 1, max: 4 },
             { k: 'd', label: 'Direction', type: 'seg', val: '<<', opts: [['<<', '⬅️ left <<'], ['>>', 'right >> ➡️']] }],
    check: v => (Number.isInteger(v.n) && v.n >= 0 && v.n <= 255 && Number.isInteger(v.k) && v.k >= 1 && v.k <= 4) ? '' : 'Use a number from 0 to 255 and 1 to 4 places.',
    frames: ({ n, k, d }) => {
      const W2 = 12, F = [{ mood: 'think', msg: `Start with <b>${n}</b>. ${d === '<<' ? 'Each step left doubles it, and a 0 slides in on the right.' : 'Each step right halves it, and the rightmost bit falls off the edge.'}`, layers: [{ t: 'bits', v: n, n: W2, cls: bitsCls(W2, b => (n >> b) & 1 ? 'cur' : '') }] }];
      let x = n;
      for (let s = 1; s <= k; s++) {
        const lost = x & 1;
        x = d === '<<' ? x << 1 : x >> 1;
        F.push({ mood: d === '>>' && lost ? 'sad' : 'work', fx: d === '>>' && lost ? 'shake' : '',
          msg: d === '<<' ? `Shift ${s}: every bit moves one place left. ${n} × ${2 ** s} = <b>${x}</b>.` : `Shift ${s}: every bit moves one place right. ${lost ? 'A 1 fell off the edge, so we lose a half. Bye bye, little bit.' : 'Only a 0 fell off, nothing lost.'} Now it is <b>${x}</b>.`,
          vars: { step: s, value: x },
          layers: [{ t: 'bits', v: x, n: W2, cls: bitsCls(W2, b => (x >> b) & 1 ? (d === '<<' ? (b === s - 1 + 0 ? '' : 'cur') : 'cur') : '') }] });
      }
      F.push({ mood: 'happy', fx: 'burst', msg: d === '<<' ? `${n} &lt;&lt; ${k} = <b>${x}</b>, the same as ${n} × 2<sup>${k}</sup>.` : `${n} &gt;&gt; ${k} = <b>${x}</b>, the same as ${n} divided by 2<sup>${k}</sup>, rounded down.`,
        say: d === '<<' ? `${n} shifted left by ${k} is ${x}, the same as ${n} times 2 to the power ${k}.` : `${n} shifted right by ${k} is ${x}, the same as ${n} divided by 2 to the power ${k}, rounded down.`,
        layers: [{ t: 'bits', v: x, n: W2, cls: bitsCls(W2, b => (x >> b) & 1 ? 'yes' : '') }] });
      return F;
    }
  });

  D.mask = el => PK.widget(el, {
    title: 'One bit at a time with a mask', sub: 'Choose a number, a bit position and a job. Pip builds the mask 1 << k and applies it.',
    inputs: [{ k: 'n', label: 'Number', type: 'num', val: 10, min: 0, max: 255 }, { k: 'k', label: 'Bit k', type: 'num', val: 2, min: 0, max: 7 },
             { k: 'op', label: 'Job', type: 'seg', val: 'check', opts: [['check', '🔍 Check'], ['set', '💡 Set'], ['clear', '🌑 Clear'], ['toggle', '🔄 Toggle']] }],
    random: () => ({ n: Math.floor(Math.random() * 256), k: Math.floor(Math.random() * 8) }),
    check: v => (Number.isInteger(v.n) && v.n >= 0 && v.n <= 255 && Number.isInteger(v.k) && v.k >= 0 && v.k <= 7) ? '' : 'Use a number from 0 to 255 and a bit position from 0 to 7.',
    frames: ({ n, k, op }) => {
      const m = 1 << k, on = (n >> k) & 1;
      const F = [{ mood: 'think', msg: `Bit positions count from 0 on the right. Bit ${k} is worth ${m}. First build the mask: 1 shifted left ${k} times.`, layers: [{ t: 'bits', name: 'n', v: n, n: 8, cls: { [k]: 'look' } }, { t: 'bits', name: '1<<' + k, v: m, n: 8, cls: { [k]: 'cur' } }] }];
      if (op === 'check') {
        F.push({ mood: 'look', msg: `Slide bit ${k} to the far right with n &gt;&gt; ${k}, then AND with 1 to keep only that bit.`, layers: [{ t: 'bits', name: 'n>>' + k, v: n >> k, n: 8, cls: { 0: 'look' } }, { t: 'bits', name: '1', v: 1, n: 8, cls: { 0: 'cur' } }] });
        F.push(on ? { mood: 'happy', fx: 'burst', msg: `The answer is <b>1</b>. Bit ${k} of ${n} is switched on.`, layers: [{ t: 'bits', name: 'n', v: n, n: 8, cls: { [k]: 'yes' } }] }
                  : { mood: 'sad', fx: 'shake', msg: `The answer is <b>0</b>. Bit ${k} of ${n} is off. Nobody is home at that switch.`, layers: [{ t: 'bits', name: 'n', v: n, n: 8, cls: { [k]: 'no' } }] });
        return F;
      }
      const res = op === 'set' ? n | m : op === 'clear' ? n & ~m & 255 : n ^ m;
      const how = op === 'set' ? `OR with the mask. OR with 1 always gives 1, and OR with 0 changes nothing.` : op === 'clear' ? `Flip the mask with ~ so only bit ${k} is 0, then AND. AND with 0 always gives 0.` : `XOR with the mask. XOR with 1 flips the bit, XOR with 0 leaves it alone.`;
      const mv = op === 'clear' ? (~m) & 255 : m;
      F.push({ mood: 'work', msg: how, layers: [{ t: 'bits', name: 'n', v: n, n: 8, cls: { [k]: 'look' } }, { t: 'bits', name: op === 'clear' ? '~mask' : 'mask', v: mv, n: 8, cls: { [k]: 'cur' } }] });
      const same = res === n;
      F.push({ mood: same ? 'sad' : 'happy', fx: same ? 'shake' : 'burst',
        msg: same ? `Result <b>${res}</b>. Nothing changed, because bit ${k} was already ${op === 'set' ? 'on' : 'off'}. Silly us.` : `Result <b>${res}</b>. Bit ${k} is now ${(res >> k) & 1 ? 'on' : 'off'} and every other bit is untouched.`,
        layers: [{ t: 'bits', name: 'result', v: res, n: 8, cls: { [k]: same ? 'no' : 'yes' } }] });
      return F;
    }
  });

  D.kernighan = el => PK.widget(el, {
    title: 'Pop the lowest 1 bit until nothing is left', sub: 'Each n & (n - 1) wipes out one 1 bit. Count the pops and you have counted the ones.',
    inputs: [{ k: 'n', label: 'Number', type: 'num', val: 44, min: 1, max: 255 }],
    random: () => ({ n: 1 + Math.floor(Math.random() * 255) }),
    check: v => (Number.isInteger(v.n) && v.n >= 1 && v.n <= 255) ? '' : 'Pick a whole number from 1 to 255.',
    frames: ({ n }) => {
      const F = [{ mood: 'think', msg: `How many 1 bits does <b>${n}</b> have. Instead of checking all 8 bits, we pop one 1 bit per round.`, layers: [{ t: 'bits', name: 'n', v: n, n: 8 }] }];
      let x = n, c = 0;
      while (x) {
        const low = x & -x, k = Math.log2(low), y = x & (x - 1);
        F.push({ mood: 'look', msg: `n − 1 turns the lowest 1 (worth ${low}) off and every 0 below it on.`, vars: { count: c },
          layers: [{ t: 'bits', name: 'n', v: x, n: 8, cls: { [k]: 'look' } }, { t: 'bits', name: 'n − 1', v: x - 1, n: 8, cls: bitsCls(8, b => b <= k ? 'cur' : '') }] });
        c++;
        F.push({ mood: 'happy', fx: 'burst', msg: `AND them: the lowest 1 is gone. Pop number <b>${c}</b>. Now n is ${y}.`, vars: { count: c },
          layers: [{ t: 'bits', name: 'n & (n−1)', v: y, n: 8, cls: { [k]: 'no' } }] });
        x = y;
      }
      const p2 = (n & (n - 1)) === 0;
      F.push({ mood: 'wow', fx: 'rain', msg: `n reached 0 after <b>${c}</b> pop${c > 1 ? 's' : ''}, so ${n} has ${c} one bit${c > 1 ? 's' : ''}. ${p2 ? `Only one pop means ${n} is a power of two.` : `More than one pop means ${n} is not a power of two.`}`, layers: [{ t: 'bits', name: 'n', v: n, n: 8, cls: bitsCls(8, b => (n >> b) & 1 ? 'yes' : '') }] });
      return F;
    }
  });

  D.subsets = el => PK.widget(el, {
    title: 'Packing bags with a counter', sub: 'Give up to four items. Each number from 0 to 2^n − 1 is one way to pack the bag.',
    inputs: [{ k: 'items', label: 'Items', type: 'text', val: '🍎, 📘, 🧢', w: 200 }],
    check: v => { const a = PK.parseList(v.items, false); return a.length >= 1 && a.length <= 4 ? '' : 'Please give one to four items, separated by commas.'; },
    frames: ({ items }) => {
      const a = PK.parseList(items, false), n = a.length, F = [];
      F.push({ mood: 'think', msg: `${n} item${n > 1 ? 's' : ''}, so there are 2<sup>${n}</sup> = <b>${1 << n}</b> different bags, from completely empty to everything.`, layers: [{ t: 'row', cells: a, idx: true, label: 'Items, numbered from 0' }] });
      for (let m = 0; m < (1 << n); m++) {
        const pick = a.filter((_, i) => (m >> i) & 1);
        F.push({ mood: m === (1 << n) - 1 ? 'wow' : m === 0 ? 'sad' : 'work', fx: m === (1 << n) - 1 ? 'burst' : '',
          msg: m === 0 ? 'Mask 0: every switch is off, so the bag is empty. A sad, light bag.' : `Mask ${m} is ${bin(m, n)}. Bit i on means take item i: <b>${pick.join(' ')}</b>.`,
          say: m === 0 ? 'Mask 0. Every switch is off, so the bag is empty.' : `Mask ${m}, which is ${bin(m, n).split('').join(' ')} in binary. Take ${pick.length} item${pick.length > 1 ? 's' : ''}.`,
          layers: [{ t: 'bits', name: 'mask', v: m, n, cls: bitsCls(n, b => (m >> b) & 1 ? 'yes' : '') }, { t: 'row', cells: a, cls: Object.fromEntries(a.map((_, i) => [i, (m >> i) & 1 ? 'yes' : 'done'])), label: 'In the bag' }] });
      }
      F.push({ mood: 'happy', msg: `All ${1 << n} bags were packed, each exactly once, just by counting.` });
      return F;
    }
  });

  D.perm = el => PK.widget(el, {
    title: 'Who may do what: chmod as bits', sub: 'Type a three digit permission like 755 or 640. Each digit is three switches: read 4, write 2, run 1.',
    inputs: [{ k: 'p', label: 'Permission', type: 'text', val: '754', w: 90 }],
    random: () => ({ p: [0, 0, 0].map(() => Math.floor(Math.random() * 8)).join('') }),
    check: v => /^[0-7]{3}$/.test(String(v.p).trim()) ? '' : 'Please type exactly three digits from 0 to 7, like 755.',
    frames: ({ p }) => {
      p = String(p).trim();
      const who = ['owner', 'group', 'others'], F = [{ mood: 'think', msg: `Permission <b>${p}</b> means three digits, one each for the owner, the group and everybody else.`, layers: [{ t: 'row', cells: p.split(''), idx: false, label: 'owner · group · others' }] }];
      const rows = [];
      p.split('').forEach((d, i) => {
        const v = +d, can = [v & 4, v & 2, v & 1].map(Boolean);
        rows.push([who[i], can[0] ? '📖 read' : '🚫', can[1] ? '✏️ write' : '🚫', can[2] ? '🏃 run' : '🚫']);
        const cls = {};
        rows.forEach((r, ri) => [1, 2, 3].forEach(c => { cls[ri + ',' + c] = r[c] === '🚫' ? 'no' : 'yes'; }));
        const nope = can.filter(x => !x).length;
        F.push({ mood: nope === 3 ? 'sad' : nope === 0 ? 'happy' : 'look', fx: nope === 0 ? 'burst' : nope === 3 ? 'shake' : '',
          msg: `${who[i][0].toUpperCase() + who[i].slice(1)} gets ${d} = ${[4, 2, 1].filter(b => v & b).join(' + ') || '0'}. ${nope === 3 ? 'No switches on at all. Sorry ' + who[i] + ', the door is locked.' : nope === 0 ? 'All three switches on. Full power.' : 'Some switches on, some off.'}`,
          layers: [{ t: 'bits', name: who[i], v, n: 3, cls: { 2: can[0] ? 'yes' : 'no', 1: can[1] ? 'yes' : 'no', 0: can[2] ? 'yes' : 'no' } },
                   { t: 'grid', rows: rows.map(r => r.slice()), cls, clab: ['who', 'read 4', 'write 2', 'run 1'] }] });
      });
      return F;
    }
  });
})();
'''

INFO = {
    'title': 'Light switches that do maths',
    'panels': [
        {'s': [['e', '💡'], ['t', '1101 = 8 + 4 + 1', {'b': 1}]], 'h': 'Binary', 't': 'Every place is worth double.', 'more': 'Bits are switches. Their place values are 1, 2, 4, 8 and so on.'},
        {'s': [['e', '🔀'], ['t', '12 ^ 10 = 6', {'b': 1}]], 'h': 'Operators', 't': 'AND, OR, XOR, NOT on every bit at once.', 'more': 'XOR is 1 where the bits differ, and x ^ x is always 0.'},
        {'s': [['e', '⏩'], ['t', 'x << k = x × 2^k', {'b': 1}]], 'h': 'Shifts', 't': 'Slide bits to double or halve.', 'more': 'Right shift drops the remainder. Java and JavaScript also have >>> that fills with zeros.'},
        {'s': [['e', '🪄'], ['t', 'n & (n − 1)', {'b': 1}]], 'h': 'The famous trick', 't': 'Removes the lowest 1 bit.', 'more': 'It counts bits, spots powers of two and powers the Fenwick tree.'},
    ],
    'remember': 'Bit operators work on all bits in one step. Masks (1 << k) pick the bits you care about, XOR cancels pairs, and counting from 0 to 2^n − 1 lists every subset.',
}

REAL = [
    ['🔐', 'chmod 755 on a web server', 'Each digit is three bits for read, write and run. The server owner gets 7 (all three), visitors get 5 (read and run), so nobody outside can change your files.'],
    ['🌐', 'Your home Wi-Fi router', 'It ANDs every address with the subnet mask 255.255.255.0 to decide whether a packet stays at home or goes out to the internet.'],
    ['🎨', 'Picking a colour in a design app', 'The hex code #FF8800 is one number holding three bytes. Apps shift and mask it to get the red, green and blue sliders.'],
]

SAY = [
    {'id': 'top', 'h': 'Welcome', 'en': 'Welcome to bit manipulation. Inside every computer, numbers are rows of tiny switches that are either off or on. In this chapter you will read and write binary, use AND, OR, XOR and NOT, slide bits with shifts, flip single bits with masks, learn the famous tricks, list every subset with a simple counter, and see how bits power file permissions, colours and home networks.'},
    {'id': 'binary', 'h': 'Binary', 'en': 'Binary uses only zero and one. Each place is worth twice the place on its right, so the places are worth one, two, four, eight and so on. To turn a number into binary, keep dividing by two and collect the remainders from right to left. To come back, double the running value and add each bit.'},
    {'id': 'operators', 'h': 'Bitwise operators', 'en': 'AND gives one only when both bits are one. OR gives one when at least one bit is one. XOR gives one when the bits are different. NOT flips every bit. XOR has two magic facts: a number XOR itself is zero, and a number XOR zero is itself. Remember to put brackets around bit operations in Java and JavaScript.'},
    {'id': 'shifts', 'h': 'Shifts', 'en': 'A left shift slides every bit to the left and fills the right with zeros, which multiplies by two for each place. A right shift slides bits to the right, the last bits fall off, and the value is halved and rounded down. Java and JavaScript also have a triple arrow shift that fills with zeros instead of copying the sign.'},
    {'id': 'masks', 'h': 'Masks', 'en': 'A mask has ones only where you want to act. One shifted left by k gives a mask for bit k. AND checks or clears, OR sets, and XOR toggles. With these four moves you can store many yes or no flags inside a single number.'},
    {'id': 'tricks', 'h': 'Bit tricks', 'en': 'The star trick is n AND n minus one. Subtracting one turns the lowest one bit off and the zeros below it on, so the AND removes exactly the lowest one bit. Repeat it to count the ones. If one round is enough to reach zero, the number is a power of two. n AND minus n keeps only the lowest one bit.'},
    {'id': 'subsets', 'h': 'Subsets', 'en': 'With n items there are two to the power n subsets, and also two to the power n numbers from zero up. Let bit i decide whether item i is taken. Counting from zero to two to the n minus one then lists every subset exactly once. It grows very fast, so it suits up to about twenty items.'},
    {'id': 'real-bits', 'h': 'Everyday bits', 'en': 'Bits run everyday systems. File permissions like seven five five are three groups of read, write and run bits. Colour codes pack red, green and blue into one number. Routers AND an address with the subnet mask to find the network. Operating systems pass options as flags joined with OR.'},
    {'id': 'leetcode', 'h': 'LeetCode', 'en': 'This chapter comes with eight LeetCode problems, from single number to maximum XOR of two numbers. Each one is solved below in Python, JavaScript, Java and TypeScript, and you can replay every solution line by line.'},
    {'id': 'practice', 'h': 'Practice', 'en': 'Time to practise. Try each LeetCode problem on your own first, then open the hint, and only then the full approach and code. Tick the box when you solve one.'},
]

QUIZ = [
    {'lv': 'e', 'q': 'What is 1011 in binary as a normal number?', 'o': ['9', '11', '13', '1011'], 'a': 1, 'hint': 'Add the place values 8, 4, 2, 1 where there is a 1.', 'why': '8 + 2 + 1 = 11.'},
    {'lv': 'e', 'q': 'What is 6 & 3?', 'o': ['2', '7', '5', '0'], 'a': 0, 'hint': '110 AND 011.', 'why': 'Only the bit worth 2 is on in both, so the answer is 2.'},
    {'lv': 'e', 'q': 'What is 6 | 3?', 'o': ['2', '7', '5', '9'], 'a': 1, 'hint': '110 OR 011.', 'why': 'Any bit on in either number is on in the result: 111, which is 7.'},
    {'lv': 'e', 'q': 'Which expression doubles x?', 'o': ['x >> 1', 'x << 1', 'x ^ 1', 'x & 1'], 'a': 1, 'hint': 'Sliding left multiplies by 2.', 'why': 'A left shift by one place multiplies by 2.'},
    {'lv': 'm', 'q': 'What is 6 ^ 3?', 'o': ['5', '7', '2', '1'], 'a': 0, 'hint': '110 XOR 011.', 'why': 'The bits differ in the places worth 4 and 1, so the answer is 101, which is 5.'},
    {'lv': 'm', 'q': 'Which expression clears bit k of n?', 'o': ['n | (1 << k)', 'n ^ (1 << k)', 'n & ~(1 << k)', 'n >> k'], 'a': 2, 'hint': 'AND with 0 makes 0.', 'why': '~(1 << k) has a 0 only at bit k, so AND turns that bit off and keeps the rest.'},
    {'lv': 'm', 'q': 'What is ~5 in Java or JavaScript?', 'o': ['-5', '-6', '2', '250'], 'a': 1, 'hint': '~x equals −x − 1 in two\'s complement.', 'why': '−5 − 1 = −6.'},
    {'lv': 'm', 'q': 'What does n & (n − 1) do?', 'o': ['Doubles n', 'Removes the lowest 1 bit', 'Keeps only the lowest 1 bit', 'Flips every bit'], 'a': 1, 'hint': 'Try it with 12.', 'why': '12 is 1100 and 11 is 1011. AND gives 1000, so the lowest 1 bit is gone.'},
    {'lv': 'h', 'q': 'What does this print in JavaScript?', 'code': 'console.log(1 << 32);', 'o': ['0', '4294967296', '1', 'Error'], 'a': 2, 'hint': 'JavaScript shifts use only the low 5 bits of the count.', 'why': '32 & 31 is 0, so 1 << 32 is the same as 1 << 0, which is 1.'},
    {'lv': 'h', 'q': 'What is 12 & -12?', 'o': ['0', '4', '8', '12'], 'a': 1, 'hint': 'n & −n keeps only the lowest 1 bit.', 'why': '12 is 1100, and the lowest 1 bit is worth 4.'},
    {'lv': 'h', 'q': 'Why must you write (x & 1) == 0 with brackets in Java?', 'o': ['It is a style rule only', '== binds tighter than &', '& is not allowed on ints', 'It runs faster'], 'a': 1, 'hint': 'Look at operator precedence.', 'why': 'Without brackets Java reads x & (1 == 0), which mixes an int with a boolean and does not compile. JavaScript silently computes the wrong thing.'},
    {'lv': 'h', 'q': 'How many subsets does a set of 10 items have?', 'o': ['10', '100', '512', '1024'], 'a': 3, 'hint': 'Two choices per item.', 'why': '2^10 = 1024, including the empty set and the full set.'},
    {'lv': 'x', 'q': 'What does this print in Python?', 'code': 'print(-16 >> 2, -1 >> 10)', 'o': ['-4 -1', '-4 0', '4 0', '-4 -0'], 'a': 0, 'hint': 'Python shifts keep the sign, rounding toward minus infinity.', 'why': '−16 divided by 4 is −4. −1 shifted right stays −1 forever, because its endless sign bits keep coming in.'},
    {'lv': 'x', 'q': 'What is the Gray code for i = 6?', 'o': ['4', '5', '6', '7'], 'a': 1, 'hint': 'i ^ (i >> 1).', 'why': '6 is 110 and 6 >> 1 is 011. 110 XOR 011 = 101, which is 5.'},
    {'lv': 'x', 'q': 'Counting Bits uses ans[i] = ans[i >> 1] + (i & 1). What is ans[13]?', 'o': ['2', '3', '4', '13'], 'a': 1, 'hint': '13 >> 1 is 6, and 6 has two 1 bits.', 'why': 'ans[6] = 2 and 13 is odd, so ans[13] = 2 + 1 = 3. Check: 1101 has three 1 bits.'},
    {'lv': 'x', 'q': 'A router has the address 10.0.5.200 with mask 255.255.252.0. What is the third byte of the network address?', 'o': ['5', '4', '0', '252'], 'a': 1, 'hint': '5 AND 252 in binary.', 'why': '5 is 00000101 and 252 is 11111100. AND gives 00000100, which is 4.'},
]

CALC = [
    {'lv': 'e', 'q': 'Write 25 in binary.', 'ans': '11001', 'hint': '16 + 8 + 1.', 'steps': ['<span class="eq">25 = 16 + 8 + 1</span>', 'Places 16, 8, 4, 2, 1 give 1 1 0 0 1.']},
    {'lv': 'e', 'q': 'What is 5 << 2?', 'ans': '20', 'hint': 'Multiply by 2 twice.', 'steps': ['<span class="eq">5 × 2² = 20</span>']},
    {'lv': 'm', 'q': 'What is 29 & 15?', 'ans': '13', 'hint': 'AND with 15 keeps the low four bits.', 'steps': ['29 is 11101 and 15 is 01111.', 'AND gives 01101, which is <span class="eq">8 + 4 + 1 = 13</span>']},
    {'lv': 'm', 'q': 'How many 1 bits does 255 have?', 'ans': '8', 'hint': '255 is 2^8 − 1.', 'steps': ['255 is 11111111, so all <span class="eq">8</span> bits are on.']},
    {'lv': 'h', 'q': 'Set bit 4 of the number 9. What do you get?', 'ans': '25', 'hint': 'Bit 4 is worth 16.', 'steps': ['<span class="eq">9 | (1 &lt;&lt; 4) = 9 | 16 = 25</span>']},
    {'lv': 'h', 'q': 'What is the Hamming distance between 7 and 12?', 'ans': '3', 'hint': 'Count the 1 bits of 7 ^ 12.', 'steps': ['7 is 0111 and 12 is 1100.', 'XOR is 1011, which has <span class="eq">3</span> ones.']},
    {'lv': 'x', 'q': 'chmod 640 is applied to a file. Out of all nine read, write and run switches, how many are on?', 'ans': '3', 'hint': '6 = 4 + 2, 4 = 4, 0 = nothing.', 'steps': ['Owner 6 has two switches on, group 4 has one, others 0 has none.', '<span class="eq">2 + 1 + 0 = 3</span>']},
    {'lv': 'x', 'q': 'What is the largest value an unsigned 12 bit number can hold?', 'ans': '4095', 'hint': '2^n − 1.', 'steps': ['<span class="eq">2¹² − 1 = 4096 − 1 = 4095</span>']},
]

TALK = {
    'binary': 'Think about the light switches in your home. Each one is either off or on, and nothing in between. A computer is built from billions of switches just like that, so it can only really count with two digits, zero and one. That is binary. In normal numbers each place is worth ten times the place to its right, ones, tens, hundreds. In binary each place is worth only twice as much, one, two, four, eight, sixteen. So the pattern one one zero one means eight plus four plus one, which is thirteen. To change a number into binary you keep dividing by two. If the number is odd the remainder is one, if it is even the remainder is zero, and those remainders are the bits from right to left. Every photo, song and message on your phone is stored like this, as very long rows of switches.',
    'operators': 'Now imagine two rows of switches standing one above the other, and a rule that decides a third row underneath. That is all a bitwise operator does, and the computer does every column at the same moment. AND is like two keys for one locker, the door opens only when both keys are turned. OR is like a doorbell with two buttons, either one rings the bell. XOR asks a simple question, are these two different. If they differ you get a one, if they match you get a zero. That gives XOR a lovely habit, anything XOR itself disappears. Spies once used XOR to hide messages, because mixing a message with a secret key scrambles it, and mixing it with the same key again brings it straight back. NOT simply flips every switch to the other side.',
    'shifts': 'A shift slides the whole row of switches sideways. Push everything one place to the left and a fresh zero comes in on the right. Every switch is now in a place worth twice as much, so the number doubles. Push left three places and it grows eight times. A right shift slides the other way. The rightmost switch falls off the edge and is lost, so the number halves and any remainder is thrown away. Seven shifted right becomes three, because the half was dropped. Long ago, multiplying was slow on chips, so programmers used shifts to multiply by two, four or eight. Modern compilers still do this for you behind the scenes. Be careful in Java and JavaScript, where numbers have only thirty two switches and a shift by thirty two does not do what you might expect.',
    'masks': 'A mask is like a stencil you hold over a painting. It has holes only where you want to work, and it covers everything else. In bit terms, a mask is a number with ones only at the switches you care about. One shifted left by k makes a mask with a single hole at switch k. Hold it over your number with AND and you can peek at that one switch. Use OR and you switch it on. Use AND with the flipped mask and you switch it off. Use XOR and you flip it. This is how a game remembers which of thirty two badges you have earned, all inside one number. It is also how settings like bold, italic and underline can be stored together in a text editor, one switch each.',
    'tricks': 'Programmers love a few short bit tricks because they replace whole loops with one line. The most famous is n AND n minus one. When you subtract one from a number, the lowest switch that was on turns off, and all the off switches below it turn on, a bit like a car odometer rolling back. AND the two together and only the lowest on switch vanishes. Do it again and again, and the number of rounds is the number of switches that were on. If one round already gives zero, the number had only one switch on, which means it is a power of two. A cousin trick, n AND minus n, keeps only that lowest switch. The Fenwick tree in the arrays chapter uses it to jump around an array very quickly.',
    'subsets': 'Imagine packing a school bag with an apple, a book and a cap. For each thing you decide yes or no. Three yes or no choices give two times two times two, which is eight possible bags. Here is the neat part. The numbers zero to seven, written in binary, are exactly every pattern of three switches. So let switch zero mean the apple, switch one the book and switch two the cap. Counting from zero to seven then packs every possible bag exactly once, from the empty bag to the full bag. Computers use this to try every combination of toppings, every team selection, or every set of cities to visit. But it grows fast. Twenty items give about a million bags, while forty items give about a trillion, which is far too many.',
    'real-bits': 'Bits are quietly working all around you. When a website owner types chmod seven five five on a server, each digit is three switches meaning read, write and run. Seven turns all three on for the owner, five lets everybody else read and run but never change the files. When you choose orange in a drawing app with the code F F eight eight zero zero, that single number holds the red, green and blue amounts side by side, and the app slides and masks it to fill the sliders. Your home Wi-Fi router also uses AND. It combines every address with a subnet mask to decide whether a message stays inside your home or travels out to the internet. Even the operating system, when it opens a file, receives its options as switches joined together with OR.',
    'leetcode': 'The LeetCode problems in this chapter are the classic bit questions asked in coding interviews at big companies. They start gentle, like finding the one number without a partner, where XOR makes all the pairs vanish. Then they climb to counting switches, measuring how many bits differ between two numbers, building every subset, producing the special Gray code used in rotary knobs and car sensors, and finally finding the biggest XOR of any two numbers by deciding the answer one switch at a time from the top. Every problem has a hint, a full explanation and code in Python, JavaScript, Java and TypeScript that you can play step by step. Try each one on your own first, even for a few minutes. Struggling a little before peeking is exactly how the idea sticks in your memory.',
}

T = t.finish({
    'slug': 'bit-manipulation', 'title': 'Bit Manipulation', 'short': 'Bit manipulation', 'emoji': '💡', 'topic': 'bit-manipulation', 'prefix': 'dsabit',
    'module': ('🧱', 'Core building blocks'),
    'lead': 'Every number inside a computer is a row of tiny switches. Learn to read them, flip them, slide them and mask them, then use the famous tricks that make code faster and solve classic interview problems in one line.',
    'desc': 'Bit manipulation in DSA: binary numbers, AND, OR, XOR and NOT, left and right shifts, masks to check, set, clear and toggle bits, n & (n - 1) and other tricks, subsets as bitmasks, and real uses in permissions, colours and networks, with LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'minutes': 18,
    'summary': 'Binary numbers, AND, OR, XOR and NOT, shifts, masks to check, set, clear and toggle one bit, n & (n - 1) and other tricks, subsets as bitmasks, and bits in permissions, colours and networks. Eight LeetCode problems in Python, JavaScript, Java and TypeScript.',
    'keywords': ['bit manipulation', 'binary', 'bitwise', 'xor', 'and', 'or', 'not', 'shift', 'mask', 'two\'s complement', 'power of two', 'count bits', 'bitmask', 'gray code', 'single number', 'hamming distance', 'chmod', 'subnet mask'],
    'added': '2026-11-22',
    'parts': PARTS, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'talk': TALK,
    'viz': VIZ_JS, 'css': '',
    'prev': ('math', 'math-in-dsa', '🧮 Mathematics in DSA'),
    'next': ('arrays', 'array-adventure', '📦 Arrays'),
})
