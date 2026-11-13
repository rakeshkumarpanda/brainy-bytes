# Unsupervised 3.3: recommender systems. Checked against Resnick, Iacovou, Suchak, Bergstrom and Riedl, GroupLens
# (CSCW 1994), Sarwar, Karypis, Konstan and Riedl, Item-based Collaborative Filtering Recommendation Algorithms (WWW 2001),
# Koren, Bell and Volinsky, Matrix Factorization Techniques for Recommender Systems (IEEE Computer 2009), Hu, Koren and
# Volinsky, Collaborative Filtering for Implicit Feedback Datasets (ICDM 2008), Jarvelin and Kekalainen, Cumulated
# Gain-based Evaluation of IR Techniques (ACM TOIS 2002), Covington, Adams and Sargin, Deep Neural Networks for YouTube
# Recommendations (RecSys 2016), and Leskovec, Rajaraman and Ullman, Mining of Massive Datasets chapter 9.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-recommenders')
K = Kit()

K.code('content_based', r'''
import numpy as np

films = ["Space Race", "Robot Love", "Haunted Inn", "Laugh Lab", "Star Siege", "Ghost Camp"]
#                  sci-fi romance horror comedy action
features = np.array([[1, 0, 0, 0, 1],
                     [1, 1, 0, 0, 0],
                     [0, 0, 1, 0, 0],
                     [0, 0, 0, 1, 0],
                     [1, 0, 0, 0, 1],
                     [0, 0, 1, 1, 0]], dtype=float)
liked = [0, 1]                                           # the user liked Space Race and Robot Love
profile = features[liked].mean(axis=0)                   # the user's taste as a mix of features
cos = features @ profile / (np.linalg.norm(features, axis=1) * np.linalg.norm(profile))
order = [i for i in np.argsort(-cos, kind="stable") if i not in liked]
print("taste profile:", profile.tolist())
for i in order:
    print(films[i].ljust(11), " cosine similarity", round(float(cos[i]), 3))
''')

K.code('user_cf', r'''
import numpy as np

# Ratings 1 to 5, 0 = not rated. Rows are users, columns are films.
R = np.array([[5, 4, 0, 1, 0],
              [4, 5, 1, 0, 1],
              [1, 0, 5, 4, 5],
              [0, 1, 4, 5, 4],
              [5, 5, 0, 2, 1]], dtype=float)
rated = R > 0
means = np.array([R[u, rated[u]].mean() for u in range(len(R))])
C = np.where(rated, R - means[:, None], 0.0)             # centre each user so harsh and generous raters compare fairly

def sim(a, b):
    both = rated[a] & rated[b]
    x, y = C[a, both], C[b, both]
    return float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-9))

user, film = 0, 2                                        # predict user 0's rating of film 2
others = [v for v in range(len(R)) if v != user and rated[v, film]]
sims = {v: round(sim(user, v), 3) for v in others}
print("similarity of user 0 to users who rated film 2:", sims)
top = sorted(others, key=lambda v: -sims[v])[:2]         # the 2 most similar users
pred = means[user] + sum(sims[v] * C[v, film] for v in top) / sum(abs(sims[v]) for v in top)
print("neighbours used:", top, " predicted rating:", round(float(pred), 2), " (user 0's average is", round(float(means[user]), 2), ")")
''')

K.code('item_cf', r'''
import numpy as np

R = np.array([[5, 4, 0, 1, 0],
              [4, 5, 1, 0, 1],
              [1, 0, 5, 4, 5],
              [0, 1, 4, 5, 4],
              [5, 5, 0, 2, 1]], dtype=float)
films = ["Space Race", "Star Siege", "Haunted Inn", "Ghost Camp", "Night Fog"]
norms = np.linalg.norm(R, axis=0)
S = (R.T @ R) / np.outer(norms, norms)                   # cosine similarity between film columns
np.fill_diagonal(S, 0)
for i, f in enumerate(films):
    j = int(np.argmax(S[i]))
    print(f.ljust(11), " most similar:", films[j].ljust(11), " cosine", round(float(S[i, j]), 3))
user = 0
seen = R[user] > 0
for i in np.where(~seen)[0]:
    w = S[i, seen]                                       # how close this film is to each film the user rated
    score = w @ R[user, seen] / w.sum()                  # weighted average of the user's own ratings
    print("for user 0, unseen", films[i].ljust(11), " predicted", round(float(score), 2))
''')

K.code('mf_sgd', r'''
import numpy as np

rng = np.random.default_rng(0)
n_users, n_items, k = 60, 30, 2
U_true, V_true = rng.normal(0, 1, (n_users, k)), rng.normal(0, 1, (n_items, k))
full = np.clip(3 + U_true @ V_true.T, 1, 5)                # hidden "true" ratings
mask = rng.random((n_users, n_items)) < 0.4                # we only see 40% of them
train = [(u, i, full[u, i]) for u in range(n_users) for i in range(n_items) if mask[u, i]]
test = [(u, i, full[u, i]) for u in range(n_users) for i in range(n_items) if not mask[u, i]]
mu = np.mean([r for _, _, r in train])
P, Q = rng.normal(0, 0.1, (n_users, k)), rng.normal(0, 0.1, (n_items, k))
bu, bi = np.zeros(n_users), np.zeros(n_items)
lr, reg = 0.02, 0.1
def rmse(data):
    return float(np.sqrt(np.mean([(r - (mu + bu[u] + bi[i] + P[u] @ Q[i])) ** 2 for u, i, r in data])))
for epoch in range(1, 61):
    for idx in rng.permutation(len(train)):
        u, i, r = train[idx]
        e = r - (mu + bu[u] + bi[i] + P[u] @ Q[i])         # error on one known rating
        bu[u] += lr * (e - reg * bu[u])
        bi[i] += lr * (e - reg * bi[i])
        P[u], Q[i] = P[u] + lr * (e * Q[i] - reg * P[u]), Q[i] + lr * (e * P[u] - reg * Q[i])
    if epoch in (1, 5, 10, 20, 40, 60):
        print("epoch", str(epoch).rjust(2), " train RMSE", round(rmse(train), 3), " test RMSE", round(rmse(test), 3))
print("always guessing the average:", round(float(np.sqrt(np.mean([(r - mu) ** 2 for _, _, r in test]))), 3))
''', long=True)

