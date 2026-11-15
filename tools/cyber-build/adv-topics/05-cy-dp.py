# Advanced 2.3: differential privacy. Checked against Warner, "Randomized Response" (JASA 1965), Sweeney's linkage of
# the Massachusetts hospital data (1997) and "Simple Demographics Often Identify People Uniquely" (2000), the AOL
# search log release (2006), Narayanan and Shmatikov on the Netflix Prize data (IEEE S&P 2008), Dinur and Nissim
# (PODS 2003), Dwork, McSherry, Nissim and Smith (TCC 2006, Godel Prize 2017), Dwork and Roth, "The Algorithmic
# Foundations of Differential Privacy" (2014), McSherry and Talwar (FOCS 2007), Erlingsson, Pihur and Korolova, RAPPOR
# (ACM CCS 2014), Apple's differential privacy overview (2017), Abadi et al., "Deep Learning with Differential Privacy"
# (ACM CCS 2016), Mironov, Renyi differential privacy (CSF 2017), McMahan et al., DP-FedAvg (ICLR 2018), Yeom et al.
# (CSF 2018), and the US Census Bureau's disclosure avoidance documentation for the 2020 Census.
import math

from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk

chapter('cy-dp')
K = Kit()

K.code('randomized_response', r'''
# Randomised response (Warner 1965): ask a sensitive yes or no question so that no single answer can be trusted
import math
import random

random.seed(1)
TRUE_RATE = 0.30                          # 30% really did cheat on the exam (unknown to the surveyor)
people = [random.random() < TRUE_RATE for _ in range(2000)]

def answer(truth):
    if random.random() < 0.5:             # first coin heads: tell the truth
        return truth
    return random.random() < 0.5          # tails: flip again and say yes on heads, no on tails

answers = [answer(t) for t in people]
yes = sum(answers) / len(answers)
estimate = 2 * yes - 0.5                  # P(yes) = 0.5 * p + 0.25, so p = 2 * P(yes) - 0.5
print(f"share answering yes: {yes:.3f}")
print(f"estimated true rate: {estimate:.3f}   (actual {sum(people) / len(people):.3f})")

# privacy: P(yes | truth yes) = 0.75 and P(yes | truth no) = 0.25, so the ratio is 3
eps = math.log(0.75 / 0.25)
print(f"epsilon = ln 3 = {eps:.4f}: any single 'yes' is at most 3 times more likely from a cheater")
''', long=True)

K.code('laplace_count', r'''
# The Laplace mechanism: answer a counting query with noise of scale sensitivity / epsilon
import random

random.seed(3)
def laplace(scale):
    # the difference of two exponential draws has a Laplace distribution
    return random.expovariate(1 / scale) - random.expovariate(1 / scale)

true_count = 412                           # patients in a database with a certain disease
sensitivity = 1                            # adding or removing one person changes a count by at most 1
for eps in (0.1, 0.5, 1.0, 5.0):
    b = sensitivity / eps
    answers = [true_count + laplace(b) for _ in range(1000)]
    mean_err = sum(abs(a - true_count) for a in answers) / len(answers)
    print(f"eps {eps:3}: scale b = {b:5.1f}, one answer {answers[0]:7.1f}, average error {mean_err:5.1f} (theory b = {b:.1f})")
print("\nSmaller epsilon means more privacy and more noise. The noise does not depend on the database size,")
print("so for large counts the relative error is tiny.")
''', long=True)

K.code('budget_tracker', r'''
# A privacy budget: sequential composition adds epsilons, parallel composition on disjoint groups does not
class Budget:
    def __init__(self, total):
        self.total, self.spent = total, 0.0

    def spend(self, eps, what):
        if self.spent + eps > self.total + 1e-12:
            print(f"  REFUSED  {what:38} needs {eps}, only {self.total - self.spent:.2f} left")
            return False
        self.spent += eps
        print(f"  ok       {what:38} eps {eps:<4}  spent {self.spent:.2f} of {self.total}")
        return True

b = Budget(1.0)
print("sequential queries on the same people:")
b.spend(0.3, "count of diabetics")
b.spend(0.3, "average age of diabetics")
b.spend(0.3, "count of smokers")
b.spend(0.3, "count of diabetic smokers")          # 1.2 would exceed the budget

print("\nparallel queries: one count per city, and each person lives in exactly one city")
cities = ["Delhi", "Mumbai", "Chennai", "Kolkata"]
per_city = 0.5
print(f"  four counts at eps {per_city} each cost only max = {per_city}, not {per_city * len(cities)}")

print("\npost processing is free: rounding or clipping a noisy answer to 0 or more uses no extra budget.")
print("group privacy: protecting a family of 4 with eps 0.5 each person means eps 2.0 for the family.")
''')

K.code('gaussian_mean', r'''
# The Gaussian mechanism and a private average with clipping
import math
import random

random.seed(8)
def gaussian_sigma(sensitivity, eps, delta):
    # classic bound (Dwork and Roth 2014), valid for eps below 1
    return sensitivity * math.sqrt(2 * math.log(1.25 / delta)) / eps

salaries = [random.gauss(60, 15) for _ in range(4999)] + [2500]   # thousands of rupees a month, one huge outlier
L, U = 0, 200                                                      # clip every value into a known range
clipped = [min(U, max(L, s)) for s in salaries]
n = len(clipped)
sens = (U - L) / n                                                  # one person can move the mean by at most this

eps, delta = 0.5, 1e-5
sigma = gaussian_sigma(sens, eps, delta)
noisy_mean = sum(clipped) / n + random.gauss(0, sigma)
print(f"true mean (with outlier) {sum(salaries) / n:.3f}, clipped mean {sum(clipped) / n:.3f}")
print(f"sensitivity {sens:.4f}, sigma {sigma:.4f}, private mean {noisy_mean:.3f}")
print(f"Laplace scale for the same eps would be {sens / eps:.4f} (std {math.sqrt(2) * sens / eps:.4f})")
print("Clipping bounds the sensitivity: without it, one billionaire could move the mean without limit.")
''', long=True)

