# Chapter 9.1: probability for AI agents. The uploaded slides and transcripts do not cover this step, so it follows
# Russell and Norvig, AIMA 3rd ed. chapter 13 (4th ed. chapter 12). The dentist table is AIMA figure 13.3. Every
# number in this chapter was checked by running its code.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()
STEP9 = (9, 'Probability and Bayesian networks', 'cai-bayes', 'Reason when facts are uncertain: probability, Bayesian networks, directed and undirected models, exact and sampling inference, and causality.', 'College')

K.code('joint', r'''
# The full joint distribution of the dentist example (AIMA figure 13.3), as a dictionary.
# A key is (toothache, catch, cavity).
P = {(True, True, True): 0.108, (True, False, True): 0.012,
     (False, True, True): 0.072, (False, False, True): 0.008,
     (True, True, False): 0.016, (True, False, False): 0.064,
     (False, True, False): 0.144, (False, False, False): 0.576}

print("total:", round(sum(P.values()), 3))

# Marginal: add up every world where cavity is true.
p_cavity = 0
for (t, c, cav), p in P.items():
    if cav:
        p_cavity = p_cavity + p
print("P(cavity) =", round(p_cavity, 3))

# Conditional: keep the worlds with a toothache, then normalise.
yes = 0
no = 0
for (t, c, cav), p in P.items():
    if t and cav:
        yes = yes + p
    if t and not cav:
        no = no + p
alpha = 1 / (yes + no)
print("P(toothache) =", round(yes + no, 3), " alpha =", round(alpha, 3))
print("P(cavity | toothache) =", round(alpha * yes, 3))
''')

K.code('bayes', r'''
# Bayes' rule for a medical test: P(disease | positive) = P(positive | disease) P(disease) / P(positive)
prior = 0.01          # 1 person in 100 has the disease
sens = 0.90           # P(positive | disease)
false_pos = 0.09      # P(positive | no disease)

p_pos = sens * prior + false_pos * (1 - prior)    # total probability
post = sens * prior / p_pos
print("P(positive) =", round(p_pos, 4))
print("P(disease | positive) =", round(post, 4))

# A second, independent positive test: yesterday's posterior is today's prior.
p_pos2 = sens * post + false_pos * (1 - post)
post2 = sens * post / p_pos2
print("after two positive tests:", round(post2, 4))

# The same in odds form: posterior odds = prior odds x likelihood ratio.
odds = prior / (1 - prior)
lr = sens / false_pos
print("likelihood ratio:", round(lr, 2), " posterior odds:", round(odds * lr, 4), " ->", round(odds * lr / (1 + odds * lr), 4))
''')

K.code('naive', r'''
# A naive Bayes spam filter with add one (Laplace) smoothing, trained on six short messages.
train = [("win money now", "spam"), ("cheap money offer", "spam"), ("win a prize now", "spam"),
         ("meeting at noon", "ham"), ("project meeting notes", "ham"), ("lunch at noon", "ham")]

count = {"spam": 0, "ham": 0}
words = {"spam": {}, "ham": {}}
vocab = []
for text, label in train:
    count[label] = count[label] + 1
    for w in text.split():
        words[label][w] = words[label].get(w, 0) + 1
        if w not in vocab:
            vocab.append(w)

def score(text, label):
    total = sum(words[label].values())
    p = count[label] / len(train)                       # prior P(label)
    for w in text.split():
        p = p * (words[label].get(w, 0) + 1) / (total + len(vocab))   # P(word | label), smoothed
    return p

for msg in ["win money", "meeting at noon", "cheap lunch"]:
    s, h = score(msg, "spam"), score(msg, "ham")
    print(msg, "-> P(spam | words) =", round(s / (s + h), 3))
''')