K.code('als', r'''
import numpy as np

rng = np.random.default_rng(0)
n_users, n_items, k = 60, 30, 2
U_true, V_true = rng.normal(0, 1, (n_users, k)), rng.normal(0, 1, (n_items, k))
full = np.clip(3 + U_true @ V_true.T, 1, 5)
mask = rng.random((n_users, n_items)) < 0.4
mu = full[mask].mean()
X = np.where(mask, full - mu, 0.0)                       # centred known ratings, 0 where unknown
P, Q = rng.normal(0, 0.1, (n_users, k)), rng.normal(0, 0.1, (n_items, k))
lam = 1.0
I = np.eye(k)
for sweep in range(1, 11):
    for u in range(n_users):                             # fix Q, solve each user exactly
        Qu = Q[mask[u]]
        P[u] = np.linalg.solve(Qu.T @ Qu + lam * I, Qu.T @ X[u, mask[u]])
    for i in range(n_items):                             # fix P, solve each item exactly
        Pi = P[mask[:, i]]
        Q[i] = np.linalg.solve(Pi.T @ Pi + lam * I, Pi.T @ X[mask[:, i], i])
    pred = mu + P @ Q.T
    if sweep in (1, 2, 3, 5, 10):
        tr = np.sqrt(np.mean((pred - full)[mask] ** 2))
        te = np.sqrt(np.mean((pred - full)[~mask] ** 2))
        print("sweep", str(sweep).rjust(2), " train RMSE", round(float(tr), 3), " test RMSE", round(float(te), 3))
print("always guessing the average:", round(float(np.sqrt(np.mean((mu - full)[~mask] ** 2))), 3))
''', long=True)

K.code('ranking_metrics', r'''
import numpy as np

recommended = ["A", "B", "C", "D", "E"]                   # our top 5, best first
relevant = {"A", "C", "F"}                                # what the user actually liked later
k = 5
hits = [1 if item in relevant else 0 for item in recommended[:k]]
print("hits:", hits)
print("precision@5 =", sum(hits) / k, " recall@5 =", round(sum(hits) / len(relevant), 3))
dcg = sum(h / np.log2(i + 2) for i, h in enumerate(hits))
ideal = sum(1 / np.log2(i + 2) for i in range(min(k, len(relevant))))
print("DCG", round(float(dcg), 3), " ideal DCG", round(float(ideal), 3), " NDCG@5 =", round(float(dcg / ideal), 3))
first = next(i for i, h in enumerate(hits) if h) + 1
print("reciprocal rank of the first hit =", 1 / first)
''')

K.code('cold_start', r'''
import numpy as np

R = np.array([[5, 4, 0, 1, 0],
              [4, 5, 1, 0, 1],
              [1, 0, 5, 4, 5],
              [0, 1, 4, 5, 4],
              [5, 5, 0, 2, 1]], dtype=float)
films = ["Space Race", "Star Siege", "Haunted Inn", "Ghost Camp", "Night Fog"]
count = (R > 0).sum(axis=0)
mean = R.sum(axis=0) / count
m, C = 3, float(R[R > 0].mean())                          # shrink films with few ratings towards the overall mean
score = (count * mean + m * C) / (count + m)
for i in np.argsort(-score, kind="stable"):
    print(films[i].ljust(11), " ratings", int(count[i]), " average", round(float(mean[i]), 2), " shrunk score", round(float(score[i]), 2))
print("a brand new user with no ratings gets this popularity list first")
''')

K.lesson('idea', 'What a recommender does, and content based filtering', f'''
{src('Leskovec, Rajaraman and Ullman, Mining of Massive Datasets chapter 9, and Ricci, Rokach and Shapira, Recommender Systems Handbook chapter 1.')}
{wwh('A <b>recommender system</b> guesses which items (films, songs, products, posts) a person will like and shows the best few first. The data is a large <b>user by item matrix</b> of ratings, clicks or purchases, and almost all of it is empty, because each person has met only a tiny share of the items. <b>Content based filtering</b> describes each item by its features (genre, words, price) and recommends items whose features match what the person liked before.',
     'Shops, streaming services and news sites have far more items than anyone can browse. A good ranked list saves people time and drives most of what they watch or buy on large platforms. Content based filtering needs no other users, so it works for a brand new item as soon as its features are known.',
     'Turn each item into a feature vector. Build a taste profile for the person as the average of the vectors of items they liked. Score every unseen item by the cosine similarity between its vector and the profile, and recommend the highest scores.')}
{run('content_based')}
{note('The person liked one action sci fi film and one romantic sci fi film, so the profile is 1 for sci fi and 0.5 for romance and action. Star Siege shares sci fi and action and scores 0.866. Every other film shares no feature with the profile and scores 0. This shows the main weakness of content based filtering: it only finds more of the same, and it can never suggest a comedy to someone who has not watched one yet.', 'exam')}
{fxs(fx('Cosine similarity', 'cos(a, b) = a &middot; b / (&#8214;a&#8214; &#8214;b&#8214;)', '1 for the same direction, 0 for no shared features.', key=True),
     fx('Taste profile', 'profile(u) = mean of x<sub>i</sub> over items i liked by u', 'Ratings can be used as weights.'))}
{table(['Kind of feedback', 'Examples', 'What it tells us'], [
    ['Explicit', 'Star ratings, thumbs up or down', 'Clear likes and dislikes, but few people give them'],
    ['Implicit', 'Clicks, plays, purchases, time watched', 'Plenty of data, but a missing click is not a dislike']])}
''', kw=['recommender system', 'user item matrix', 'sparsity', 'content based filtering', 'cosine similarity', 'explicit feedback', 'implicit feedback'])