K.code('dp_sgd', r'''
# DP-SGD (Abadi et al. 2016) on a tiny logistic regression: clip each example's gradient, add Gaussian noise
import math
import random

random.seed(2)
def make(n):
    out = []
    for _ in range(n):
        y = random.randint(0, 1)
        c = 0.65 if y else 0.35
        out.append(([random.gauss(c, 0.12), random.gauss(c, 0.12)], y))
    return out

train, test = make(600), make(400)

def grad(w, x, y):
    p = 1 / (1 + math.exp(-(w[0] * x[0] + w[1] * x[1] + w[2])))
    return [(p - y) * x[0], (p - y) * x[1], p - y]

def accuracy(w):
    return sum(((w[0] * x[0] + w[1] * x[1] + w[2]) > 0) == y for x, y in test) / len(test)

def train_model(private, C=1.0, sigma=1.0, batch=60, steps=300, lr=0.5):
    w = [0.0, 0.0, 0.0]
    for _ in range(steps):
        sample = random.sample(train, batch)
        total = [0.0, 0.0, 0.0]
        for x, y in sample:
            g = grad(w, x, y)
            if private:
                norm = math.sqrt(sum(v * v for v in g))
                g = [v * min(1, C / norm) for v in g] if norm > 0 else g   # 1. clip to length C
            total = [t + v for t, v in zip(total, g)]
        if private:
            total = [t + random.gauss(0, sigma * C) for t in total]         # 2. add noise to the sum
        w = [wi - lr * t / batch for wi, t in zip(w, total)]
    return w

print(f"ordinary SGD:             test accuracy {accuracy(train_model(False)):.3f}")
for sigma in (0.5, 4.0, 30.0):
    print(f"DP-SGD, noise sigma {sigma:4}: test accuracy {accuracy(train_model(True, sigma=sigma)):.3f}")
print(f"\nsampling rate q = 60 / 600 = {60 / 600}. A privacy accountant turns q, sigma and the number of steps into (eps, delta).")
''', long=True)

K.code('exp_mechanism', r'''
# The exponential mechanism (McSherry and Talwar 2007): pick the best option privately, for example the most
# common weak password pattern in a breach dataset, without revealing exact counts.
import math
import random

random.seed(4)
counts = {"name + year": 410, "123456 style": 395, "keyboard walk": 220, "word + !": 180, "random": 15}
SENS = 1                               # one person changes any count by at most 1

def probabilities(eps):
    weights = {k: math.exp(eps * c / (2 * SENS)) for k, c in counts.items()}
    total = sum(weights.values())
    return {k: w / total for k, w in weights.items()}

for eps in (0.01, 0.05, 0.2):
    p = probabilities(eps)
    print(f"eps {eps}: " + ", ".join(f"{k} {v:.3f}" for k, v in p.items()))

p = probabilities(0.05)
pick = random.choices(list(p), weights=list(p.values()))[0]
print("\nreleased answer with eps 0.05:", pick)
''')

K.lesson('idea', 'Why anonymising data is not enough', f'''
{talk('For decades organisations protected people in released data by removing names. It kept failing. In 1997 Latanya Sweeney, then a graduate student at MIT, bought the voter list of Cambridge, Massachusetts for twenty dollars, joined it with supposedly anonymous hospital records using ZIP code, birth date and sex, and found the medical records of the state governor, William Weld. She later estimated that those three facts alone single out about 87 percent of Americans. In 2006 AOL released twenty million search queries with user names replaced by numbers, and New York Times reporters identified user 4417749 as a sixty two year old widow in Georgia from her searches. In 2008 Arvind Narayanan and Vitaly Shmatikov re identified Netflix Prize users by matching their anonymous movie ratings with public reviews on IMDb. Irit Dinur and Kobbi Nissim proved in 2003 that answering too many statistical queries too accurately lets anyone rebuild the database, and the US Census Bureau later showed it could rebuild many individual records from its own published 2010 tables. The answer, introduced by Cynthia Dwork, Frank McSherry, Kobbi Nissim and Adam Smith in 2006, is differential privacy. It is not a property of a dataset but of the process that produces an answer. It promises that the answer would be almost the same whether or not any one person’s data was included, so nobody can learn much about you from it, whatever else they know. The four authors received the Gödel Prize in 2017, the 2020 US Census became the first census to protect its published tables with differential privacy, and Apple and Google use it to collect statistics from phones.')}
{src('Warner (1965), Sweeney (1997, 2000), AOL search logs (2006), Narayanan and Shmatikov (2008), Dinur and Nissim (2003), Dwork, McSherry, Nissim and Smith (2006), Dwork and Roth (2014), McSherry and Talwar (2007), RAPPOR (2014), Apple (2017), Abadi et al. (2016), Mironov (2017), McMahan et al. (2018), Yeom et al. (2018), US Census Bureau 2020 disclosure avoidance.')}
{wwh('<b>Differential privacy (DP)</b> is a mathematical promise about a data release: adding or removing any one person changes the probability of every possible output by at most a factor e<sup>&epsilon;</sup>.',
     'Removing names fails because other facts link records back to people, and accurate answers to many queries can rebuild a database. DP holds whatever an attacker already knows.',
     'Add carefully sized random noise to answers (Laplace or Gaussian), or to the data itself (randomised response), track the total privacy loss as a budget, and clip each person’s contribution so the noise can hide it.')}
{table(['Failure of anonymisation', 'Year', 'How people were found'], [
    ['Massachusetts hospital records', '1997', 'ZIP code, birth date and sex joined with a voter list'],
    ['AOL search logs', '2006', 'The searches themselves described the person'],
    ['Netflix Prize ratings', '2008', 'Matched with public IMDb reviews'],
    ['Database reconstruction', '2003 theory, 2010 Census tests', 'Too many accurate statistics rebuild the records']])}
''', kw=['anonymisation', 'de identification', 'Sweeney', 'quasi identifiers', 'AOL search logs', 'Netflix Prize', 'Narayanan Shmatikov', 'Dinur Nissim', 'reconstruction attack', 'differential privacy', 'Dwork', 'US Census 2020', 'Godel Prize'])

