# Foundations 1.1: what machine learning is. Checked against Tom Mitchell, Machine Learning (1997) chapter 1 for the
# definition (task T, experience E, performance P), Arthur Samuel's 1959 checkers paper in the IBM Journal, the
# scikit-learn 1.8 user guide (estimator API, LinearRegression, KNeighborsClassifier), the Google Machine Learning Crash
# Course (framing, labels, features) and Stanford CS229 lecture notes (supervised learning set up).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items

chapter('ml-intro')
K = Kit()

K.code('rules_vs_learning', r'''
# Way 1: a person writes the rule by hand
def spam_by_rule(message):
    words = message.lower().split()
    if "free" in words and "win" in words:
        return "spam"
    return "not spam"

# Way 2: the machine counts words in examples and learns the rule itself
examples = [
    ("win a free phone now", "spam"),
    ("free tickets win big", "spam"),
    ("claim your free prize", "spam"),
    ("lunch at one tomorrow", "not spam"),
    ("see you at the meeting", "not spam"),
    ("your free time this week", "not spam"),
]

spam_count = {}
ham_count = {}
for text, label in examples:
    for word in text.split():
        if label == "spam":
            spam_count[word] = spam_count.get(word, 0) + 1
        else:
            ham_count[word] = ham_count.get(word, 0) + 1

def spam_by_learning(message):
    score = 0
    for word in message.lower().split():
        score = score + spam_count.get(word, 0) - ham_count.get(word, 0)
    if score > 0:
        return "spam"
    return "not spam"

for msg in ["claim a free prize", "win free cash", "free lunch tomorrow"]:
    print(msg, "| rule:", spam_by_rule(msg), "| learned:", spam_by_learning(msg))
''')

K.code('learning_loop', r'''
# Learn the rule "marks = w x hours" from examples, by guess, check, adjust, repeat
hours = [1, 2, 3, 4, 5]
marks = [12, 19, 31, 38, 52]

w = 2.0                  # a bad first guess
learning_rate = 0.02

for round_number in range(6):
    # 1. check: how wrong is the guess? (mean squared error)
    error = 0
    for h, m in zip(hours, marks):
        error = error + (w * h - m) ** 2
    error = error / len(hours)

    # 2. which way to move: the slope of the error
    slope = 0
    for h, m in zip(hours, marks):
        slope = slope + 2 * (w * h - m) * h
    slope = slope / len(hours)

    print("round", round_number, "w =", round(w, 2), "error =", round(error, 1))
    # 3. adjust the guess a little, against the slope
    w = w - learning_rate * slope

print("learned rule: marks =", round(w, 2), "x hours")
print("6 hours of study gives about", round(w * 6), "marks")
''')

K.code('words_of_ml', r'''
# A tiny dataset: each row is one example (one house)
houses = [
    # size_m2, rooms, age_years -> price in lakh
    {"size_m2": 50, "rooms": 1, "age_years": 10, "price": 30},
    {"size_m2": 80, "rooms": 2, "age_years": 5, "price": 52},
    {"size_m2": 120, "rooms": 3, "age_years": 2, "price": 80},
    {"size_m2": 65, "rooms": 2, "age_years": 20, "price": 35},
]

feature_names = ["size_m2", "rooms", "age_years"]   # the inputs (features)
label_name = "price"                                 # the answer we want (label or target)

X = []   # features of every example
y = []   # label of every example
for house in houses:
    row = []
    for name in feature_names:
        row.append(house[name])
    X.append(row)
    y.append(house[label_name])

print("number of examples:", len(X))
print("number of features:", len(feature_names))
print("X =", X)
print("y =", y)
print("first example: features", X[0], "label", y[0])
''')

K.code('regression_or_classification', r'''
# Regression: the answer is a number
sizes = [50, 80, 120]
prices = [30, 52, 80]
price_per_m2 = sum(prices) / sum(sizes)            # a very simple model with one parameter
print("predicted price for 100 m2:", round(price_per_m2 * 100, 1), "lakh")

# Classification: the answer is a category
fruits = [
    (150, "smooth", "apple"),
    (170, "smooth", "apple"),
    (130, "bumpy", "orange"),
    (140, "bumpy", "orange"),
]

def guess_fruit(weight, skin):
    # copy the label of the most similar example (fewest differences)
    best_label = None
    best_distance = None
    for w, s, label in fruits:
        distance = abs(w - weight) / 10
        if s != skin:
            distance = distance + 5
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_label = label
    return best_label

print("160 g, smooth skin ->", guess_fruit(160, "smooth"))
print("135 g, bumpy skin  ->", guess_fruit(135, "bumpy"))
''')

K.code('memorise_or_learn', r'''
# Training data: hours studied -> passed (1) or failed (0)
train = [(1, 0), (2, 0), (3, 0), (5, 1), (6, 1), (8, 1)]
test = [(4, 1), (7, 1), (2.5, 0), (9, 1)]   # new students the model never saw

# Model A memorises: it stores the answers in a table
table_of_answers = {}
for h, passed in train:
    table_of_answers[h] = passed

def memoriser(h):
    return table_of_answers.get(h, "no idea")

# Model B learns a rule: pass when hours are at least a cut off
best_cut = None
best_correct = -1
for cut in [1, 2, 3, 4, 5, 6, 7, 8]:
    correct = 0
    for h, passed in train:
        guess = 1 if h >= cut else 0
        if guess == passed:
            correct = correct + 1
    if correct > best_correct:
        best_correct = correct
        best_cut = cut

def rule_learner(h):
    return 1 if h >= best_cut else 0

print("learned cut off:", best_cut, "hours")
for h, passed in test:
    print("hours", h, "true", passed, "| memoriser:", memoriser(h), "| rule:", rule_learner(h))
''')

