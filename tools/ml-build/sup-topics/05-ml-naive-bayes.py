# Supervised 2.3: naive Bayes. Checked against Manning, Raghavan and Schutze, Introduction to Information Retrieval
# (2008) chapter 13 (multinomial and Bernoulli naive Bayes for text), Jurafsky and Martin, Speech and Language
# Processing (3rd edition draft) chapter 4, Murphy, Machine Learning: A Probabilistic Perspective chapter 3.5, Ng and
# Jordan, On Discriminative vs. Generative Classifiers (NeurIPS 2002), and the scikit-learn 1.8 user guide section 1.9.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-naive-bayes')
K = Kit()

K.code('spam_by_hand', r'''
spam = ["win money now", "win a free prize", "free money offer", "claim your prize now"]
ham = ["meeting at noon", "lunch money for friday", "project meeting now", "see you at lunch"]

def count_words(messages):
    counts = {}
    total = 0
    for m in messages:
        for w in m.split():
            counts[w] = counts.get(w, 0) + 1
            total = total + 1
    return counts, total

spam_counts, spam_total = count_words(spam)
ham_counts, ham_total = count_words(ham)
vocab = set(spam_counts) | set(ham_counts)
v = len(vocab)
print("vocabulary size:", v, " words in spam:", spam_total, " words in ham:", ham_total)

def word_prob(word, counts, total):
    return (counts.get(word, 0) + 1) / (total + v)      # Laplace smoothing

new = "free money now"
p_spam = len(spam) / (len(spam) + len(ham))
p_ham = 1 - p_spam
for w in new.split():
    ps = word_prob(w, spam_counts, spam_total)
    ph = word_prob(w, ham_counts, ham_total)
    print("word", w.ljust(6), " P(w|spam)", round(ps, 4), " P(w|ham)", round(ph, 4))
    p_spam = p_spam * ps
    p_ham = p_ham * ph
print("P(spam | message) =", round(p_spam / (p_spam + p_ham), 4))
''')

K.code('multinomial_text', r'''
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
''')

K.code('gaussian_iris', r'''
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
from sklearn.naive_bayes import GaussianNB

X, y = load_iris(return_X_y=True)
print("cross validated accuracy:", round(cross_val_score(GaussianNB(), X, y, cv=5).mean(), 3))
model = GaussianNB().fit(X, y)
print("petal length mean per class:", np.round(model.theta_[:, 2], 2).tolist())
print("petal length variance per class:", np.round(model.var_[:, 2], 3).tolist())
print("a flower with petal length 4.8:", np.round(model.predict_proba([[6.0, 2.9, 4.8, 1.6]]), 3).tolist())
''')

K.code('log_probabilities', r'''
import math

probs = [0.01] * 400            # 400 words, each with probability 0.01
product = 1.0
for p in probs:
    product = product * p
print("multiply 400 small probabilities:", product)

log_sum = 0.0
for p in probs:
    log_sum = log_sum + math.log(p)
print("add their logs instead:", round(log_sum, 2))
print("compare classes with log scores, the larger one wins")
''', long=True)

K.code('nb_vs_logistic', r'''
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
X_rest, X_test, y_rest, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
for size in [10, 30, 100, 398]:
    nb_scores = []
    lr_scores = []
    for seed in range(20):
        rng = np.random.default_rng(seed)
        idx = rng.choice(len(X_rest), size, replace=False)
        if len(set(y_rest[idx])) < 2:
            continue
        nb_scores.append(GaussianNB().fit(X_rest[idx], y_rest[idx]).score(X_test, y_test))
        lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
        lr_scores.append(lr.fit(X_rest[idx], y_rest[idx]).score(X_test, y_test))
    print("training rows", str(size).rjust(3), " naive Bayes", round(np.mean(nb_scores), 3), " logistic", round(np.mean(lr_scores), 3))
''', long=True)

K.code('overconfident', r'''
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
prob = GaussianNB().fit(X_train, y_train).predict_proba(X_test)[:, 1]
extreme = np.mean((prob < 0.01) | (prob > 0.99))
print("share of predictions below 1% or above 99%:", round(float(extreme), 3))
wrong_and_sure = np.sum(((prob > 0.99) & (y_test == 0)) | ((prob < 0.01) & (y_test == 1)))
print("wrong but more than 99% sure:", int(wrong_and_sure), "of", len(y_test))
''')

