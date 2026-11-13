# Foundations 2.3: probability and statistics for machine learning. Checked against Blitzstein and Hwang, Introduction
# to Probability (2nd edition) chapters 1 to 5 and 10, Deisenroth, Faisal and Ong, Mathematics for Machine Learning
# (2020) chapter 6, Bishop, Pattern Recognition and Machine Learning (2006) chapters 1.2 and 1.6, Cover and Thomas,
# Elements of Information Theory chapter 2, the Stanford CS229 probability review, and the SciPy 1.18 stats reference.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, lc, leet, files, grow, leet_items
from mlkit import link

chapter('ml-probability')
K = Kit()

K.code('dice_counting', r'''
import random
random.seed(7)
rolls = [random.randint(1, 6) for i in range(6000)]
sixes = rolls.count(6)
print("rolls:", len(rolls), " sixes:", sixes)
print("share of sixes:", round(sixes / len(rolls), 4), " theory 1/6 =", round(1 / 6, 4))
both = 0
for i in range(0, 6000, 2):
    if rolls[i] == 6 and rolls[i + 1] == 6:
        both = both + 1
print("two sixes in a row:", round(both / 3000, 4), " theory 1/36 =", round(1 / 36, 4))
even_or_big = 0
for r in rolls:
    if r % 2 == 0 or r >= 5:
        even_or_big = even_or_big + 1
print("even or at least 5:", round(even_or_big / 6000, 4), " theory 4/6 =", round(4 / 6, 4))
''', long=True)

K.code('bayes_test', r'''
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
''')

K.code('distributions', r'''
import numpy as np
from scipy import stats

rng = np.random.default_rng(0)
n = 100000

coin = rng.binomial(1, 0.3, size=n)            # Bernoulli: one yes or no
print("Bernoulli p=0.3   mean", round(coin.mean(), 3), " var", round(coin.var(), 3), " theory 0.3 and 0.21")

heads = rng.binomial(10, 0.5, size=n)          # Binomial: heads in 10 flips
print("Binomial 10, 0.5  mean", round(heads.mean(), 3), " var", round(heads.var(), 3), " theory 5 and 2.5")

calls = rng.poisson(4, size=n)                 # Poisson: calls per hour
print("Poisson rate 4    mean", round(calls.mean(), 3), " var", round(calls.var(), 3), " theory 4 and 4")

height = rng.normal(170, 8, size=n)            # Normal: heights in cm
print("Normal 170, 8     mean", round(height.mean(), 2), " std", round(height.std(), 2))

print("P(exactly 5 heads in 10) =", round(stats.binom.pmf(5, 10, 0.5), 4))
print("P(height below 186) =", round(stats.norm.cdf(186, 170, 8), 4))
print("share within 1, 2, 3 std:", [round(float(np.mean(abs(height - 170) < k * 8)), 3) for k in (1, 2, 3)])
''')

K.code('mean_var_corr', r'''
import numpy as np

hours = np.array([1, 2, 3, 4, 5, 6, 7, 8])
score = np.array([52, 55, 61, 64, 70, 71, 78, 95])

print("mean score:", score.mean(), " median:", np.median(score))
print("variance:", round(score.var(), 2), " std:", round(score.std(), 2))
print("sample std (ddof=1):", round(score.std(ddof=1), 2))
cov = np.mean((hours - hours.mean()) * (score - score.mean()))
corr = cov / (hours.std() * score.std())
print("covariance:", round(cov, 2), " correlation:", round(corr, 3))
print("numpy corrcoef:", round(np.corrcoef(hours, score)[0, 1], 3))
''')

K.code('clt_demo', r'''
import numpy as np

rng = np.random.default_rng(1)
for n in [1, 4, 16, 64]:
    rolls = rng.integers(1, 7, size=(20000, n))   # 20000 groups of n dice
    means = rolls.mean(axis=1)
    print("n =", n, " mean of means", round(means.mean(), 3), " std of means", round(means.std(), 3),
          " theory", round(1.7078 / np.sqrt(n), 3))
''')

K.code('mle_coin', r'''
import numpy as np

flips = [1, 0, 1, 1, 0, 1, 1, 0, 1, 1]       # 7 heads in 10 flips
heads = sum(flips)
tails = len(flips) - heads

best_p = 0
best_ll = -1e9
for p in np.arange(0.05, 1.0, 0.05):
    log_likelihood = heads * np.log(p) + tails * np.log(1 - p)
    if log_likelihood > best_ll:
        best_ll = log_likelihood
        best_p = p
print("best p on the grid:", round(best_p, 2), " formula heads / n =", heads / len(flips))
print("log likelihood there:", round(best_ll, 3))
print("negative log likelihood per flip (log loss):", round(-best_ll / len(flips), 4))

data = np.array([4.0, 6.0, 5.5, 7.0, 4.5])
print("Gaussian MLE mean:", data.mean(), " MLE variance:", round(data.var(), 3))
''', long=True)

K.code('entropy_loss', r'''
import numpy as np
from sklearn.metrics import log_loss

def entropy(p):
    p = np.array(p)
    return -np.sum(p * np.log2(p))

print("fair coin entropy:", entropy([0.5, 0.5]), "bit")
print("biased coin 0.9 / 0.1:", round(entropy([0.9, 0.1]), 3), "bits")
print("fair die:", round(entropy([1 / 6] * 6), 3), "bits")

true = np.array([1, 0, 0])          # the real class is the first one
pred = np.array([0.7, 0.2, 0.1])    # what the model said
ce = -np.sum(true * np.log(pred))
print("cross entropy:", round(ce, 4), " equals -ln(0.7)")

p = np.array([0.5, 0.5])
q = np.array([0.9, 0.1])
kl = np.sum(p * np.log(p / q))
print("KL(p || q):", round(kl, 4), " KL(q || p):", round(np.sum(q * np.log(q / p)), 4))

y = [1, 0, 1, 1]
probs = [0.9, 0.2, 0.6, 0.8]
by_hand = -np.mean([np.log(pr) if t == 1 else np.log(1 - pr) for t, pr in zip(y, probs)])
print("log loss by hand:", round(by_hand, 4), " sklearn:", round(log_loss(y, probs), 4))
''')