K.lesson('why', 'Why agents need probability', f'''
{src('Russell and Norvig, AIMA 3rd ed., sections 13.1 and 13.2 (4th ed., sections 12.1 and 12.2). The uploaded slides and transcripts do not cover this step, so it follows the textbook.')}
{wwh('Probability gives a number between 0 and 1 to a sentence, saying how strongly the agent believes it. 1 means sure it is true, 0 means sure it is false. Everything in between is a degree of belief.',
     'Logic needs facts that are surely true or false. Real agents rarely have that. A dentist cannot list every cause of a toothache (laziness), does not know all of medicine (theoretical ignorance), and has not run every test on this patient (practical ignorance). Logic rules like "Toothache ⇒ Cavity" are simply false for many patients.',
     'Give each possible world a probability. The probability of a sentence is the sum over the worlds where it is true. New evidence changes beliefs by conditioning: throw away the worlds the evidence rules out and rescale the rest.')}
{fxs(fx('Kolmogorov axioms', '0 ≤ P(ω) ≤ 1 for every world ω, and the sum of P(ω) over all worlds is 1', 'Everything else follows from these.', key=True),
     fx('Probability of a sentence', 'P(φ) = Σ P(ω) over worlds ω where φ is true', 'A sentence is a set of worlds.'),
     fx('Inclusion and exclusion', 'P(a ∨ b) = P(a) + P(b) − P(a ∧ b)', 'Do not count the shared worlds twice.'),
     fx('Conditional probability', 'P(a | b) = P(a ∧ b) ÷ P(b), when P(b) > 0', 'Belief in a after learning only b.', key=True))}
{note('Why these rules and no others: de Finetti (1931) showed that an agent whose beliefs break the axioms can be offered a set of bets it accepts and always loses (a Dutch book). So a rational agent that bets on its beliefs must follow the axioms.', 'tip')}
{note('P(a | b) is not "if b then a with probability p". It is belief in a when b is all the agent knows. If more evidence c arrives, the agent must use P(a | b ∧ c).', 'warn')}
''', kw=['uncertainty', 'degree of belief', 'Kolmogorov axioms', 'Dutch book', 'conditional probability', 'qualification problem'])

K.lesson('jointdist', 'The full joint distribution and inference by enumeration', f'''
{src('AIMA 3rd ed., section 13.3, figure 13.3 (the dentist example).')}
{wwh('A random variable has a set of possible values, such as Cavity ∈ {true, false}. The full joint distribution P(Toothache, Catch, Cavity) gives the probability of every combination of values.',
     'From the full joint we can answer every question about these variables: a marginal such as P(cavity), or a conditional such as P(cavity | toothache).',
     'Marginalise (sum out) the variables we do not care about. Condition by keeping only the rows that match the evidence. Normalise by dividing by the total that is left, written with α = 1 ÷ P(evidence).')}
{fxs(fx('Marginalisation', 'P(Y) = Σ over z of P(Y, z)', 'Sum out the other variables Z.'),
     fx('Inference by enumeration', 'P(X | e) = α P(X, e) = α Σ over y of P(X, e, y)', 'X query, e evidence, y hidden variables.', key=True),
     fx('Size of the full joint', '2ⁿ entries for n true or false variables (2ⁿ − 1 free numbers)', 'This is why we need Bayesian networks.'))}
{viz('joint')}
{code('joint')}
{steps('Worked example: P(cavity ∨ toothache)', [
    'The worlds where cavity or toothache is true: all four cavity rows, plus the two no cavity rows with a toothache.',
    'Cavity rows: 0.108 + 0.012 + 0.072 + 0.008 = 0.2.',
    'No cavity, toothache rows: 0.016 + 0.064 = 0.08.',
    eq('P(cavity ∨ toothache) = 0.2 + 0.08 = 0.28')])}
''', kw=['random variable', 'full joint distribution', 'marginalisation', 'conditioning', 'normalisation', 'alpha', 'inference by enumeration'])

