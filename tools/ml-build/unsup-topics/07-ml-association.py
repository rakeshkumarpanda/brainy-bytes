# Unsupervised 3.2: association rules. Checked against Agrawal, Imielinski and Swami, Mining Association Rules between
# Sets of Items in Large Databases (SIGMOD 1993), Agrawal and Srikant, Fast Algorithms for Mining Association Rules
# (VLDB 1994), Han, Pei and Yin, Mining Frequent Patterns without Candidate Generation (SIGMOD 2000), Brin, Motwani,
# Ullman and Tsur, conviction (SIGMOD 1997), Leskovec, Rajaraman and Ullman, Mining of Massive Datasets chapter 6, and
# Tan, Steinbach and Kumar, Introduction to Data Mining chapter 5.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-association')
K = Kit()

K.code('measures', r'''
baskets = [{"bread", "milk"}, {"bread", "butter", "milk"}, {"bread", "butter"}, {"milk", "tea"},
           {"bread", "butter", "jam"}, {"bread", "milk", "butter"}, {"tea", "biscuits"}, {"bread", "jam"},
           {"milk", "biscuits", "tea"}, {"bread", "butter", "milk", "jam"}]
n = len(baskets)
def support(items):
    return sum(1 for b in baskets if items <= b) / n      # share of baskets that contain all the items

A, B = {"bread"}, {"butter"}
s_ab, s_a, s_b = support(A | B), support(A), support(B)
print("support(bread) =", s_a, " support(butter) =", s_b, " support(bread and butter) =", s_ab)
conf = s_ab / s_a
lift = conf / s_b
print("confidence(bread -> butter) =", round(conf, 3))
print("lift =", round(lift, 3), " (above 1 means they appear together more than by chance)")
print("leverage =", round(s_ab - s_a * s_b, 3), " conviction =", round((1 - s_b) / (1 - conf), 3))
''')

K.code('lift_trap', r'''
baskets = 100
milk = 80                     # milk is in 80 of 100 baskets
cereal = 25
both = 18
conf = both / cereal
print("confidence(cereal -> milk) =", conf)
print("but support(milk) alone =", milk / baskets)
print("lift =", round(conf / (milk / baskets), 3), " so buying cereal makes milk slightly LESS likely")
''')

K.code('apriori', r'''
from itertools import combinations

baskets = [{"bread", "milk"}, {"bread", "butter", "milk"}, {"bread", "butter"}, {"milk", "tea"},
           {"bread", "butter", "jam"}, {"bread", "milk", "butter"}, {"tea", "biscuits"}, {"bread", "jam"},
           {"milk", "biscuits", "tea"}, {"bread", "butter", "milk", "jam"}]
min_count = 3                                              # an itemset must appear in at least 3 of 10 baskets
items = sorted(set().union(*baskets))
level = [frozenset([i]) for i in items]
frequent = {}
k = 1
while level:
    counts = {c: sum(1 for b in baskets if c <= b) for c in level}
    keep = {c: v for c, v in counts.items() if v >= min_count}
    print("size", k, ": counted", len(level), "candidates, kept", len(keep), sorted((sorted(c), v) for c, v in keep.items()))
    frequent.update(keep)
    k = k + 1
    # join frequent sets that differ in one item, then drop any candidate with an infrequent subset (Apriori rule)
    joined = {a | b for a in keep for b in keep if len(a | b) == k}
    level = [c for c in joined if all(frozenset(s) in keep for s in combinations(c, k - 1))]
print("frequent itemsets found:", len(frequent))
''', long=True)

K.code('matrix_counts', r'''
import numpy as np
import pandas as pd

baskets = [{"bread", "milk"}, {"bread", "butter", "milk"}, {"bread", "butter"}, {"milk", "tea"},
           {"bread", "butter", "jam"}, {"bread", "milk", "butter"}, {"tea", "biscuits"}, {"bread", "jam"},
           {"milk", "biscuits", "tea"}, {"bread", "butter", "milk", "jam"}]
items = sorted(set().union(*baskets))
X = pd.DataFrame([[int(i in b) for i in items] for b in baskets], columns=items)   # one row per basket
pairs = X.T @ X                                             # item by item table: baskets containing both
print(pairs.to_string())
print("support(bread, butter) =", pairs.loc["bread", "butter"] / len(X))
''')

