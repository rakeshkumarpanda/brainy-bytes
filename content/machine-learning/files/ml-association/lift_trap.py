# 3.2 Association rules and market basket analysis
# Example "lift_trap" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

baskets = 100
milk = 80                     # milk is in 80 of 100 baskets
cereal = 25
both = 18
conf = both / cereal
print("confidence(cereal -> milk) =", conf)
print("but support(milk) alone =", milk / baskets)
print("lift =", round(conf / (milk / baskets), 3), " so buying cereal makes milk slightly LESS likely")