K.code('ab_test', r'''
import numpy as np
from scipy import stats

clicks_a, users_a = 120, 2400     # old page
clicks_b, users_b = 156, 2400     # new page
pa = clicks_a / users_a
pb = clicks_b / users_b
pooled = (clicks_a + clicks_b) / (users_a + users_b)
se = np.sqrt(pooled * (1 - pooled) * (1 / users_a + 1 / users_b))
z = (pb - pa) / se
p_value = 2 * (1 - stats.norm.cdf(abs(z)))
print("rate A:", pa, " rate B:", pb)
print("z =", round(z, 3), " p value =", round(p_value, 4))
print("significant at 5%:", p_value < 0.05)

se_diff = np.sqrt(pa * (1 - pa) / users_a + pb * (1 - pb) / users_b)
low = (pb - pa) - 1.96 * se_diff
high = (pb - pa) + 1.96 * se_diff
print("95% confidence interval for B - A:", round(low, 4), "to", round(high, 4))
''')

K.lesson('rules', 'Probability: counting how likely things are', f'''
{src('Blitzstein and Hwang, Introduction to Probability chapters 1 to 5 and 10, Deisenroth, Faisal and Ong, Mathematics for Machine Learning chapter 6, Bishop, Pattern Recognition and Machine Learning chapters 1.2 and 1.6, and Cover and Thomas, Elements of Information Theory chapter 2.')}
{wwh('<b>Probability</b> is a number from 0 to 1 that says how likely something is. 0 means it never happens, 1 means it always happens, and 0.5 means half the time. A <b>random variable</b> is a number whose value depends on chance, like the result of a dice roll.',
     'Real data is noisy and the future is uncertain. A spam filter cannot be sure an email is spam, but it can say "93% likely". Probability gives models a clean way to talk about what they do not know, and most loss functions come straight from it.',
     'Count the outcomes you care about and divide by all equally likely outcomes. For harder cases, combine simple probabilities with a few rules (the sum rule, the product rule and conditional probability), or simulate many times and count, as the program below does.')}
{run('dice_counting')}
{table(['Rule', 'Formula', 'Example with one die'], [
    ['Complement', 'P(not A) = 1 &minus; P(A)', 'P(not 6) = 1 &minus; 1/6 = 5/6'],
    ['Sum rule (or)', 'P(A or B) = P(A) + P(B) &minus; P(A and B)', 'P(even or at least 5) = 3/6 + 2/6 &minus; 1/6 = 4/6'],
    ['Product rule (and)', 'P(A and B) = P(A) &times; P(B | A)', 'Two sixes in a row = 1/6 &times; 1/6 = 1/36'],
    ['Independent events', 'P(A and B) = P(A) &times; P(B)', 'Dice rolls do not affect each other'],
    ['Conditional', 'P(A | B) = P(A and B) / P(B)', 'P(6 | even) = (1/6) / (3/6) = 1/3']])}
{note('P(A | B) is read "the probability of A given B". It means: only look at the cases where B happened, and ask how often A happened among them.', 'tip')}
{scene('a weather forecast', '<p>When the forecast says "70% chance of rain", it means that on many days with weather like today, it rained on about 7 out of 10 of them. A classifier that says "70% spam" makes the same kind of promise. If it is well calibrated, about 7 in 10 of the emails it scores at 0.7 really are spam.</p>')}
''', kw=['probability', 'random variable', 'sum rule', 'product rule', 'conditional probability', 'independence', 'complement'])

K.lesson('bayes', 'Bayes rule: updating a belief with new evidence', f'''
{viz('mlbayes')}
{wwh('<b>Bayes rule</b> turns P(evidence | cause) into P(cause | evidence). It says how much to change a belief (the <b>prior</b>) after you see new evidence, giving the updated belief (the <b>posterior</b>).',
     'We usually know how a cause produces evidence (how often a sick person tests positive), but we want the reverse (how likely a person with a positive test is sick). Our intuition gets this badly wrong when the cause is rare. Bayes rule gets it right, and it is the base of naive Bayes classifiers and Bayesian machine learning.',
     'Multiply the prior by the likelihood of the evidence, then divide by the total chance of the evidence so the answers add up to 1. The counting picture above shows the same thing with people: positives that are really sick, divided by all positives.')}
{run('bayes_test')}
{fxs(fx('Bayes rule', 'P(A | B) = P(B | A) &times; P(A) / P(B)', 'Posterior = likelihood &times; prior / evidence.', key=True),
     fx('Total probability', 'P(B) = P(B | A) P(A) + P(B | not A) P(not A)', 'Adds up every way B can happen.', key=True))}
{steps('Worked example: the medical test by hand', [
    '1% are sick, the test finds 95% of sick people, and wrongly flags 5% of healthy people.',
    'P(+) = 0.95 &times; 0.01 + 0.05 &times; 0.99 = 0.0095 + 0.0495 = 0.059.',
    eq('P(sick | +) = 0.0095 / 0.059 = 0.161'),
    'So only about 16% of the people who test positive are really sick, even with a "95% accurate" test. The disease is so rare that the false alarms outnumber the real cases.'])}
{note('Ignoring the prior is called the <b>base rate fallacy</b>. It is a common exam trap and a real problem in fraud and disease detection, where the event you look for is rare.', 'exam')}
''', kw=['Bayes rule', 'prior', 'posterior', 'likelihood', 'evidence', 'total probability', 'base rate fallacy'])