K.lesson('bayesrule', "Bayes' rule", f'''
{src('AIMA 3rd ed., section 13.5. Thomas Bayes (1763) and Pierre Simon Laplace (1812).')}
{wwh("Bayes' rule turns a probability around: from P(effect | cause), which is easy to measure, to P(cause | effect), which we need for diagnosis.",
     'A doctor knows how often a disease causes a symptom. That number stays the same in an epidemic. The chance that a symptom means the disease changes with how common the disease is, and Bayes’ rule takes care of that.',
     'Multiply the likelihood P(e | c) by the prior P(c), then divide by P(e). Find P(e) by adding the same product over every possible cause (total probability).')}
{fxs(fx("Bayes' rule", 'P(c | e) = P(e | c) P(c) ÷ P(e)', 'posterior = likelihood × prior ÷ evidence.', key=True),
     fx('Total probability', 'P(e) = P(e | c) P(c) + P(e | ¬c) P(¬c)', 'The bottom line of Bayes’ rule.'),
     fx('Odds form', 'posterior odds = prior odds × likelihood ratio, where the likelihood ratio is P(e | c) ÷ P(e | ¬c)', 'Easy to update one test at a time.'))}
{code('bayes')}
{steps('Worked example: the medical test (base rate)', [
    'Prior: 1 percent of people have the disease, P(d) = 0.01.',
    'The test finds 90 percent of real cases, P(+ | d) = 0.9, and wrongly says positive for 9 percent of healthy people, P(+ | ¬d) = 0.09.',
    'P(+) = 0.9 × 0.01 + 0.09 × 0.99 = 0.009 + 0.0891 = 0.0981.',
    'P(d | +) = 0.009 ÷ 0.0981.',
    eq('P(d | +) ≈ 0.0917, only about 9 percent')])}
{note('The base rate fallacy: most people guess about 90 percent for the test above. Healthy people are so many that their few false positives outnumber the true positives.', 'warn')}
''', kw=["Bayes' rule", 'prior', 'likelihood', 'posterior', 'total probability', 'base rate fallacy', 'odds', 'likelihood ratio'])

K.lesson('indep', 'Independence, conditional independence and naive Bayes', f'''
{src('AIMA 3rd ed., sections 13.4 and 13.5.2, and the naive Bayes text classifier in section 13.5.3 (4th ed., 12.6).')}
{wwh('Two variables are <b>independent</b> when learning one tells nothing about the other: P(a | b) = P(a). They are <b>conditionally independent given C</b> when, once C is known, one tells nothing more about the other: P(a | b, c) = P(a | c).',
     'Independence splits a huge joint table into small pieces. Absolute independence is rare, but conditional independence is common: Toothache and Catch both depend on Cavity, but given Cavity they no longer depend on each other.',
     'Write the joint as a product of small tables. With a cause and n effects that are conditionally independent given the cause, the joint needs 2n + 1 numbers instead of 2ⁿ⁺¹ − 1. This is the <b>naive Bayes</b> model.')}
{fxs(fx('Independence', 'P(a ∧ b) = P(a) P(b)', 'Same as P(a | b) = P(a).'),
     fx('Conditional independence', 'P(a ∧ b | c) = P(a | c) P(b | c)', 'Written a ⫫ b | c.', key=True),
     fx('Naive Bayes', 'P(Cause, e₁, ..., eₙ) = P(Cause) × Π P(eᵢ | Cause)', 'Then P(Cause | e) = α P(Cause) Π P(eᵢ | Cause).'),
     fx('Laplace (add one) smoothing', 'P(w | c) = (count(w, c) + 1) ÷ (total words in c + vocabulary size)', 'A word never seen with class c no longer gives probability 0.'))}
{code('naive')}
{steps('Worked example: check Toothache ⫫ Catch | Cavity in the dentist table', [
    'P(toothache ∧ catch | cavity) = 0.108 ÷ 0.2 = 0.54.',
    'P(toothache | cavity) = (0.108 + 0.012) ÷ 0.2 = 0.6.',
    'P(catch | cavity) = (0.108 + 0.072) ÷ 0.2 = 0.9.',
    eq('0.6 × 0.9 = 0.54, so they are conditionally independent given Cavity')])}
{note('Naive Bayes is called naive because the effects are rarely truly independent given the class. It still classifies well in practice (spam filters, document topics), because the class with the highest score is often right even when the probabilities themselves are off.', 'tip')}
''', kw=['independence', 'conditional independence', 'naive Bayes', 'Laplace smoothing', 'spam filter', 'factoring the joint'])