K.code('first_sklearn', r'''
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsClassifier

# Regression with scikit-learn: hours -> marks
X = [[1], [2], [3], [4], [5]]       # features: a list of rows, one row per example
y = [12, 19, 31, 38, 52]            # labels
model = LinearRegression()          # 1. choose a model
model.fit(X, y)                     # 2. learn from the examples
print("slope:", round(model.coef_[0], 2), "intercept:", round(model.intercept_, 2))
print("predict 6 hours:", round(model.predict([[6]])[0], 1))   # 3. predict

# Classification with scikit-learn: weight in grams, skin (0 smooth, 1 bumpy) -> fruit
X2 = [[150, 0], [170, 0], [130, 1], [140, 1]]
y2 = ["apple", "apple", "orange", "orange"]
clf = KNeighborsClassifier(n_neighbors=1)
clf.fit(X2, y2)
print("predict [160, 0]:", clf.predict([[160, 0]])[0])
print("predict [135, 1]:", clf.predict([[135, 1]])[0])
''')

K.code('measure_a_model', r'''
# How good is a model? Compare its answers with the true answers.
true_marks = [12, 19, 31, 38, 52]
predicted = [9.6, 19.6, 29.6, 39.6, 49.6]

total = 0
for t, p in zip(true_marks, predicted):
    total = total + (t - p) ** 2
mse = total / len(true_marks)
print("mean squared error:", round(mse, 2))

true_labels = ["spam", "ham", "spam", "ham", "ham"]
guesses = ["spam", "ham", "ham", "ham", "spam"]
right = 0
for t, g in zip(true_labels, guesses):
    if t == g:
        right = right + 1
print("accuracy:", right, "of", len(true_labels), "=", right / len(true_labels))
''')

K.lesson('idea', 'What machine learning is', f'''
{src('Tom Mitchell, Machine Learning (1997) chapter 1, Arthur Samuel (1959), the scikit-learn 1.8 user guide and the Google Machine Learning Crash Course.')}
{wwh('<b>Machine learning</b> (ML) is a way to make a computer good at a task by showing it examples, instead of writing every rule by hand. The computer finds the pattern in the examples and uses it on new cases.',
     'Many tasks have rules that are too many, too fuzzy or too fast changing for a person to write down: spotting a face, reading handwriting, catching spam, guessing tomorrow’s sales. People can do these tasks but cannot explain the exact rules. ML lets the data teach the rules.',
     'We collect examples, pick a <b>model</b> (a rule with adjustable numbers called <b>parameters</b>), and let a learning method change those numbers until the model’s answers match the examples well. Then we use the trained model on new data.')}
<p>Tom Mitchell gave the definition most courses use: a program <b>learns</b> from experience E for a task T, measured by P, if its performance on T, measured by P, gets better with experience E. For a spam filter, T is "sort emails", E is "emails people already marked", and P is "the share of emails sorted correctly". If P goes up as E grows, the program is learning.</p>
{scene('your email spam folder', '<p>Nobody at your email company wrote a rule for every spam message in the world. Spammers change their words every day. Instead, every time someone clicks "Report spam", that email becomes a new example. The filter keeps learning which words, links and senders show up in spam, so it catches new tricks without a programmer writing new rules.</p>')}
<p>The program below shows both ways side by side. The hand written rule only knows the two words a person thought of. The learned rule counted words in six examples and so it also knows that "claim" and "prize" point to spam.</p>
{run('rules_vs_learning')}
{note('Machine learning is not magic and not always the right tool. If a simple fixed rule works (for example "a password must have 8 characters"), write the rule. Use ML when the rule is hard to write but examples are easy to get.', 'tip')}
''', kw=['machine learning', 'definition', 'Tom Mitchell', 'task experience performance', 'rules vs learning', 'spam filter'])