K.lesson('distributions', 'The distributions you will meet everywhere', f'''
{wwh('A <b>probability distribution</b> lists every value a random variable can take and how likely each one is. A few shapes appear again and again in real data, so they have names.',
     'If you know which shape your data has, you can pick the right model and loss. Counts of rare events follow a Poisson shape, yes or no answers follow a Bernoulli shape, and measurements like height follow a normal (bell) shape.',
     'Each named distribution has a formula with one or two parameters. Once you set the parameters (for example the mean and spread of a normal), you can compute the chance of any value, or draw random samples, with scipy.stats and numpy.')}
{run('distributions')}
{table(['Distribution', 'What it counts', 'Parameters', 'Mean', 'Variance', 'ML example'], [
    ['Bernoulli', 'One yes or no', 'p', 'p', 'p(1 &minus; p)', 'Is this email spam'],
    ['Binomial', 'Number of yes in n tries', 'n, p', 'np', 'np(1 &minus; p)', 'Clicks out of n ads shown'],
    ['Poisson', 'Events in a fixed time', '&lambda;', '&lambda;', '&lambda;', 'Calls per hour, website visits'],
    ['Uniform', 'Any value in a range, all equal', 'a, b', '(a + b)/2', '(b &minus; a)<sup>2</sup>/12', 'Random initial weights'],
    ['Normal (Gaussian)', 'Measurements around a centre', '&mu;, &sigma;', '&mu;', '&sigma;<sup>2</sup>', 'Heights, errors of a regression'],
    ['Categorical', 'One of k classes', 'p<sub>1</sub> to p<sub>k</sub>', '', '', 'Softmax output of a classifier']])}
{fxs(fx('Binomial', 'P(X = k) = C(n, k) p<sup>k</sup> (1 &minus; p)<sup>n&minus;k</sup>', 'C(n, k) = n! / (k! (n &minus; k)!) ways to pick which tries are yes.', key=True),
     fx('Normal density', 'f(x) = (1 / (&sigma;&radic;(2&pi;))) e<sup>&minus;(x &minus; &mu;)<sup>2</sup> / (2&sigma;<sup>2</sup>)</sup>', 'The bell curve.', key=True),
     fx('Poisson', 'P(X = k) = &lambda;<sup>k</sup> e<sup>&minus;&lambda;</sup> / k!', 'Mean and variance are both &lambda;.'),
     fx('68, 95, 99.7 rule', 'P(|X &minus; &mu;| &lt; k&sigma;) &asymp; 0.68, 0.95, 0.997 for k = 1, 2, 3', 'The program above measures 0.684, 0.954, 0.997.'))}
{note('A <b>PMF</b> (probability mass function) gives probabilities for whole numbers like counts. A <b>PDF</b> (probability density function) is for continuous values. For a PDF, a single exact value has probability 0, and you get probabilities from areas under the curve, which is what the <b>CDF</b> (cumulative distribution function) adds up.', 'tip')}
''', kw=['distribution', 'Bernoulli', 'binomial', 'Poisson', 'uniform', 'normal distribution', 'Gaussian', 'PMF', 'PDF', 'CDF'])

K.lesson('describe', 'Mean, variance and correlation', f'''
{wwh('The <b>mean</b> (average) is the centre of the data, the <b>median</b> is the middle value, the <b>variance</b> and <b>standard deviation</b> measure the spread, and <b>covariance</b> and <b>correlation</b> measure how two features move together.',
     'Before you train any model you describe the data. The mean and spread tell you whether to scale features. Correlation tells you which features carry similar information and which are related to the target.',
     'The mean adds the values and divides by the count. The variance averages the squared distances from the mean, and the standard deviation is its square root, so it has the same unit as the data. Correlation divides the covariance by both standard deviations, so it always lands between &minus;1 and 1.')}
{run('mean_var_corr')}
{fxs(fx('Mean (expected value)', 'E[X] = &Sigma; x P(x), sample mean x&#772; = (1/n) &Sigma; x<sub>i</sub>', 'The centre.', key=True),
     fx('Variance', 'Var(X) = E[(X &minus; &mu;)<sup>2</sup>] = E[X<sup>2</sup>] &minus; (E[X])<sup>2</sup>', 'Average squared distance from the mean.', key=True),
     fx('Correlation', 'r = Cov(X, Y) / (&sigma;<sub>X</sub> &sigma;<sub>Y</sub>)', 'Between &minus;1 and 1. 0 means no straight line relation.', key=True),
     fx('Linearity of expectation', 'E[aX + bY] = a E[X] + b E[Y]', 'Always true, even when X and Y depend on each other.'),
     fx('Variance of a sum', 'Var(X + Y) = Var(X) + Var(Y) + 2 Cov(X, Y)', 'The covariance term vanishes when X and Y are independent.'))}
{note('The sample standard deviation divides by n &minus; 1 instead of n (ddof=1 in numpy, the default in pandas). This small change corrects for the fact that the sample mean is closer to the data than the true mean is. The program shows 12.9 with n and 13.79 with n &minus; 1.', 'warn')}
{note('Correlation is not causation. Ice cream sales and drownings both rise in summer, but one does not cause the other. Correlation also only measures straight line relations: y = x<sup>2</sup> on symmetric x has correlation 0.', 'exam')}
''', kw=['mean', 'median', 'variance', 'standard deviation', 'covariance', 'correlation', 'expected value', 'ddof', 'causation'])

K.lesson('clt', 'The law of large numbers and the central limit theorem', f'''
{viz('mlclt')}
{wwh('The <b>law of large numbers</b> says that the average of many samples gets close to the true mean. The <b>central limit theorem</b> (CLT) says more: the average of n samples follows a bell shaped normal distribution, whatever shape the original data had, and its spread shrinks like &sigma; / &radic;n.',
     'It explains why we can trust a test score measured on a few thousand examples, how wide the error bars on that score should be, and why the normal distribution appears in so many statistical tests.',
     'Each average mixes many independent values, so the highs and lows cancel. The cancelling makes the averages pile up near the mean in a bell shape, and more values per average means more cancelling, so a narrower bell.')}
{run('clt_demo')}
{fx('Standard error of the mean', 'SE = &sigma; / &radic;n', 'To halve the error bar, you need four times as much data.', key=True)}
{note('A model scores 90% accuracy on 400 test examples. The standard error is &radic;(0.9 &times; 0.1 / 400) = 0.015, so the real accuracy is likely within about 90% &plusmn; 3%. Two models that differ by 1% on this test set may not really differ at all.', 'tip')}
''', kw=['law of large numbers', 'central limit theorem', 'standard error', 'sampling distribution', 'error bars'])