K.lesson('rr', 'Randomised response: the first private survey', f'''
{talk('The oldest differentially private method is older than the definition. In 1965 the statistician Stanley Warner wanted honest answers to embarrassing survey questions, such as whether someone had used drugs or cheated in an exam. His idea was to let each person randomise their own answer with a coin. In the version we use, the person flips a coin in secret. On heads they answer truthfully. On tails they flip again and say yes on heads and no on tails, whatever the truth. Any single yes could have come from the coin, so every person can deny it. But the surveyor knows exactly how the coins behave, so from the share of yes answers across many people they can work out the true rate. Someone who cheated says yes three quarters of the time, someone who did not says yes one quarter of the time, so a yes is at most three times as likely from a cheater. That ratio of 3 is e to the power epsilon, so this survey is differentially private with epsilon equal to the natural log of 3, about 1.1. Because each person adds the noise themselves, before the data leaves them, this is called local differential privacy. Google’s RAPPOR, published by Úlfar Erlingsson and colleagues in 2014, used a version of it to learn which home pages Chrome users had set without learning any one user’s setting, and Apple uses local differential privacy for things like popular emoji and new words typed on iPhones.')}
{viz('cyrr')}
{run('randomized_response')}
{fxs(fx('Probability of a yes', 'P(yes) = &frac12; p + &frac14;', 'p = 0.3: 0.15 + 0.25 = 0.40.', key=True),
     fx('Unbiased estimate of the true rate', 'p&#770; = 2 &times; (share of yes) &minus; &frac12;', 'Share 0.405: 0.81 &minus; 0.5 = 0.31.', key=True),
     fx('Privacy of randomised response', '&epsilon; = ln(P(yes | yes) / P(yes | no)) = ln((3/4) / (1/4)) = ln 3', 'ln 3 &asymp; 1.0986.', key=True),
     fx('General coin with truth probability t', '&epsilon; = ln((t + (1 &minus; t)/2) / ((1 &minus; t)/2))', 't = 0.5 gives ln 3. t = 0.75 gives ln 7 &asymp; 1.95, less privacy, less noise.'))}
''', kw=['randomised response', 'Warner 1965', 'plausible deniability', 'local differential privacy', 'LDP', 'RAPPOR', 'Apple differential privacy', 'unbiased estimate', 'ln 3'])

K.lesson('defn', 'The definition, sensitivity and the Laplace mechanism', f'''
{talk('Here is the definition carefully. Two databases are neighbours if they differ in one person’s data. A randomised algorithm M is epsilon differentially private if, for every pair of neighbouring databases and every set of possible outputs, the probability that M gives an output in that set is at most e to the epsilon times the probability for the neighbour. Small epsilon means strong privacy: with epsilon of 0.1 the two probabilities differ by at most about 10 percent. The relaxed version, epsilon delta privacy, allows the promise to fail with a tiny probability delta, which should be much smaller than one over the number of people. To achieve DP for a numeric query we first ask how much one person can change the answer. That is the sensitivity. For a count it is 1. For an average of n values clipped to a range from L to U, it is U minus L divided by n. The Laplace mechanism then adds noise drawn from a Laplace distribution with scale b equal to the sensitivity divided by epsilon. The Laplace curve falls off exponentially, and moving its centre by the sensitivity changes the height at any point by at most e to the epsilon, which is exactly the definition. The animation shows the curves for a count of 100 without you and 101 with you. The typical error is b, independent of how many people are in the database, so DP is very accurate for large populations and noisy for small groups.')}
{viz('cylaplace')}
{run('laplace_count')}
{fxs(fx('&epsilon;-differential privacy', 'P[M(D) &isin; S] &le; e<sup>&epsilon;</sup> &middot; P[M(D&prime;) &isin; S] for all neighbours D, D&prime; and all S', 'Approximate (&epsilon;, &delta;)-DP adds + &delta; on the right.', key=True),
     fx('Sensitivity', '&Delta;f = max over neighbours of |f(D) &minus; f(D&prime;)|', 'A count: 1. A mean of n values in [L, U]: (U &minus; L) / n.', key=True),
     fx('Laplace mechanism', 'M(D) = f(D) + Lap(b), b = &Delta;f / &epsilon;, density (1 / 2b) e<sup>&minus;|x| / b</sup>', '&Delta;f = 1, &epsilon; = 0.5: b = 2, mean absolute error 2, standard deviation 2&radic;2 &asymp; 2.83.', key=True),
     fx('Why it works', 'p(x &minus; f(D)) / p(x &minus; f(D&prime;)) = e<sup>(|x &minus; f(D&prime;)| &minus; |x &minus; f(D)|) / b</sup> &le; e<sup>&Delta;f / b</sup> = e<sup>&epsilon;</sup>', 'By the triangle inequality the exponent is at most &Delta;f / b.'))}
{deep('What does &epsilon; mean in practice', '<p>Think of an attacker who believes with probability 50% that you are in a database. After seeing an &epsilon;-DP answer, their belief can rise to at most e<sup>&epsilon;</sup> / (1 + e<sup>&epsilon;</sup>): 52.5% for &epsilon; = 0.1, 73% for &epsilon; = 1, 88% for &epsilon; = 2. Researchers often call &epsilon; &le; 1 strong. Real deployments have used values from below 1 to above 10, so always ask what &epsilon; a system uses and over what time period.</p>')}
''', kw=['definition', 'neighbouring databases', 'epsilon', 'delta', 'approximate DP', 'sensitivity', 'Laplace mechanism', 'scale', 'triangle inequality', 'posterior belief'])