K.code('rules_table', r'''
from itertools import combinations
import numpy as np
import pandas as pd

rng = np.random.default_rng(0)
items = ["bread", "butter", "milk", "tea", "biscuits", "jam", "coffee", "sugar"]
rows = []
for _ in range(1000):                                      # simulate 1,000 shopping trips with some habits
    b = set(rng.choice(items, size=rng.integers(1, 4), replace=False))
    if "bread" in b and rng.random() < 0.6: b.add("butter")
    if "tea" in b and rng.random() < 0.5: b.add("biscuits")
    if "coffee" in b and rng.random() < 0.7: b.add("sugar")
    rows.append(b)
onehot = pd.DataFrame([[i in b for i in items] for b in rows], columns=items)
sup = onehot.mean()
out = []
for a, c in combinations(items, 2):
    for x, y in [(a, c), (c, a)]:
        s_xy = float((onehot[x] & onehot[y]).mean())
        if s_xy >= 0.05:
            conf = s_xy / sup[x]
            out.append((x, y, round(s_xy, 3), round(conf, 3), round(conf / sup[y], 2)))
rules = pd.DataFrame(out, columns=["if", "then", "support", "confidence", "lift"]).sort_values(["lift", "confidence"], ascending=False, kind="stable")
print(rules.head(6).to_string(index=False))
print("rules with lift below 1:", int((rules["lift"] < 1).sum()), "of", len(rules))
''', long=True)

K.lesson('idea', 'Items that go together: support, confidence and lift', f'''
{src('Agrawal, Imielinski and Swami (SIGMOD 1993), Brin, Motwani, Ullman and Tsur (SIGMOD 1997), and Tan, Steinbach and Kumar, Introduction to Data Mining chapter 5.')}
{viz('mlrules')}
{wwh('<b>Association rule mining</b> finds rules of the form "if a basket has A, it often also has B" in lists of transactions. Three numbers judge a rule: <b>support</b> (how often A and B appear together), <b>confidence</b> (how often B appears when A does) and <b>lift</b> (confidence compared with how common B is anyway).',
     'Shops use rules for shelf layout, bundles and "frequently bought together" offers. The same idea finds symptoms that occur together, web pages visited in the same session, and features of software that are used together. It needs no labels.',
     'Count baskets. support(A &rArr; B) = count(A and B) / n, confidence = support(A and B) / support(A), lift = confidence / support(B). Keep rules with enough support to matter, enough confidence to act on, and lift clearly above 1.')}
{run('measures')}
{note('Bread is in 7 of 10 baskets, butter in 5, and both in 5. So every basket with butter also has bread. Confidence(bread &rArr; butter) = 0.5 / 0.7 = 0.714, and lift = 0.714 / 0.5 = 1.43: buying bread makes butter 43% more likely than in a random basket.', 'exam')}
{run('lift_trap')}
{note('72% of cereal buyers also buy milk, which sounds like a strong rule. But 80% of all shoppers buy milk. Cereal buyers are slightly less likely to buy milk than everyone else, so the lift is 0.9. Confidence alone can mislead whenever the right hand side is very common.', 'exam')}
{fxs(fx('Support', 'supp(A &rArr; B) = P(A &cap; B)', 'Share of baskets with both.', key=True),
     fx('Confidence', 'conf(A &rArr; B) = P(B | A) = supp(A &cap; B) / supp(A)', 'Not symmetric.', key=True),
     fx('Lift', 'lift = conf(A &rArr; B) / supp(B) = P(A &cap; B) / (P(A) P(B))', 'Symmetric. 1 means independent.', key=True))}
''', kw=['association rules', 'market basket analysis', 'support', 'confidence', 'lift', 'itemset'])