K.lesson('maths', 'The maths: rules every probability step uses', f'''
{fxs(
    fx('Product rule', 'P(a ∧ b) = P(a | b) P(b) = P(b | a) P(a)', 'Bayes’ rule comes from these two forms.'),
    fx('Chain rule', 'P(x₁, ..., xₙ) = Π over i of P(xᵢ | x₁, ..., xᵢ₋₁)', 'Always true. Bayesian networks shorten each condition.', key=True),
    fx('Bayes with background evidence', 'P(c | e, b) = P(e | c, b) P(c | b) ÷ P(e | b)', 'Keep b on every term.'),
    fx('Expected value', 'E[X] = Σ x P(X = x)', 'Used again for decisions and for reinforcement learning.'),
    fx('Variance', 'Var[X] = E[X²] − (E[X])²', 'How spread out X is.'))}
{steps('Worked example: Monty Hall with Bayes’ rule', [
    'The car is behind door 1, 2 or 3, each with prior 1/3. You pick door 1. The host, who knows where the car is, opens door 3 and shows a goat.',
    'Likelihood of "host opens 3": if the car is behind 1, he picks 2 or 3 at random, so 1/2. If behind 2, he must open 3, so 1. If behind 3, he cannot open it, so 0.',
    'P(host opens 3) = 1/2 × 1/3 + 1 × 1/3 + 0 × 1/3 = 1/2.',
    'P(car behind 2 | host opens 3) = (1 × 1/3) ÷ 1/2 = 2/3.',
    eq('switching wins with probability 2/3, staying with 1/3')])}
{deep('Where probabilities come from', '<p>The <b>frequentist</b> view says a probability is a long run frequency. The <b>Bayesian</b> (subjective) view says it is a degree of belief that must obey the axioms, updated with Bayes’ rule. The principle of indifference gives equal probability to symmetric outcomes. AI systems mostly take the Bayesian view, while learning the numbers from data (chapter on learning in AIMA chapter 20).</p>')}
''', kw=['product rule', 'chain rule', 'expected value', 'variance', 'Monty Hall', 'frequentist', 'Bayesian'])

K.lesson('compare', 'Probability compared with other ways to handle uncertainty', f'''
{versus('Ways to reason under uncertainty', ['', 'Probability theory', 'Logic with default rules', 'Certainty factors (MYCIN)', 'Fuzzy logic', 'Dempster Shafer theory'], [
    ['What a number means', 'degree of belief that a fact is true', 'no numbers, rules hold "by default"', 'change in belief from one rule', 'degree to which a vague fact holds ("tall")', 'belief and plausibility, an interval'],
    ['Combines evidence by', "Bayes' rule", 'withdrawing conclusions', 'fixed formulas per rule', 'min and max', "Dempster's rule"],
    ['Sound for chains of reasoning', 'Yes', 'Partly', 'No (can double count evidence)', 'It answers a different question (vagueness)', 'Yes, but costly'],
    ['Used today', 'Everywhere: medicine, robotics, speech, spam', 'Knowledge bases', 'Historic', 'Control systems', 'Sensor fusion niches']],
    'probability is the standard because it is the only system that rational betting forces (Dutch book) and because Bayesian networks make it efficient.')}
{scene('A spam filter that learns', '<p>Paul Graham’s 2002 essay "A Plan for Spam" made naive Bayes spam filters popular. Each word gets P(word | spam) and P(word | ham) from mail the user has already sorted. A new message is spam when α P(spam) Π P(wordᵢ | spam) is larger than the same product for ham. Smoothing keeps a word seen only in ham from making spam impossible.</p>')}
''', kw=['comparison', 'certainty factors', 'fuzzy logic', 'Dempster Shafer', 'default logic', 'spam filter'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Probability is a number for how sure you are. When you learn something new, cross out the cases that cannot happen and share the belief among the cases left.</p>',
    '<p>Axioms, the full joint, marginalising and conditioning, Bayes’ rule with total probability, independence and conditional independence, naive Bayes with smoothing.</p>',
    '<p>Exchangeability (de Finetti), conjugate priors (Beta for a coin, Dirichlet for word counts), maximum likelihood versus maximum a posteriori estimates, and why the full joint is exponential: the motivation for graphical models.</p>',
    '<p>Research: probabilistic programming languages (Stan, Pyro) that compile models into inference code, calibration of neural network probabilities, and imprecise probability for agents that cannot pin down a single number.</p>')}