K.code('bernoulli_words', r'''
import numpy as np
from sklearn.naive_bayes import BernoulliNB

# columns: contains "free", contains "win", contains "meeting", contains "lunch"
X = [[1, 1, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [1, 1, 0, 1],
     [0, 0, 1, 0], [0, 0, 1, 1], [0, 0, 0, 1], [1, 0, 1, 0]]
y = [1, 1, 1, 1, 0, 0, 0, 0]
model = BernoulliNB(alpha=1.0).fit(X, y)
print("P(word present | spam):", np.round(np.exp(model.feature_log_prob_[1]), 2).tolist())
print("message with free and win:", np.round(model.predict_proba([[1, 1, 0, 0]])[0], 3).tolist())
print("message with only meeting:", np.round(model.predict_proba([[0, 0, 1, 0]])[0], 3).tolist())
''')

K.lesson('idea', 'Bayes rule as a classifier', f'''
{src('Manning, Raghavan and Schutze, Introduction to Information Retrieval chapter 13, Jurafsky and Martin, Speech and Language Processing chapter 4, Murphy, Machine Learning: A Probabilistic Perspective chapter 3.5, Ng and Jordan (2002), and the scikit-learn 1.8 user guide section 1.9.')}
{viz('mlnbspam')}
{wwh('<b>Naive Bayes</b> classifies with Bayes rule: P(class | features) &prop; P(class) &times; P(features | class). It makes one big simplification, the "naive" assumption: given the class, every feature is independent, so P(features | class) is just the product of one probability per feature.',
     'It trains in a single pass of counting, needs very little data, handles thousands of features (like every word in a dictionary) with ease, and gives a probability. It was the first successful spam filter and is still a strong baseline for text.',
     'Training: count how often each class appears (the prior) and how often each feature value appears within each class (the likelihoods). Prediction: for each class, multiply the prior by the likelihood of every feature of the new example, and pick the class with the largest product. Dividing by the sum turns the scores into probabilities.')}
{run('spam_by_hand')}
{fxs(fx('Naive Bayes rule', 'P(c | x<sub>1</sub>, ..., x<sub>d</sub>) &prop; P(c) &Pi;<sub>j</sub> P(x<sub>j</sub> | c)', 'Prior times one likelihood per feature.', key=True),
     fx('Prediction', 'ŷ = argmax<sub>c</sub> [log P(c) + &Sigma;<sub>j</sub> log P(x<sub>j</sub> | c)]', 'Logs turn the product into a sum.', key=True))}
{scene('a doctor with a checklist', '<p>A doctor knows flu is common in winter (the prior). Fever makes flu more likely, a cough makes it more likely again, a rash makes it less likely. The doctor combines each clue one by one, as if each told its own story. That is naive Bayes: often a little overconfident, but quick and usually pointing the right way.</p>')}
''', kw=['naive Bayes', 'Bayes rule', 'conditional independence', 'prior', 'likelihood', 'posterior', 'generative classifier'])

K.lesson('text', 'Text classification with multinomial naive Bayes', f'''
{wwh('<b>MultinomialNB</b> works on word counts. P(word | class) is the share of that class’s words that are this word. With CountVectorizer in front, it becomes a complete text classifier in two lines.',
     'Email filtering, support ticket routing, sentiment and language detection all start from word counts. Naive Bayes trains in seconds on millions of documents and needs no feature scaling.',
     'CountVectorizer turns each text into word counts. MultinomialNB learns P(word | class) with smoothing α and the class priors. predict_proba then gives the class probabilities for new texts.')}
{run('multinomial_text')}
{note('The hand made filter gave 0.871 for "free money now" and scikit-learn gives 0.882. The difference is the vocabulary: CountVectorizer ignores one letter words like "a" by default, so it has 17 words instead of 18, which changes the smoothing slightly. Always check what the tokeniser keeps.', 'tip')}
''', kw=['MultinomialNB', 'text classification', 'CountVectorizer', 'word counts', 'spam filter', 'tokeniser'])

