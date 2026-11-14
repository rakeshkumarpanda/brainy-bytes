# 3.3 Recommender systems
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn


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


# ================================================================== task 1: Cosine similarity
# Write rec_cosine(a, b) that returns the cosine similarity of two lists of numbers, rounded to 4
# decimals. Return 0.0 if either list is all zeros.
# Hint: Dot product divided by the product of the two lengths.

def rec_cosine(a, b):
    # your code here
    pass


# ================================================================== task 2: Precision and recall at k
# Write prec_recall_at_k(recommended, relevant, k). recommended is a ranked list and relevant a list
# of items the user really liked. Return [precision@k, recall@k], each rounded to 4 decimals.
# Hint: Count hits in the first k items, then divide by k and by the number of relevant items.

def prec_recall_at_k(recommended, relevant, k):
    # your code here
    pass


# ================================================================== task 3: User based prediction
# Write user_cf_predict(R, u, j, k). R is a list of rows of ratings from 1 to 5, with 0 for not
# rated. Centre each user on the mean of their own ratings, compute the cosine of centred ratings on
# items both users rated, keep the k users with the highest similarity among those who rated item j,
# and return the user mean plus the similarity weighted average of their centred ratings of j,
# rounded to 2 decimals.
# Hint: Write small helpers for the mean of a row and the similarity of two users, then follow the
# formula.

def user_cf_predict(R, u, j, k):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: Cosine similarity", [('rec_cosine([1, 0, 1], [1, 1, 0])', 0.5), ('rec_cosine([1, 2, 3], [2, 4, 6])', 1.0), ('rec_cosine([1, 0], [0, 1])', 0.0), ('rec_cosine([0, 0], [1, 1])', 0.0)]))
    results.append(check("Task 2: Precision and recall at k", [('prec_recall_at_k(["A", "B", "C", "D", "E"], ["A", "C", "F"], 5)', [0.4, 0.6667]), ('prec_recall_at_k(["A", "B", "C", "D", "E"], ["A", "C", "F"], 2)', [0.5, 0.3333]), ('prec_recall_at_k(["X", "Y"], ["A"], 2)', [0.0, 0.0])]))
    results.append(check("Task 3: User based prediction", [('user_cf_predict([[5, 4, 0, 1, 0], [4, 5, 1, 0, 1], [1, 0, 5, 4, 5], [0, 1, 4, 5, 4], [5, 5, 0, 2, 1]], 0, 2, 2)', 1.81), ('user_cf_predict([[5, 4, 0, 1, 0], [4, 5, 1, 0, 1], [1, 0, 5, 4, 5], [0, 1, 4, 5, 4], [5, 5, 0, 2, 1]], 4, 2, 2)', 2.07), ('user_cf_predict([[5, 4, 0, 1, 0], [4, 5, 1, 0, 1], [1, 0, 5, 4, 5], [0, 1, 4, 5, 4], [5, 5, 0, 2, 1]], 3, 0, 2)', 1.37)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