''', kw=['conjugate prior', 'MAP', 'maximum likelihood', 'probabilistic programming', 'calibration'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Probability measures degree of belief. The Kolmogorov axioms, forced by the Dutch book argument, fix its rules.',
    'The full joint distribution answers every query: marginalise hidden variables, keep worlds that match the evidence, normalise with α.',
    "Bayes' rule P(c | e) = P(e | c) P(c) ÷ P(e) turns causal knowledge into diagnosis. Watch the base rate.",
    'Independence and conditional independence break the joint into small factors. Naive Bayes needs 2n + 1 numbers for a cause with n effects.',
    'The full joint has 2ⁿ entries, too many for real problems. Bayesian networks, next, fix this.'],
    'chapter 9.2 draws conditional independence as a graph: Bayesian networks and Markov networks.')}
{nbcard('probability-basics', 'Answer queries from the dentist joint table, apply Bayes’ rule to a medical test and train a naive Bayes spam filter, then write marginals, conditionals and Bayes’ rule yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'A probability of 0.3 for "the patient has a cavity" means', ['30 percent of the tooth is decayed', 'the agent believes it to degree 0.3, given what it knows', 'the logic rule is 30 percent true', 'the dentist is unsure about the word cavity'], 1,
       'Degree of belief.', 'It is about the agent’s knowledge, not about the tooth.')
K.quiz('e', 'Which is a Kolmogorov axiom?', ['P(a) can be negative', 'the probabilities of all worlds add up to 1', 'P(a ∨ b) = P(a) + P(b) always', 'P(a | b) = P(b | a)'], 1,
       'Normalisation.', 'The sum rule needs the overlap term in general.')
K.quiz('e', 'P(a | b) is defined as', ['P(a) P(b)', 'P(a ∧ b) ÷ P(b)', 'P(b) ÷ P(a)', 'P(a) + P(b)'], 1,
       'Keep the b worlds, rescale.', 'It needs P(b) > 0.')
K.quiz('e', 'How many entries does the full joint of 5 true or false variables have?', ['5', '10', '25', '32'], 3,
       '2 to the power 5.', 'One per world.')
K.quiz('m', 'The normalisation constant α in P(X | e) = α P(X, e) equals', ['P(X)', '1 ÷ P(e)', 'P(e)', '1'], 1,
       'Make the answer add up to 1.', 'Divide by the total probability of the evidence.')
K.quiz('m', 'A test is 90 percent sensitive with a 9 percent false positive rate, and 1 percent of people are ill. After one positive test, P(ill) is about', ['0.9', '0.5', '0.09', '0.01'], 2,
       'Use total probability for P(+).', '0.009 ÷ 0.0981 ≈ 0.092. This is the base rate fallacy.')
K.quiz('m', 'Toothache ⫫ Catch | Cavity means', ['Toothache and Catch are independent', 'once Cavity is known, Toothache tells nothing more about Catch', 'Cavity causes nothing', 'P(Toothache) = P(Catch)'], 1,
       'Conditional independence.', 'Without knowing Cavity they are dependent.')
K.quiz('m', 'Why does naive Bayes use Laplace smoothing?', ['to make it faster', 'so that a word never seen with a class does not make that class probability 0', 'to remove the prior', 'to make features independent'], 1,
       'Zero counts.', 'One unseen word would wipe out the whole product.')
K.quiz('h', 'A naive Bayes model with a true or false class and 20 true or false features needs how many numbers?', ['21', '41', '2²⁰', '2²¹ − 1'], 1,
       '1 for the prior, 2 per feature.', '1 + 2 × 20 = 41, against 2²¹ − 1 for the full joint.')
K.quiz('h', 'The Dutch book theorem says an agent whose beliefs break the axioms', ['cannot reason', 'can be offered bets it accepts that lose money whatever happens', 'is always right', 'must use fuzzy logic'], 1,
       'de Finetti.', 'Rational betting forces the axioms.')
K.quiz('x', 'In the style of a Stanford CS221 exam: A and B are independent, and A and B are each independent of C. Must A, B and C be mutually independent?', ['Yes', 'No: pairwise independence does not give P(a, b, c) = P(a) P(b) P(c)', 'Only if all are true or false', 'Only if P(C) = 0.5'], 1,
       'Think of two fair coins and C = "they match".', 'Each pair is independent, yet A and B together decide C.')
K.quiz('x', 'In the style of an MIT 6.034 exam: X and Y are independent. Are they still independent given Z?', ['Always', 'Not always: if both cause Z, observing Z makes them dependent (explaining away)', 'Never', 'Only when Z is independent of both'], 1,
       'Colliders.', 'Two independent causes of an observed effect become dependent.')

# ---------------------------------------------------------------- calc
K.calc('e', 'From the dentist table, P(cavity).', '0.2', 'Add the four cavity rows.',
       ['0.108 + 0.012 = 0.12.', '0.072 + 0.008 = 0.08.', eq('0.12 + 0.08 = 0.2')], check=0.2, tol=0.0005)
K.calc('e', 'From the dentist table, P(toothache).', '0.2', 'Add the four toothache rows.',
       ['Cavity: 0.108 + 0.012 = 0.12.', 'No cavity: 0.016 + 0.064 = 0.08.', eq('0.2')], check=0.2, tol=0.0005)
K.calc('e', 'From the dentist table, P(¬cavity | toothache).', '0.4', '0.08 ÷ 0.2.',
       ['P(¬cavity ∧ toothache) = 0.016 + 0.064 = 0.08.', 'P(toothache) = 0.2.', eq('0.08 ÷ 0.2 = 0.4')], check=0.4, tol=0.0005)
K.calc('m', 'From the dentist table, P(cavity ∨ toothache).', '0.28', 'P(cavity) + P(toothache) − P(both).',
       ['P(cavity) = 0.2, P(toothache) = 0.2.', 'P(cavity ∧ toothache) = 0.108 + 0.012 = 0.12.', eq('0.2 + 0.2 − 0.12 = 0.28')], check=0.28, tol=0.0005)
K.calc('m', 'From the dentist table, P(cavity | toothache ∧ catch). Give 3 decimals.', '0.871', '0.108 ÷ (0.108 + 0.016).',
       ['Rows with toothache and catch: 0.108 (cavity) and 0.016 (no cavity).', 'Total 0.124.', eq('0.108 ÷ 0.124 ≈ 0.871')], check=0.871, tol=0.001)
K.calc('m', 'Prior 0.01, P(+ | ill) = 0.9, P(+ | well) = 0.09. Find P(ill | +) to 4 decimals.', '0.0917', 'Total probability first.',
       ['P(+) = 0.9 × 0.01 + 0.09 × 0.99 = 0.0981.', 'Top: 0.9 × 0.01 = 0.009.', eq('0.009 ÷ 0.0981 ≈ 0.0917')], check=0.0917, tol=0.0005)
K.calc('m', 'How many free numbers does the full joint of 10 true or false variables need?', '1023', '2¹⁰ entries, minus one because they add up to 1.',
       ['2¹⁰ = 1024 entries.', 'The last one is 1 minus the rest.', eq('1023')], check=1023)
K.calc('h', 'The same test is taken twice, independently given the true state, and both are positive. Find P(ill | +, +) to 4 decimals.', '0.5025', 'Use 0.0917 as the new prior, or odds.',
       ['Prior odds 0.01 ÷ 0.99. Likelihood ratio per test 0.9 ÷ 0.09 = 10.', 'Posterior odds = (1 ÷ 99) × 100 = 100 ÷ 99.', eq('P = (100/99) ÷ (1 + 100/99) = 100 ÷ 199 ≈ 0.5025')], check=0.5025, tol=0.0005)
K.calc('h', 'Monty Hall: you pick door 1, the host opens door 3. P(car behind door 2)? Give 3 decimals.', '0.667', "Bayes' rule with the host's choices.",
       ['P(opens 3 | car 1) = 1/2, P(opens 3 | car 2) = 1, P(opens 3 | car 3) = 0.', 'P(opens 3) = 1/2.', eq('(1 × 1/3) ÷ (1/2) = 2/3 ≈ 0.667')], check=0.667, tol=0.001)
K.calc('x', 'Check conditional independence in the dentist table: P(toothache ∧ catch | cavity).', '0.54', '0.108 ÷ 0.2, and compare with 0.6 × 0.9.',
       ['P(toothache ∧ catch ∧ cavity) = 0.108.', 'Divide by P(cavity) = 0.2.', eq('0.54 = 0.6 × 0.9, so the product rule for conditional independence holds')], check=0.54, tol=0.0005)

# ---------------------------------------------------------------- assignments
JOINT = '''JOINT = {(True, True, True): 0.108, (True, False, True): 0.012,
         (False, True, True): 0.072, (False, False, True): 0.008,
         (True, True, False): 0.016, (True, False, False): 0.064,
         (False, True, False): 0.144, (False, False, False): 0.576}   # key: (toothache, catch, cavity)