K.lesson('mle', 'Maximum likelihood: where loss functions come from', f'''
{wwh('<b>Maximum likelihood estimation</b> (MLE) picks the parameters that make the data you saw most likely. The <b>likelihood</b> is the probability of the data, seen as a function of the parameters.',
     'It is the reason behind the losses you will use. Minimising mean squared error is MLE when the noise is normal. Minimising log loss (cross entropy) is MLE for a yes or no target. So a loss is not a random choice, it comes from an assumption about the data.',
     'Write the probability of every data point using the model, multiply them (they are independent), take the log so the product becomes a sum, and find the parameters that make it largest. Minimising the negative log likelihood is the same thing, which is how libraries do it.')}
{run('mle_coin')}
{fxs(fx('Likelihood', 'L(&theta;) = &Pi;<sub>i</sub> P(x<sub>i</sub> | &theta;)', 'Product over independent data points.', key=True),
     fx('Log likelihood', 'log L(&theta;) = &Sigma;<sub>i</sub> log P(x<sub>i</sub> | &theta;)', 'Sums are easier than products and do not underflow.', key=True),
     fx('Coin MLE', 'p&#770; = heads / n', 'Set the derivative of h log p + t log(1 &minus; p) to 0.', key=True),
     fx('Normal noise gives MSE', '&minus;log L = (1 / (2&sigma;<sup>2</sup>)) &Sigma; (y<sub>i</sub> &minus; ŷ<sub>i</sub>)<sup>2</sup> + constant', 'Maximising likelihood is minimising squared error.'),
     fx('Bernoulli gives log loss', '&minus;log L = &minus;&Sigma; [y log p + (1 &minus; y) log(1 &minus; p)]', 'The loss of logistic regression.'))}
{steps('Worked example: the coin MLE with calculus', [
    'Data: h = 7 heads and t = 3 tails. log L(p) = 7 log p + 3 log(1 &minus; p).',
    'Derivative: 7/p &minus; 3/(1 &minus; p). Set it to 0.',
    '7(1 &minus; p) = 3p, so 7 = 10p.',
    eq('p&#770; = 0.7'),
    'This matches the grid search in the program and the simple rule heads / n.'])}
{deep('MAP: adding a prior turns into regularisation', '<p>Maximum a posteriori (MAP) estimation maximises P(&theta; | data) &prop; P(data | &theta;) P(&theta;). Taking logs adds log P(&theta;) to the log likelihood. A normal prior on the weights adds &minus;&lambda;||w||<sup>2</sup>, which is exactly ridge (L2) regularisation, and a Laplace prior gives lasso (L1). You will use both in Supervised 1.2.</p>')}
''', kw=['maximum likelihood', 'likelihood', 'log likelihood', 'negative log likelihood', 'MAP', 'prior', 'regularisation link'])

K.lesson('entropy', 'Entropy, cross entropy and KL divergence', f'''
{wwh('<b>Entropy</b> measures how uncertain a distribution is. <b>Cross entropy</b> measures how well a predicted distribution matches the true one. <b>KL divergence</b> is the extra cost of using the prediction instead of the truth.',
     'Cross entropy is the loss used to train almost every classifier, from logistic regression to large language models. Entropy is also how decision trees choose splits (information gain), and KL divergence appears in variational autoencoders and in modern reinforcement learning.',
     'Entropy averages &minus;log p over the outcomes: rare outcomes carry more surprise. Cross entropy averages &minus;log q, the surprise of the model, over what really happens. When the true label is one class, it is simply &minus;log of the probability the model gave to that class.')}
{run('entropy_loss')}
{fxs(fx('Entropy', 'H(p) = &minus;&Sigma; p<sub>i</sub> log<sub>2</sub> p<sub>i</sub>', 'In bits. A fair coin has 1 bit, a sure thing has 0.', key=True),
     fx('Cross entropy', 'H(p, q) = &minus;&Sigma; p<sub>i</sub> log q<sub>i</sub>', 'p is the truth, q the prediction. This is the classification loss.', key=True),
     fx('KL divergence', 'KL(p || q) = &Sigma; p<sub>i</sub> log(p<sub>i</sub> / q<sub>i</sub>) = H(p, q) &minus; H(p)', 'Always 0 or more, and 0 only when p = q. Not symmetric.', key=True))}
{note('The program shows KL(p || q) = 0.5108 but KL(q || p) = 0.3681. KL divergence is not a true distance because swapping the two distributions changes the answer.', 'exam')}
''', kw=['entropy', 'cross entropy', 'KL divergence', 'information gain', 'log loss', 'bits', 'surprise'])

K.lesson('testing', 'Hypothesis tests and confidence intervals', f'''
{wwh('A <b>hypothesis test</b> asks whether a difference you measured could be just luck. The <b>p value</b> is the chance of seeing a difference at least this big if there were really no difference. A <b>confidence interval</b> gives a range of believable values for the true difference.',
     'You will compare models, features and website versions (A/B tests). A model that is 1% better on one test set may be no better at all. Tests tell you when a difference is real enough to act on.',
     'Assume there is no difference (the <b>null hypothesis</b>). Use the central limit theorem to know how much the measured difference would wobble by chance (the standard error). Divide the measured difference by that wobble to get a z score, and turn it into a p value. If p is below a chosen level, usually 0.05, call the result significant.')}
{run('ab_test')}
{fxs(fx('z score', 'z = (measured &minus; expected under null) / standard error', 'How many standard errors away the result is.', key=True),
     fx('95% confidence interval', 'estimate &plusmn; 1.96 &times; standard error', '1.96 is where the normal curve leaves 2.5% in each tail.', key=True))}
{table(['Term', 'Plain meaning'], [
    ['Null hypothesis', 'The boring explanation: there is no real difference'],
    ['p value', 'How surprising the data would be if the null were true'],
    ['Significance level &alpha;', 'The cut off you chose before the test, often 0.05'],
    ['Type I error', 'Saying there is a difference when there is none (false alarm)'],
    ['Type II error', 'Missing a difference that is really there'],
    ['Power', 'The chance of finding a real difference. More data gives more power']])}
{note('A p value is not the chance that the null hypothesis is true. If you test 20 useless features at the 0.05 level, about one will look significant by luck. Correct for many tests (for example the Bonferroni correction divides &alpha; by the number of tests).', 'warn')}
''', kw=['hypothesis test', 'p value', 'null hypothesis', 'confidence interval', 'z test', 'A/B test', 'type I error', 'type II error', 'power'])

K.lesson('versus', 'Frequentist and Bayesian thinking compared', f'''
{versus('Two ways to think about probability', ['', 'Frequentist', 'Bayesian'], [
    ['What probability means', 'How often something happens over many repeats', 'How strongly you believe something'],
    ['Parameters', 'Fixed but unknown numbers', 'Random variables with a distribution'],
    ['Uses a prior', 'No', 'Yes, updated by the data'],
    ['Typical answer', 'A point estimate (MLE) and a confidence interval', 'A full posterior distribution and a credible interval'],
    ['With little data', 'Can overfit or be unstable', 'The prior keeps estimates sensible'],
    ['ML examples', 'Most of scikit-learn, p values, A/B tests', 'Naive Bayes, Gaussian processes, Bayesian optimisation for tuning']],
    'most everyday ML uses frequentist MLE with regularisation, which is the same as a Bayesian MAP estimate with a simple prior.')}
{link('ml-maths', 'More probability practice', 'Maths for Machine Learning has longer chapters on probability, random variables, Bayes rule and statistics.', 'Open Maths for ML')}
''', kw=['frequentist', 'Bayesian', 'credible interval', 'posterior distribution', 'MAP vs MLE'])