K.lesson('smooth', 'Smoothing and log probabilities', f'''
{wwh('<b>Laplace smoothing</b> adds a small count &alpha; (usually 1) to every word in every class. <b>Log probabilities</b> add logs instead of multiplying tiny numbers.',
     'Without smoothing, a word that never appeared in ham during training gets P(word | ham) = 0, and one such word makes the whole ham score 0, no matter how hammy the rest of the message is. Without logs, multiplying hundreds of small probabilities underflows to exactly 0.0 on a computer, as the program shows.',
     'Smoothed P(w | c) = (count(w, c) + &alpha;) / (total words in c + &alpha;V), where V is the vocabulary size. Compare classes by log P(c) + &Sigma; log P(w | c). scikit-learn does both for you.')}
{run('log_probabilities')}
{fx('Laplace (add alpha) smoothing', 'P(w | c) = (n<sub>w,c</sub> + &alpha;) / (n<sub>c</sub> + &alpha;V)', 'Every word gets a small chance, so no probability is ever 0.', key=True)}
''', kw=['Laplace smoothing', 'additive smoothing', 'alpha', 'zero probability', 'log probabilities', 'underflow'])

K.lesson('gauss', 'Gaussian naive Bayes for numbers', f'''
{viz('mlgnb')}
{wwh('<b>GaussianNB</b> handles numeric features by fitting a normal (bell) curve per feature and per class. P(x<sub>j</sub> | c) is the height of that curve at the feature value.',
     'Measurements such as length, weight or blood pressure are numbers, not counts. Gaussian naive Bayes gives a fast probabilistic classifier for them with just a mean and a variance per feature and class.',
     'For each class and feature, compute the mean &mu; and variance &sigma;<sup>2</sup> from the training data. For a new example, multiply the prior by the normal density of every feature value, and normalise.')}
{run('gaussian_iris')}
{fx('Gaussian likelihood', 'p(x<sub>j</sub> | c) = (1 / &radic;(2&pi;&sigma;<sub>jc</sub><sup>2</sup>)) exp(&minus;(x<sub>j</sub> &minus; &mu;<sub>jc</sub>)<sup>2</sup> / (2&sigma;<sub>jc</sub><sup>2</sup>))', 'One mean and one variance per feature and class.', key=True)}
''', kw=['GaussianNB', 'Gaussian naive Bayes', 'normal distribution', 'class mean', 'class variance', 'numeric features'])

K.lesson('kinds', 'Which naive Bayes to use', f'''
{run('bernoulli_words')}
{table(['Model', 'Features', 'P(x<sub>j</sub> | c)', 'Typical use'], [
    ['MultinomialNB', 'Counts (how many times)', 'Share of counts', 'Text with word counts or TF-IDF'],
    ['BernoulliNB', '0 or 1 (present or not)', 'Chance the feature is present, and absent words count too', 'Short texts, binary flags'],
    ['GaussianNB', 'Real numbers', 'Normal density', 'Measurements'],
    ['CategoricalNB', 'Categories', 'Share of each category', 'Tabular categorical data'],
    ['ComplementNB', 'Counts', 'Learned from the other classes', 'Text with imbalanced classes']])}
{note('BernoulliNB also uses the words that are missing: a message without "meeting" is a little more likely to be spam. MultinomialNB ignores missing words entirely.', 'exam')}
''', kw=['BernoulliNB', 'MultinomialNB', 'GaussianNB', 'CategoricalNB', 'ComplementNB', 'choosing naive Bayes'])

K.lesson('limits', 'Strengths and weaknesses', f'''
{wwh('Naive Bayes is fast and data efficient, but its probabilities are usually <b>overconfident</b>, and it cannot learn interactions between features.',
     'Correlated features are counted as if they were separate evidence. "free", "FREE" and "free!!!" all say the same thing, but naive Bayes multiplies them in three times, pushing probabilities towards 0 or 1.',
     'Use naive Bayes for its ranking and speed, not for exact probabilities. If you need trustworthy probabilities, calibrate it (Supervised 4.3). With enough data, a discriminative model like logistic regression usually wins on accuracy.')}
{run('overconfident')}
{run('nb_vs_logistic')}
{note('On this numeric dataset logistic regression is better at every training size. Naive Bayes stays close at 30 rows and needs no iterations at all. Ng and Jordan (2002) showed that naive Bayes reaches its best error with fewer examples, while logistic regression reaches a lower best error with more examples, so naive Bayes shines when data is tiny and its assumptions roughly hold, as with text.', 'tip')}
''', kw=['overconfidence', 'correlated features', 'calibration', 'generative vs discriminative', 'Ng and Jordan', 'data efficiency'])