K.lesson('loop', 'The learning loop: guess, check, adjust, repeat', f'''
<p>Almost every ML method, from a straight line to a huge chatbot, learns with the same four step loop. Press <b>Step</b> to watch it find the rule between study hours and marks. Change the data or the learning rate and play it again.</p>
{viz('mlloop')}
{wwh('The <b>learning loop</b> is the repeated cycle of making a prediction, measuring how wrong it is with a <b>loss</b> (an error score), and changing the parameters a little to make the loss smaller.',
     'We almost never know the best parameters in advance. Trying every possible value would take forever. The loop lets the model walk towards good values one small step at a time.',
     'The slope of the loss tells which direction makes the loss smaller. We move the parameter a small amount, called the <b>learning rate</b>, in that direction. This method is called <b>gradient descent</b> and you will meet it in almost every chapter.')}
{run('learning_loop')}
{steps('Worked example: one round of the loop by hand', [
    'Data: hours 1 and 2, marks 10 and 20. First guess w = 5. Learning rate 0.1.',
    'Predictions: 5 &times; 1 = 5 and 5 &times; 2 = 10. Errors: 5 &minus; 10 = &minus;5 and 10 &minus; 20 = &minus;10.',
    'Loss (mean squared error) = ((&minus;5)<sup>2</sup> + (&minus;10)<sup>2</sup>) / 2 = (25 + 100) / 2 = 62.5.',
    'Slope of the loss = (2 &times; (&minus;5) &times; 1 + 2 &times; (&minus;10) &times; 2) / 2 = (&minus;10 &minus; 40) / 2 = &minus;25.',
    eq('new w = 5 &minus; 0.1 &times; (&minus;25) = 7.5'),
    'With w = 7.5 the predictions are 7.5 and 15, much closer to 10 and 20. The true best value is w = 10.'])}
{note('A learning rate that is too big makes the guess jump past the best value and the loss can grow. One that is too small makes learning very slow. Choosing it well is part of the job.', 'warn')}
''', kw=['learning loop', 'loss', 'gradient descent', 'learning rate', 'parameters', 'training'])

K.lesson('types', 'The kinds of machine learning', f'''
{viz('mltypes')}
{table(['Kind', 'What the data looks like', 'What it learns', 'Everyday example'], [
    ['Supervised', 'Examples with the right answer (a label)', 'A map from inputs to answers', 'Spam filter, house prices, face unlock'],
    ['Unsupervised', 'Examples with no answers', 'Groups, structure, unusual points', 'Customer groups, odd card payments'],
    ['Semi supervised', 'A few labelled examples and many unlabelled ones', 'Uses the unlabelled data to help the labelled task', 'Photo apps that ask you to name a face once, then find it everywhere'],
    ['Self supervised', 'Raw data where the label is hidden inside the data itself', 'Predict a hidden part from the rest', 'Language models that guess the next word'],
    ['Reinforcement', 'No fixed data. An agent acts and gets rewards', 'A policy: what to do in each situation', 'Game playing, robots, ad choice']])}
<p>Inside supervised learning there are two big jobs. <b>Regression</b> predicts a number (a price, a temperature). <b>Classification</b> predicts a category (spam or not, cat or dog). The Supervised section of this subject covers both. Unsupervised and Reinforcement learning each have their own section.</p>
{run('regression_or_classification')}
{note('A quick test: "Is there a right answer for each example in my data?" Yes means supervised. No means unsupervised. "Does the system learn by acting and getting rewards?" means reinforcement.', 'exam')}
''', kw=['supervised', 'unsupervised', 'reinforcement', 'semi supervised', 'self supervised', 'regression', 'classification'])

K.lesson('words', 'The words of machine learning', f'''
{run('words_of_ml')}
{table(['Word', 'Plain meaning', 'In the house example'], [
    ['Example (sample, row, instance)', 'One case in the data', 'One house'],
    ['Feature (input, attribute, column)', 'A measured fact we give the model', 'size_m2, rooms, age_years'],
    ['Label (target, output, y)', 'The answer we want to predict', 'price'],
    ['Dataset', 'All the examples together', 'The four houses'],
    ['X and y', 'The table of features and the list of labels', 'X has 4 rows and 3 columns, y has 4 numbers'],
    ['Model', 'A rule with adjustable numbers', 'price = a &times; size + b &times; rooms + c'],
    ['Parameters (weights)', 'The adjustable numbers the model learns', 'a, b and c'],
    ['Hyperparameters', 'Settings we choose before learning', 'The learning rate, the number of rounds'],
    ['Training (fitting)', 'Finding good parameters from the data', 'model.fit(X, y)'],
    ['Prediction (inference)', 'Using the trained model on new input', 'model.predict(new_house)'],
    ['Loss (cost, error)', 'A number that says how wrong the model is', 'Average squared price error']])}
{note('Parameters are learned by the model. Hyperparameters are set by you. The learning rate is a hyperparameter, the slope of a line is a parameter. Interviewers love this question.', 'exam')}
''', kw=['feature', 'label', 'target', 'example', 'dataset', 'X and y', 'model', 'parameter', 'hyperparameter', 'training', 'inference', 'loss'])

K.lesson('generalise', 'Learning, not memorising: generalisation', f'''
{wwh('<b>Generalisation</b> means doing well on new data the model has never seen, not only on the examples it trained on.',
     'A model that only remembers its training examples is useless in real life, because real inputs are always new. A face unlock that works only on the exact photos you gave it would fail the moment you change your hair.',
     'We keep some data hidden from the model (a <b>test set</b>) and measure the model on it. A model that does great on training data but badly on test data has <b>overfitted</b>: it learned the noise and the details, not the pattern.')}
{run('memorise_or_learn')}
{scene('learning for an exam', '<p>Two students prepare for a maths exam. The first memorises the answers to last year’s paper. The second learns how to solve each type of question. On last year’s paper both score 100. On the new paper the first student is lost, while the second does well. The first student overfitted. ML models face exactly this risk, which is why we always test them on unseen data.</p>')}
{note('Never measure a model only on its training data. The score will look great and mean nothing. Always keep a separate test set, and look at it only at the end.', 'warn')}
''', kw=['generalisation', 'overfitting', 'underfitting', 'test set', 'training set', 'memorising'])