K.lesson('maths', 'The maths, all in one place', f'''
{fxs(fx('Conditional probability', 'P(A | B) = P(A and B) / P(B)', 'Only look at the cases where B happened.', key=True),
     fx('Bayes rule', 'P(A | B) = P(B | A) P(A) / P(B)', 'Posterior from prior and likelihood.', key=True),
     fx('Expectation and variance', 'E[X] = &Sigma; x P(x), Var(X) = E[X<sup>2</sup>] &minus; E[X]<sup>2</sup>', 'Centre and spread.', key=True),
     fx('Standard error', 'SE = &sigma; / &radic;n', 'From the central limit theorem.', key=True),
     fx('Log likelihood', 'log L(&theta;) = &Sigma; log P(x<sub>i</sub> | &theta;)', 'Maximise it, or minimise its negative.', key=True),
     fx('Cross entropy', 'H(p, q) = &minus;&Sigma; p log q', 'The classification loss.', key=True))}
{steps('Worked example: expectation and variance of a die', [
    'E[X] = (1 + 2 + 3 + 4 + 5 + 6) / 6 = 21 / 6 = 3.5.',
    'E[X<sup>2</sup>] = (1 + 4 + 9 + 16 + 25 + 36) / 6 = 91 / 6 = 15.167.',
    eq('Var(X) = 15.167 &minus; 3.5<sup>2</sup> = 15.167 &minus; 12.25 = 2.917'),
    '&sigma; = &radic;2.917 = 1.708. This is the 1.708 used in the central limit program.'])}
{steps('Worked example: binomial probability', [
    'What is the chance of exactly 2 heads in 4 fair flips?',
    'C(4, 2) = 4! / (2! 2!) = 6 ways.',
    eq('P = 6 &times; 0.5<sup>2</sup> &times; 0.5<sup>2</sup> = 6 / 16 = 0.375'),
    'scipy.stats.binom.pmf(2, 4, 0.5) gives 0.375 as well.'])}
{deep('Jensen and the reason log loss punishes confident mistakes', '<p>log is concave, so Jensen’s inequality gives E[log X] &le; log E[X]. Gibbs’ inequality, KL(p || q) &ge; 0, follows from it, which proves that cross entropy is smallest exactly when the predicted distribution equals the true one. That is why minimising cross entropy produces calibrated probabilities. Because &minus;log q grows without limit as q goes to 0, a model that gives probability 0.001 to the true class pays &minus;ln(0.001) = 6.9, about 19 times the cost of predicting 0.7.</p>')}
''', kw=['conditional probability formula', 'Bayes formula', 'expectation', 'variance', 'binomial', 'Jensen inequality', 'Gibbs inequality'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Probability is a number from 0 to 1 saying how likely something is. Bayes rule updates a belief when new facts arrive. The mean is the centre of data and the standard deviation is its spread.</p>',
    '<p>Use the sum, product and conditional rules, apply Bayes rule with the base rate, know the Bernoulli, binomial, Poisson and normal distributions, compute mean, variance and correlation, and know that averages shrink their error like &sigma; / &radic;n.</p>',
    '<p>Derive losses from maximum likelihood (MSE from normal noise, log loss from Bernoulli), relate MAP to regularisation, use entropy, cross entropy and KL divergence, and run hypothesis tests and confidence intervals with care about multiple testing.</p>',
    '<p>Exponential families unify the common distributions and give generalised linear models. MLE is consistent and asymptotically normal with variance given by the inverse Fisher information (the Cram&eacute;r Rao bound). Concentration inequalities (Hoeffding, Chernoff) give finite sample guarantees that underpin PAC learning theory.</p>')}
{grow('Compute simple probabilities, use Bayes rule on a medical test, and describe data with mean and spread.',
      'Work with named distributions in scipy, derive the coin MLE, and run an A/B test with a confidence interval.',
      'Explain where every common loss comes from, reason with KL divergence, and use concentration bounds.')}
''', kw=['beginner', 'expert', 'exponential family', 'Fisher information', 'Cramer Rao', 'Hoeffding', 'PAC learning'])

lc(1227, 'Airplane Seat Assignment Probability', 'airplane-seat-assignment-probability', 'm', 'Probability by cases', 'Try small n by hand. With one person the answer is 1. With more, the first person picks their own seat or the last person’s seat with the same chance, and every other choice just passes the same problem to someone else, so the answer is 0.5.', r'''
def nth_person_gets_nth_seat(n):
    # f(1) = 1. For n >= 2 the first passenger picks seat 1 (last person wins) or seat n (last person loses)
    # with equal chance, and any other pick restarts the same game with fewer people. So f(n) = 0.5.
    if n == 1:
        return 1.0
    return 0.5
''', [('nth_person_gets_nth_seat(1)', 1.0), ('nth_person_gets_nth_seat(2)', 0.5), ('nth_person_gets_nth_seat(100)', 0.5)])
lc(528, 'Random Pick with Weight', 'random-pick-with-weight', 'm', 'Prefix sums and binary search', 'Turn the weights into running totals. Pick a random number from 1 to the total and binary search for the first running total that reaches it. Index i is chosen with chance w[i] / total.', r'''
import random


class Solution:
    def __init__(self, w):
        self.totals = []
        running = 0
        for weight in w:
            running = running + weight
            self.totals.append(running)

    def pickIndex(self):
        target = random.randint(1, self.totals[-1])
        low = 0
        high = len(self.totals) - 1
        while low < high:
            mid = (low + high) // 2
            if self.totals[mid] < target:
                low = mid + 1
            else:
                high = mid
        return low


def pick_shares(w, picks):
    random.seed(0)
    s = Solution(w)
    counts = [0] * len(w)
    for i in range(picks):
        counts[s.pickIndex()] += 1
    return [round(c / picks, 1) for c in counts]
