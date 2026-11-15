# 2.2 Access control models: from the access matrix to RBAC and ABAC
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.


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


# ================================================================== task 1: Check an ACL
# Write acl_allows(acl, user, obj, op). acl maps each object to a dict that maps users to a list of
# operations. Return True if the user may do op on obj, and False otherwise, including when the
# object or user is missing.
# Hint: Chain .get with empty defaults so missing objects and users fall through to False.

def acl_allows(acl, user, obj, op):
    # your code here
    pass


# ================================================================== task 2: Bell-LaPadula with categories
# A label is [level, categories] with level a number and categories a list. Write blp_ok(subject,
# obj, op). Label a dominates b if a’s level ≥ b’s level and every category of b is in a. Reading is
# allowed if the subject dominates the object, writing if the object dominates the subject.
# Hint: Write a helper dominates(a, b) using set(b[1]) <= set(a[1]) for the subset test.

def blp_ok(subject, obj, op):
    # your code here
    pass


# ================================================================== task 3: RBAC with role inheritance
# Write rbac_has(user_roles, juniors, role_perms, user, perm). user_roles maps users to lists of
# roles, juniors maps a role to the roles it inherits (which may inherit further), and role_perms
# maps roles to lists of permissions. Return True if any role of the user, or any role reachable
# through inheritance, holds perm.
# Hint: Walk the role graph with a stack or recursion, keep a seen set to avoid loops, and check
# each role’s permissions.

def rbac_has(user_roles, juniors, role_perms, user, perm):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Check an ACL", [('acl_allows({"payroll": {"asha": ["read", "write"], "ravi": ["read"]}}, "ravi", "payroll", "read")', True), ('acl_allows({"payroll": {"asha": ["read", "write"], "ravi": ["read"]}}, "ravi", "payroll", "write")', False), ('acl_allows({"payroll": {"asha": ["read"]}}, "dev", "wiki", "read")', False)]))
    results.append(check("Task 2: Bell-LaPadula with categories", [('blp_ok([2, ["NUC"]], [0, []], "read")', True), ('blp_ok([2, ["NUC"]], [0, []], "write")', False), ('blp_ok([2, ["NUC"]], [3, ["NUC"]], "write")', True), ('blp_ok([2, ["NUC"]], [2, ["CRY"]], "read")', False)]))
    results.append(check("Task 3: RBAC with role inheritance", [('rbac_has({"ravi": ["accountant"]}, {"accountant": ["employee"]}, {"employee": ["read wiki"], "accountant": ["pay"]}, "ravi", "read wiki")', True), ('rbac_has({"ravi": ["accountant"]}, {"accountant": ["employee"]}, {"employee": ["read wiki"], "accountant": ["pay"]}, "ravi", "approve")', False), ('rbac_has({"cfo": ["director"]}, {"director": ["manager"], "manager": ["employee"]}, {"employee": ["read wiki"], "manager": ["approve"], "director": []}, "cfo", "read wiki")', True)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
