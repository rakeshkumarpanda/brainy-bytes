# 2.3 Naive Bayes: classify by counting clues
# Model solutions. Try practice.py first.
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


# ================================================================== task 1: A smoothed word probability
# Write word_prob(word, class_words, vocab_size, alpha). class_words is the list of all words in one
# class. Return (count of word + alpha) / (len(class_words) + alpha × vocab_size), rounded to 4
# decimals.
# Why it works: With alpha = 0, any unseen word gets probability 0. With alpha = 1 it gets a small
# share.

def word_prob(word, class_words, vocab_size, alpha):
    count = 0
    for w in class_words:
        if w == word:
            count = count + 1
    return round((count + alpha) / (len(class_words) + alpha * vocab_size), 4)


# ================================================================== task 2: A naive Bayes decision with logs
# Write nb_predict(priors, likelihoods, words). priors maps class to P(class). likelihoods maps
# class to a dictionary of word to P(word | class). Add log P(class) and log P(word | class) for
# each word, and return the class with the largest log score.
# Why it works: The third test shows a strong prior winning: "hi" is 5 times likelier in ham, but
# spam is 9 times likelier to start with.

import math


def nb_predict(priors, likelihoods, words):
    best = None
    best_score = None
    for c in priors:
        score = math.log(priors[c])
        for w in words:
            score = score + math.log(likelihoods[c][w])
        if best_score is None or score > best_score:
            best = c
            best_score = score
    return best


# ================================================================== task 3: Gaussian likelihood
# Write gauss_likelihood(x, mean, var) that returns the normal density (1/√(2π var)) e−(x −
# mean)2/(2 var), rounded to 4 decimals.
# Why it works: GaussianNB multiplies one of these per feature with the class prior.

import math


def gauss_likelihood(x, mean, var):
    top = math.exp(-((x - mean) ** 2) / (2 * var))
    return round(top / math.sqrt(2 * math.pi * var), 4)


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A smoothed word probability", [('word_prob("free", ["win", "free", "free", "money"], 10, 1)', 0.2143), ('word_prob("lunch", ["win", "free"], 10, 1)', 0.0833), ('word_prob("win", ["win", "win"], 5, 0)', 1.0)]))
    results.append(check("Task 2: A naive Bayes decision with logs", [('nb_predict({"spam": 0.5, "ham": 0.5}, {"spam": {"free": 0.09, "lunch": 0.01}, "ham": {"free": 0.03, "lunch": 0.06}}, ["free", "free"])', 'spam'), ('nb_predict({"spam": 0.5, "ham": 0.5}, {"spam": {"free": 0.09, "lunch": 0.01}, "ham": {"free": 0.03, "lunch": 0.06}}, ["lunch"])', 'ham'), ('nb_predict({"spam": 0.9, "ham": 0.1}, {"spam": {"hi": 0.01}, "ham": {"hi": 0.05}}, ["hi"])', 'spam')]))
    results.append(check("Task 3: Gaussian likelihood", [('gauss_likelihood(0, 0, 1)', 0.3989), ('gauss_likelihood(1, 0, 1)', 0.242), ('gauss_likelihood(5, 5, 4)', 0.1995)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
