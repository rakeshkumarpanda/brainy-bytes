# 3.1 Autoencoders and variational autoencoders
# LeetCode solutions for this chapter. Try each problem on leetcode.com before you read its answer.
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


# ================================================================== 461. Hamming Distance (Easy)
# https://leetcode.com/problems/hamming-distance/
# Pattern: XOR the numbers and count the 1 bits
# Idea: Bits that differ become 1 after XOR, so count them. Binary codes compared by Hamming
# distance are used for fast similarity search with learned hash codes, a close cousin of
# autoencoder codes.

def hamming_distance(x, y):
    return bin(x ^ y).count('1')


# ================================================================== 535. Encode and Decode TinyURL (Medium)
# https://leetcode.com/problems/encode-and-decode-tinyurl/
# Pattern: Map each long URL to a short code and back with two dictionaries
# Idea: The encoder turns a long URL into a short code and the decoder turns the code back. This is
# lossless, unlike an autoencoder, but the same encoder and decoder pair. Our helper checks that
# every URL survives a round trip.

class Codec:
    def __init__(self):
        self.long_to_code, self.code_to_long = {}, {}

    def encode(self, long_url):
        if long_url not in self.long_to_code:
            code = str(len(self.long_to_code))
            self.long_to_code[long_url] = code
            self.code_to_long[code] = long_url
        return 'http://tinyurl.com/' + self.long_to_code[long_url]

    def decode(self, short_url):
        return self.code_to_long[short_url.rsplit('/', 1)[1]]


def round_trip(urls):
    c = Codec()
    return [c.decode(c.encode(u)) == u for u in urls]


# ================================================================== 443. String Compression (Medium)
# https://leetcode.com/problems/string-compression/
# Pattern: Two pointers: read a run, write the character and its count
# Idea: Walk through runs of the same character and overwrite the array in place with the character
# followed by the run length. Run length encoding is a simple lossless compressor, the opposite end
# from an autoencoder’s learned, lossy one. Our helper returns the new length and the compressed
# text.

def compress(chars):
    write = read = 0
    while read < len(chars):
        ch, start = chars[read], read
        while read < len(chars) and chars[read] == ch:
            read += 1
        chars[write] = ch
        write += 1
        if read - start > 1:
            for d in str(read - start):
                chars[write] = d
                write += 1
    return write


def compress_result(s):
    chars = list(s)
    n = compress(chars)
    return [n, ''.join(chars[:n])]


# ================================================================== 89. Gray Code (Medium)
# https://leetcode.com/problems/gray-code/
# Pattern: i XOR (i shifted right by 1) gives the i-th Gray code
# Idea: Neighbouring Gray codes differ in exactly one bit, so a small step in the sequence is a
# small change in the code. A good VAE latent space has the same property: nearby codes decode to
# similar outputs.

def gray_code(n):
    return [i ^ (i >> 1) for i in range(2 ** n)]


# ================================================================== 297. Serialize and Deserialize Binary Tree (Hard)
# https://leetcode.com/problems/serialize-and-deserialize-binary-tree/
# Pattern: Preorder with a marker for empty children, then rebuild recursively
# Idea: Write the value of each node before its children and "#" for a missing child. Reading the
# list back in the same order rebuilds the exact tree. An encoder and decoder that must agree on a
# format is the core of any autoencoder. Our helper builds a tree from level order, serialises it
# and checks the round trip.

class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def serialize(root):
    out = []

    def walk(node):
        if node is None:
            out.append('#')
            return
        out.append(str(node.val))
        walk(node.left)
        walk(node.right)
    walk(root)
    return ','.join(out)


def deserialize(data):
    vals = iter(data.split(','))

    def build():
        v = next(vals)
        if v == '#':
            return None
        node = TreeNode(int(v))
        node.left = build()
        node.right = build()
        return node
    return build()


def tree_round_trip(level_order):
    nodes = [None if v is None else TreeNode(v) for v in level_order]
    kids = iter(nodes[1:])
    for node in nodes:
        if node:
            node.left, node.right = next(kids, None), next(kids, None)
    root = nodes[0] if nodes else None
    text = serialize(root)
    return [text, serialize(deserialize(text)) == text]


if __name__ == "__main__":
    results = []
    results.append(check("461. Hamming Distance", [('hamming_distance(1, 4)', 2), ('hamming_distance(3, 1)', 1)]))
    results.append(check("535. Encode and Decode TinyURL", [("round_trip(['https://leetcode.com/problems/design-tinyurl', 'https://example.org/a'])", [True, True])]))
    results.append(check("443. String Compression", [("compress_result('aabbccc')", [6, 'a2b2c3']), ("compress_result('a')", [1, 'a']), ("compress_result('abbbbbbbbbbbb')", [4, 'ab12'])]))
    results.append(check("89. Gray Code", [('gray_code(2)', [0, 1, 3, 2]), ('gray_code(1)', [0, 1]), ('gray_code(3)', [0, 1, 3, 2, 6, 7, 5, 4])]))
    results.append(check("297. Serialize and Deserialize Binary Tree", [('tree_round_trip([1, 2, 3, None, None, 4, 5])', ['1,2,#,#,3,4,#,#,5,#,#', True]), ('tree_round_trip([])', ['#', True])]))
    if all(results):
        print("Every solution passes its tests.")