K.lesson('versus', 'Naive Bayes compared', f'''
{versus('Three classifiers side by side', ['', 'Naive Bayes', 'Logistic regression', 'KNN'], [
    ['Type', 'Generative (models P(x | y))', 'Discriminative (models P(y | x))', 'Instance based'],
    ['Training', 'One pass of counting', 'Iterative optimisation', 'None'],
    ['Little data', 'Good', 'Can overfit', 'Poor'],
    ['Many features (text)', 'Excellent', 'Good with a penalty', 'Poor'],
    ['Feature interactions', 'No', 'Only if you add them', 'Yes'],
    ['Probabilities', 'Overconfident', 'Well calibrated', 'Rough (share of votes)']],
    'naive Bayes is the fastest strong baseline for text, and logistic regression is usually better when data is plentiful.')}
''', kw=['naive Bayes vs logistic regression', 'naive Bayes vs KNN', 'generative', 'discriminative'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Bayes rule', 'P(c | x) = P(x | c) P(c) / P(x)', 'P(x) is the same for every class, so it can be ignored when comparing.', key=True),
     fx('Naive assumption', 'P(x<sub>1</sub>, ..., x<sub>d</sub> | c) = &Pi;<sub>j</sub> P(x<sub>j</sub> | c)', 'Features independent given the class.', key=True),
     fx('Multinomial likelihood', 'P(w | c) = (n<sub>w,c</sub> + &alpha;) / (n<sub>c</sub> + &alpha;V)', 'Smoothed word share.', key=True),
     fx('Bernoulli likelihood', 'P(x | c) = &Pi;<sub>j</sub> p<sub>jc</sub><sup>x<sub>j</sub></sup> (1 &minus; p<sub>jc</sub>)<sup>1 &minus; x<sub>j</sub></sup>', 'Absent features count through (1 &minus; p).'),
     fx('Log score', 'score(c) = log P(c) + &Sigma; log P(x<sub>j</sub> | c)', 'Pick the largest. No underflow.', key=True))}
{steps('Worked example: the spam filter by hand', [
    'Prior: 4 spam and 4 ham, so P(spam) = P(ham) = 0.5. Vocabulary V = 18, each class has 14 words.',
    'P(free | spam) = (2 + 1) / (14 + 18) = 0.0938. P(free | ham) = (0 + 1) / 32 = 0.0312.',
    'P(money | spam) = 3/32 = 0.0938, P(money | ham) = 2/32 = 0.0625. Same numbers for "now".',
    eq('spam: 0.5 &times; 0.0938<sup>3</sup> = 4.12 &times; 10<sup>&minus;4</sup>, ham: 0.5 &times; 0.0312 &times; 0.0625<sup>2</sup> = 6.1 &times; 10<sup>&minus;5</sup>'),
    'P(spam | message) = 4.12 / (4.12 + 0.61) = 0.871, as the program prints.'])}
{deep('Naive Bayes is a linear classifier', '<p>For multinomial or Bernoulli naive Bayes with two classes, the log odds log P(spam | x) &minus; log P(ham | x) = log(P(spam)/P(ham)) + &Sigma;<sub>j</sub> x<sub>j</sub> log(P(w<sub>j</sub> | spam)/P(w<sub>j</sub> | ham)), which is linear in the counts x<sub>j</sub>. So naive Bayes and logistic regression draw the same kind of boundary. Naive Bayes sets the weights by counting (generative), logistic regression by maximising the conditional likelihood (discriminative). Gaussian naive Bayes with a shared variance per feature is also linear, and with separate variances its boundary is quadratic.</p>')}
''', kw=['Bayes formula', 'naive assumption', 'multinomial likelihood', 'Bernoulli likelihood', 'log score', 'linear classifier'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Naive Bayes counts how often each clue appears with each answer during training, then multiplies the clues for a new example to see which answer is most likely.</p>',
    '<p>Build text classifiers with CountVectorizer and MultinomialNB, use GaussianNB for numbers and BernoulliNB for binary features, and explain smoothing and log probabilities.</p>',
    '<p>Explain why its probabilities are overconfident, show that it is a linear classifier for text, and compare it with logistic regression using the generative vs discriminative view.</p>',
    '<p>Study the Ng and Jordan learning rate results, Bayesian networks that relax the independence assumption, semi supervised naive Bayes with EM (Nigam and others, 2000), and why naive Bayes classifies well even when its independence assumption is badly wrong (Domingos and Pazzani, 1997).</p>')}
{grow('Classify a message by multiplying word probabilities.',
      'Pick the right naive Bayes model and build a smoothed text pipeline.',
      'Analyse its bias, calibration and linear form against discriminative models.')}
''', kw=['beginner', 'expert', 'Bayesian network', 'EM', 'Domingos Pazzani'])

