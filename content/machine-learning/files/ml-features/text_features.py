# 3.2 Features: encoding, scaling, engineering and selection
# Example "text_features" from the lesson.
# From the Brainy Bytes Machine Learning subject. Run it with: python3 <this file>
# Programs that use numpy, pandas or scikit-learn need them installed: pip install numpy pandas scikit-learn

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

reviews = ["great phone great camera", "bad battery", "great battery life"]

count = CountVectorizer()
counts = count.fit_transform(reviews)
print("words:", count.get_feature_names_out().tolist())
print(counts.toarray().tolist())

tfidf = TfidfVectorizer()
weights = tfidf.fit_transform(reviews).toarray()
words = tfidf.get_feature_names_out().tolist()
first = {w: round(float(v), 2) for w, v in zip(words, weights[0]) if v > 0}
print("tf-idf of review 1:", first)