K.lesson('sklearn', 'Your first models with scikit-learn', f'''
<p><b>scikit-learn</b> is the most used Python library for classic machine learning. Every model in it follows the same three steps: make the model, call <code>fit(X, y)</code> to learn, call <code>predict(X_new)</code> to use it. Once you know these three steps, you can use any of its hundreds of models.</p>
{run('first_sklearn')}
{table(['Step', 'Code', 'What happens'], [
    ['Choose', 'model = LinearRegression()', 'Make an empty model with its settings (hyperparameters)'],
    ['Learn', 'model.fit(X, y)', 'The model finds its parameters from the examples'],
    ['Use', 'model.predict(X_new)', 'The model gives answers for new rows'],
    ['Check', 'model.score(X_test, y_test)', 'R<sup>2</sup> for regression, accuracy for classification']])}
{note('X must be two dimensional: a list of rows, even when there is only one feature. Write [[1], [2], [3]], not [1, 2, 3]. Passing a flat list is the most common first error in scikit-learn.', 'warn')}
''', kw=['scikit-learn', 'sklearn', 'fit', 'predict', 'score', 'LinearRegression', 'KNeighborsClassifier', 'estimator API'])

K.lesson('where', 'Where machine learning is used, and a short history', f'''
{table(['Area', 'What ML does there'], [
    ['Phones', 'Face unlock, voice assistants, the keyboard that guesses your next word, photo search'],
    ['Shopping and streaming', 'Recommends products, songs and videos you are likely to like'],
    ['Banks', 'Flags card payments that look like fraud, scores loan applications'],
    ['Health', 'Reads X rays and eye scans, predicts which patients need care first'],
    ['Maps and transport', 'Predicts traffic and arrival times, plans delivery routes'],
    ['Farming and weather', 'Predicts rain and crop yields, spots plant disease from photos'],
    ['Factories', 'Predicts when a machine will break so it is fixed in time'],
    ['Language', 'Translation, chatbots, summaries, search']])}
{table(['Year', 'Milestone'], [
    ['1943', 'McCulloch and Pitts describe an artificial neuron'],
    ['1958', 'Frank Rosenblatt publishes the perceptron, a neuron that learns its weights'],
    ['1959', 'Arthur Samuel’s checkers program improves by playing itself. He uses the words "machine learning"'],
    ['1967', 'Cover and Hart study the nearest neighbour rule'],
    ['1984', 'Breiman and others publish CART decision trees'],
    ['1986', 'Rumelhart, Hinton and Williams make backpropagation popular for training neural networks'],
    ['1995', 'Cortes and Vapnik publish support vector machines'],
    ['2001', 'Breiman publishes random forests'],
    ['2012', 'A deep network (AlexNet) wins the ImageNet image contest by a large margin'],
    ['2016', 'AlphaGo beats a world champion at Go, using deep and reinforcement learning'],
    ['2017', 'The transformer model is published. It powers today’s language models'],
    ['2022', 'Chatbots built on large language models reach millions of people']])}
''', kw=['applications', 'history', 'Samuel', 'perceptron', 'AlexNet', 'transformer', 'where ML is used'])

K.lesson('versus', 'Machine learning compared with similar ideas', f'''
{versus('ML and its neighbours', ['', 'Traditional programming', 'Machine learning', 'Statistics', 'Deep learning'], [
    ['Who writes the rule', 'A person', 'The computer, from examples', 'A person picks a model, data fits it', 'The computer, with many layers'],
    ['Input to the process', 'Rules and data', 'Data and answers', 'Data and a model', 'Lots of data and answers'],
    ['Main goal', 'Exact, explainable steps', 'Good predictions on new data', 'Understand and test relationships', 'Predictions on images, sound, text'],
    ['Data needed', 'None', 'Hundreds to millions of rows', 'Often small samples', 'Usually very large'],
    ['Best when', 'Rules are clear', 'Rules are hard to write', 'You must explain cause and certainty', 'Data is raw: pixels, audio, words']],
    'Artificial intelligence is the big goal (machines that act smart). Machine learning is the main way we reach it today. Deep learning is one family of ML methods. Write rules when you can, use ML when you cannot.')}
{note('AI, ML and deep learning are nested: every deep learning model is a machine learning model, and machine learning is one part of artificial intelligence. The Artificial Intelligence subject draws these as nested circles.', 'tip')}
''', kw=['ML vs programming', 'ML vs statistics', 'AI vs ML vs deep learning', 'comparison'])