lc(242, 'Valid Anagram', 'valid-anagram', 'e', 'Compare two count tables', 'Two strings are anagrams when every letter appears the same number of times. Build a count table for each and compare them, exactly like comparing word counts per class.', r'''
def is_anagram(s, t):
    if len(s) != len(t):
        return False
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    for ch in t:
        if counts.get(ch, 0) == 0:
            return False
        counts[ch] = counts[ch] - 1
    return True
''', [('is_anagram("anagram", "nagaram")', True), ('is_anagram("rat", "car")', False)])
lc(383, 'Ransom Note', 'ransom-note', 'e', 'Counts as a budget', 'Count the letters in the magazine. Each letter of the note uses one count. If a count would go below zero, the note cannot be made.', r'''
def can_construct(ransom_note, magazine):
    counts = {}
    for ch in magazine:
        counts[ch] = counts.get(ch, 0) + 1
    for ch in ransom_note:
        if counts.get(ch, 0) == 0:
            return False
        counts[ch] = counts[ch] - 1
    return True
''', [('can_construct("a", "b")', False), ('can_construct("aa", "aab")', True)])
lc(819, 'Most Common Word', 'most-common-word', 'e', 'Tokenise, then count', 'Turn punctuation into spaces, lower the case, split into words, skip banned words, and count. This is the same tokenising step CountVectorizer does before naive Bayes.', r'''
def most_common_word(paragraph, banned):
    clean = ""
    for ch in paragraph.lower():
        if ch.isalpha():
            clean = clean + ch
        else:
            clean = clean + " "
    blocked = set(banned)
    counts = {}
    for w in clean.split():
        if w not in blocked:
            counts[w] = counts.get(w, 0) + 1
    return max(counts, key=counts.get)
''', [('most_common_word("Bob hit a ball, the hit BALL flew far after it was hit.", ["hit"])', 'ball'), ('most_common_word("a.", [])', 'a')])
lc(884, 'Uncommon Words from Two Sentences', 'uncommon-words-from-two-sentences', 'e', 'Count words across both texts', 'A word is uncommon when it appears exactly once in the two sentences together. Count all words of both and keep the ones with count 1.', r'''
def uncommon_from_sentences(s1, s2):
    counts = {}
    for w in (s1 + " " + s2).split():
        counts[w] = counts.get(w, 0) + 1
    return sorted([w for w in counts if counts[w] == 1])
''', [('uncommon_from_sentences("this apple is sweet", "this apple is sour")', ['sour', 'sweet']), ('uncommon_from_sentences("apple apple", "banana")', ['banana'])])
lc(1160, 'Find Words That Can Be Formed by Characters', 'find-words-that-can-be-formed-by-characters', 'e', 'Compare counts per word', 'Count the available characters once. A word is good when, for every letter, it needs no more than are available. Add up the lengths of the good words.', r'''
def count_characters(words, chars):
    have = {}
    for ch in chars:
        have[ch] = have.get(ch, 0) + 1
    total = 0
    for word in words:
        need = {}
        for ch in word:
            need[ch] = need.get(ch, 0) + 1
        ok = True
        for ch in need:
            if need[ch] > have.get(ch, 0):
                ok = False
        if ok:
            total = total + len(word)
    return total
''', [('count_characters(["cat", "bt", "hat", "tree"], "atach")', 6), ('count_characters(["hello", "world", "leetcode"], "welldonehoneyr")', 10)])
lc(692, 'Top K Frequent Words', 'top-k-frequent-words', 'm', 'Count, then sort by count and word', 'Count every word. Sort by count from high to low, and alphabetically when counts tie. Keep the first k. This is how you find the most telling words of a class.', r'''
def top_k_frequent(words, k):
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    ordered = sorted(counts, key=lambda w: (-counts[w], w))
    return ordered[:k]
''', [('top_k_frequent(["i", "love", "leetcode", "i", "love", "coding"], 2)', ['i', 'love']), ('top_k_frequent(["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], 4)', ['the', 'is', 'sunny', 'day'])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Training naive Bayes is counting. These problems practise building and comparing count tables: anagrams, using counts as a budget, tokenising and counting words, words that appear once, and the top k most frequent words. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'hash map', 'counting', 'word frequency', 'tokenising'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Naive Bayes</b>: P(c | x) &prop; P(c) &Pi; P(x<sub>j</sub> | c), assuming features are independent given the class.',
    'Training is counting: class priors and per class feature likelihoods. Prediction picks the largest log score.',
    '<b>Laplace smoothing</b> (add &alpha;) stops a single unseen word from making a probability 0.',
    'Add <b>log probabilities</b> instead of multiplying, to avoid underflow.',
    'MultinomialNB for word counts, BernoulliNB for 0 or 1 features, GaussianNB for numbers.',
    'Fast, good with little data and many features, but overconfident and blind to feature interactions.',
    'For text it is a linear classifier, the generative cousin of logistic regression.'],
    'Supervised 2.4 is the support vector machine, which looks for the widest possible gap between classes.')}
{files('Three tasks: a smoothed word probability, a naive Bayes score with logs, and a Gaussian likelihood.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Naive Bayes is based on', ['Gradient descent', 'Bayes rule', 'Decision trees', 'Distances'], 1, 'The name.', 'It applies Bayes rule with an independence assumption.')
K.quiz('e', 'The "naive" assumption is that', ['All classes are equally likely', 'Features are independent given the class', 'Data is normal', 'There are two classes'], 1, 'Independence.', 'The joint likelihood becomes a product of single feature likelihoods.')
K.quiz('e', 'Which naive Bayes suits word counts?', ['GaussianNB', 'MultinomialNB', 'BernoulliNB only', 'None'], 1, 'Counts.', 'MultinomialNB models counts.')
K.quiz('e', 'Training naive Bayes mainly means', ['Many epochs of gradient descent', 'Counting frequencies', 'Storing all examples', 'Building a tree'], 1, 'One pass.', 'Priors and likelihoods come from counts.')
K.quiz('m', 'Why use Laplace smoothing?', ['To speed up training', 'So unseen words do not give a probability of 0', 'To scale features', 'To remove stop words'], 1, 'Zero kills a product.', 'Adding &alpha; keeps every probability above 0.')
K.quiz('m', 'Why add logs of probabilities instead of multiplying?', ['Logs are more accurate for big numbers', 'Products of many small numbers underflow to 0', 'sklearn requires it', 'It changes the prediction'], 1, 'Floating point limits.', '0.01<sup>400</sup> is 0.0 on a computer, its log is &minus;1842.')
K.quiz('m', 'GaussianNB stores, per class and feature', ['A weight', 'A mean and a variance', 'All values', 'A tree'], 1, 'A bell curve.', 'Each likelihood is a normal density.')
K.quiz('m', 'Naive Bayes probabilities are often', ['Perfectly calibrated', 'Too extreme (overconfident)', 'Always 0.5', 'Negative'], 1, 'Correlated features counted twice.', 'The independence assumption multiplies the same evidence several times.')
K.quiz('m', 'BernoulliNB differs from MultinomialNB because it', ['Uses counts', 'Also uses the absence of a feature as evidence', 'Needs scaling', 'Only works with numbers'], 1, '1 &minus; p.', 'Missing words contribute (1 &minus; p) terms.')
K.quiz('h', 'With little training data, naive Bayes often beats logistic regression because', ['It is discriminative', 'It reaches its best error with fewer examples (Ng and Jordan)', 'It uses more parameters', 'It has no assumptions'], 1, 'Generative models converge faster.', 'Its higher bias pays off when data is scarce.')
K.quiz('h', 'For two classes and word counts, the naive Bayes decision boundary is', ['Quadratic', 'Linear in the counts', 'A circle', 'Undefined'], 1, 'Write out the log odds.', 'The log odds are a constant plus a weighted sum of counts.')
K.quiz('h', 'You duplicate every feature column. Naive Bayes probabilities will', ['Stay the same', 'Become more extreme', 'Become 0.5', 'Error out'], 1, 'Each copy is counted as new evidence.', 'The log odds double, pushing probabilities towards 0 or 1.')
K.quiz('x', 'In the style of a Stanford CS229 exam: multinomial naive Bayes with Laplace smoothing, a class with 100 words total and vocabulary 50. A word seen 4 times in that class gets', ['4/100', '5/150', '5/101', '4/150'], 1, '(n + 1)/(N + V).', '(4 + 1)/(100 + 50) = 5/150.')
K.quiz('x', 'In the style of a CMU 10-601 exam: Gaussian naive Bayes where each feature has a separate variance per class gives a decision boundary that is', ['Always linear', 'Quadratic in general', 'Piecewise constant', 'Circular only'], 1, 'Different variances keep the x<sup>2</sup> terms.', 'With a shared variance the quadratic terms cancel and it becomes linear.')

K.calc('e', '6 of 10 training emails are spam. Prior P(spam)?', '0.6', 'Share.', ['6 spam emails.', '10 emails in all.', eq('6 / 10 = 0.6')], check=0.6)
K.calc('e', 'Word appears 3 times in 30 spam words. Unsmoothed P(word | spam)?', '0.1', 'Share of words.', ['3 occurrences.', '30 words.', eq('3 / 30 = 0.1')], check=0.1)
K.calc('e', 'Same word, smoothing &alpha; = 1, vocabulary 20. Smoothed P?', '0.08', '(3 + 1)/(30 + 20).', ['Top 3 + 1 = 4.', 'Bottom 30 + 20 = 50.', eq('4 / 50 = 0.08')], check=0.08)
K.calc('m', 'Prior 0.5, likelihoods 0.2 and 0.1 for spam. Spam score?', '0.01', 'Multiply.', ['0.5 &times; 0.2 = 0.1.', 'Times 0.1.', eq('0.01')], check=0.01)
K.calc('m', 'Scores: spam 0.01, ham 0.04. P(spam | x)?', '0.2', 'Normalise.', ['Sum 0.05.', '0.01 / 0.05.', eq('0.2')], check=0.2)
K.calc('m', 'log score: ln 0.5 + ln 0.1 + ln 0.1, 3 decimals?', '-5.298', 'Add the logs.', ['ln 0.5 = &minus;0.693.', 'ln 0.1 = &minus;2.303, twice is &minus;4.605.', eq('&minus;5.298')], check=-5.298)
K.calc('m', 'Normal density at the mean with variance 1, 3 decimals?', '0.399', '1/&radic;(2&pi;).', ['At the mean the exponent is 0.', '1 / &radic;6.283.', eq('0.399')], check=0.399)
K.calc('h', 'BernoulliNB: p(free | spam) = 0.7 and the word is absent. Factor for that feature?', '0.3', '1 &minus; p.', ['Absent, so use 1 &minus; p.', '1 &minus; 0.7.', eq('0.3')], check=0.3)
K.calc('h', 'Log odds of spam: prior part 0, words add ln 3 and ln 2. Probability of spam?', '0.857', 'odds = e<sup>log odds</sup>.', ['ln 3 + ln 2 = ln 6, so the odds are 6.', 'p = 6 / (1 + 6).', eq('0.857')], check=0.857)
K.calc('x', 'In the style of an MIT 6.036 problem: 2 classes, 1,000 vocabulary words, multinomial NB. How many word likelihood numbers are learned?', '2000', 'One per word per class.', ['1,000 words.', '2 classes.', eq('2,000 (plus 2 priors)')], check=2000)

K.assign('wordprob', 'e', 'A smoothed word probability',
         '<p>Write <code>word_prob(word, class_words, vocab_size, alpha)</code>. class_words is the list of all words in one class. Return (count of word + alpha) / (len(class_words) + alpha &times; vocab_size), rounded to 4 decimals.</p>',
         '''
def word_prob(word, class_words, vocab_size, alpha):
    # your code here
    pass
''', [('word_prob("free", ["win", "free", "free", "money"], 10, 1)', 0.2143), ('word_prob("lunch", ["win", "free"], 10, 1)', 0.0833), ('word_prob("win", ["win", "win"], 5, 0)', 1.0)],
         '''
def word_prob(word, class_words, vocab_size, alpha):
    count = 0
    for w in class_words:
        if w == word:
            count = count + 1
    return round((count + alpha) / (len(class_words) + alpha * vocab_size), 4)
''', 'Count the word, then apply the smoothing formula.', '<p>With alpha = 0, any unseen word gets probability 0. With alpha = 1 it gets a small share.</p>')
K.assign('nbscore', 'm', 'A naive Bayes decision with logs',
         '<p>Write <code>nb_predict(priors, likelihoods, words)</code>. priors maps class to P(class). likelihoods maps class to a dictionary of word to P(word | class). Add log P(class) and log P(word | class) for each word, and return the class with the largest log score.</p>',
         '''
import math


def nb_predict(priors, likelihoods, words):
    # your code here
    pass
''', [('nb_predict({"spam": 0.5, "ham": 0.5}, {"spam": {"free": 0.09, "lunch": 0.01}, "ham": {"free": 0.03, "lunch": 0.06}}, ["free", "free"])', 'spam'), ('nb_predict({"spam": 0.5, "ham": 0.5}, {"spam": {"free": 0.09, "lunch": 0.01}, "ham": {"free": 0.03, "lunch": 0.06}}, ["lunch"])', 'ham'), ('nb_predict({"spam": 0.9, "ham": 0.1}, {"spam": {"hi": 0.01}, "ham": {"hi": 0.05}}, ["hi"])', 'spam')],
         '''
import math


def nb_predict(priors, likelihoods, words):
    best = None
    best_score = None
    for c in priors:
        score = math.log(priors[c])
        for w in words:
            score = score + math.log(likelihoods[c][w])
        if best_score is None or score > best_score:
            best = c
            best_score = score
    return best
''', 'Loop over classes. Start from log of the prior and add log of each word likelihood. Keep the best.', '<p>The third test shows a strong prior winning: "hi" is 5 times likelier in ham, but spam is 9 times likelier to start with.</p>')
K.assign('gausslik', 'm', 'Gaussian likelihood',
         '<p>Write <code>gauss_likelihood(x, mean, var)</code> that returns the normal density (1/&radic;(2&pi; var)) e<sup>&minus;(x &minus; mean)<sup>2</sup>/(2 var)</sup>, rounded to 4 decimals.</p>',
         '''
import math


def gauss_likelihood(x, mean, var):
    # your code here
    pass
''', [('gauss_likelihood(0, 0, 1)', 0.3989), ('gauss_likelihood(1, 0, 1)', 0.242), ('gauss_likelihood(5, 5, 4)', 0.1995)],
         '''
import math


def gauss_likelihood(x, mean, var):
    top = math.exp(-((x - mean) ** 2) / (2 * var))
    return round(top / math.sqrt(2 * math.pi * var), 4)
''', 'Compute the exponent part and divide by the square root of 2&pi; var.', '<p>GaussianNB multiplies one of these per feature with the class prior.</p>')

K.must('Rule', 'P(c | x) &prop; P(c)&Pi;P(x<sub>j</sub> | c). Features independent given the class. Pick argmax of log P(c) + &Sigma;log P(x<sub>j</sub> | c).')
K.must('Smoothing', 'P(w | c) = (n<sub>w,c</sub> + &alpha;)/(n<sub>c</sub> + &alpha;V). Prevents zeros. Use logs to avoid underflow.')
K.must('Variants', 'MultinomialNB counts (text), BernoulliNB 0 or 1 (absence counts), GaussianNB numbers (mean, variance), ComplementNB imbalanced text.')
K.must('Strengths', 'One pass of counting, little data, many features, no scaling. Great text baseline.')
K.must('Weaknesses', 'Overconfident probabilities, no feature interactions, correlated features double counted. Calibrate if probabilities matter.')
K.must('Theory', 'Generative. Linear boundary for text. Ng and Jordan: faster to its (higher) best error than logistic regression.')

T = K.topic(
    slug='ml-naive-bayes', topic='ml-naive-bayes', step=(2, 'Classification', 'ml-s2', 'Predict categories: yes or no, spam or not, or which of many classes, with four very different families of models.', 'Intermediate'),
    title='Naive Bayes: classify by counting clues', short='Naive Bayes', badge='2.3', minutes=50,
    lead='Learn the classic spam filter: Bayes rule with the naive independence assumption, multinomial naive Bayes for text, smoothing and log probabilities, Gaussian and Bernoulli versions, and why its probabilities are overconfident.',
    desc='naive Bayes, Bayes rule, conditional independence, priors and likelihoods, MultinomialNB, CountVectorizer, text classification, Laplace smoothing, log probabilities and underflow, GaussianNB, BernoulliNB, CategoricalNB, ComplementNB, overconfidence, generative vs discriminative, Ng and Jordan, linear boundary.',
    summary='Bayes rule as a classifier, text with multinomial naive Bayes, smoothing, logs, Gaussian and Bernoulli versions, and its limits.',
    keywords=['naive Bayes', 'Bayes rule', 'MultinomialNB', 'GaussianNB', 'BernoulliNB', 'Laplace smoothing', 'spam filter', 'text classification', 'log probabilities', 'generative model'],
    recap='<p>Naive Bayes multiplies simple clues with a prior. It is fast and strong for text, but do not trust its exact probabilities.</p>',
    added='2026-11-13', leet=leet_items())
