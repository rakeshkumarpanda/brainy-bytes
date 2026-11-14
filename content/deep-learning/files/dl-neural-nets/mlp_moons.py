# 1.1 Neural networks: from perceptrons to MLPs
# Example "mlp_moons" from the lesson.
# From the Brainy Bytes Deep Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.datasets import make_moons
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

# Two interleaving half circles: no straight line separates them.
X, y = make_moons(n_samples=600, noise=0.25, random_state=0)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0)

logreg = LogisticRegression().fit(X_tr, y_tr)
print(f"logistic regression (a straight line): test accuracy {logreg.score(X_te, y_te):.3f}")
for hidden in [(2,), (8,), (32,), (32, 32)]:
    mlp = MLPClassifier(hidden_layer_sizes=hidden, activation="relu", max_iter=2000, random_state=0).fit(X_tr, y_tr)
    n_params = sum(w.size for w in mlp.coefs_) + sum(b.size for b in mlp.intercepts_)
    print(f"MLP hidden layers {str(hidden):9s}: {n_params:5d} weights, train {mlp.score(X_tr, y_tr):.3f}, test {mlp.score(X_te, y_te):.3f}")