K.lesson('maths', 'The maths of learning', f'''
<p>You do not need hard maths to start, but these four lines appear in every chapter. Read them slowly. They are the whole idea of supervised learning written as formulas.</p>
{fxs(fx('A model', 'ŷ = f(x, θ)', 'x is the input, θ (theta) are the parameters, ŷ (y hat) is the prediction.', key=True),
     fx('Mean squared error (loss for numbers)', 'MSE = (1/n) &Sigma; (y<sub>i</sub> &minus; ŷ<sub>i</sub>)<sup>2</sup>', 'Average of the squared gaps between true answers y and predictions ŷ over n examples.', key=True),
     fx('Accuracy (score for categories)', 'accuracy = correct predictions / all predictions', 'Between 0 and 1. Higher is better.'),
     fx('One gradient descent step', 'θ<sub>new</sub> = θ &minus; η &times; (slope of the loss at θ)', 'η (eta) is the learning rate. Move against the slope, because the slope points uphill.', key=True),
     fx('Learning as a search', 'θ* = the θ that makes the average loss on the training data smallest', 'Training is finding θ*. Generalisation asks if θ* also works on new data.'))}
{run('measure_a_model')}
{steps('Worked example: score a tiny model', [
    'True prices 30, 50, 80. Predicted prices 35, 45, 80.',
    'Gaps: 30 &minus; 35 = &minus;5, 50 &minus; 45 = 5, 80 &minus; 80 = 0.',
    'Squares: 25, 25, 0. Sum = 50.',
    eq('MSE = 50 / 3 &asymp; 16.67'),
    'The root of the MSE, about 4.08, is in the same unit as the price. So the model is off by about 4 lakh on a typical house.'])}
{deep('Why squared errors?', '<p>Squaring makes every gap positive, so errors above and below do not cancel. It punishes big mistakes much more than small ones (a gap of 10 counts 100 times a gap of 1). It also gives a smooth curve with a single lowest point for a straight line model, which makes gradient descent easy. If the noise in the data follows a bell curve (normal distribution), minimising squared error is the same as choosing the most likely parameters (maximum likelihood). You will prove this in Foundations 2.3.</p>')}
''', kw=['model formula', 'theta', 'y hat', 'MSE', 'accuracy', 'gradient descent formula', 'empirical risk'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Machine learning means teaching a computer with examples instead of rules. It looks at many examples, finds the pattern, and uses it to answer new questions.</p>',
    '<p>A model has parameters. Training changes the parameters to make a loss small on training data, usually with gradient descent. We judge a model on separate test data, because the real goal is to generalise.</p>',
    '<p>Supervised learning is empirical risk minimisation: pick θ to minimise the average loss over n samples drawn from an unknown distribution. The gap between training loss and true loss depends on how flexible the model family is (its capacity) and on n. Regularisation and validation control that gap.</p>',
    '<p>Learning theory bounds the gap. In the PAC framework (Valiant, 1984) a finite hypothesis class H needs about (1/&epsilon;)(ln|H| + ln(1/&delta;)) samples to be probably (1 &minus; &delta;) approximately (&epsilon;) correct, and VC dimension extends this to infinite classes. The no free lunch theorem (Wolpert, 1996) says no learner is best on every possible problem: every method relies on an inductive bias that matches some worlds and not others.</p>')}
{grow('Explain ML in your own words, name the three kinds of learning and spot features and labels in a table.',
      'Run the learning loop by hand, use fit and predict in scikit-learn, and explain overfitting with a test set.',
      'Write supervised learning as risk minimisation, explain inductive bias and no free lunch, and reason about sample size with PAC bounds.')}
{deep('Inductive bias and no free lunch', '<p>From a finite set of examples, infinitely many rules fit the data perfectly. A learner must prefer some rules over others, for example "simple lines first" or "nearby points share labels". This preference is its <b>inductive bias</b>. The no free lunch theorem shows that, averaged over every possible problem, all learners do equally well. ML works in practice because real problems are not random: nearby inputs usually have similar outputs, and simple explanations usually beat complicated ones.</p>')}
''', kw=['beginner', 'expert', 'empirical risk minimisation', 'PAC learning', 'VC dimension', 'no free lunch', 'inductive bias'])

lc(1491, 'Average Salary Excluding the Minimum and Maximum Salary', 'average-salary-excluding-the-minimum-and-maximum-salary', 'e', 'Robust average', 'Add everything, then take away the smallest and the largest before you divide by n &minus; 2. Dropping extreme values is how a trimmed mean protects a model from outliers.', r'''
def average(salary):
    total = 0
    smallest = salary[0]
    largest = salary[0]
    for s in salary:
        total = total + s
        if s < smallest:
            smallest = s
        if s > largest:
            largest = s
    return (total - smallest - largest) / (len(salary) - 2)
''', [('average([4000, 3000, 1000, 2000])', 2500.0), ('average([1000, 2000, 3000])', 2000.0)])
lc(643, 'Maximum Average Subarray I', 'maximum-average-subarray-i', 'e', 'Sliding window (a moving average)', 'Keep the sum of the last k numbers. Add the new number and take away the one that leaves the window. This is how a moving average feature is computed fast.', r'''
def find_max_average(nums, k):
    window = 0
    for i in range(k):
        window = window + nums[i]
    best = window
    for i in range(k, len(nums)):
        window = window + nums[i] - nums[i - k]
        if window > best:
            best = window
    return best / k
''', [('find_max_average([1, 12, -5, -6, 50, 3], 4)', 12.75), ('find_max_average([5], 1)', 5.0)])
lc(1502, 'Can Make Arithmetic Progression From Sequence', 'can-make-arithmetic-progression-from-sequence', 'e', 'Sort, then check one constant step', 'After sorting, every gap must be the same. A sequence like this fits a straight line exactly, the simplest pattern a model can learn.', r'''
def can_make_arithmetic_progression(arr):
    arr = sorted(arr)
    step = arr[1] - arr[0]
    for i in range(2, len(arr)):
        if arr[i] - arr[i - 1] != step:
            return False
    return True