'''
K.assign('marginal', 'e', 'A marginal from the joint table',
         '<p>JOINT maps (toothache, catch, cavity) to a probability. Write <code>marginal(joint, i)</code> that returns the probability that variable number i (0, 1 or 2) is true.</p>',
         JOINT + '''
def marginal(joint, i):
    # your code here
    pass
''', [("round(marginal(JOINT, 2), 3)", 0.2), ("round(marginal(JOINT, 0), 3)", 0.2), ("round(marginal(JOINT, 1), 3)", 0.34)],
         JOINT + '''
def marginal(joint, i):
    total = 0
    for world in joint:
        if world[i]:
            total = total + joint[world]
    return total
''', 'Loop over the keys and add the probability when position i is True.', '<p>P(catch) = 0.108 + 0.072 + 0.016 + 0.144 = 0.34.</p>')
K.assign('cond', 'm', 'A conditional probability from the joint table',
         '<p>Write <code>conditional(joint, q, e, v)</code> that returns P(variable q is true | variable e has value v).</p>',
         JOINT + '''
def conditional(joint, q, e, v):
    # your code here
    pass
''', [("round(conditional(JOINT, 2, 0, True), 3)", 0.6), ("round(conditional(JOINT, 2, 1, True), 3)", 0.529),
      ("round(conditional(JOINT, 1, 2, True), 3)", 0.9), ("round(conditional(JOINT, 2, 0, False), 3)", 0.1)],
         JOINT + '''