K.lesson('compose', 'Composition and the privacy budget', f'''
{talk('Every differentially private answer leaks a little. Ask enough questions and the leaks add up, which is exactly how reconstruction attacks work. Differential privacy measures this precisely, which is one of its great strengths. Sequential composition says that running mechanisms with epsilons epsilon 1, epsilon 2 and so on, on the same people, gives a total that is at most their sum. So an organisation sets a privacy budget, for example a total epsilon of 1, and every query spends some of it, as the animation and program show. Parallel composition says that queries on separate groups of people, such as one count per city when everyone lives in one city, cost only the largest of their epsilons, because each person is affected by just one of them. Post processing is free: anything you compute from a DP answer without looking at the data again, such as rounding or forcing a count to be at least zero, stays DP with the same epsilon. Group privacy says that protecting a group of k people, such as a family, costs k times epsilon. For many small queries, simple addition is too pessimistic. Advanced composition and newer accountants such as Rényi differential privacy, introduced by Ilya Mironov in 2017, give much tighter totals, and they are what makes training neural networks with DP practical.')}
{viz('cybudget')}
{run('budget_tracker')}
{fxs(fx('Sequential composition', '&epsilon;<sub>total</sub> &le; &Sigma; &epsilon;<sub>i</sub>', '0.3 + 0.3 + 0.3 = 0.9. A fourth query of 0.3 would exceed a budget of 1.', key=True),
     fx('Parallel composition (disjoint groups)', '&epsilon;<sub>total</sub> = max &epsilon;<sub>i</sub>', 'Four city counts at 0.5 each cost 0.5, not 2.', key=True),
     fx('Group privacy', '&epsilon;<sub>group</sub> = k &epsilon;', 'A family of 4 at &epsilon; = 0.5: 2.', key=True),
     fx('Advanced composition (k queries)', '&epsilon;<sub>total</sub> &asymp; &epsilon; &radic;(2k ln(1/&delta;&prime;)) + k &epsilon; (e<sup>&epsilon;</sup> &minus; 1)', 'Grows like &radic;k rather than k for small &epsilon;.'))}
''', kw=['composition', 'sequential composition', 'parallel composition', 'privacy budget', 'post processing', 'group privacy', 'advanced composition', 'Renyi differential privacy', 'privacy accountant'])

K.lesson('mech', 'The Gaussian and exponential mechanisms', f'''
{talk('Two more mechanisms complete the basic toolkit. The Gaussian mechanism adds normally distributed noise instead of Laplace noise. It gives epsilon delta privacy rather than pure epsilon privacy, and its noise is set by the L2 sensitivity, the length of the largest change one person can make to a whole vector of answers. That makes it the natural choice for high dimensional outputs such as gradients, and it composes very well with modern accountants, which is why DP-SGD uses it. For a single number, as in our program, the Laplace mechanism often adds less noise. Both need bounded sensitivity, so data is usually clipped first: salaries forced into a range, or each gradient scaled to a maximum length. Clipping is what stops one billionaire, or one very unusual patient, from dominating an answer. The exponential mechanism, from Frank McSherry and Kunal Talwar in 2007, handles answers that are not numbers, such as choosing the most common item, the best price, or the best split in a decision tree. It scores every possible answer with a utility function, then picks one at random with probability that grows exponentially with the score. Good answers are very likely, but no single person can change the probabilities by more than a factor e to the epsilon.')}
{run('gaussian_mean')}
{run('exp_mechanism')}
{fxs(fx('Gaussian mechanism', 'M(D) = f(D) + N(0, &sigma;<sup>2</sup>), &sigma; = &Delta;<sub>2</sub>f &radic;(2 ln(1.25/&delta;)) / &epsilon;', 'For &epsilon; &lt; 1. &Delta;<sub>2</sub> = 0.04, &epsilon; = 0.5, &delta; = 10<sup>&minus;5</sup>: &sigma; &asymp; 0.3876.', key=True),
     fx('Sensitivity of a clipped mean', '&Delta; = (U &minus; L) / n', 'Range 0 to 200, n = 5000: exactly 0.04.', key=True),
     fx('Exponential mechanism', 'P(r) &prop; exp(&epsilon; u(D, r) / (2 &Delta;u))', 'Counts 410 and 395 with &epsilon; = 0.05: odds e<sup>0.025 &times; 15</sup> = e<sup>0.375</sup> &asymp; 1.45 to 1.', key=True))}
''', kw=['Gaussian mechanism', 'L2 sensitivity', 'clipping', 'bounded sensitivity', 'exponential mechanism', 'McSherry Talwar', 'utility function', 'private selection'])