K.lesson('apriori', 'Apriori: finding frequent itemsets fast', f'''
{src('Agrawal and Srikant, Fast Algorithms for Mining Association Rules (VLDB 1994).')}
{viz('mlapriori')}
{wwh('Rules come from <b>frequent itemsets</b>: sets of items that appear in at least a minimum share of baskets. <b>Apriori</b> finds them level by level. Its key fact, the <b>Apriori property</b>, is that every subset of a frequent itemset is also frequent, so a set with any infrequent subset can be skipped without counting.',
     'With d items there are 2<sup>d</sup> &minus; 1 possible itemsets, far too many to count for a shop with 10,000 products. The Apriori property cuts the search down to the few sets that could still be frequent.',
     'Count single items and keep the frequent ones. Join frequent sets of size k into candidates of size k + 1, drop any candidate with an infrequent size k subset, count the rest, and repeat until no candidates remain. Then split each frequent itemset into rules and keep those with high confidence.')}
{run('apriori')}
{note('With a minimum of 3 baskets, 5 of the 6 items are frequent (biscuits is in only 2). The 5 frequent items give 10 candidate pairs, and 4 pairs survive. Joining those pairs gives triples such as bread, butter and jam, but butter and jam appear together only twice, so that triple is skipped without counting. Only bread, butter and milk is counted, and it is frequent.', 'exam')}
{run('matrix_counts')}
{note('For pairs, one matrix product does all the counting: with X the basket by item table of 0s and 1s, X<sup>T</sup> X holds the number of baskets containing each pair of items, with single item counts on the diagonal. Bread and butter appear together in 5 baskets, a support of 0.5.', 'tip')}
''', kw=['Apriori', 'frequent itemsets', 'Apriori property', 'candidate generation', 'minimum support', 'pruning'])

K.lesson('rules', 'From itemsets to a table of rules', f'''
{wwh('Each frequent itemset can be split into a left side and a right side to make rules. Each rule then gets its support, confidence and lift, plus <b>leverage</b> (supp(A &cap; B) &minus; supp(A) supp(B)) and <b>conviction</b> ((1 &minus; supp(B)) / (1 &minus; confidence)). Sorting the table by lift shows the strongest links.',
     'A real shop produces thousands of rules, most of them obvious, rare or caused by chance. Filtering by support, confidence and lift, and reading the top of the table with domain knowledge, turns that into a few useful actions.',
     'Put the transactions in a one hot table (one column per item), compute supports with column means, then confidence and lift for each candidate rule. In Python the mlxtend package offers apriori, fpgrowth and association_rules, but the core is just this counting, which runs here with pandas alone.')}
{run('rules_table')}
{note('The three habits built into the simulation come out on top: bread with butter (lift 1.97), tea with biscuits (1.82) and coffee with sugar (1.79). Each pair appears in both directions with the same lift but different confidence, because lift is symmetric and confidence is not. 38 of the 44 rules with support of at least 5% have lift below 1, so support alone is a poor filter.', 'exam')}
{table(['Measure', 'Formula', 'Reads as'], [
    ['Support', 'P(A &cap; B)', 'How often the rule applies'],
    ['Confidence', 'P(B | A)', 'How often it is right when it applies'],
    ['Lift', 'P(A &cap; B) / P(A)P(B)', 'Times more likely than chance'],
    ['Leverage', 'P(A &cap; B) &minus; P(A)P(B)', 'Extra share of baskets beyond chance'],
    ['Conviction', '(1 &minus; P(B)) / (1 &minus; P(B | A))', 'How much more often the rule would be wrong if A and B were independent']])}
''', kw=['rule generation', 'leverage', 'conviction', 'one hot encoding', 'mlxtend', 'ranking rules'])

K.lesson('fpgrowth', 'FP-Growth, big data and pitfalls', f'''
{src('Han, Pei and Yin, Mining Frequent Patterns without Candidate Generation (SIGMOD 2000), and Leskovec, Rajaraman and Ullman, Mining of Massive Datasets chapter 6.')}
{wwh('<b>FP-Growth</b> compresses all baskets into a prefix tree (the FP-tree) where shared beginnings of baskets share a path, then mines frequent itemsets from the tree without generating candidates. On very large data, algorithms such as PCY and SON count pairs with hashing or in parallel chunks.',
     'Apriori scans the data once per level and can generate huge numbers of candidates when the minimum support is low. FP-Growth usually needs only two scans and is much faster on dense data. Knowing the costs helps choose settings that finish.',
     'Start with a minimum support that keeps the result small, raise it if mining is slow, and use FP-Growth for large or dense data. Be careful with rules that only reflect popular items, rules found by testing thousands of pairs (some will look strong by chance), and correlation that is not causation.')}
{steps('How an FP-tree is built', [
    'Scan once and count every item. Drop the infrequent items.',
    'Sort the items in each basket by overall frequency, most frequent first.',
    'Insert each sorted basket into a tree from the root, sharing nodes with earlier baskets that start the same way and adding 1 to each count.',
    'Link all nodes of the same item with a list, so each item’s paths can be found quickly.',
    'For each item, collect the paths that end in it (its conditional pattern base) and mine them recursively.'])}
{note('A rule found in the data is a pattern, not a cause. "Diapers and beer" type stories need a test, such as an experiment with shelf placement, before acting on them.', 'tip')}
''', kw=['FP-Growth', 'FP-tree', 'PCY', 'SON algorithm', 'multiple testing', 'correlation vs causation'])

