# 3.1 Clean code: PEP 8, docstrings and type hints
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


# ================================================================== task 1: Is it a good PEP 8 function name?
# Write is_good_function_name(name). It returns True only if name is a valid Python identifier, is
# not a keyword, and is written in lower case snake_case (letters, digits and underscores, no
# capital letters). Use str.isidentifier and the keyword module.
# Why it works: isidentifier already refuses names that start with a digit or contain spaces or
# dashes, so three checks are enough.

import keyword


def is_good_function_name(name):
    if not name.isidentifier():
        return False
    if keyword.iskeyword(name):
        return False
    return name == name.lower()


# ================================================================== task 2: Read the type hints of a function
# Write hint_names(func) that returns a dict from each annotated parameter name (and "return") to
# the hint written as text. Classes give their name (int gives "int"), other hints give str(hint)
# (list[str] gives "list[str]"). Parameters without a hint are left out.
# Why it works: list[str] is not a class but a generic alias, which is why it needs str(). For real
# projects inspect.get_annotations and typing.get_type_hints handle more cases.

def hint_names(func):
    result = {}
    for name, hint in func.__annotations__.items():
        if isinstance(hint, type):
            result[name] = hint.__name__
        else:
            result[name] = str(hint)
    return result


def sample(a: int, b: list[str], c, d: float = 1.0) -> bool:
    return True


def no_hints(x):
    return x


# ================================================================== task 3: Convert CamelCase names to snake_case
# Write snake_case(name) that turns CamelCase or mixedCase into snake_case: "CircleArea" gives
# "circle_area", "getHTTPResponse" gives "get_http_response", "version2Name" gives "version2_name".
# A name already in snake_case stays the same.
# Why it works: The tricky case is a run of capitals like HTTP: the underscore goes before the last
# capital, the one that starts the next word (Response).

def snake_case(name):
    result = ""
    for i in range(len(name)):
        ch = name[i]
        if ch.isupper() and i > 0:
            before = name[i - 1]
            after = name[i + 1] if i + 1 < len(name) else ""
            if before.islower() or before.isdigit() or (before.isupper() and after.islower()):
                result += "_"
        result += ch.lower()
    return result


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Is it a good PEP 8 function name?", [('is_good_function_name("circle_area")', True), ('is_good_function_name("CircleArea")', False), ('is_good_function_name("2nd_try")', False), ('is_good_function_name("class")', False), ('is_good_function_name("get_v2")', True)]))
    results.append(check("Task 2: Read the type hints of a function", [('hint_names(sample)', {'a': 'int', 'b': 'list[str]', 'd': 'float', 'return': 'bool'}), ('hint_names(no_hints)', {}), ('list(hint_names(sample))[-1]', 'return')]))
    results.append(check("Task 3: Convert CamelCase names to snake_case", [('snake_case("CircleArea")', 'circle_area'), ('snake_case("getHTTPResponse")', 'get_http_response'), ('snake_case("version2Name")', 'version2_name'), ('snake_case("already_snake")', 'already_snake'), ('snake_case("X")', 'x')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