K.lesson('dpml', 'Differential privacy for machine learning: DP-SGD and DP-FedAvg', f'''
{talk('Advanced 1.2 showed that trained models can leak their training data through membership inference and extraction. Differential privacy is the strongest known defence, because it bounds what any output reveals about one example. In 2016 Martín Abadi and colleagues at Google introduced DP-SGD, differentially private stochastic gradient descent. Each training step does three things differently. It computes the gradient for each example separately, not just for the batch. It clips each per example gradient to a maximum length C, so no single example can push the model further than C. And it adds Gaussian noise with standard deviation sigma times C to the sum before taking the step. The batches are random samples, which adds privacy amplification by sampling. A privacy accountant, the moments accountant in the original paper and Rényi DP accountants today, adds up the privacy cost over all steps to report a final epsilon and delta. The cost is some accuracy, more computation for per example gradients, and careful tuning. For federated learning, Brendan McMahan and colleagues gave DP-FedAvg in 2018: clip each user’s whole update and add noise to the sum, which protects every user, not just every example. Samuel Yeom and colleagues showed that epsilon differential privacy caps any membership inference attacker’s advantage at e to the epsilon minus 1, which links this chapter back to the attacks.')}
{viz('cydpsgd')}
{run('dp_sgd')}
{steps('One DP-SGD step', ['Sample a batch: each example is included with probability q = batch size / dataset size.',
        'For each example compute its own gradient g<sub>i</sub>.',
        'Clip: g<sub>i</sub> &larr; g<sub>i</sub> &middot; min(1, C / &Vert;g<sub>i</sub>&Vert;).',
        'Add up the clipped gradients and add noise N(0, &sigma;<sup>2</sup>C<sup>2</sup>) to each coordinate.',
        'Divide by the batch size and take the step w &larr; w &minus; &eta; &middot; noisy average.',
        'The accountant records q, &sigma; and the step, and updates the total (&epsilon;, &delta;).'])}
{fxs(fx('DP-SGD noisy gradient', 'g&#771; = (1/B) (&Sigma;<sub>i</sub> clip<sub>C</sub>(g<sub>i</sub>) + N(0, &sigma;<sup>2</sup>C<sup>2</sup> I))', 'B = 60, C = 1, &sigma; = 1: noise of size about 1 on a sum of up to 60.', key=True),
     fx('Sampling rate', 'q = B / N', '60 / 600 = 0.1. Smaller q gives stronger privacy amplification.', key=True),
     fx('Membership advantage under &epsilon;-DP', 'Adv &le; e<sup>&epsilon;</sup> &minus; 1', '&epsilon; = 0.5: at most 0.6487.'))}
{versus('Local and central differential privacy', ['', 'Local DP', 'Central DP'], [
    ['Who adds the noise', 'Each person, before data leaves their device', 'A trusted curator, after collecting the data'],
    ['Trust needed', 'None in the collector', 'The curator must keep raw data safe'],
    ['Accuracy', 'Much noisier, needs very many people', 'Far more accurate for the same &epsilon;'],
    ['Examples', 'Randomised response, RAPPOR, Apple emoji statistics', 'US Census 2020, DP-SGD, DP-FedAvg with secure aggregation']],
    'Secure aggregation in federated learning gives a middle path: noise added to a sum that nobody sees unmasked, with accuracy close to central DP.')}
''', kw=['DP-SGD', 'Abadi', 'per example gradients', 'gradient clipping', 'noise multiplier', 'sampling rate', 'privacy amplification', 'moments accountant', 'DP-FedAvg', 'user level privacy', 'local DP', 'central DP', 'membership advantage'])