''', [('Solution([5]).pickIndex()', 0), ('pick_shares([1, 3], 10000)', [0.2, 0.8]), ('pick_shares([1, 1, 2], 10000)', [0.2, 0.3, 0.5])])
lc(1093, 'Statistics from a Large Sample', 'statistics-from-a-large-sample', 'm', 'Mean, median and mode from counts', 'count[v] says how many times value v appears. Walk the counts once for the minimum, maximum, total, and the most common value. For the median, walk again until you pass the middle position (or the two middle positions).', r'''
def sample_stats(count):
    n = sum(count)
    smallest = -1
    largest = -1
    total = 0
    mode = 0
    for v in range(len(count)):
        if count[v] > 0:
            if smallest == -1:
                smallest = v
            largest = v
            total = total + v * count[v]
            if count[v] > count[mode]:
                mode = v

    def value_at(position):
        seen = 0
        for v in range(len(count)):
            seen = seen + count[v]
            if seen > position:
                return v

    if n % 2 == 1:
        median = value_at(n // 2)
    else:
        median = (value_at(n // 2 - 1) + value_at(n // 2)) / 2
    return [float(smallest), float(largest), total / n, float(median), float(mode)]


def stats_of(values):
    count = [0] * 256
    for v in values:
        count[v] += 1
    return sample_stats(count)
''', [('stats_of([1, 2, 2, 2, 3, 3, 3, 3])', [1.0, 3.0, 2.375, 2.5, 3.0]), ('stats_of([1, 2, 2, 2, 4])', [1.0, 4.0, 2.2, 2.0, 2.0])])
lc(295, 'Find Median from Data Stream', 'find-median-from-data-stream', 'h', 'Two heaps', 'Keep the smaller half in a max heap and the larger half in a min heap, with sizes that differ by at most one. The median is the top of the bigger heap, or the average of both tops.', r'''
import heapq


class MedianFinder:
    def __init__(self):
        self.low = []    # max heap of the smaller half (numbers stored as negatives)
        self.high = []   # min heap of the larger half

    def addNum(self, num):
        heapq.heappush(self.low, -num)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def findMedian(self):
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2


def medians_of(nums):
    finder = MedianFinder()
    result = []
    for x in nums:
        finder.addNum(x)
        result.append(finder.findMedian())
    return result
''', [('medians_of([1, 2, 3])', [1.0, 1.5, 2.0]), ('medians_of([5, 15, 1, 3])', [5.0, 10.0, 5.0, 4.0])])
lc(837, 'New 21 Game', 'new-21-game', 'm', 'Probability with dynamic programming', 'prob[x] is the chance of ever having exactly x points. Each draw adds 1 to maxPts with equal chance, so prob[x] is the sum of prob over the last maxPts totals that are still drawing (below k), divided by maxPts. Keep that sum in a sliding window.', r'''
def new21_game(n, k, max_pts):
    if k == 0 or n >= k - 1 + max_pts:
        return 1.0
    prob = [0.0] * (n + 1)
    prob[0] = 1.0
    window = 1.0        # sum of prob[x] for the totals that can still draw
    answer = 0.0
    for x in range(1, n + 1):
        prob[x] = window / max_pts
        if x < k:
            window = window + prob[x]
        else:
            answer = answer + prob[x]
        if x - max_pts >= 0 and x - max_pts < k:
            window = window - prob[x - max_pts]
    return round(answer, 5)
''', [('new21_game(10, 1, 10)', 1.0), ('new21_game(6, 1, 10)', 0.6), ('new21_game(21, 17, 10)', 0.73278)])
lc(688, 'Knight Probability in Chessboard', 'knight-probability-in-chessboard', 'm', 'Spread the probability step by step', 'Keep a board of chances. Each move, every square sends 1/8 of its chance to each of its 8 knight moves that stay on the board. After k moves, add up the board.', r'''
def knight_probability(n, k, row, column):
    moves = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
    board = [[0.0] * n for i in range(n)]
    board[row][column] = 1.0
    for step in range(k):
        new_board = [[0.0] * n for i in range(n)]
        for r in range(n):
            for c in range(n):
                if board[r][c] > 0:
                    for dr, dc in moves:
                        nr = r + dr
                        nc = c + dc
                        if 0 <= nr < n and 0 <= nc < n:
                            new_board[nr][nc] += board[r][c] / 8
        board = new_board
    total = 0.0
    for r in range(n):
        total = total + sum(board[r])
    return round(total, 5)
''', [('knight_probability(3, 2, 0, 0)', 0.0625), ('knight_probability(1, 0, 0, 0)', 1.0)])
lc(808, 'Soup Servings', 'soup-servings', 'm', 'Expected value with memoised recursion', 'Count in units of 25 ml. Each of the 4 serving choices has chance 0.25. The chance that A runs out first, plus half the chance both run out together, is the average over the 4 choices. For big n the answer is so close to 1 that you can return 1.', r'''
from functools import lru_cache


def soup_servings(n):
    if n > 4800:
        return 1.0
    units = (n + 24) // 25

    @lru_cache(maxsize=None)
    def chance(a, b):
        if a <= 0 and b <= 0:
            return 0.5
        if a <= 0:
            return 1.0
        if b <= 0:
            return 0.0
        return 0.25 * (chance(a - 4, b) + chance(a - 3, b - 1) + chance(a - 2, b - 2) + chance(a - 1, b - 3))

    return round(chance(units, units), 5)
''', [('soup_servings(50)', 0.625), ('soup_servings(100)', 0.71875), ('soup_servings(5000)', 1.0)])

K.lesson('leetcode', 'LeetCode practice', leet('<p>These problems use probability and statistics directly: reason about chances by cases, pick items by weight, compute mean, median and mode from counts, keep a running median, and spread probability step by step with dynamic programming. The page gives only a hint. Solve on LeetCode first, then compare with the downloadable solution.</p>'),
         kw=['LeetCode', 'probability', 'dynamic programming', 'median', 'heap', 'prefix sum', 'weighted sampling'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Probability</b> runs from 0 (never) to 1 (always). Use the complement, sum, product and conditional rules.',
    '<b>Bayes rule</b>: P(A | B) = P(B | A) P(A) / P(B). Never ignore the prior (the base rate).',
    'Named distributions: Bernoulli (yes or no), binomial (yes count), Poisson (event count), normal (bell), categorical (classes).',
    'Describe data with the mean, median, variance and standard deviation. Correlation runs from &minus;1 to 1 and is not causation.',
    'The <b>central limit theorem</b>: averages become normal with spread &sigma; / &radic;n.',
    '<b>Maximum likelihood</b> picks the parameters that make the data most likely. Normal noise gives MSE, yes or no data gives log loss.',
    '<b>Cross entropy</b> is the classification loss. <b>KL divergence</b> is the extra cost of a wrong distribution.',
    'A <b>p value</b> says how surprising the data is if there were no difference. Confidence interval = estimate &plusmn; 1.96 SE.'],
    'Foundations 3.1 moves to real data: loading it with pandas, finding missing values and outliers, and cleaning it.')}
{files('Three tasks: Bayes rule for a test result, the mean and standard deviation by hand, and the log loss of some predictions.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'A fair die is rolled. What is P(roll is 5 or 6)?', ['1/6', '1/3', '1/2', '5/6'], 1, 'Two good outcomes out of six.', '2/6 = 1/3.')
K.quiz('e', 'Two fair coins are flipped. P(both heads) is', ['1/2', '1/4', '1/3', '3/4'], 1, 'Independent, so multiply.', '1/2 &times; 1/2 = 1/4.')
K.quiz('e', 'Which distribution fits "number of emails that arrive in one hour"?', ['Bernoulli', 'Poisson', 'Normal', 'Uniform'], 1, 'Counts of events in a fixed time.', 'Poisson models counts of events in a fixed window.')
K.quiz('e', 'The standard deviation is', ['The middle value', 'The square root of the variance', 'The most common value', 'The largest value minus the smallest'], 1, 'Same unit as the data.', 'It is &radic;Var.')
K.quiz('m', 'In Bayes rule, the prior is', ['The probability of the evidence', 'Your belief before seeing the evidence', 'The answer after the evidence', 'The test accuracy'], 1, 'Before.', 'The prior P(A) is updated to the posterior P(A | B).')
K.quiz('m', 'Correlation between two features is 0. Which is true?', ['They are independent', 'There is no straight line relation, but they may still be related', 'One causes the other', 'They have the same mean'], 1, 'Think of y = x<sup>2</sup>.', 'Correlation only measures linear relations.')
K.quiz('m', 'Minimising mean squared error is maximum likelihood when the noise is', ['Uniform', 'Normal (Gaussian)', 'Poisson', 'Bernoulli'], 1, 'The bell curve has a squared term in its exponent.', '&minus;log of a normal density is a squared error plus a constant.')
K.quiz('m', 'If you collect four times as much data, the standard error of the mean', ['Stays the same', 'Halves', 'Quarters', 'Doubles'], 1, '&sigma; / &radic;n.', '&radic;4 = 2, so it halves.')
K.quiz('m', 'An A/B test gives p = 0.03 at &alpha; = 0.05. This means', ['There is a 3% chance the null is true', 'Data this extreme would happen 3% of the time if there were no difference', 'B is 3% better', 'The test has 97% power'], 1, 'p values are about the data, assuming the null.', 'That is the definition of a p value.')
K.quiz('h', 'Which is always true about KL divergence?', ['KL(p || q) = KL(q || p)', 'KL(p || q) &ge; 0 with equality only when p = q', 'It can be negative', 'It is a true distance'], 1, 'Gibbs inequality.', 'KL is non negative and not symmetric.')
K.quiz('h', 'A disease affects 1 in 1,000 people. A test is 99% sensitive with a 1% false positive rate. P(sick | positive) is about', ['99%', '9%', '50%', '1%'], 1, 'Count 100,000 people.', '99 true positives against 999 false positives: 99 / 1,098 &asymp; 0.09.')
K.quiz('h', 'Adding a normal (Gaussian) prior on the weights to maximum likelihood gives', ['Lasso (L1)', 'Ridge (L2) regularisation', 'Dropout', 'No change'], 1, 'log of a Gaussian is a square.', 'MAP with a Gaussian prior adds &lambda;||w||<sup>2</sup>.')
K.quiz('x', 'In the style of a Stanford CS109 exam: X and Y are independent with Var(X) = 4 and Var(Y) = 9. What is Var(2X &minus; Y)?', ['7', '25', '1', '17'], 1, 'Var(aX) = a<sup>2</sup> Var(X), and variances add for independent variables, even when you subtract.', '4 &times; 4 + 9 = 25.')
K.quiz('x', 'In the style of an MIT 6.041 exam: the MLE of the rate &lambda; from Poisson counts 2, 4, 3 is', ['2', '3', '4', '9'], 1, 'Set the derivative of &Sigma;(x<sub>i</sub> log &lambda; &minus; &lambda;) to 0.', '&Sigma;x<sub>i</sub>/&lambda; &minus; n = 0, so &lambda; = mean = 3.')

K.calc('e', 'A bag has 3 red and 7 blue balls. P(red)?', '0.3', 'Good over all.', ['3 red.', '10 balls.', eq('3 / 10 = 0.3')], check=3 / 10)
K.calc('e', 'Mean of 4, 8, 6, 2?', '5', 'Add and divide.', ['Sum = 20.', '4 values.', eq('20 / 4 = 5')], check=(4 + 8 + 6 + 2) / 4)
K.calc('e', 'P(rain) = 0.3. P(no rain)?', '0.7', 'Complement.', ['Rain and no rain cover every case, so they add to 1.', 'Subtract the chance of rain from 1.', eq('1 &minus; 0.3 = 0.7')], check=1 - 0.3)
K.calc('m', 'Expected value of a fair die?', '3.5', 'Average of 1 to 6.', ['Sum 21.', '6 faces.', eq('21 / 6 = 3.5')], check=21 / 6)
K.calc('m', 'Variance of 2, 4, 6 (population, divide by n)?', '2.667', 'Mean is 4.', ['Squared distances: 4, 0, 4.', 'Sum 8.', eq('8 / 3 = 2.667')], check=round(8 / 3, 3))
K.calc('m', 'P(exactly 2 heads in 4 fair flips)?', '0.375', 'C(4, 2) = 6.', ['6 ways.', 'Each way has 1/16.', eq('6 / 16 = 0.375')], check=6 / 16)
K.calc('m', 'Heights are normal with mean 170 and std 8. z score of 186?', '2', '(x &minus; &mu;) / &sigma;.', ['186 &minus; 170 = 16.', '16 / 8.', eq('z = 2')], check=(186 - 170) / 8)
K.calc('h', '2% are sick, the test finds 90%, false positive rate 5%. P(sick | positive), 3 decimals?', '0.269', 'Bayes rule.', ['P(+) = 0.9 &times; 0.02 + 0.05 &times; 0.98 = 0.018 + 0.049 = 0.067.', 'Top: 0.018.', eq('0.018 / 0.067 = 0.269')], check=round(0.9 * 0.02 / (0.9 * 0.02 + 0.05 * 0.98), 3))
K.calc('h', 'Cross entropy (natural log) when the true class gets probability 0.5, 4 decimals?', '0.6931', '&minus;ln q.', ['Cross entropy with one true class is &minus;ln of its probability.', 'Here that is &minus;ln(0.5).', eq('&minus;ln(0.5) = ln 2 = 0.6931')], check=0.6931)
K.calc('x', 'In the style of a CMU 10-701 problem: entropy in bits of the distribution (0.5, 0.25, 0.25)?', '1.5', '&minus;&Sigma; p log<sub>2</sub> p.', ['0.5 &times; 1 = 0.5.', '0.25 &times; 2 = 0.5, twice.', eq('0.5 + 0.5 + 0.5 = 1.5 bits')], check=1.5)

K.assign('bayes', 'e', 'Bayes rule for a test result',
         '<p>Write <code>posterior(prior, sensitivity, false_positive)</code> that returns P(sick | positive) rounded to 3 decimals. prior is P(sick), sensitivity is P(positive | sick) and false_positive is P(positive | healthy).</p>',
         '''
def posterior(prior, sensitivity, false_positive):
    # your code here
    pass
''', [('posterior(0.01, 0.95, 0.05)', 0.161), ('posterior(0.5, 0.9, 0.1)', 0.9), ('posterior(0.02, 0.9, 0.05)', 0.269)],
         '''
def posterior(prior, sensitivity, false_positive):
    top = sensitivity * prior
    evidence = top + false_positive * (1 - prior)
    return round(top / evidence, 3)
''', 'The top is sensitivity &times; prior. The bottom adds the false positives: false_positive &times; (1 &minus; prior).', '<p>The bottom line is the total probability of a positive test. Dividing by it makes P(sick | +) and P(healthy | +) add up to 1.</p>')
K.assign('meanstd', 'e', 'Mean and standard deviation by hand',
         '<p>Write <code>mean_std(nums)</code> that returns a list [mean, std], both rounded to 2 decimals. Use the population standard deviation (divide by n). Do not use numpy or statistics.</p>',
         '''
def mean_std(nums):
    # your code here
    pass
''', [('mean_std([2, 4, 6])', [4.0, 1.63]), ('mean_std([5, 5, 5])', [5.0, 0.0]), ('mean_std([1, 2, 3, 4])', [2.5, 1.12])],
         '''
def mean_std(nums):
    n = len(nums)
    mean = sum(nums) / n
    total = 0
    for x in nums:
        total = total + (x - mean) ** 2
    std = (total / n) ** 0.5
    return [round(mean, 2), round(std, 2)]
''', 'First find the mean. Then average the squared distances from it and take the square root.', '<p>For the sample standard deviation you would divide by n &minus; 1 instead. That is what pandas does by default.</p>')
K.assign('logloss', 'm', 'Log loss of some predictions',
         '<p>Write <code>binary_log_loss(labels, probs)</code>. labels are 0 or 1 and probs are the predicted chances of 1. Return the average of &minus;[y ln p + (1 &minus; y) ln(1 &minus; p)], rounded to 4 decimals. Use math.log.</p>',
         '''
import math


def binary_log_loss(labels, probs):
    # your code here
    pass
''', [('binary_log_loss([1, 0, 1, 1], [0.9, 0.2, 0.6, 0.8])', 0.2656), ('binary_log_loss([1], [0.5])', 0.6931), ('binary_log_loss([0, 1], [0.1, 0.9])', 0.1054)],
         '''
import math


def binary_log_loss(labels, probs):
    total = 0
    for y, p in zip(labels, probs):
        if y == 1:
            total = total - math.log(p)
        else:
            total = total - math.log(1 - p)
    return round(total / len(labels), 4)
''', 'For a 1 label add &minus;ln p. For a 0 label add &minus;ln(1 &minus; p). Divide by the count.', '<p>This is exactly what sklearn.metrics.log_loss computes. It is the negative log likelihood of the labels under the model.</p>')

K.must('Rules', 'Complement 1 &minus; P(A). Or: P(A) + P(B) &minus; P(A and B). And: P(A) P(B | A). Conditional P(A | B) = P(A and B) / P(B).')
K.must('Bayes rule', 'P(A | B) = P(B | A) P(A) / P(B), with P(B) from total probability. Rare events: false alarms dominate.')
K.must('Distributions', 'Bernoulli p, binomial np and np(1 &minus; p), Poisson &lambda; and &lambda;, normal &mu; and &sigma;<sup>2</sup>. 68, 95, 99.7 rule.')
K.must('Describe', 'Mean, median, Var = E[X<sup>2</sup>] &minus; E[X]<sup>2</sup>, sample std uses n &minus; 1. Correlation in [&minus;1, 1], not causation.')
K.must('CLT', 'Averages become normal. Standard error &sigma; / &radic;n. 95% interval: estimate &plusmn; 1.96 SE.')
K.must('Likelihood and losses', 'MLE maximises &Sigma; log P(x | &theta;). Normal noise gives MSE, Bernoulli gives log loss. Gaussian prior gives L2. Cross entropy &minus;&Sigma; p log q.')

T = K.topic(
    slug='ml-probability', topic='ml-probability', step=(2, 'Maths you need', 'ml-f2', 'The linear algebra, calculus and probability that every model uses, explained with simple words, pictures and code.', 'Beginner'),
    title='Probability and statistics for ML', short='Probability and statistics', badge='2.3', minutes=65,
    lead='Learn how models deal with uncertainty: probability rules, Bayes rule, the common distributions, mean, variance and correlation, the central limit theorem, maximum likelihood (where losses come from), entropy and cross entropy, and hypothesis tests.',
    desc='probability rules, conditional probability, independence, Bayes rule, prior and posterior, base rate fallacy, Bernoulli, binomial, Poisson, uniform and normal distributions, PMF, PDF, CDF, expectation, variance, standard deviation, covariance, correlation, law of large numbers, central limit theorem, standard error, maximum likelihood, log likelihood, MAP and regularisation, entropy, cross entropy, KL divergence, hypothesis tests, p values, confidence intervals, A/B tests, frequentist and Bayesian views.',
    summary='probability rules, Bayes rule, distributions, mean and variance, the central limit theorem, maximum likelihood, cross entropy and hypothesis tests.',
    keywords=['probability', 'Bayes rule', 'distribution', 'normal distribution', 'variance', 'correlation', 'central limit theorem', 'maximum likelihood', 'cross entropy', 'p value'],
    recap='<p>Probability lets a model say how sure it is. Maximum likelihood turns that into the loss functions you train with.</p>',
    added='2026-11-13', leet=leet_items())