K.lesson('cf', 'Collaborative filtering: people like you and items like this', f'''
{src('Resnick, Iacovou, Suchak, Bergstrom and Riedl, GroupLens (CSCW 1994), and Sarwar, Karypis, Konstan and Riedl, Item-based Collaborative Filtering Recommendation Algorithms (WWW 2001).')}
{viz('mlcf')}
{wwh('<b>Collaborative filtering</b> uses only the ratings, not item features. <b>User based</b> filtering finds users whose past ratings agree with yours and predicts your rating of a film from theirs. <b>Item based</b> filtering finds items rated in the same pattern as items you rated, and predicts from your own ratings of those similar items.',
     'It finds links that features miss: people who like one quiet foreign drama often like a certain documentary, even though the two share no genre. It needs no hand made features at all, only a record of who liked what.',
     'Centre each user’s ratings on that user’s mean, because some people rate everything high. Measure similarity with the cosine of centred ratings on items both users rated (this is the Pearson correlation). Keep the k most similar users who rated the target item, and predict the user’s mean plus a similarity weighted average of their centred ratings.')}
{run('user_cf')}
{note('User 1 agrees with user 0 (similarity 0.776) and rated the film 1, well below user 1’s mean of 2.75. User 2 disagrees with user 0 (similarity &minus;0.653) and loved the film. Both signals point the same way, so the guess for user 0 is 1.81, far below user 0’s mean of 3.33. A negative similarity flips the neighbour’s opinion. Many systems simply keep only positive similarities.', 'exam')}
{run('item_cf')}
{note('Space Race and Star Siege are rated almost the same way by everyone (cosine 0.97), and so are the three horror films. User 0 loved the two sci fi films and gave Ghost Camp a 1, so the unseen horror films get low predictions of 1.95 and 2.25. This version uses plain cosine on raw ratings, which treats a missing rating as 0 and makes every similarity positive. Sarwar and colleagues found that the adjusted cosine, which subtracts each user’s mean first, works better.', 'tip')}
{table(['', 'User based', 'Item based'], [
    ['Similarity between', 'Rows (users)', 'Columns (items)'],
    ['Stable over time', 'No, tastes and users change fast', 'Yes, item links change slowly, so they can be computed offline'],
    ['Typical scale', 'Many more users than items makes it slow', 'Used by Amazon for item to item recommendations'],
    ['Explains itself as', '"People like you liked this"', '"Because you liked X"']])}
''', kw=['collaborative filtering', 'user based', 'item based', 'neighbourhood methods', 'Pearson correlation', 'adjusted cosine', 'k nearest neighbours'])

K.lesson('mf', 'Matrix factorisation: hidden tastes learned from ratings', f'''
{src('Koren, Bell and Volinsky, Matrix Factorization Techniques for Recommender Systems (IEEE Computer 2009), the Netflix Prize write up.')}
{viz('mlmf')}
{wwh('<b>Matrix factorisation</b> gives every user u a short vector p<sub>u</sub> and every item i a short vector q<sub>i</sub> of k hidden numbers, called <b>latent factors</b>. The predicted rating is r&#770; = &mu; + b<sub>u</sub> + b<sub>i</sub> + p<sub>u</sub> &middot; q<sub>i</sub>: the overall mean, plus how generous the user is, plus how well liked the item is, plus how well the user’s tastes match the item’s traits. The factors are learned only from the known ratings.',
     'It was the core of the winning methods in the Netflix Prize (2006 to 2009). It handles sparse data better than neighbour methods, because every rating helps shape factors that all users and items share. The learned factors often line up with real traits such as serious against light hearted, without anyone naming them.',
     'Minimise the squared error on known ratings plus a penalty &lambda; on the size of all factors and biases. Train with stochastic gradient descent (SGD), one rating at a time, or with alternating least squares (ALS), which fixes the item factors and solves every user exactly, then swaps. Choose k and &lambda; on held out ratings.')}
{run('mf_sgd')}
{note('Guessing the average gives a test RMSE of 1.068. For the first 10 epochs SGD is no better, because the small random factors need time to grow. By epoch 20 test RMSE falls to 0.689 and by epoch 60 to 0.36, while train RMSE is 0.2. Run the same program with 30 users, 20 films, only 30% of ratings seen and &lambda; = 0.02, and it overfits: train RMSE 0.194 but test RMSE 1.145, worse than the average guess. With sparse data the penalty is not optional.', 'exam')}
{run('als')}
{note('ALS reaches a test RMSE of 0.319 after only 3 sweeps and 0.259 after 10, against 1.068 for the average guess. Each sweep solves small k by k linear systems exactly, so it needs far fewer passes than SGD. ALS also parallelises well, since every user can be solved at the same time, which is why Spark MLlib uses it.', 'tip')}
{deep('Implicit feedback and weighted ALS', '<p>With clicks or plays there are no low ratings, only signs of interest. Hu, Koren and Volinsky (2008) turn every cell into a preference p<sub>ui</sub> (1 if the user interacted, else 0) and a confidence c<sub>ui</sub> = 1 + &alpha; r<sub>ui</sub>, where r<sub>ui</sub> counts the interactions. They then minimise &Sigma; c<sub>ui</sub>(p<sub>ui</sub> &minus; p<sub>u</sub> &middot; q<sub>i</sub>)<sup>2</sup> over all cells, including the empty ones, plus the usual penalty. ALS stays fast because the sum over empty cells can be rewritten with one shared k by k matrix. The Python package implicit offers this method, and so does Spark MLlib with implicitPrefs set to true.</p>')}
''', kw=['matrix factorisation', 'latent factors', 'biases', 'SGD', 'alternating least squares', 'regularisation', 'Netflix Prize', 'implicit ALS'])

K.lesson('evaluate', 'Measuring recommendations and starting cold', f'''
{src('Jarvelin and Kekalainen, Cumulated Gain-based Evaluation of IR Techniques (ACM TOIS 2002), and Schein, Popescul, Ungar and Pennock, Methods and Metrics for Cold-Start Recommendations (SIGIR 2002).')}
{wwh('Recommenders are judged in two ways. <b>Rating error</b> (RMSE or MAE) measures how close predicted ratings are to real ones. <b>Ranking metrics</b> measure the short list a person actually sees: <b>precision@k</b> (share of the top k that are relevant), <b>recall@k</b> (share of the relevant items that reach the top k), <b>NDCG@k</b> (rewards hits near the top more) and <b>MRR</b> (how early the first hit comes).',
     'People look at the first few items only. A model can have a low RMSE and still put the wrong films first. The <b>cold start problem</b>, a new user or new item with no history, is where collaborative methods fail completely, so every real system needs a fallback.',
     'Hold out some later interactions of each user, recommend from the earlier ones, and score the list against what the user really chose next. Split by time rather than at random, to avoid using the future. For cold start, show popular items with a shrunk score, ask new users a few questions, and use content features for new items.')}
{run('ranking_metrics')}
{note('Two of the five recommendations (A and C) are relevant, so precision@5 = 0.4, and two of the three relevant items are found, so recall@5 = 0.667. The hits are at positions 1 and 3, giving DCG = 1 + 1/log<sub>2</sub>4 = 1.5. The best possible list would put all three relevant items first, with ideal DCG 2.131, so NDCG@5 = 0.704. The first item is a hit, so the reciprocal rank is 1.', 'exam')}
{run('cold_start')}
{note('Sorting by plain average favours items with very few ratings: one 5 star rating would beat everything. The shrunk score (n &times; mean + m &times; C) / (n + m) pulls items with few ratings towards the overall mean C. Haunted Inn has only 3 ratings, so its average of 3.33 moves to 3.32 here. With one rating it would move much more. This is the score IMDb used for its top 250 list.', 'tip')}
{table(['Metric', 'Formula', 'Cares about order'], [
    ['Precision@k', 'hits in top k / k', 'No'],
    ['Recall@k', 'hits in top k / number relevant', 'No'],
    ['NDCG@k', 'DCG@k / ideal DCG@k, with DCG = &Sigma; rel<sub>i</sub> / log<sub>2</sub>(i + 1)', 'Yes'],
    ['MRR', 'mean of 1 / rank of first hit', 'Yes, first hit only'],
    ['RMSE', '&radic;(mean of (r &minus; r&#770;)<sup>2</sup>)', 'No, judges ratings not lists']])}
''', kw=['precision at k', 'recall at k', 'NDCG', 'MRR', 'RMSE', 'cold start', 'popularity baseline', 'time based split'])

