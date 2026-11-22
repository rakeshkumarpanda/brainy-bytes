# 4.1 Social engineering and phishing: tricks, email authentication and defences
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


# ================================================================== task 1: Find the registered domain
# Write registered(host) that returns the last two labels of a host name, or the last three when the
# last two are one of co.in, gov.in, co.uk. Make it lowercase.
# Hint: Split on dots, join the last two, and check them against the short list.

def registered(host):
    # your code here
    pass


# ================================================================== task 2: Edit distance between two names
# Write edit_distance(a, b) that returns the Levenshtein distance: the fewest single letter
# insertions, deletions or substitutions that turn a into b.
# Hint: Dynamic programming: keep one row of distances. Each cell is the minimum of delete, insert
# and substitute.

def edit_distance(a, b):
    # your code here
    pass


# ================================================================== task 3: Where does the email go?
# Write fate(from_domain, spf_domain, spf_pass, dkim_domain, policy). DMARC passes if (spf_pass and
# spf_domain == from_domain) or dkim_domain == from_domain. On pass return "inbox". On fail return
# "rejected" for policy "reject", "spam" for "quarantine", and "inbox" for "none".
# Hint: Compute one boolean for alignment, then map the policy with a small dictionary.

def fate(from_domain, spf_domain, spf_pass, dkim_domain, policy):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Find the registered domain", [('registered("indiapost.gov.in.track-parcel.top")', 'track-parcel.top'), ('registered("www.ONLINESBI.sbi")', 'onlinesbi.sbi'), ('registered("mail.example.co.in")', 'example.co.in'), ('registered("example.com")', 'example.com')]))
    results.append(check("Task 2: Edit distance between two names", [('edit_distance("paypa1", "paypal")', 1), ('edit_distance("flipkrt", "flipkart")', 1), ('edit_distance("google", "google")', 0), ('edit_distance("kitten", "sitting")', 3)]))
    results.append(check("Task 3: Where does the email go?", [('fate("bank.example", "bank.example", True, None, "reject")', 'inbox'), ('fate("bank.example", "evil.example", True, None, "reject")', 'rejected'), ('fate("bank.example", "list.example", False, "bank.example", "reject")', 'inbox'), ('fate("bank.example", "evil.example", False, None, "quarantine")', 'spam'), ('fate("bank.example", "evil.example", False, None, "none")', 'inbox')]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