K.lesson('versus', 'Differential privacy compared with other privacy methods', f'''
{talk('Differential privacy is often compared with older anonymisation methods such as k anonymity, and with cryptographic tools. They answer different questions.')}
{versus('Privacy methods compared', ['', 'Removing names', 'k anonymity', 'Differential privacy', 'Encryption, MPC, HE'], [
    ['Promise', 'None formal', 'Each record looks like at least k &minus; 1 others', 'Any one person changes outputs by at most e<sup>&epsilon;</sup>', 'Data unreadable without keys, or computed on blindly'],
    ['Holds against extra knowledge?', 'No', 'No, linkage and homogeneity attacks', 'Yes, whatever the attacker knows', 'Yes, for the data in transit or in use'],
    ['Protects the output?', 'No', 'Partly', 'Yes, that is its purpose', 'No, the result itself can still leak'],
    ['Cost', 'None', 'Generalised, less useful data', 'Noise, a privacy budget', 'Computation and engineering']],
    'Use cryptography to protect data while it is stored, sent or computed on, and differential privacy to protect what the published result reveals.')}
''', kw=['k anonymity', 'linkage attack', 'comparison', 'encryption', 'MPC', 'homomorphic encryption'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows that removing names is not enough and that adding the right amount of noise can protect people while keeping statistics useful. A student can apply randomised response, the Laplace and Gaussian mechanisms and composition, and run DP-SGD. A professional chooses epsilon, sets budgets and deploys DP in analytics and ML. Experts design new mechanisms and tighter accountants.')}
{ladder(
    '<p>Data with names removed can often be matched back to people. Adding the right amount of random noise lets researchers learn about groups while protecting each person.</p>',
    '<p>&epsilon;-DP definition, sensitivity, Laplace b = &Delta;/&epsilon;, randomised response &epsilon; = ln 3, Gaussian &sigma;, composition (sum, max, k&epsilon;), exponential mechanism, DP-SGD clip and noise, Adv &le; e<sup>&epsilon;</sup> &minus; 1.</p>',
    '<p>Use libraries such as OpenDP, Google’s DP library, Opacus or TensorFlow Privacy, choose &epsilon; and &delta; with stakeholders, track budgets, and combine DP with secure aggregation in FL.</p>',
    '<p>Research tighter accounting, private synthetic data, DP for large language models, fairness under DP, and the policy question of what &epsilon; society should accept.</p>')}
{grow('Explain why anonymisation fails and how noise can protect people.',
      'Apply the core mechanisms and budget their total cost.',
      'Deploy differential privacy in analytics and machine learning systems.')}
''', kw=['beginner', 'expert', 'OpenDP', 'Opacus', 'TensorFlow Privacy', 'synthetic data'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Why</b>: removing names fails (Sweeney 1997, AOL 2006, Netflix 2008), too many accurate answers rebuild data (Dinur and Nissim 2003). DP (Dwork et al. 2006) protects the process, not the dataset.',
    '<b>Randomised response</b>: P(yes) = p/2 + 1/4, p&#770; = 2 &times; share &minus; 1/2, &epsilon; = ln 3. Local DP: RAPPOR, Apple.',
    '<b>Definition</b>: P[M(D) &isin; S] &le; e<sup>&epsilon;</sup> P[M(D&prime;) &isin; S] (+ &delta;). Sensitivity &Delta;f. Laplace noise b = &Delta;f / &epsilon;.',
    '<b>Composition</b>: sequential sum, parallel max, post processing free, group k&epsilon;, advanced and Rényi accountants. Budgets.',
    '<b>Mechanisms</b>: Gaussian &sigma; = &Delta;<sub>2</sub>&radic;(2 ln(1.25/&delta;))/&epsilon;, clipping bounds sensitivity, exponential mechanism P &prop; e<sup>&epsilon;u/(2&Delta;u)</sup>.',
    '<b>ML</b>: DP-SGD clips per example gradients to C and adds N(0, &sigma;<sup>2</sup>C<sup>2</sup>), accountant gives (&epsilon;, &delta;). DP-FedAvg for users. Adv &le; e<sup>&epsilon;</sup> &minus; 1.'],
    'Advanced 3.1: certification revision, bringing the whole subject together for exams such as Security+, CISSP and CEH style theory.')}
{files('Three tasks: a Laplace scale, the randomised response estimate, and a privacy budget checker.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Why did removing names fail to protect the Massachusetts hospital records in 1997?', ['The names were encrypted badly', 'ZIP code, birth date and sex could be linked to a voter list', 'The hospital published passwords', 'It did not fail'], 1, 'Quasi identifiers.', 'Sweeney found the governor’s records this way.')
K.quiz('e', 'A smaller &epsilon; means', ['Less privacy and less noise', 'More privacy and more noise', 'No change', 'Faster queries'], 1, 'e<sup>&epsilon;</sup> close to 1.', 'Outputs with and without you become almost the same.')
K.quiz('e', 'What is the sensitivity of a counting query?', ['0', '1', 'n', 'Infinite'], 1, 'One person.', 'Adding or removing one person changes a count by at most 1.')
K.quiz('e', 'In randomised response, who adds the noise?', ['The server', 'Each person, with a coin', 'The government', 'Nobody'], 1, 'Local.', 'This is local differential privacy.')
K.quiz('m', 'What noise scale does the Laplace mechanism use?', ['&epsilon; / &Delta;f', '&Delta;f / &epsilon;', '&Delta;f &times; &epsilon;', '1'], 1, 'Sensitivity over epsilon.', 'Bigger sensitivity or smaller &epsilon; means more noise.')
K.quiz('m', 'Three queries at &epsilon; = 0.2 each on the same people cost at most', ['0.2', '0.6', '0.008', '1'], 1, 'Sequential composition.', 'Epsilons add.')
K.quiz('m', 'Counts for 5 separate cities at &epsilon; = 0.4 each, everyone in exactly one city, cost', ['2.0', '0.4', '0.08', '5'], 1, 'Parallel composition.', 'Each person is in only one query.')
K.quiz('m', 'Why is post processing free in DP?', ['It is not', 'Anything computed from a DP output without the data cannot reveal more about a person', 'It uses a new budget', 'Rounding adds noise'], 1, 'No new access to data.', 'Rounding or clipping a noisy count keeps the same &epsilon;.')
K.quiz('m', 'Why does DP-SGD clip each example’s gradient?', ['To speed up training', 'To bound each example’s influence so noise of known size can hide it', 'To save memory', 'To remove outliers from the test set'], 1, 'Sensitivity.', 'Without clipping the sensitivity is unbounded.')
K.quiz('h', 'Randomised response with a fair coin has &epsilon; equal to', ['ln 2', 'ln 3', '1', '3'], 1, '(3/4) / (1/4).', 'ln 3 &asymp; 1.0986.')
K.quiz('h', 'Under &epsilon;-DP, a membership inference attacker’s advantage is at most', ['&epsilon;', 'e<sup>&epsilon;</sup> &minus; 1', '1 &minus; e<sup>&minus;&epsilon;</sup>', '0'], 1, 'Yeom et al. 2018.', 'For &epsilon; = 0.1 that is about 0.105.')
K.quiz('h', 'Which mechanism privately chooses a non numeric answer such as the most common category?', ['Laplace', 'Gaussian', 'Exponential mechanism', 'Randomised response'], 2, 'Scores and exponential weights.', 'P(r) &prop; exp(&epsilon; u / 2&Delta;u).')
K.quiz('h', 'Why is local DP much noisier than central DP for the same &epsilon;?', ['It uses Gaussian noise', 'Every person adds noise, so the total noise grows with the number of people', 'It has no budget', 'It is not noisier'], 1, 'Noise per record.', 'Central DP adds noise once to the final answer.')
K.quiz('x', 'In the style of a Harvard CS 208 question: an attacker’s prior that you are in a dataset is 50%. After one &epsilon; = 1 DP release, what is the highest their belief can be?', ['50%', 'About 73%', '100%', 'About 99%'], 1, 'e / (1 + e).', 'e<sup>1</sup> / (1 + e<sup>1</sup>) &asymp; 0.731.')
K.quiz('x', 'In the style of an IIT Bombay privacy course: the mean of n = 1000 salaries clipped to [0, 200]. What is its sensitivity?', ['200', '0.2', '1', '1000'], 1, '(U &minus; L) / n.', '200 / 1000 = 0.2.')

K.calc('e', 'A count with sensitivity 1 and &epsilon; = 0.5. Laplace scale b?', '2', '&Delta; / &epsilon;.', ['&Delta; = 1.', '1 / 0.5.', eq('b = 2')], check=2)
K.calc('e', 'Randomised response with a true rate p = 0.3. Expected share of yes answers?', '0.4', 'p/2 + 1/4.', ['0.3 / 2 = 0.15.', 'Plus 0.25.', eq('0.40')], check=0.4)
K.calc('e', 'A yes share of 0.405. Estimated true rate?', '0.31', '2 &times; share &minus; 0.5.', ['2 &times; 0.405 = 0.81.', 'Minus 0.5.', eq('0.31')], check=0.31)
K.calc('m', 'Randomised response &epsilon; = ln 3. Round to 4 decimals.', '1.0986', 'Natural log.', ['P(yes | yes) / P(yes | no) = 3.', 'ln 3.', eq('&asymp; 1.0986')], check=round(math.log(3), 4))
K.calc('m', 'Laplace scale b = 2. Standard deviation of the noise? Round to 4 decimals.', '2.8284', '&radic;2 b.', ['Variance of Laplace(b) is 2b<sup>2</sup> = 8.', '&radic;8.', eq('&asymp; 2.8284')], check=round(math.sqrt(8), 4))
K.calc('m', 'Queries of &epsilon; 0.3, 0.3 and 0.3 on the same people. Total?', '0.9', 'Sequential composition.', ['Add the epsilons.', '0.3 &times; 3.', eq('0.9')], check=0.9)
K.calc('m', 'A family of 4 with &epsilon; = 0.5 per person. Group &epsilon;?', '2', 'k &epsilon;.', ['k = 4.', '4 &times; 0.5.', eq('2')], check=2)
K.calc('m', 'Mean of 5000 values clipped to [0, 200]. Sensitivity? Round to 4 decimals.', '0.04', '(U &minus; L) / n.', ['U &minus; L = 200 &minus; 0 = 200.', 'n = 5000, so one person changes the sum by at most 200 and the mean by 200 / n.', eq('200 / 5000 = 0.04')], check=round(200 / 5000, 4))
K.calc('h', 'Gaussian mechanism with &Delta;<sub>2</sub> = 0.04, &epsilon; = 0.5, &delta; = 10<sup>&minus;5</sup>. &sigma;? Round to 4 decimals.', '0.3876', '&Delta; &radic;(2 ln(1.25/&delta;)) / &epsilon;.', ['ln(125000) &asymp; 11.7361, times 2 = 23.4721, &radic; &asymp; 4.8448.', '0.04 &times; 4.8448 = 0.1938.', eq('0.1938 / 0.5 &asymp; 0.3876')], check=round(0.04 * math.sqrt(2 * math.log(1.25 / 1e-5)) / 0.5, 4))
K.calc('h', 'Exponential mechanism, &epsilon; = 0.05, &Delta;u = 1, scores 410 and 395. Odds of the first over the second? Round to 4 decimals.', '1.455', 'exp(&epsilon; &times; difference / 2).', ['Difference 15.', '0.05 &times; 15 / 2 = 0.375.', eq('e<sup>0.375</sup> &asymp; 1.4550')], check=round(math.exp(0.375), 4))
K.calc('h', 'Membership advantage cap for &epsilon; = 0.5? Round to 4 decimals.', '0.6487', 'e<sup>&epsilon;</sup> &minus; 1.', ['e<sup>0.5</sup> &asymp; 1.6487.', 'Minus 1.', eq('&asymp; 0.6487')], check=round(math.exp(0.5) - 1, 4))
K.calc('h', 'DP-SGD with batch 60 from 600 examples. Sampling rate q?', '0.1', 'B / N.', ['60 / 600.', 'Each example joins a batch with this probability.', eq('0.1')], check=0.1)
K.calc('x', 'Prior belief 50%. Highest posterior after an &epsilon; = 1 release? Round to 4 decimals.', '0.7311', 'e<sup>&epsilon;</sup> / (1 + e<sup>&epsilon;</sup>).', ['Odds can grow by at most e<sup>1</sup> &asymp; 2.7183.', 'Odds 1 become 2.7183.', eq('2.7183 / 3.7183 &asymp; 0.7311')], check=round(math.e / (1 + math.e), 4))
K.calc('x', 'Randomised response where the first coin says truth with t = 0.75. &epsilon;? Round to 4 decimals.', '1.9459', 'ln((t + (1 &minus; t)/2) / ((1 &minus; t)/2)).', ['P(yes | yes) = 0.75 + 0.125 = 0.875.', 'P(yes | no) = 0.125. Ratio 7.', eq('ln 7 &asymp; 1.9459')], check=round(math.log(7), 4))

K.assign('laplace_scale', 'e', 'Laplace noise scale',
         '<p>Write <code>laplace_scale(sensitivity, eps)</code> that returns b = sensitivity / eps rounded to 4 decimals, and raises <code>ValueError</code> when eps is not positive.</p>',
         '''
def laplace_scale(sensitivity, eps):
    # your code here
    pass
''', [('laplace_scale(1, 0.5)', 2.0), ('laplace_scale(1, 0.1)', 10.0), ('laplace_scale(0.04, 0.5)', 0.08), ('laplace_scale(3, 2)', 1.5)],
         '''
def laplace_scale(sensitivity, eps):
    if eps <= 0:
        raise ValueError("epsilon must be positive")
    return round(sensitivity / eps, 4)
''', 'Check eps first, then divide.', '<p>&epsilon; = 0 would mean infinite noise: perfect privacy and no information at all. Real systems refuse it rather than divide by zero.</p>')
K.assign('rr_estimate', 'm', 'Randomised response estimate',
         '<p>answers is a list of True and False from the fair coin randomised response survey. Write <code>rr_estimate(answers)</code> that returns the estimated true rate 2 &times; (share of True) &minus; 0.5, clipped to the range 0 to 1 (post processing is free), rounded to 4 decimals.</p>',
         '''
def rr_estimate(answers):
    # your code here
    pass
''', [('rr_estimate([True, True, False, False, False])', 0.3),
      ('rr_estimate([False, False, False, False])', 0.0),
      ('rr_estimate([True] * 9 + [False])', 1.0),
      ('rr_estimate([True, False])', 0.5)],
         '''
def rr_estimate(answers):
    share = sum(answers) / len(answers)
    p = 2 * share - 0.5
    p = min(1.0, max(0.0, p))
    return round(p, 4)
''', 'sum() counts the True values. Compute the share, apply the formula, then clip with min and max.', '<p>With few answers the raw estimate can fall below 0 or above 1. Clipping after the fact costs no privacy, because it never looks at the data again.</p>')
K.assign('budget_ok', 'h', 'Privacy budget checker',
         '<p>queries is a list of (epsilon, group) pairs. Queries with group None touch everyone and add up. Queries with a group name touch disjoint groups, and all named group queries together cost only their largest epsilon. Write <code>budget_ok(queries, total)</code> that returns the total cost rounded to 4 decimals if it is at most total, or <code>-1.0</code> if it is over the budget.</p>',
         '''
def budget_ok(queries, total):
    # your code here
    pass
''', [('budget_ok([(0.3, None), (0.3, None), (0.3, None)], 1.0)', 0.9),
      ('budget_ok([(0.3, None), (0.3, None), (0.3, None), (0.3, None)], 1.0)', -1.0),
      ('budget_ok([(0.5, "Delhi"), (0.5, "Mumbai"), (0.4, "Pune"), (0.2, None)], 1.0)', 0.7),
      ('budget_ok([], 1.0)', 0.0)],
         '''
def budget_ok(queries, total):
    seq = 0.0
    par = 0.0
    for eps, group in queries:
        if group is None:
            seq += eps
        else:
            par = max(par, eps)
    cost = round(seq + par, 4)
    if cost > total + 1e-9:
        return -1.0
    return cost
''', 'Add the None queries, keep the maximum of the named ones, then compare the sum with the total.', '<p>Real budget managers also record when each query ran and for whom, because a budget is a promise to the people in the data, not just a number in code.</p>')

K.must('Why DP', 'Anonymisation fails: Sweeney 1997 (ZIP, birth date, sex, 87%), AOL 2006, Netflix 2008. Reconstruction (Dinur and Nissim 2003, Census 2010 tests). DP: Dwork, McSherry, Nissim, Smith 2006, Gödel Prize 2017, US Census 2020.')
K.must('Definition', 'P[M(D) &isin; S] &le; e<sup>&epsilon;</sup> P[M(D&prime;) &isin; S] + &delta; for neighbours D, D&prime;. Small &epsilon; strong. &delta; much smaller than 1/n. Posterior from 50% at most e<sup>&epsilon;</sup>/(1 + e<sup>&epsilon;</sup>).')
K.must('Mechanisms', 'Randomised response (Warner 1965): P(yes) = p/2 + 1/4, &epsilon; = ln 3. Laplace b = &Delta;f/&epsilon; (count &Delta; = 1, std &radic;2 b). Gaussian &sigma; = &Delta;<sub>2</sub>&radic;(2 ln(1.25/&delta;))/&epsilon;. Exponential P &prop; e<sup>&epsilon;u/(2&Delta;u)</sup>.')
K.must('Composition', 'Sequential &Sigma;&epsilon;<sub>i</sub>, parallel max, post processing free, group k&epsilon;. Advanced composition grows like &radic;k. Rényi DP (Mironov 2017) and moments accountant for tight budgets.')
K.must('Sensitivity and clipping', 'Count 1, clipped mean (U &minus; L)/n, clipped gradient C. Clipping bounds each person’s influence so finite noise can hide it.')
K.must('DP in ML', 'DP-SGD (Abadi 2016): per example gradients, clip to C, add N(0, &sigma;<sup>2</sup>C<sup>2</sup>), sampling q = B/N, accountant gives (&epsilon;, &delta;). DP-FedAvg (2018) user level. Local DP (RAPPOR, Apple) versus central DP (Census). Adv &le; e<sup>&epsilon;</sup> &minus; 1.')

T = K.topic(
    slug='cy-dp', topic='cy-dp', step=(2, 'Federated learning and privacy', 'cy-a2', 'Training models across many devices and organisations without collecting their data, the attacks on such systems, and differential privacy.', 'Advanced'),
    title='Differential privacy', short='Differential privacy', badge='2.3', minutes=85,
    lead='The maths of privacy for statistics and machine learning: why anonymisation fails, randomised response, the definition with sensitivity and the Laplace mechanism, composition and privacy budgets, the Gaussian and exponential mechanisms, local and central DP, and DP-SGD and DP-FedAvg for training models that do not leak their data.',
    desc='differential privacy, DP, anonymisation, de identification, Sweeney, AOL, Netflix Prize, reconstruction attack, randomised response, Warner, local differential privacy, RAPPOR, Apple, epsilon, delta, neighbouring databases, sensitivity, Laplace mechanism, Gaussian mechanism, exponential mechanism, composition, privacy budget, post processing, group privacy, Renyi differential privacy, moments accountant, clipping, DP-SGD, Abadi, DP-FedAvg, central DP, US Census 2020, membership advantage',
    summary='Why anonymisation fails, randomised response, the DP definition, sensitivity and Laplace noise, composition and budgets, Gaussian and exponential mechanisms, local and central DP, DP-SGD and DP-FedAvg.',
    keywords=['differential privacy', 'epsilon', 'Laplace mechanism', 'Gaussian mechanism', 'randomised response', 'composition', 'privacy budget', 'DP-SGD', 'DP-FedAvg', 'local DP'],
    recap='<p>Bound each person’s influence, add noise sized to that bound, count every query against a budget, and remember that anything computed afterwards stays private.</p>',
    added='2026-11-15')