K.lesson('production', 'Recommenders at scale and their side effects', f'''
{src('Covington, Adams and Sargin, Deep Neural Networks for YouTube Recommendations (RecSys 2016), Yi and colleagues, Sampling-Bias-Corrected Neural Modeling for Large Corpus Item Recommendations (RecSys 2019), and Chaney, Stewart and Engelhardt, How Algorithmic Confounding in Recommendation Systems Increases Homogeneity (RecSys 2018).')}
{wwh('Large systems work in two stages. <b>Candidate generation</b> quickly picks a few hundred items out of millions, often with a <b>two tower</b> neural network that maps users and items to vectors and finds the nearest item vectors with approximate nearest neighbour search. <b>Ranking</b> then scores those candidates with a richer model that uses many features, such as time of day and recent clicks, and predicts watch time or the chance of a click.',
     'Scoring millions of items with a big model for every page view is too slow. Splitting the work keeps answers fast. Recommenders also change what people see, so they change the data they learn from next, which can narrow choices and favour already popular items.',
     'Train the towers on past interactions, index the item vectors with a library such as FAISS, rank with gradient boosting or a deep network, then re rank for variety, freshness and business rules. Test changes with online A/B tests, since offline metrics on logged data are biased by what the old system chose to show.')}
{steps('A typical serving path', [
    'A user opens the app. Look up or compute the user vector from recent activity.',
    'Candidate generation: approximate nearest neighbour search returns about 500 items from millions in a few milliseconds.',
    'Ranking: a model with many features scores the 500 candidates.',
    'Re ranking: remove items already seen, add variety, apply rules.',
    'Log what was shown and what was clicked. This log becomes the next training data.'])}
{note('Popularity bias and feedback loops: items that are shown get clicks, clicks make them shown more, and items that were never shown never get a chance. Exploration (sometimes showing less certain items) and corrections such as inverse propensity weighting reduce this. Measure variety and coverage, not only clicks.', 'tip')}
''', kw=['two tower model', 'candidate generation', 'ranking', 'approximate nearest neighbours', 'FAISS', 'feedback loops', 'popularity bias', 'A/B testing'])

