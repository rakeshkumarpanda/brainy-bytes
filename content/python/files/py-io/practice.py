# 1.4 Input, output and formatting text
# Practice tasks. Fill in each function, then run this file.
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


# ================================================================== task 1: One line of a bill
# Write bill_line(item, qty, price) that returns the item left aligned in 10 characters, qty right
# aligned in 4, and qty × price right aligned in 10 with 2 decimals. Use one f-string.
# Hint: Three fields: {item:<10}, {qty:>4} and {qty * price:>10.2f}.

def bill_line(item, qty, price):
    # your code here
    pass


# ================================================================== task 2: Centre a title by hand
# Write centre(text, width, fill) that does the same as f"{text:{fill}^{width}}" but without format
# specs: work out the padding yourself.
# Hint: pad = width - len(text). left = pad // 2, right = pad - left.

def centre(text, width, fill):
    # your code here
    pass


# ================================================================== task 3: Read a line of marks
# Write marks_report(line). line holds whole numbers separated by spaces, for example "78 91 64".
# Return f"Total {{t}}, average {{a:.2f}}". Return "No marks" for an empty or blank line.
# Hint: split() with no argument splits on any spaces and drops empty pieces.

def marks_report(line):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: One line of a bill", [('bill_line("Pen", 2, 10)', 'Pen          2     20.00'), ('bill_line("Notebook", 3, 45.5)', 'Notebook     3    136.50')]))
    results.append(check("Task 2: Centre a title by hand", [('centre("Menu", 11, "*")', '***Menu****'), ('centre("ab", 6, "-")', '--ab--'), ('centre("long text", 4, "*")', 'long text')]))
    results.append(check("Task 3: Read a line of marks", [('marks_report("78 91 64")', 'Total 233, average 77.67'), ('marks_report("  ")', 'No marks'), ('marks_report("100")', 'Total 100, average 100.00')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