''', [('can_make_arithmetic_progression([3, 5, 1])', True), ('can_make_arithmetic_progression([1, 2, 4])', False)])
lc(896, 'Monotonic Array', 'monotonic-array', 'e', 'One pass with two flags', 'Keep two flags, "can still be going up" and "can still be going down". Any drop clears the first, any rise clears the second. Checking a trend like this is a common data sanity check.', r'''
def is_monotonic(nums):
    going_up = True
    going_down = True
    for i in range(1, len(nums)):
        if nums[i] < nums[i - 1]:
            going_up = False
        if nums[i] > nums[i - 1]:
            going_down = False
    return going_up or going_down
''', [('is_monotonic([1, 2, 2, 3])', True), ('is_monotonic([6, 5, 4, 4])', True), ('is_monotonic([1, 3, 2])', False)])
lc(1984, 'Minimum Difference Between Highest and Lowest of K Scores', 'minimum-difference-between-highest-and-lowest-of-k-scores', 'e', 'Sort, then slide a window of size k', 'After sorting, the best k scores sit next to each other. Check every window of k neighbours and keep the smallest spread.', r'''
def minimum_difference(nums, k):
    nums = sorted(nums)
    best = nums[k - 1] - nums[0]
    for i in range(1, len(nums) - k + 1):
        spread = nums[i + k - 1] - nums[i]
        if spread < best:
            best = spread
    return best
''', [('minimum_difference([90], 1)', 0), ('minimum_difference([9, 4, 1, 7], 2)', 2)])
lc(2148, 'Count Elements With Strictly Smaller and Greater Elements', 'count-elements-with-strictly-smaller-and-greater-elements', 'e', 'Find min and max, then count', 'An element counts when it is not the minimum and not the maximum. Finding the range of a feature is the first step of scaling it.', r'''
def count_elements(nums):
    smallest = min(nums)
    largest = max(nums)
    count = 0
    for x in nums:
        if smallest < x < largest:
            count = count + 1
    return count