K.lesson('versus', 'Recommendation methods compared', f'''
{versus('Four ways to recommend', ['', 'Popularity', 'Content based', 'Neighbour collaborative filtering', 'Matrix factorisation'], [
    ['Data needed', 'Counts only', 'Item features', 'Ratings or clicks', 'Ratings or clicks'],
    ['Personal', 'No', 'Yes', 'Yes', 'Yes'],
    ['New item', 'Needs some ratings', 'Works at once', 'Fails', 'Fails'],
    ['New user', 'Works at once', 'Needs a few likes', 'Fails', 'Fails'],
    ['Finds surprising items', 'No', 'Rarely', 'Yes', 'Yes'],
    ['Explains itself', 'Very easily', 'Easily', 'Fairly', 'Hardly']],
    'start with a popularity baseline, add matrix factorisation once there are enough interactions, and use content features for new items. Hybrids that mix them are the norm.')}
''', kw=['content based vs collaborative filtering', 'matrix factorisation vs nearest neighbours', 'hybrid recommender'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Centred cosine (Pearson)', 'sim(u, v) = &Sigma;<sub>i</sub> (r<sub>ui</sub> &minus; r&#772;<sub>u</sub>)(r<sub>vi</sub> &minus; r&#772;<sub>v</sub>) / &radic;(&Sigma;<sub>i</sub> (r<sub>ui</sub> &minus; r&#772;<sub>u</sub>)<sup>2</sup> &Sigma;<sub>i</sub> (r<sub>vi</sub> &minus; r&#772;<sub>v</sub>)<sup>2</sup>)', 'Sums over items both users rated.', key=True),
     fx('User based prediction', 'r&#770;<sub>ui</sub> = r&#772;<sub>u</sub> + &Sigma;<sub>v</sub> sim(u, v)(r<sub>vi</sub> &minus; r&#772;<sub>v</sub>) / &Sigma;<sub>v</sub> |sim(u, v)|', 'v runs over the k nearest users who rated i.', key=True),
     fx('Matrix factorisation', 'r&#770;<sub>ui</sub> = &mu; + b<sub>u</sub> + b<sub>i</sub> + p<sub>u</sub> &middot; q<sub>i</sub>', 'k hidden factors per user and item.', key=True),
     fx('Training loss', 'min &Sigma;<sub>(u,i) known</sub> (r<sub>ui</sub> &minus; r&#770;<sub>ui</sub>)<sup>2</sup> + &lambda;(&#8214;p<sub>u</sub>&#8214;<sup>2</sup> + &#8214;q<sub>i</sub>&#8214;<sup>2</sup> + b<sub>u</sub><sup>2</sup> + b<sub>i</sub><sup>2</sup>)', 'Only known cells count.', key=True),
     fx('SGD step', 'e = r &minus; r&#770;, p<sub>u</sub> &larr; p<sub>u</sub> + &eta;(e q<sub>i</sub> &minus; &lambda; p<sub>u</sub>), q<sub>i</sub> &larr; q<sub>i</sub> + &eta;(e p<sub>u</sub> &minus; &lambda; q<sub>i</sub>)', 'Use the old p<sub>u</sub> when updating q<sub>i</sub>.'),
     fx('ALS step', 'p<sub>u</sub> = (Q<sub>u</sub><sup>T</sup> Q<sub>u</sub> + &lambda;I)<sup>&minus;1</sup> Q<sub>u</sub><sup>T</sup> r<sub>u</sub>', 'Q<sub>u</sub> holds the factors of items u rated. A ridge regression per user.'),
     fx('NDCG@k', 'DCG@k = &Sigma;<sub>i=1</sub><sup>k</sup> rel<sub>i</sub> / log<sub>2</sub>(i + 1), NDCG@k = DCG@k / IDCG@k', 'Between 0 and 1.', key=True),
     fx('Shrunk average', 'score = (n r&#772; + m C) / (n + m)', 'm acts as m extra ratings at the overall mean C.'))}
{steps('Worked example: one SGD update', [
    'Known rating r = 4. Current guess r&#770; = 3, so the error e = 1.',
    'Take &eta; = 0.1, &lambda; = 0.1, p<sub>u</sub> = (1, 0) and q<sub>i</sub> = (0.5, 0.5).',
    eq('p<sub>u</sub> &larr; (1, 0) + 0.1 &times; (1 &times; (0.5, 0.5) &minus; 0.1 &times; (1, 0)) = (1.04, 0.05)'),
    eq('q<sub>i</sub> &larr; (0.5, 0.5) + 0.1 &times; (1 &times; (1, 0) &minus; 0.1 &times; (0.5, 0.5)) = (0.595, 0.495)'),
    'The new dot product is 1.04 &times; 0.595 + 0.05 &times; 0.495 = 0.644, up from 0.5, so the guess moved towards 4.'])}
{deep('Why it is called factorisation, and its link to SVD', '<p>Stack the user vectors as rows of P (size users by k) and the item vectors as rows of Q (items by k). Then all predictions together form P Q<sup>T</sup>, a rank k matrix, so the method approximates the rating matrix by a product of two thin matrices. If every cell were known, the best rank k approximation in squared error would be the truncated SVD (the Eckart and Young theorem, as in the PCA chapter). With most cells missing, SVD cannot be applied directly, and filling the gaps with zeros or means biases it. That is why the loss sums only over known cells and why it is solved with SGD or ALS. The loss is not convex in P and Q together, but it is convex in either one when the other is fixed, which is exactly the property ALS uses.</p>')}
''', kw=['Pearson correlation', 'prediction formula', 'matrix factorisation loss', 'SGD update', 'ALS', 'NDCG formula', 'low rank', 'SVD'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>A recommender guesses what you will like from what you and people like you liked before, and shows the best guesses first.</p>',
    '<p>Build content based and collaborative recommenders, centre ratings, compute precision@k, recall@k and NDCG, and handle cold start with a shrunk popularity list.</p>',
    '<p>Train matrix factorisation with biases by SGD and ALS, tune k and &lambda; on a time based split, and use weighted ALS for implicit feedback.</p>',
    '<p>Design two stage systems with two tower retrieval and approximate nearest neighbours, correct exposure bias with propensity weighting, study bandits for exploration, and measure long term effects with online experiments.</p>')}
{grow('Explain how a recommender uses past ratings.',
      'Build and evaluate a working recommender.',
      'Analyse factorisation methods and the effects of recommenders at scale.')}
''', kw=['beginner', 'expert', 'two tower', 'bandits', 'propensity weighting'])

