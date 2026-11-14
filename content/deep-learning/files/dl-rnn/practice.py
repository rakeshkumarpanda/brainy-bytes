# 2.2 Recurrent networks, LSTM and GRU
# Practice tasks. Fill in each function, then run this file.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
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


# ================================================================== task 1: A scalar RNN forward pass
# Write rnn_forward(xs, w, u, b) that runs ht = tanh(w ht−1 + u xt + b) from h0 = 0 over the list xs
# and returns the list of hidden states h1, h2, …, each rounded to 4 decimals.
# Hint: Keep one running state h, update it with the same w, u and b at every step, and record it.

def rnn_forward(xs, w, u, b):
    # your code here
    pass


# ================================================================== task 2: An LSTM cell update
# Write lstm_cell_update(f, i, g, o, c_prev) that returns [c, h] with c = f c_prev + i g and h = o
# tanh(c), each rounded to 4 decimals.
# Hint: Keep f times the old memory, add i times the candidate, then show o times tanh of the new
# memory.

def lstm_cell_update(f, i, g, o, c_prev):
    # your code here
    pass


# ================================================================== task 3: Counting recurrent weights
# Write count_rnn_weights(cell, n_in, hidden) for cell in "RNN", "GRU" or "LSTM", returning the
# number of weights including biases, using gates × (n_in × hidden + hidden² + hidden) with 1, 3 or
# 4 gate blocks.
# Hint: Each gate or candidate block has an input matrix, a recurrent matrix and a bias. Multiply
# one block by the number of blocks.

def count_rnn_weights(cell, n_in, hidden):
    # your code here
    pass


if __name__ == "__main__":
    results = []
    results.append(check("Task 1: A scalar RNN forward pass", [('rnn_forward([1, 0, 0], 0.5, 1.0, 0.0)', [0.7616, 0.3634, 0.1797]), ('rnn_forward([0.5, 0.5], 1.0, 2.0, 0.0)', [0.7616, 0.9427])]))
    results.append(check("Task 2: An LSTM cell update", [('lstm_cell_update(0.9, 0.5, 0.4, 0.5, 2.0)', [2.0, 0.482]), ('lstm_cell_update(0.0, 1.0, 0.8, 1.0, 5.0)', [0.8, 0.664])]))
    results.append(check("Task 3: Counting recurrent weights", [("count_rnn_weights('LSTM', 100, 128)", 117248), ("count_rnn_weights('GRU', 100, 128)", 87936), ("count_rnn_weights('RNN', 10, 20)", 620)]))
    if all(results):
        print("Every task passes. Well done!")
    else:
        print("Some tests fail. Read the FAIL lines, fix the code and run the file again.")