''', [('count_elements([11, 7, 2, 15])', 2), ('count_elements([-3, 3, 3, 90])', 2)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>These warm up problems practise the small data skills every ML program needs: averages that ignore outliers, moving averages, spotting a straight line pattern, checking a trend and finding a range. The page gives only a hint. Solve each one on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'sliding window', 'moving average', 'trimmed mean', 'monotonic'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Machine learning</b> makes a computer good at a task by learning from examples instead of hand written rules.',
    'Mitchell’s definition: performance P on task T improves with experience E.',
    'Every model learns with the same loop: <b>guess, measure the loss, adjust the parameters, repeat</b>. Gradient descent moves each parameter against the slope of the loss, by the learning rate.',
    'Supervised learning uses labelled examples (regression for numbers, classification for categories). Unsupervised learning finds structure without labels. Reinforcement learning learns from rewards.',
    'Features are the inputs, the label is the answer, parameters are learned, hyperparameters are chosen by you.',
    'The goal is <b>generalisation</b>: do well on new data. Always test on data the model never saw.',
    'scikit-learn models all use the same steps: create, fit(X, y), predict(X_new), score.'],
    'Foundations 1.2 walks through a whole ML project, from framing the problem to a deployed model.')}
{files('Three tasks: mean squared error by hand, accuracy by hand, and a "predict the most common class" baseline model.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What does a machine learning model learn from?', ['Rules typed by a programmer', 'Examples (data)', 'The internet only', 'Random guesses'], 1, 'Think of the spam filter.', 'A model learns patterns from examples. Rules are what traditional programs use.')
K.quiz('e', 'In a house price table, what is the price column?', ['A feature', 'The label (target)', 'A hyperparameter', 'The loss'], 1, 'It is what we want to predict.', 'The value we want to predict is the label.')
K.quiz('e', 'Predicting tomorrow’s temperature in degrees is which task?', ['Classification', 'Regression', 'Clustering', 'Reinforcement learning'], 1, 'The answer is a number.', 'A number output means regression.')
K.quiz('e', 'Which scikit-learn method trains a model?', ['predict()', 'fit()', 'train()', 'learn()'], 1, 'Same name for every model.', 'fit(X, y) learns the parameters.')
K.quiz('m', 'Grouping customers by buying habits when nobody gave group names is', ['Supervised learning', 'Unsupervised learning', 'Reinforcement learning', 'Regression'], 1, 'Are there labels?', 'No labels, find structure: unsupervised (clustering).')
K.quiz('m', 'Which one is a hyperparameter?', ['The slope of a fitted line', 'The learning rate', 'A weight in a network', 'The intercept'], 1, 'Chosen before training.', 'You set the learning rate. The others are learned.')
K.quiz('m', 'A model scores 99% on training data and 60% on new data. This is', ['Underfitting', 'Overfitting', 'Good generalisation', 'Data leakage proof'], 1, 'It remembered the training set.', 'A big gap between training and test scores means overfitting.')
K.quiz('m', 'In gradient descent, if the slope of the loss at w is positive, w should', ['Increase', 'Decrease', 'Stay the same', 'Become zero'], 1, 'The slope points uphill.', 'w_new = w &minus; rate &times; slope, so a positive slope lowers w.')
K.quiz('m', 'A language model trained to guess the next word of internet text is mainly', ['Unsupervised clustering', 'Self supervised learning', 'Reinforcement learning only', 'Rule based'], 1, 'Where does the label come from?', 'The next word is already in the text, so the data labels itself.')
K.quiz('h', 'Why must X be [[1], [2], [3]] and not [1, 2, 3] in scikit-learn?', ['Lists are not allowed', 'X must be a table: one row per example, one column per feature', 'It makes the model faster', 'Because y is one dimensional'], 1, 'Rows and columns.', 'scikit-learn always expects a 2D table of shape (samples, features).')
K.quiz('h', 'True prices 10 and 20, predictions 12 and 18. What is the MSE?', ['2', '4', '8', '0'], 1, 'Square, then average.', '(2<sup>2</sup> + 2<sup>2</sup>) / 2 = 4.')
K.quiz('h', 'Which statement about the no free lunch theorem is right?', ['Deep learning beats every method on every problem', 'Averaged over all possible problems, no learner beats another', 'More data always helps every model equally', 'Free datasets give worse models'], 1, 'All problems, equally weighted.', 'Every learner’s advantage on some problems is paid for on others.')
K.quiz('x', 'In the style of a Stanford CS229 exam: with loss L(w) = (w &minus; 3)<sup>2</sup>, start w = 0 and learning rate 0.5. Where is w after one gradient step?', ['1.5', '3', '6', '0'], 1, 'L′(w) = 2(w &minus; 3).', 'Slope at 0 is &minus;6. w = 0 &minus; 0.5 &times; (&minus;6) = 3, the minimum in one step.')
K.quiz('x', 'In the style of a CMU 10-601 exam: with loss (w &minus; 3)<sup>2</sup> and learning rate 1.5, starting at w = 0, what happens?', ['It converges to 3', 'It jumps between sides and moves further away each step', 'It stops at 0', 'It converges to 4.5'], 1, 'Each step multiplies the distance to 3 by (1 &minus; 2 &times; 1.5).', 'Distance is multiplied by &minus;2 each step: 0, 9, &minus;9, 27... It diverges.')

K.calc('e', 'True marks 10, 20, 30. Predictions 10, 20, 30. What is the MSE?', '0', 'Perfect predictions.', ['Every gap is 0.', 'Squares are 0.', eq('MSE = 0')], check=0)
K.calc('e', 'A spam filter gets 45 of 50 emails right. What is its accuracy (as a decimal)?', '0.9', 'Right / all.', ['Right = 45.', 'All = 50.', eq('45 / 50 = 0.9')], check=45 / 50)
K.calc('e', 'A model predicts marks = 9 &times; hours. What does it predict for 4 hours?', '36', 'Multiply.', ['w = 9.', 'hours = 4.', eq('9 &times; 4 = 36')], check=9 * 4)
K.calc('m', 'True values 3 and 7, predictions 5 and 4. What is the MSE?', '6.5', 'Square each gap.', ['Gaps: &minus;2 and 3.', 'Squares: 4 and 9.', eq('(4 + 9) / 2 = 6.5')], check=(4 + 9) / 2)
K.calc('m', 'Loss L(w) = (w &minus; 4)<sup>2</sup>. What is the slope at w = 1?', '-6', 'Slope = 2(w &minus; 4).', ['Formula 2(w &minus; 4).', 'Put w = 1.', eq('2 &times; (1 &minus; 4) = &minus;6')], check=2 * (1 - 4))
K.calc('m', 'With L(w) = (w &minus; 4)<sup>2</sup>, w = 1 and learning rate 0.25, what is w after one step?', '2.5', 'w &minus; rate &times; slope.', ['Slope = &minus;6.', 'Step = 0.25 &times; (&minus;6) = &minus;1.5.', eq('1 &minus; (&minus;1.5) = 2.5')], check=1 - 0.25 * (2 * (1 - 4)))
K.calc('m', 'A dataset table has 200 rows and 8 feature columns. How many feature values are there?', '1600', 'Rows &times; columns.', ['200 examples.', '8 features each.', eq('200 &times; 8 = 1,600')], check=200 * 8)
K.calc('h', 'MSE is 16 (lakh squared). What is the RMSE in lakh?', '4', 'Square root.', ['RMSE = &radic;MSE.', '&radic;16.', eq('4')], check=16 ** 0.5)
K.calc('h', 'Data: hours 1, 2 with marks 10, 20. With w = 5, what is the slope of the MSE, (1/n) &Sigma; 2(w x &minus; y) x?', '-25', 'Add both terms, divide by 2.', ['First: 2(5 &minus; 10)(1) = &minus;10.', 'Second: 2(10 &minus; 20)(2) = &minus;40.', eq('(&minus;10 &minus; 40) / 2 = &minus;25')], check=(2 * (5 - 10) * 1 + 2 * (10 - 20) * 2) / 2)
K.calc('x', 'In the style of an MIT 6.036 question: for L(w) = (w &minus; 3)<sup>2</sup>, each gradient step multiplies the distance to 3 by (1 &minus; 2&eta;). What is the largest learning rate &eta; that does not diverge (distance does not grow)?', '1', 'Need |1 &minus; 2&eta;| &le; 1.', ['|1 &minus; 2&eta;| &le; 1 means 0 &le; &eta; &le; 1.', 'At &eta; = 1 the factor is &minus;1: it bounces forever without growing.', eq('largest &eta; = 1')], check=1)

K.assign('mse', 'e', 'Mean squared error by hand',
         '<p>Write <code>mean_squared_error(y_true, y_pred)</code> that returns the average of the squared differences between two lists of the same length.</p>',
         '''
