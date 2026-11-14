# 2.3 Naive Bayes: classify by counting clues
# Example "multinomial_text" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

texts = ["win money now", "win a free prize", "free money offer", "claim your prize now",
         "meeting at noon", "lunch money for friday", "project meeting now", "see you at lunch"]
labels = ["spam", "spam", "spam", "spam", "ham", "ham", "ham", "ham"]

model = make_pipeline(CountVectorizer(), MultinomialNB(alpha=1.0)).fit(texts, labels)
tests = ["free money now", "lunch meeting", "claim free lunch"]
for t, probs in zip(tests, model.predict_proba(tests)):
    print(t.ljust(17), {str(c): round(float(p), 3) for c, p in zip(model.classes_, probs)})
