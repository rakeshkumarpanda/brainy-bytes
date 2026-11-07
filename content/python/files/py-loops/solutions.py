# 2.2 Loops: while, for, range, break and continue
# Model solutions. Try practice.py first.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>


# ------------------------------------------------------------------ the checker
# check(tests) runs each test and says PASS or FAIL. A test is a pair: the call to make and the answer we expect.
import json


def check(name, tests):
    passed = 0
    for call, expected in tests:
        try:
            got = eval(call)
        except Exception as error:
            got = "error: " + type(error).__name__ + ": " + str(error)
        if json.dumps(got, sort_keys=True, default=repr) == json.dumps(expected, sort_keys=True, default=repr):
            passed = passed + 1
            print("  PASS", call)
        else:
            print("  FAIL", call, "expected", repr(expected), "but got", repr(got))
    print(name + ":", passed, "of", len(tests), "tests pass")
    return passed == len(tests)


# ================================================================== task 1: FizzBuzz as one line of text
# Write fizzbuzz_line(n) that returns the FizzBuzz words for 1 to n joined by spaces: multiples of
# 15 give FizzBuzz, of 3 Fizz, of 5 Buzz, and other numbers themselves.
# Why it works: FizzBuzz is a famous first interview question because it tests loops, % and the
# order of conditions.

def fizzbuzz_line(n):
    words = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            words.append("FizzBuzz")
        elif i % 3 == 0:
            words.append("Fizz")
        elif i % 5 == 0:
            words.append("Buzz")
        else:
            words.append(str(i))
    return " ".join(words)


# ================================================================== task 2: Prime check with a loop else
# Write is_prime(n). n is prime if n ≥ 2 and no number d from 2 up to the square root of n divides
# it. Use a for loop with break and else.
# Why it works: Checking up to √n is enough: if n = a × b and both were above √n, then a × b would
# be above n. 91 = 7 × 13 fools many people.

def is_prime(n):
    if n < 2:
        return False
    d = 2
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            break
    else:
        return True
    return False


# ================================================================== task 3: Digital root
# Write digital_root(n) for n ≥ 0: add the digits of n, then the digits of the result, until one
# digit is left. Use while loops, not str().
# Why it works: The maths shortcut 1 + (n − 1) % 9 gives the same answer for n > 0 (LeetCode 258).

def digital_root(n):
    while n >= 10:
        total = 0
        while n > 0:
            total = total + n % 10
            n = n // 10
        n = total
    return n


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: FizzBuzz as one line of text", [('fizzbuzz_line(5)', '1 2 Fizz 4 Buzz'), ('fizzbuzz_line(15).split()[-1]', 'FizzBuzz'), ('fizzbuzz_line(1)', '1')]))
    results.append(check("Task 2: Prime check with a loop else", [('is_prime(2)', True), ('is_prime(1)', False), ('is_prime(97)', True), ('is_prime(91)', False), ('is_prime(49)', False)]))
    results.append(check("Task 3: Digital root", [('digital_root(38)', 2), ('digital_root(0)', 0), ('digital_root(99999)', 9), ('digital_root(12345)', 6)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
