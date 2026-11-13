# 3.2 Association rules and market basket analysis
# Example "measures" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

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