K.lesson('versus', 'Association rules compared', f'''
{versus('Association rules against nearby methods', ['', 'Association rules', 'Clustering', 'Collaborative filtering', 'Classification'], [
    ['Labels needed', 'No', 'No', 'No (uses ratings or clicks)', 'Yes'],
    ['Finds', 'Items that co-occur', 'Groups of similar records', 'Items a person may like', 'A label for each record'],
    ['Output', 'If A then B rules', 'Cluster for each record', 'Ranked list per person', 'Predictions'],
    ['Personal', 'No, the same for everyone', 'No', 'Yes', 'Per record'],
    ['Readable', 'Very', 'Fairly', 'Less', 'Depends on the model']],
    'use association rules for readable store wide patterns, and collaborative filtering (next chapter) for personal recommendations.')}
''', kw=['association rules vs clustering', 'association rules vs recommender systems'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Support', 'supp(X) = |{{t : X &sube; t}}| / n', 'Share of transactions t containing itemset X.', key=True),
     fx('Confidence', 'conf(A &rArr; B) = supp(A &cup; B) / supp(A)', 'A &cup; B here means both itemsets in the basket.', key=True),
     fx('Lift', 'lift(A &rArr; B) = supp(A &cup; B) / (supp(A) supp(B))', '1 = independent.', key=True),
     fx('Leverage', 'supp(A &cup; B) &minus; supp(A) supp(B)', '0 = independent.'),
     fx('Conviction', '(1 &minus; supp(B)) / (1 &minus; conf(A &rArr; B))', 'Infinite for a rule that is never wrong.'),
     fx('Apriori property', 'X &sube; Y &rArr; supp(X) &ge; supp(Y)', 'Support never rises when a set grows.', key=True))}
{steps('Worked example: one rule, every measure', [
    '1,000 baskets. Bread in 200, butter in 300, both in 120.',
    'Support = 120 / 1,000 = 0.12. Confidence(bread &rArr; butter) = 120 / 200 = 0.6.',
    'Lift = 0.6 / 0.3 = 2: butter is twice as likely in a bread basket.',
    eq('Leverage = 0.12 &minus; 0.2 &times; 0.3 = 0.06'),
    'Conviction = (1 &minus; 0.3) / (1 &minus; 0.6) = 0.7 / 0.4 = 1.75.'])}
{deep('Why rule counts explode, and how many rules an itemset gives', '<p>d items give 2<sup>d</sup> &minus; 1 non empty itemsets and 3<sup>d</sup> &minus; 2<sup>d+1</sup> + 1 possible rules, because each item can be on the left, on the right or absent, minus the cases with an empty side. One frequent itemset of size k gives 2<sup>k</sup> &minus; 2 rules. Confidence has a useful partial monotonicity: for a fixed itemset, moving items from the left side to the right side can only lower confidence, so rule generation can prune too. Lift is symmetric and does not have that property. When thousands of rules are tested, some will show high lift by chance, so serious analyses use significance tests or hold out data, as in any multiple testing problem.</p>')}
''', kw=['support formula', 'lift formula', 'Apriori property', 'number of rules', 'multiple testing'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Association rules find things that are often bought or done together, like bread and butter, and say how strong each link is.</p>',
    '<p>Compute support, confidence and lift, run Apriori with a sensible minimum support, read a rule table sorted by lift, and avoid the high confidence trap.</p>',
    '<p>Explain the Apriori property and candidate pruning, build an FP-tree, count rules from itemsets, and use leverage and conviction.</p>',
    '<p>Study closed and maximal itemsets, sequential pattern mining, PCY and SON for massive data, significance testing of rules, and causal checks of mined patterns.</p>')}
{grow('Explain what support, confidence and lift mean.',
      'Mine and filter rules from transaction data.',
      'Analyse the algorithms and the statistics of rules.')}
''', kw=['beginner', 'expert', 'closed itemsets', 'sequential patterns'])