def conditional(joint, q, e, v):
    both = 0
    given = 0
    for world in joint:
        if world[e] == v:
            given = given + joint[world]
            if world[q]:
                both = both + joint[world]
    return both / given
''', 'Add up the worlds that match the evidence, and separately the ones that also have q true. Divide.', '<p>Test 4: P(cavity | no toothache) = (0.072 + 0.008) ÷ 0.8 = 0.1.</p>')
K.assign('bayes', 'm', "Bayes' rule for a test",
         "<p>Write <code>posterior(prior, sens, fpr)</code> that returns P(ill | positive) given P(ill) = prior, P(positive | ill) = sens and P(positive | well) = fpr.</p>",
         '''
def posterior(prior, sens, fpr):
    # your code here
    pass
''', [("round(posterior(0.01, 0.9, 0.09), 4)", 0.0917), ("round(posterior(0.5, 0.9, 0.1), 4)", 0.9),
      ("round(posterior(0.001, 0.99, 0.01), 4)", 0.0902), ("round(posterior(0.2, 1.0, 0.0), 4)", 1.0)],
         '''
def posterior(prior, sens, fpr):
    p_pos = sens * prior + fpr * (1 - prior)
    return sens * prior / p_pos
''', 'P(positive) = sens × prior + fpr × (1 − prior).', '<p>Test 3: a 99 percent accurate test for a disease of 1 in 1000 still gives only about 9 percent.</p>')

K.must('Axioms', '0 ≤ P(ω) ≤ 1, Σ P(ω) = 1. P(a ∨ b) = P(a) + P(b) − P(a ∧ b). P(a | b) = P(a ∧ b) ÷ P(b).')
K.must('Enumeration', 'P(X | e) = α Σ_y P(X, e, y). Marginalise, keep matching worlds, normalise. Full joint: 2ⁿ entries.')
K.must("Bayes' rule", 'P(c | e) = P(e | c) P(c) ÷ P(e), P(e) = Σ_c P(e | c) P(c). Odds form: posterior odds = prior odds × LR.')
K.must('Base rate', 'Prior 0.01, sensitivity 0.9, false positive 0.09 gives P(ill | +) ≈ 0.092.')
K.must('Conditional independence', 'P(a, b | c) = P(a | c) P(b | c). Naive Bayes: P(C | e) = α P(C) Π P(eᵢ | C), 2n + 1 numbers.')
K.must('Dentist numbers', 'P(cavity) = 0.2, P(toothache) = 0.2, P(cavity | toothache) = 0.6, P(cavity | toothache, catch) ≈ 0.871.')

T = K.topic(
    slug='probability-basics', topic='probability-basics', step=STEP9,
    title='Probability for AI agents', short='Probability basics', badge='9.1', minutes=50,
    lead='Measure belief with numbers. Answer questions from a full joint table, turn causes into diagnoses with Bayes’ rule, and use conditional independence to build a naive Bayes classifier.',
    desc='Uncertainty and degrees of belief, the Kolmogorov axioms and the Dutch book argument, random variables, the full joint distribution, marginalisation, conditioning, normalisation, inference by enumeration, Bayes’ rule, total probability, the base rate fallacy, odds and likelihood ratios, independence, conditional independence, naive Bayes with Laplace smoothing, and Monty Hall.',
    summary='Probability axioms, joint distributions, Bayes’ rule, independence and naive Bayes.',
    keywords=['probability', 'joint distribution', 'marginalisation', 'conditional probability', "Bayes' rule", 'base rate', 'independence', 'conditional independence', 'naive Bayes'],
    recap='<p>Marginalise, condition, normalise. Bayes: posterior ∝ likelihood × prior. Conditional independence makes the joint small.</p>',
    nb={'joint': 'Queries from the dentist joint table', 'bayes': "Bayes' rule for a medical test", 'naive': 'A naive Bayes spam filter'})