def mean_squared_error(y_true, y_pred):
    # your code here
    pass
''', [('mean_squared_error([10, 20, 30], [10, 20, 30])', 0.0), ('mean_squared_error([3, 7], [5, 4])', 6.5), ('mean_squared_error([1], [4])', 9.0)],
         '''
def mean_squared_error(y_true, y_pred):
    total = 0
    for t, p in zip(y_true, y_pred):
        total = total + (t - p) ** 2
    return total / len(y_true)
''', 'Loop over both lists together with zip. Add (t &minus; p) squared. Divide by the length at the end.', '<p>This is exactly what sklearn.metrics.mean_squared_error does. Squaring keeps every gap positive and punishes big mistakes most.</p>')
K.assign('acc', 'e', 'Accuracy by hand',
         '<p>Write <code>accuracy(y_true, y_pred)</code> that returns the share of positions where the two lists hold the same label, as a number between 0 and 1.</p>',
         '''
def accuracy(y_true, y_pred):
    # your code here
    pass
''', [('accuracy(["a", "b", "a"], ["a", "b", "b"])', 2 / 3), ('accuracy([1, 1, 0, 0], [1, 1, 0, 0])', 1.0), ('accuracy([1, 0], [0, 1])', 0.0)],
         '''
def accuracy(y_true, y_pred):
    right = 0
    for t, p in zip(y_true, y_pred):
        if t == p:
            right = right + 1
    return right / len(y_true)
''', 'Count the matches, then divide by how many there are.', '<p>Accuracy is easy to read but can mislead when one class is rare. The Supervised section shows precision and recall for that case.</p>')
K.assign('base', 'm', 'A baseline model: always predict the most common label',
         '<p>Write <code>most_common_label(labels)</code> that returns the label that appears most often in the training labels. When two labels tie, return the one that appears first in the list. This "majority class" model is the first baseline every project should beat.</p>',
         '''
def most_common_label(labels):
    # your code here
    pass
''', [('most_common_label(["ham", "spam", "ham"])', 'ham'), ('most_common_label([1, 0, 0, 1])', 1), ('most_common_label(["cat"])', 'cat')],
         '''
def most_common_label(labels):
    counts = {}
    order = []
    for label in labels:
        if label not in counts:
            counts[label] = 0
            order.append(label)
        counts[label] = counts[label] + 1
    best = order[0]
    for label in order:
        if counts[label] > counts[best]:
            best = label
    return best
''', 'Count each label in a dict. Keep the order of first appearance in a list, so ties go to the earliest label.', '<p>If 95 of 100 emails are not spam, this model already gets 95% accuracy without learning anything. Any real model must beat it, which is why you always compute a baseline first.</p>')

K.must('Machine learning', 'Learn the rule from examples instead of writing it. Mitchell: performance P on task T improves with experience E.')
K.must('The loop', 'Guess, measure the loss, adjust parameters against the slope (gradient descent), repeat. Learning rate sets the step size.')
K.must('Kinds', 'Supervised (labels: regression for numbers, classification for categories), unsupervised (no labels), reinforcement (rewards), plus semi and self supervised.')
K.must('Words', 'Features are inputs (X), label is the answer (y). Parameters are learned, hyperparameters are chosen.')
K.must('Generalise', 'Judge a model on unseen test data. High training score with low test score means overfitting.')
K.must('scikit-learn', 'model = Model(), model.fit(X, y), model.predict(X_new), model.score(X_test, y_test). X is 2D.')

T = K.topic(
    slug='ml-intro', topic='ml-intro', step=(1, 'Start here', 'ml-f1', 'What machine learning is, how a project runs from raw data to a working model, and the Python tools every ML engineer uses.', 'Beginner'),
    title='What machine learning is: learning from examples', short='What ML is', badge='1.1', minutes=55,
    lead='Find out what machine learning really means, how a machine learns by guessing and correcting itself, the kinds of learning, the words every ML person uses, why we test on unseen data, and your first models in scikit-learn.',
    desc='definition of machine learning, Mitchell task experience performance, rules vs learning, the learning loop, loss, gradient descent, learning rate, supervised, unsupervised, semi supervised, self supervised and reinforcement learning, regression vs classification, features, labels, parameters, hyperparameters, generalisation, overfitting, scikit-learn fit and predict, applications, history, ML vs statistics vs deep learning, inductive bias, PAC learning, no free lunch.',
    summary='what ML is, the learning loop, kinds of learning, the vocabulary, generalisation and your first scikit-learn models.',
    keywords=['machine learning', 'supervised', 'unsupervised', 'reinforcement', 'features', 'labels', 'loss', 'gradient descent', 'overfitting', 'scikit-learn'],
    recap='<p>Machine learning finds rules from examples with a guess, check, adjust loop, and is judged by how well it does on data it has never seen.</p>',
    added='2026-11-13', leet=leet_items())
