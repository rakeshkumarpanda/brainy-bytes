# 2.3 Probability and statistics for ML
# Example "bayes_test" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

p_sick = 0.01          # 1 in 100 people have the disease
p_pos_if_sick = 0.95   # the test finds 95% of sick people
p_pos_if_well = 0.05   # it wrongly says yes for 5% of healthy people

p_pos = p_pos_if_sick * p_sick + p_pos_if_well * (1 - p_sick)
p_sick_if_pos = p_pos_if_sick * p_sick / p_pos
print("chance a test is positive:", round(p_pos, 4))
print("chance you are sick if the test is positive:", round(p_sick_if_pos, 4))

people = 10000
sick = people * p_sick
true_pos = sick * p_pos_if_sick
false_pos = (people - sick) * p_pos_if_well
print("out of", people, "people:", int(true_pos), "true positives and", int(false_pos), "false positives")
print("so only", int(true_pos), "of", int(true_pos + false_pos), "positives are really sick")