lc(1, 'Two Sum', 'two-sum', 'e', 'Remember each value you have seen', 'Walk the list and keep a dictionary from value to index. For each number, check whether target minus it has been seen. Finding pairs that belong together quickly is the heart of pair counting.', r"""
def two_sum(nums, target):
    seen = {}
    for i, v in enumerate(nums):
        if target - v in seen:
            return [seen[target - v], i]
        seen[v] = i
    return []
""", [('two_sum([2, 7, 11, 15], 9)', [0, 1]), ('two_sum([3, 2, 4], 6)', [1, 2])])
lc(349, 'Intersection of Two Arrays', 'intersection-of-two-arrays', 'e', 'Set intersection', 'Turn both lists into sets and intersect them. Support counting asks the same question many times: is every item of this set in that basket. Ours sorts the answer so it can be checked.', r"""
def intersection(nums1, nums2):
    return sorted(set(nums1) & set(nums2))
""", [('intersection([1, 2, 2, 1], [2, 2])', [2]), ('intersection([4, 9, 5], [9, 4, 9, 8, 4])', [4, 9])])
lc(78, 'Subsets', 'subsets', 'm', 'Each item is in or out', 'Start with the empty set and, for every item, add it to every subset found so far. n items give 2<sup>n</sup> subsets, which is exactly why Apriori avoids listing them all. Ours sorts the subsets so the answer can be checked.', r"""
def subsets(nums):
    result = [[]]
    for v in nums:
        result = result + [s + [v] for s in result]
    return sorted(sorted(s) for s in result)
""", [('subsets([1, 2, 3])', [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]), ('subsets([0])', [[], [0]])])
lc(77, 'Combinations', 'combinations', 'm', 'Backtrack, choosing numbers in increasing order', 'Build each combination by adding numbers larger than the last one, and record it once it has k numbers. Generating all size k sets in order is how candidate itemsets are listed.', r"""
def combine(n, k):
    result = []

    def build(start, current):
        if len(current) == k:
            result.append(current[:])
            return
        for v in range(start, n + 1):
            current.append(v)
            build(v + 1, current)
            current.pop()

    build(1, [])
    return result
""", [('combine(4, 2)', [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]), ('combine(1, 1)', [[1]])])
lc(49, 'Group Anagrams', 'group-anagrams', 'm', 'Use the sorted letters as a key', 'Words with the same letters share the same sorted string. Group by that key in a dictionary. Turning a basket into a sorted key is also how identical itemsets are counted together. Ours sorts the groups so the answer can be checked.', r"""
def group_anagrams(strs):
    groups = {}
    for s in strs:
        groups.setdefault("".join(sorted(s)), []).append(s)
    return sorted(sorted(g) for g in groups.values())
""", [('group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])', [['ate', 'eat', 'tea'], ['bat'], ['nat', 'tan']])])
lc(1178, 'Number of Valid Words for Each Puzzle', 'number-of-valid-words-for-each-puzzle', 'h', 'Count word letter sets as bitmasks, then enumerate each puzzle’s subsets', 'Turn each word into a bitmask of its letters and count masks. A puzzle has only 7 letters, so list all subsets of its letters that contain its first letter (at most 64) and add up their counts. Enumerating subsets of a small itemset is exactly how rules are generated from a frequent itemset.', r"""
def find_num_of_valid_words(words, puzzles):
    count = {}
    for w in words:
        m = 0
        for ch in w:
            m = m | (1 << (ord(ch) - 97))
        count[m] = count.get(m, 0) + 1
    answer = []
    for p in puzzles:
        first = 1 << (ord(p[0]) - 97)
        rest = 0
        for ch in p[1:]:
            rest = rest | (1 << (ord(ch) - 97))
        total = 0
        sub = rest
        while True:
            total = total + count.get(sub | first, 0)
            if sub == 0:
                break
            sub = (sub - 1) & rest
        answer.append(total)
    return answer
""", [('find_num_of_valid_words(["aaaa", "asas", "able", "ability", "actt", "actor", "access"], ["aboveyz", "abrodyz", "abslute", "absoryz", "actresz", "gaswxyz"])', [1, 1, 3, 2, 4, 0])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Association mining is counting sets that occur together. These problems practise finding pairs with a dictionary, intersecting sets, listing all subsets and all size k combinations (the lattice Apriori searches), grouping identical sets by a key, and counting subsets with bitmasks. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'hash map', 'sets', 'subsets', 'combinations', 'bitmask'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Rules "if A then B" are judged by <b>support</b> P(A &cap; B), <b>confidence</b> P(B | A) and <b>lift</b> P(A &cap; B) / P(A)P(B).',
    'High confidence can mislead when B is common anyway. Lift below 1 means the items avoid each other.',
    '<b>Apriori property</b>: subsets of frequent sets are frequent, so candidates with an infrequent subset are skipped.',
    'Apriori goes level by level. <b>FP-Growth</b> compresses baskets into a prefix tree and avoids candidate generation.',
    'Leverage and conviction add views of the same link. Sort rules by lift, filter by support, and read them with domain knowledge.',
    'Mined rules are correlations found among many tests. Check them before acting.'],
    'Unsupervised 3.3 covers recommender systems: content based, collaborative filtering and matrix factorisation.')}
{files('Three tasks: support of an itemset, the support, confidence and lift of a rule, and all frequent pairs.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Support of a rule A &rArr; B is', ['P(B | A)', 'The share of baskets containing both A and B', 'Confidence divided by lift', 'The number of items'], 1, 'How often.', 'P(A &cap; B).')
K.quiz('e', 'Confidence of A &rArr; B is', ['P(A)', 'P(B | A)', 'P(A &cap; B) / P(B)', 'Always 1'], 1, 'Given A.', 'supp(A &cap; B) / supp(A).')
K.quiz('e', 'A lift of 1 means', ['A strong rule', 'A and B are independent', 'B never appears', 'A always appears'], 1, 'Chance level.', 'Above 1 positive, below 1 negative association.')
K.quiz('e', 'Association rules need', ['Labels', 'Transactions (baskets of items)', 'A neural network', 'Images'], 1, 'Unsupervised.', 'Just lists of items.')
K.quiz('m', 'Rule cereal &rArr; milk has confidence 0.72, and milk is in 80% of baskets. The rule is', ['Strong', 'Misleading: lift is 0.9', 'Perfect', 'Impossible'], 1, 'Compare with P(milk).', 'Cereal buyers buy milk less than average.')
K.quiz('m', 'The Apriori property says', ['Bigger sets are more frequent', 'Every subset of a frequent itemset is frequent', 'All pairs are frequent', 'Rules are symmetric'], 1, 'Downward closure.', 'So infrequent subsets prune supersets.')
K.quiz('m', 'Which measure is symmetric in A and B?', ['Confidence', 'Lift', 'Conviction', 'None'], 1, 'P(A &cap; B)/P(A)P(B).', 'Swapping A and B changes nothing.')
K.quiz('m', 'Lowering the minimum support usually', ['Finds fewer itemsets', 'Finds many more itemsets and takes longer', 'Has no effect', 'Removes all rules'], 1, 'More survive.', 'Candidate counts can explode.')
K.quiz('m', 'X<sup>T</sup> X for a basket by item 0/1 table gives', ['Item supports only', 'Pair counts, with item counts on the diagonal', 'Lift values', 'Rules'], 1, 'Co-occurrence.', 'Divide by n for supports.')
K.quiz('h', 'FP-Growth is faster than Apriori mainly because it', ['Uses labels', 'Compresses baskets into a prefix tree and avoids candidate generation', 'Uses fewer items', 'Ignores support'], 1, 'Han, Pei and Yin (2000).', 'About two scans of the data.')
K.quiz('h', 'A frequent itemset of size 4 gives how many rules (both sides non empty)?', ['4', '8', '14', '16'], 2, '2<sup>k</sup> &minus; 2.', '16 &minus; 2 = 14.')
K.quiz('h', 'Testing thousands of candidate rules causes', ['No problem', 'Some rules to look strong purely by chance', 'Lift to become 1', 'Support to rise'], 1, 'Multiple testing.', 'Use hold out data or significance tests.')
K.quiz('x', 'In the style of a Stanford CS246 exam: conviction of a rule with confidence 1 is', ['0', '1', 'Infinite', 'Equal to lift'], 2, '(1 &minus; supp(B)) / (1 &minus; conf).', 'Division by zero: the rule is never wrong.')
K.quiz('x', 'In the style of a Stanford CS246 exam: how many possible rules are there over d items?', ['2<sup>d</sup>', 'd<sup>2</sup>', '3<sup>d</sup> &minus; 2<sup>d+1</sup> + 1', 'd!'], 2, 'Left, right or absent.', 'Minus rules with an empty side.')

K.calc('e', '1,000 baskets, bread in 200. Support of bread?', '0.2', 'Count / n.', ['200 baskets.', '1,000 total.', eq('200 / 1,000 = 0.2')], check=0.2)
K.calc('e', 'Bread in 200 baskets, bread and butter in 120. Confidence(bread &rArr; butter)?', '0.6', 'Both / A.', ['Both: 120.', 'Bread: 200.', eq('120 / 200 = 0.6')], check=0.6)
K.calc('e', 'Confidence 0.6 and support of butter 0.3. Lift?', '2', 'Confidence / supp(B).', ['0.6.', '0.3.', eq('0.6 / 0.3 = 2')], check=2)
K.calc('m', 'supp(A &cup; B) = 0.12, supp(A) = 0.2, supp(B) = 0.3. Leverage?', '0.06', 'Joint minus product.', ['Product 0.2 &times; 0.3 = 0.06.', 'Joint 0.12.', eq('0.12 &minus; 0.06 = 0.06')], check=0.06)
K.calc('m', 'supp(B) = 0.3 and confidence 0.6. Conviction?', '1.75', '(1 &minus; supp(B)) / (1 &minus; conf).', ['1 &minus; 0.3 = 0.7.', '1 &minus; 0.6 = 0.4.', eq('0.7 / 0.4 = 1.75')], check=1.75)
K.calc('m', 'How many non empty itemsets can 20 items form?', '1048575', '2<sup>d</sup> &minus; 1.', ['2<sup>20</sup> = 1,048,576.', 'Remove the empty set.', eq('1,048,575')], check=1048575)
K.calc('m', 'How many rules come from one frequent itemset of 3 items?', '6', '2<sup>k</sup> &minus; 2.', ['2<sup>3</sup> = 8 ways to choose a left side.', 'Remove empty left and empty right.', eq('8 &minus; 2 = 6')], check=6)
K.calc('h', '4 frequent single items. Candidate pairs Apriori must count?', '6', 'C(4, 2).', ['4 &times; 3 = 12 ordered pairs.', 'Divide by 2.', eq('6')], check=6)
K.calc('h', 'supp(milk) = 0.8 and conf(cereal &rArr; milk) = 0.72. Lift?', '0.9', 'Confidence / supp(B).', ['0.72.', '0.8.', eq('0.72 / 0.8 = 0.9, below 1')], check=0.9)
K.calc('x', 'In the style of a Stanford CS246 problem: counting every pair of 100,000 items in a triangular array needs how many counters?', '4999950000', 'n(n &minus; 1)/2.', ['n = 100,000.', 'n(n &minus; 1) = 9,999,900,000.', eq('4,999,950,000 counters, which is why PCY hashes pairs')], check=4999950000)

K.assign('support', 'e', 'Support of an itemset',
         '<p>Write <code>support(baskets, items)</code> that returns the share of baskets containing every item in items, rounded to 4 decimals.</p>',
         """
def support(baskets, items):
    # your code here
    pass
""", [('support([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["a", "b"])', 0.5), ('support([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["c"])', 0.5), ('support([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["a", "c"])', 0.25)],
         """
def support(baskets, items):
    need = set(items)
    hits = sum(1 for b in baskets if need <= set(b))
    return round(hits / len(baskets), 4)
""", 'A basket counts when the item set is a subset of it.', '<p>Using sets makes the subset test one operator: need &lt;= set(b).</p>')
K.assign('rule_stats', 'm', 'Support, confidence and lift of a rule',
         '<p>Write <code>rule_stats(baskets, a, b)</code> for the rule "if all of a then all of b". Return [support, confidence, lift], each rounded to 4 decimals.</p>',
         """
def rule_stats(baskets, a, b):
    # your code here
    pass
""", [('rule_stats([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["a"], ["b"])', [0.5, 0.6667, 0.8889]), ('rule_stats([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], ["c"], ["b"])', [0.5, 1.0, 1.3333])],
         """
def rule_stats(baskets, a, b):
    n = len(baskets)
    sa = sum(1 for t in baskets if set(a) <= set(t)) / n
    sb = sum(1 for t in baskets if set(b) <= set(t)) / n
    sab = sum(1 for t in baskets if set(a) | set(b) <= set(t)) / n
    conf = sab / sa
    return [round(sab, 4), round(conf, 4), round(conf / sb, 4)]
""", 'Compute the three supports, then combine them.', '<p>In the first test a appears with b two times out of three, but b is in three of four baskets anyway, so the lift is below 1.</p>')
K.assign('frequent_pairs', 'm', 'All frequent pairs',
         '<p>Write <code>frequent_pairs(baskets, min_count)</code> that returns every pair of items [x, y] with x before y alphabetically that appears together in at least min_count baskets, as a sorted list.</p>',
         """
def frequent_pairs(baskets, min_count):
    # your code here
    pass
""", [('frequent_pairs([["a", "b"], ["a"], ["b", "c"], ["a", "b", "c"]], 2)', [['a', 'b'], ['b', 'c']]), ('frequent_pairs([["bread", "milk"], ["bread", "butter", "milk"], ["bread", "butter"], ["milk", "tea"], ["bread", "butter", "jam"], ["bread", "milk", "butter"], ["tea", "biscuits"], ["bread", "jam"], ["milk", "biscuits", "tea"], ["bread", "butter", "milk", "jam"]], 3)', [['bread', 'butter'], ['bread', 'jam'], ['bread', 'milk'], ['butter', 'milk']])],
         """
from itertools import combinations


def frequent_pairs(baskets, min_count):
    counts = {}
    for b in baskets:
        for x, y in combinations(sorted(set(b)), 2):
            counts[(x, y)] = counts.get((x, y), 0) + 1
    return sorted([list(p) for p, c in counts.items() if c >= min_count])
""", 'For each basket, count every pair of its items once.', '<p>Counting pairs basket by basket only touches pairs that actually occur, which is far cheaper than checking every possible pair against every basket.</p>')

K.must('Measures', 'support P(A &cap; B), confidence P(B | A), lift P(A &cap; B)/P(A)P(B). Lift 1 independent, below 1 negative.')
K.must('Trap', 'High confidence with a very common B can still mean lift below 1. Always check lift.')
K.must('Apriori', 'Subsets of frequent sets are frequent. Count level by level, join, prune candidates with infrequent subsets.')
K.must('Rules', 'Each frequent k itemset gives 2<sup>k</sup> &minus; 2 rules. Filter by support, confidence, lift. Leverage and conviction.')
K.must('Scale', 'FP-Growth prefix tree, no candidates, two scans. PCY and SON for massive data. Pair counts via X<sup>T</sup>X.')
K.must('Caution', 'Many tests give chance patterns. Rules are correlations, not causes.')

T = K.topic(
    slug='ml-association', topic='ml-association', step=(3, 'Patterns, anomalies and recommendations', 'ml-u3', 'Spot unusual records, find items that go together, and recommend what a person may like next.', 'Intermediate'),
    title='Association rules and market basket analysis', short='Association rules', badge='3.2', minutes=45,
    lead='Find items that go together: support, confidence and lift and the trap of high confidence, frequent itemsets with Apriori and its pruning rule, rule tables with leverage and conviction, FP-Growth, and how to read mined rules with care.',
    desc='association rules, market basket analysis, itemset, support, confidence, lift, leverage, conviction, frequent itemsets, Apriori, Apriori property, candidate pruning, FP-Growth, FP-tree, PCY, multiple testing.',
    summary='Support, confidence and lift, Apriori and pruning, rule tables, FP-Growth, and reading rules safely.',
    keywords=['association rules', 'market basket analysis', 'Apriori', 'support', 'confidence', 'lift', 'FP-Growth', 'frequent itemsets', 'leverage', 'conviction'],
    recap='<p>Association rules turn baskets into readable "if A then B" patterns. Count with Apriori or FP-Growth, judge with lift as well as confidence, and treat rules as leads to test.</p>',
    added='2026-11-13', leet=leet_items())