lc(506, 'Relative Ranks', 'relative-ranks', 'e', 'Sort indices by score, best first', 'Sort the positions by score from high to low, then hand out "Gold Medal", "Silver Medal", "Bronze Medal" and numbers in that order. Turning scores into ranks is the last step of every recommender.', r"""
def find_relative_ranks(score):
    order = sorted(range(len(score)), key=lambda i: -score[i])
    medals = ["Gold Medal", "Silver Medal", "Bronze Medal"]
    answer = [""] * len(score)
    for place, i in enumerate(order):
        answer[i] = medals[place] if place < 3 else str(place + 1)
    return answer
""", [('find_relative_ranks([5, 4, 3, 2, 1])', ['Gold Medal', 'Silver Medal', 'Bronze Medal', '4', '5']), ('find_relative_ranks([10, 3, 8, 9, 4])', ['Gold Medal', '5', 'Bronze Medal', 'Silver Medal', '4'])])
lc(1636, 'Sort Array by Increasing Frequency', 'sort-array-by-increasing-frequency', 'e', 'Sort by a key made of the count and the negative value', 'Count each value, then sort by (count, minus value). A sort key with a tie breaker is how popularity lists are ordered when two items have the same score.', r"""
def frequency_sort(nums):
    count = {}
    for v in nums:
        count[v] = count.get(v, 0) + 1
    return sorted(nums, key=lambda v: (count[v], -v))
""", [('frequency_sort([1, 1, 2, 2, 2, 3])', [3, 1, 1, 2, 2, 2]), ('frequency_sort([2, 3, 1, 3, 2])', [1, 3, 3, 2, 2])])
lc(1311, 'Get Watched Videos by Your Friends', 'get-watched-videos-by-your-friends', 'm', 'Breadth first search to the given level, then count', 'Walk the friend graph level by level from the person, keeping a visited set, and stop at the asked level. Count the videos those friends watched and sort by count, then by name. This is the simplest social recommender: suggest what your friends watched.', r"""
from collections import deque


def watched_videos_by_friends(watched_videos, friends, id, level):
    seen = {id}
    frontier = deque([id])
    for _ in range(level):
        nxt = deque()
        for person in frontier:
            for f in friends[person]:
                if f not in seen:
                    seen.add(f)
                    nxt.append(f)
        frontier = nxt
    count = {}
    for person in frontier:
        for v in watched_videos[person]:
            count[v] = count.get(v, 0) + 1
    return sorted(count, key=lambda v: (count[v], v))
""", [('watched_videos_by_friends([["A", "B"], ["C"], ["B", "C"], ["D"]], [[1, 2], [0, 3], [0, 3], [1, 2]], 0, 1)', ['B', 'C']), ('watched_videos_by_friends([["A", "B"], ["C"], ["B", "C"], ["D"]], [[1, 2], [0, 3], [0, 3], [1, 2]], 0, 2)', ['D'])])
lc(1268, 'Search Suggestions System', 'search-suggestions-system', 'm', 'Sort the products, then binary search each prefix', 'After sorting, all products with a given prefix sit next to each other. For each prefix typed so far, find the first match with bisect and take up to three products that still start with the prefix. Suggestions while typing are a recommender with a very simple score.', r"""
from bisect import bisect_left


def suggested_products(products, search_word):
    products = sorted(products)
    answer = []
    prefix = ""
    for ch in search_word:
        prefix = prefix + ch
        start = bisect_left(products, prefix)
        answer.append([p for p in products[start:start + 3] if p.startswith(prefix)])
    return answer
""", [('suggested_products(["mobile", "mouse", "moneypot", "monitor", "mousepad"], "mouse")', [['mobile', 'moneypot', 'monitor'], ['mobile', 'moneypot', 'monitor'], ['mouse', 'mousepad'], ['mouse', 'mousepad'], ['mouse', 'mousepad']])])
lc(1366, 'Rank Teams by Votes', 'rank-teams-by-votes', 'm', 'Count votes per position and sort by the whole count list', 'For each team, count how many voters put it in each position. Sort teams by those counts, highest first position by position, and by name to break full ties. Combining many people’s rankings into one is the core of popularity and group recommendations.', r"""
def rank_teams(votes):
    n = len(votes[0])
    count = {t: [0] * n for t in votes[0]}
    for v in votes:
        for pos, t in enumerate(v):
            count[t][pos] = count[t][pos] + 1
    return "".join(sorted(votes[0], key=lambda t: ([-c for c in count[t]], t)))
""", [('rank_teams(["ABC", "ACB", "ABC", "ACB", "ACB"])', 'ACB'), ('rank_teams(["WXYZ", "XYZW"])', 'XWYZ')])
lc(2102, 'Sequentially Ordinal Rank Tracker', 'sequentially-ordinal-rank-tracker', 'h', 'Two heaps: the items already shown, and the rest', 'Keep the i best items seen so far in a heap whose top is the worst of them, and every other item in a heap whose top is the best. To add, push into the first heap and move its worst item to the second. To get, move the best of the second heap into the first and return it. Each call costs O(log n), the pattern behind serving a ranked feed that keeps changing.', r"""
import heapq


class _Worst:
    def __init__(self, score, name):
        self.score, self.name = score, name

    def __lt__(self, other):
        return (self.score, other.name) < (other.score, self.name)


class SORTracker:
    def __init__(self):
        self.shown = []
        self.rest = []

    def add(self, name, score):
        heapq.heappush(self.shown, _Worst(score, name))
        w = heapq.heappop(self.shown)
        heapq.heappush(self.rest, (-w.score, w.name))

    def get(self):
        s, name = heapq.heappop(self.rest)
        heapq.heappush(self.shown, _Worst(-s, name))
        return name


def sor_tracker_run(ops):
    t = SORTracker()
    out = []
    for op in ops:
        if op[0] == "add":
            t.add(op[1], op[2])
        else:
            out.append(t.get())
    return out
""", [('sor_tracker_run([["add", "bradford", 2], ["add", "branford", 3], ["get"], ["add", "alps", 2], ["get"], ["add", "orland", 2], ["get"], ["add", "orlando", 3], ["get"], ["add", "alpine", 2], ["get"], ["get"]])', ['branford', 'alps', 'bradford', 'bradford', 'bradford', 'orland'])])

