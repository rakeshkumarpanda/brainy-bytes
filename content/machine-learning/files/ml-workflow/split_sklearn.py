# 1.2 The machine learning project: from a question to a working model
# Example "split_sklearn" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.model_selection import train_test_split

X = [[i] for i in range(20)]
y = [1, 0, 0, 0, 0] * 4          # 4 of 20 examples are the rare class 1

# plain split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=3)
print("plain     : rare in test =", sum(y_test), "of", len(y_test), "<- no rare examples to test on!")

# stratified split keeps the same share of class 1 in both parts
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=3, stratify=y)
print("stratified: rare in test =", sum(y_test), "of", len(y_test))
print("stratified: rare in train =", sum(y_train), "of", len(y_train))