K.lesson('leetcode', 'LeetCode practice', leet('<p>Recommenders score items and sort them. These problems practise turning scores into ranks, sorting with tie breakers, a friends of friends recommender with breadth first search, prefix suggestions with binary search, merging many rankings into one, and keeping a changing ranked list with two heaps. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'sorting', 'ranking', 'breadth first search', 'binary search', 'heap'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'A recommender ranks items for each person from a huge, mostly empty <b>user by item matrix</b>.',
    '<b>Content based</b> filtering matches item features to a taste profile. It handles new items but only finds more of the same.',
    '<b>Collaborative filtering</b> uses ratings only: centred cosine similarity between users or items, then a weighted average.',
    '<b>Matrix factorisation</b> predicts &mu; + b<sub>u</sub> + b<sub>i</sub> + p<sub>u</sub> &middot; q<sub>i</sub>, trained on known cells with a penalty by SGD or ALS.',
    'Judge lists with precision@k, recall@k, NDCG and MRR on a time based split. RMSE alone misses the order.',
    'Cold start needs fallbacks: shrunk popularity, a few questions, content features. At scale use two stages and watch feedback loops.'],
    'This ends Unsupervised learning. The Reinforcement learning section comes next: agents that learn from rewards.')}
{files('Three tasks: cosine similarity, precision and recall at k, and a full user based prediction.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Most cells of a user by item rating matrix are', ['Ratings of 5', 'Empty, because each person has rated very few items', 'Negative', 'Equal to the mean'], 1, 'Sparsity.', 'Often well over 99% empty.')
K.quiz('e', 'Content based filtering recommends items that', ['Are most popular', 'Have features similar to items the person liked', 'Other users bought', 'Are newest'], 1, 'Features.', 'No other users needed.')
K.quiz('e', 'Collaborative filtering needs', ['Item descriptions', 'Only who rated or clicked what', 'Labels from experts', 'Images'], 1, 'The ratings matrix.', 'No features at all.')
K.quiz('e', 'Precision@5 of a list with 3 relevant items in the top 5 is', ['0.3', '0.6', '3', '5'], 1, 'Hits / k.', '3 / 5.')
K.quiz('m', 'Why centre ratings on each user’s mean before comparing users?', ['To make them positive', 'Some users rate everything high and others low', 'To remove films', 'It is required by Python'], 1, 'Generous and harsh raters.', 'Centring compares likes and dislikes, not rating habits.')
K.quiz('m', 'Recall@k is', ['Hits in top k / k', 'Hits in top k / number of relevant items', 'Position of first hit', 'RMSE on top k'], 1, 'Share of relevant found.', 'Precision divides by k instead.')
K.quiz('m', 'In matrix factorisation the training loss sums over', ['All cells, missing as 0', 'Only the known ratings', 'Only the diagonal', 'Only new users'], 1, 'Missing is unknown, not zero.', 'Plus a penalty on the factors.')
K.quiz('m', 'The cold start problem is', ['A slow server', 'A new user or item has no interactions to learn from', 'Overfitting', 'Too many features'], 1, 'No history.', 'Use popularity, questions or content features.')
K.quiz('m', 'Item based filtering is often preferred to user based on large shops because', ['Items have no ratings', 'Item similarities change slowly and can be computed offline', 'It needs no data', 'It is always more accurate'], 1, 'Stability.', 'Sarwar and colleagues (2001), and Amazon’s item to item method.')
K.quiz('h', 'ALS is attractive for big data because', ['It needs no ratings', 'With item factors fixed, each user is a separate small ridge regression, so all users can be solved in parallel', 'It is convex in both factors at once', 'It never overfits'], 1, 'Fix one side.', 'Spark MLlib uses it.')
K.quiz('h', 'Why can plain SVD not be used directly on a rating matrix?', ['It is too accurate', 'Most cells are missing, and filling them with zeros biases the result', 'SVD needs square matrices', 'Ratings are integers'], 1, 'Missing data.', 'So the loss sums over known cells only.')
K.quiz('h', 'A model with lower RMSE than another can still be worse for users because', ['RMSE is always wrong', 'People see only the top of the list, and RMSE ignores ranking order', 'RMSE is a ranking metric', 'It is impossible'], 1, 'Order matters.', 'Check NDCG or precision@k too.')
K.quiz('x', 'In the style of a Stanford CS246 exam: in implicit feedback ALS, confidence c<sub>ui</sub> = 1 + &alpha; r<sub>ui</sub> means an empty cell is treated as', ['Ignored', 'Preference 0 with low confidence 1', 'Preference 1', 'A rating of 5'], 1, 'Hu, Koren and Volinsky (2008).', 'Missing clicks are weak evidence of no interest.')
K.quiz('x', 'In the style of a Stanford CS246 exam: logged click data from a deployed recommender gives biased offline estimates mainly because', ['Users lie', 'Users could only click what the old system chose to show', 'Clicks are rare', 'Logs are too large'], 1, 'Exposure bias.', 'Inverse propensity weighting or online tests fix it.')

K.calc('e', 'Cosine similarity of feature vectors (1, 0, 1) and (1, 1, 0)?', '0.5', 'Dot over lengths.', ['Dot product = 1.', 'Each length is &radic;2.', eq('1 / (&radic;2 &times; &radic;2) = 1 / 2 = 0.5')], check=0.5)
K.calc('e', 'Top 5 list with 2 relevant items in it. Precision@5?', '0.4', 'Hits / k.', ['Hits = 2.', 'k = 5.', eq('2 / 5 = 0.4')], check=0.4)
K.calc('e', 'Prediction errors 1, &minus;1, 2 and 0. RMSE?', '1.225', 'Square, mean, root.', ['Squares: 1, 1, 4, 0.', 'Mean = 6 / 4 = 1.5.', eq('&radic;1.5 = 1.225')], check=1.2247, tol=0.002)
K.calc('m', '&mu; = 3.5, b<sub>u</sub> = 0.3, b<sub>i</sub> = &minus;0.4, p<sub>u</sub> = (1, 0.5), q<sub>i</sub> = (0.6, &minus;0.2). Predicted rating?', '3.9', 'Mean plus biases plus dot product.', ['Dot = 1 &times; 0.6 + 0.5 &times; (&minus;0.2) = 0.5.', 'Biases: 0.3 &minus; 0.4 = &minus;0.1.', eq('3.5 &minus; 0.1 + 0.5 = 3.9')], check=3.9)
K.calc('m', 'User mean 3. Neighbour A: similarity 0.8, centred rating +1. Neighbour B: similarity 0.4, centred rating &minus;0.5. Prediction?', '3.5', 'Mean plus weighted average.', ['Weighted sum = 0.8 &times; 1 + 0.4 &times; (&minus;0.5) = 0.6.', 'Sum of |similarity| = 1.2.', eq('3 + 0.6 / 1.2 = 3.5')], check=3.5)
K.calc('m', 'Hits at positions 1 and 3 of a list (relevance 1 each). DCG?', '1.5', 'rel / log<sub>2</sub>(i + 1).', ['Position 1: 1 / log<sub>2</sub>2 = 1.', 'Position 3: 1 / log<sub>2</sub>4 = 0.5.', eq('1 + 0.5 = 1.5')], check=1.5)
K.calc('m', 'A film has 2 ratings with mean 5. Overall mean C = 3.4 and m = 3. Shrunk score?', '4.04', '(n r&#772; + m C) / (n + m).', ['n r&#772; = 10.', 'm C = 10.2.', eq('20.2 / 5 = 4.04')], check=4.04)
K.calc('h', 'Error e = 1, &eta; = 0.1, &lambda; = 0.1, p<sub>u</sub> = (1, 0), q<sub>i</sub> = (0.5, 0.5). New first entry of p<sub>u</sub>?', '1.04', 'p + &eta;(e q &minus; &lambda; p).', ['e q<sub>1</sub> = 0.5.', '&lambda; p<sub>1</sub> = 0.1, so the bracket is 0.4.', eq('1 + 0.1 &times; 0.4 = 1.04')], check=1.04)
K.calc('h', 'Matrix factorisation with 1,000 users, 500 items, k = 20, plus a bias for every user and item and one global mean. Number of parameters?', '31501', 'Factors plus biases plus 1.', ['Factors: (1,000 + 500) &times; 20 = 30,000.', 'Biases: 1,000 + 500 = 1,500.', eq('30,000 + 1,500 + 1 = 31,501')], check=31501)
K.calc('x', 'In the style of a Stanford CS246 problem: hits at positions 1 and 3 of a top 3 list, with 2 relevant items in total. NDCG@3?', '0.92', 'DCG / ideal DCG.', ['DCG = 1 + 1 / log<sub>2</sub>4 = 1.5.', 'Ideal: hits at 1 and 2, so 1 + 1 / log<sub>2</sub>3 = 1.631.', eq('1.5 / 1.631 = 0.92')], check=0.9197, tol=0.002)

K.assign('rec_cosine', 'e', 'Cosine similarity',
         '<p>Write <code>rec_cosine(a, b)</code> that returns the cosine similarity of two lists of numbers, rounded to 4 decimals. Return 0.0 if either list is all zeros.</p>',
         """
def rec_cosine(a, b):
    # your code here
    pass
""", [('rec_cosine([1, 0, 1], [1, 1, 0])', 0.5), ('rec_cosine([1, 2, 3], [2, 4, 6])', 1.0), ('rec_cosine([1, 0], [0, 1])', 0.0), ('rec_cosine([0, 0], [1, 1])', 0.0)],
         """
def rec_cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return round(dot / (na * nb), 4)
""", 'Dot product divided by the product of the two lengths.', '<p>Guarding against a zero length avoids dividing by zero for an item with no features or a user with no ratings.</p>')
K.assign('prec_recall_at_k', 'm', 'Precision and recall at k',
         '<p>Write <code>prec_recall_at_k(recommended, relevant, k)</code>. recommended is a ranked list and relevant a list of items the user really liked. Return [precision@k, recall@k], each rounded to 4 decimals.</p>',
         """
def prec_recall_at_k(recommended, relevant, k):
    # your code here
    pass
""", [('prec_recall_at_k(["A", "B", "C", "D", "E"], ["A", "C", "F"], 5)', [0.4, 0.6667]), ('prec_recall_at_k(["A", "B", "C", "D", "E"], ["A", "C", "F"], 2)', [0.5, 0.3333]), ('prec_recall_at_k(["X", "Y"], ["A"], 2)', [0.0, 0.0])],
         """
def prec_recall_at_k(recommended, relevant, k):
    rel = set(relevant)
    hits = sum(1 for item in recommended[:k] if item in rel)
    return [round(hits / k, 4), round(hits / len(rel), 4)]
""", 'Count hits in the first k items, then divide by k and by the number of relevant items.', '<p>Precision falls as k grows past the hits, while recall can only rise. That trade off is why both are reported.</p>')
K.assign('user_cf_predict', 'h', 'User based prediction',
         '<p>Write <code>user_cf_predict(R, u, j, k)</code>. R is a list of rows of ratings from 1 to 5, with 0 for not rated. Centre each user on the mean of their own ratings, compute the cosine of centred ratings on items both users rated, keep the k users with the highest similarity among those who rated item j, and return the user mean plus the similarity weighted average of their centred ratings of j, rounded to 2 decimals.</p>',
         """
def user_cf_predict(R, u, j, k):
    # your code here
    pass
""", [('user_cf_predict([[5, 4, 0, 1, 0], [4, 5, 1, 0, 1], [1, 0, 5, 4, 5], [0, 1, 4, 5, 4], [5, 5, 0, 2, 1]], 0, 2, 2)', 1.81), ('user_cf_predict([[5, 4, 0, 1, 0], [4, 5, 1, 0, 1], [1, 0, 5, 4, 5], [0, 1, 4, 5, 4], [5, 5, 0, 2, 1]], 4, 2, 2)', 2.07), ('user_cf_predict([[5, 4, 0, 1, 0], [4, 5, 1, 0, 1], [1, 0, 5, 4, 5], [0, 1, 4, 5, 4], [5, 5, 0, 2, 1]], 3, 0, 2)', 1.37)],
         """
def user_cf_predict(R, u, j, k):
    def mean(row):
        vals = [v for v in row if v > 0]
        return sum(vals) / len(vals)

    means = [mean(r) for r in R]

    def sim(a, b):
        xs, ys = [], []
        for t in range(len(R[a])):
            if R[a][t] > 0 and R[b][t] > 0:
                xs.append(R[a][t] - means[a])
                ys.append(R[b][t] - means[b])
        nx = sum(x * x for x in xs) ** 0.5
        ny = sum(y * y for y in ys) ** 0.5
        if nx == 0 or ny == 0:
            return 0.0
        return sum(x * y for x, y in zip(xs, ys)) / (nx * ny)

    others = [v for v in range(len(R)) if v != u and R[v][j] > 0]
    sims = {v: sim(u, v) for v in others}
    top = sorted(others, key=lambda v: -sims[v])[:k]
    num = sum(sims[v] * (R[v][j] - means[v]) for v in top)
    den = sum(abs(sims[v]) for v in top)
    if den == 0:
        return round(means[u], 2)
    return round(means[u] + num / den, 2)
""", 'Write small helpers for the mean of a row and the similarity of two users, then follow the formula.', '<p>The first test matches the program in the lesson: user 1 agrees with user 0 and disliked the film, user 2 disagrees and loved it, and both push the guess down to 1.81.</p>')

K.must('Data', 'A huge sparse user by item matrix. Explicit ratings or implicit clicks. Missing is unknown, not a dislike.')
K.must('Content based', 'Item features, taste profile, cosine similarity. Works for new items, but only finds more of the same.')
K.must('Neighbours', 'Centre on user means, centred cosine (Pearson) on co rated items, top k, r&#770; = r&#772;<sub>u</sub> + &Sigma; sim (r &minus; r&#772;<sub>v</sub>) / &Sigma; |sim|.')
K.must('Factorisation', 'r&#770; = &mu; + b<sub>u</sub> + b<sub>i</sub> + p<sub>u</sub> &middot; q<sub>i</sub>. Loss on known cells plus &lambda; penalty. SGD or ALS. Tune k and &lambda; on held out data.')
K.must('Evaluation', 'Precision@k, recall@k, NDCG@k, MRR on a time based split. RMSE ignores order.')
K.must('Practice', 'Cold start fallbacks, shrunk popularity, two stage retrieval and ranking, feedback loops and popularity bias.')

T = K.topic(
    slug='ml-recommenders', topic='ml-recommenders', step=(3, 'Patterns, anomalies and recommendations', 'ml-u3', 'Spot unusual records, find items that go together, and recommend what a person may like next.', 'Intermediate'),
    title='Recommender systems', short='Recommenders', badge='3.3', minutes=55,
    lead='Recommend what a person may like next: content based filtering, user and item based collaborative filtering, matrix factorisation by SGD and ALS, ranking metrics such as NDCG, cold start, and how large two stage systems work.',
    desc='recommender systems, user item matrix, content based filtering, collaborative filtering, user based, item based, Pearson correlation, matrix factorisation, latent factors, SGD, ALS, implicit feedback, precision at k, recall at k, NDCG, MRR, cold start, two tower model, popularity bias.',
    summary='Content based and collaborative filtering, matrix factorisation by SGD and ALS, ranking metrics, cold start and production systems.',
    keywords=['recommender systems', 'collaborative filtering', 'content based filtering', 'matrix factorisation', 'ALS', 'NDCG', 'cold start', 'latent factors', 'two tower model', 'implicit feedback'],
    recap='<p>Recommenders rank items for each person. Start from popularity, use neighbours or matrix factorisation once interactions pile up, judge the top of the list with ranking metrics, and plan for cold start and feedback loops.</p>',
    added='2026-11-13', leet=leet_items())
