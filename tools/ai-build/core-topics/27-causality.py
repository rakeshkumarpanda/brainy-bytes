# Chapter 9.4: causality. The uploaded slides and transcripts do not cover this step, so it follows Pearl (2009),
# Causality, Pearl and Mackenzie (2018) and AIMA 4th ed. section 13.5. The kidney stone counts are from Charig and
# others (1986). Every number in this chapter was checked by running its code and the causal animation.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, code, viz, eq
from coreaikit import wwh, versus, nbcard, recap, src, algo

K = Kit()
STEP9 = (9, 'Probability and Bayesian networks', 'cai-bayes', 'Reason when facts are uncertain: probability, Bayesian networks, directed and undirected models, exact and sampling inference, and causality.', 'College')

K.code('surgery', r'''
# Seeing versus doing in the sprinkler network: Cloudy -> Sprinkler, Cloudy -> Rain, both -> WetGrass.
p_c = 0.5
p_s = {True: 0.1, False: 0.5}      # P(Sprinkler = true | Cloudy)
p_r = {True: 0.8, False: 0.2}      # P(Rain = true | Cloudy)
p_w = {(True, True): 0.99, (True, False): 0.90, (False, True): 0.90, (False, False): 0.0}

# Seeing: P(Rain | Sprinkler = true). The sprinkler being on tells us something about Cloudy.
top, bottom = 0, 0
for c in [True, False]:
    pc = p_c if c else 1 - p_c
    top = top + pc * p_s[c] * p_r[c]
    bottom = bottom + pc * p_s[c]
print("P(Rain | Sprinkler = true)     =", round(top / bottom, 3))

# Doing: do(Sprinkler = true) cuts Cloudy -> Sprinkler, so P(s | c) leaves the product.
rain = 0
for c in [True, False]:
    pc = p_c if c else 1 - p_c
    rain = rain + pc * p_r[c]
print("P(Rain | do(Sprinkler = true)) =", round(rain, 3))

# Doing, then looking at an effect: P(WetGrass | do(Sprinkler = true)).
wet = 0
for c in [True, False]:
    pc = p_c if c else 1 - p_c
    for r in [True, False]:
        pr = p_r[c] if r else 1 - p_r[c]
        wet = wet + pc * pr * p_w[(True, r)]
print("P(WetGrass | do(Sprinkler = true)) =", round(wet, 3))
''')

K.code('simpson', r'''
# Kidney stones (Charig and others, 1986): (stone size, treatment, recovered, total).
data = [("small", "A", 81, 87), ("small", "B", 234, 270),
        ("large", "A", 192, 263), ("large", "B", 55, 80)]
everyone = sum(n for z, t, k, n in data)

def observed(t):                       # seeing: P(recovery | T = t)
    k = sum(k for z, tt, k, n in data if tt == t)
    n = sum(n for z, tt, k, n in data if tt == t)
    return k / n

def adjusted(t):                       # doing: P(recovery | do(T = t)) = sum over z of P(r | t, z) P(z)
    total = 0
    for z in ["small", "large"]:
        pz = sum(n for zz, tt, k, n in data if zz == z) / everyone
        for zz, tt, k, n in data:
            if zz == z and tt == t:
                total = total + (k / n) * pz
    return total

for t in ["A", "B"]:
    print(t, " seeing:", round(observed(t), 3), " doing:", round(adjusted(t), 3))
print("causal effect of A over B:", round(adjusted("A") - adjusted("B"), 3))
''')

K.lesson('ladder', 'Seeing, doing and imagining: the ladder of causation', f'''
{src('Pearl (2009), Causality, 2nd ed., Pearl and Mackenzie (2018), The Book of Why, and AIMA 4th ed., section 13.5 (causal networks). The uploaded slides and transcripts do not cover this topic.')}
{wwh('A <b>causal network</b> is a Bayesian network whose arrows mean "directly causes". It answers three kinds of question: seeing (what does the evidence tell me), doing (what happens if I act), and imagining (what would have happened if things had been different).',
     'Probability alone mixes up correlation and cause. Ice cream sales and drownings rise together because hot weather causes both. Banning ice cream would not save swimmers. An agent that acts on the world needs to know what its actions cause, not only what goes with what.',
     'Seeing uses conditioning: P(y | x). Doing uses the do operator: P(y | do(x)) means we set X to x by our own hand, which cuts every arrow into X. Imagining uses a structural causal model to replay one case with a change.')}
{table(['Rung', 'Question', 'Written as', 'Example'], [
    ['1. Association (seeing)', 'What if I see x?', 'P(y | x)', 'Patients who took the drug recovered more often.'],
    ['2. Intervention (doing)', 'What if I do x?', 'P(y | do(x))', 'Would recovery rise if we gave everyone the drug?'],
    ['3. Counterfactual (imagining)', 'What if I had done x instead?', 'P(y_x | x′, y′)', 'This patient took the drug and recovered. Would they have recovered without it?']])}
{note('A plain Bayesian network can be read in a non causal order and still give the right P(y | x). It can only answer rung 2 questions when its arrows are causal.', 'warn')}
''', kw=['causality', 'causal network', 'ladder of causation', 'association', 'intervention', 'counterfactual', 'do operator', 'correlation is not causation'])

K.lesson('dooper', 'The do operator and graph surgery', f'''
{src('Pearl (2009), sections 1.3 and 3.2, and Spirtes, Glymour and Scheines (1993), the manipulation theorem.')}
{wwh('do(X = x) is an action that sets X to x from outside the system. In the graph it removes every arrow into X and fixes X. The rest of the network stays the same.',
     'When we observe the sprinkler on, it also tells us the day is probably not cloudy, so rain is less likely. When we switch the sprinkler on ourselves, the weather is untouched. Conditioning cannot tell these apart, and the do operator can.',
     'Use the <b>truncated product</b>: the same product of CPTs as the network, but leave out the table of X and plug in X = x everywhere.')}
{fxs(fx('Truncated factorisation', 'P(v | do(x)) = Π over i with Vᵢ not X of P(vᵢ | parents(Vᵢ)), with X = x', 'The table of X is removed.', key=True),
     fx('Root causes', 'if X has no parents, P(y | do(x)) = P(y | x)', 'Nothing to cut, so seeing equals doing.'),
     fx('Average causal effect', 'ACE = P(y | do(x)) − P(y | do(¬x))', 'The quantity a randomised trial estimates.'))}
{code('surgery')}
{steps('Worked example: seeing versus doing for the sprinkler', [
    'Seeing: P(Rain | Sprinkler = true) = Σ_c P(c) P(s | c) P(r | c) ÷ Σ_c P(c) P(s | c) = (0.5 × 0.1 × 0.8 + 0.5 × 0.5 × 0.2) ÷ (0.05 + 0.25).',
    'That is 0.09 ÷ 0.3 = 0.3. The sprinkler being on suggests a sunny day.',
    'Doing: cut Cloudy → Sprinkler. Rain is untouched: P(Rain | do(s)) = Σ_c P(c) P(r | c) = 0.5 × 0.8 + 0.5 × 0.2.',
    eq('P(Rain | do(Sprinkler = true)) = 0.5, not 0.3')])}
{note('A randomised controlled trial (Fisher, 1935) performs do(X) in the real world: a coin, not the patient or the doctor, decides the treatment, so every arrow into the treatment is cut.', 'tip')}
''', kw=['do operator', 'graph surgery', 'truncated factorisation', 'manipulation', 'average causal effect', 'randomised controlled trial'])

K.lesson('backdoor', "Confounders, the back door criterion and Simpson's paradox", f'''
{src('Pearl (1993, 2009), section 3.3, Simpson (1951), and Charig and others (1986) for the kidney stone data.')}
{wwh('A <b>confounder</b> is a common cause of the treatment and the outcome. It opens a <b>back door path</b> T ← Z → R, so the observed link between T and R mixes the real effect with the effect of Z.',
     'We often cannot run an experiment. The back door criterion says when we can still compute P(r | do(t)) from observational data, and how.',
     'A set Z satisfies the back door criterion for (T, R) when no node in Z is a descendant of T, and Z blocks every path between T and R that starts with an arrow into T. Then adjust: average P(r | t, z) over the population share P(z).')}
{fxs(fx('Back door adjustment', 'P(r | do(t)) = Σ_z P(r | t, z) P(z)', 'Weight each group by its share of everyone, not its share among those treated.', key=True),
     fx('Compare with seeing', 'P(r | t) = Σ_z P(r | t, z) P(z | t)', 'The only difference is P(z | t) in place of P(z).'))}
{viz('causal')}
{code('simpson')}
{table(['Role of Z', 'Graph', 'Adjust for Z?'], [
    ['Confounder', 'T ← Z → R', 'Yes: it closes the back door'],
    ['Mediator', 'T → Z → R', 'No: it would remove part of the effect you want'],
    ['Collider', 'T → Z ← R', 'No: conditioning on it creates a false link (Berkson’s paradox)']])}
{note('Simpson’s paradox is not a fault in arithmetic. Which answer is right, the pooled one or the one inside groups, depends on the causal graph. With stone size as a confounder, the group answer (A is better) is right. If Z were a mediator, the pooled answer would be right.', 'warn')}
''', kw=['confounder', 'back door path', 'back door criterion', 'adjustment formula', "Simpson's paradox", 'mediator', 'collider', "Berkson's paradox"])

K.lesson('counterfactual', 'Counterfactuals with structural causal models', f'''
{src('Pearl (2009), chapter 7, and Balke and Pearl (1994).')}
{wwh('A <b>structural causal model</b> (SCM) writes each variable as a function of its parents and a hidden noise term U: Y = f(X, U). A counterfactual asks what Y would have been in this very case if X had been different.',
     'Questions about blame, fairness and regret are counterfactual: "would she have been hired if she were a man", "would the patient have lived without the drug". Rung 2 answers are about populations. Rung 3 answers are about one case.',
     'Three steps. Abduction: use what happened to work out the noise U for this case. Action: replace the equation of X by X = x′. Prediction: compute Y from the changed model with the same U.')}
{steps('Worked example: Y = 2X + U', [
    'We saw X = 1 and Y = 3.',
    'Abduction: 3 = 2 × 1 + U, so U = 1 for this case.',
    'Action: set X = 0.',
    'Prediction: Y = 2 × 0 + 1.',
    eq('Y would have been 1')])}
{deep('Identification and the do calculus', '<p>Pearl’s three rules of the do calculus (1995) turn expressions with do into expressions without it whenever that is possible. The calculus is complete: if the rules cannot remove every do, no method can compute the effect from observational data alone (Shpitser and Pearl, 2006, Huang and Valtorta, 2006). The <b>front door adjustment</b> P(y | do(x)) = Σ_m P(m | x) Σ_x′ P(y | m, x′) P(x′) handles a hidden confounder when the effect passes through an observed mediator M, as in smoking → tar → cancer.</p>')}
''', kw=['counterfactual', 'structural causal model', 'abduction action prediction', 'do calculus', 'front door adjustment', 'identification'])

K.lesson('maths', 'The maths: adjustment, front door and effects', f'''
{fxs(
    fx('Back door', 'P(y | do(x)) = Σ_z P(y | x, z) P(z)', 'Z blocks every back door path and has no descendants of X.', key=True),
    fx('Front door', 'P(y | do(x)) = Σ_m P(m | x) Σ_x′ P(y | m, x′) P(x′)', 'M carries all of the effect and has no hidden common cause with X.'),
    fx('Inverse probability weighting', 'P(y | do(x)) = Σ over units with X = x of 1 ÷ (N P(x | z))', 'Same answer as back door adjustment, used with many variables in Z.'),
    fx('Average causal effect', 'ACE = P(y | do(x)) − P(y | do(¬x))', 'Kidney stones: 0.833 − 0.779 ≈ 0.054.'))}
{steps('Worked example: a front door problem', [
    'P(x) = 0.5. P(m | x) = 0.9, P(m | ¬x) = 0.1. P(y | m, x) = 0.6, P(y | m, ¬x) = 0.4, P(y | ¬m, x) = 0.3, P(y | ¬m, ¬x) = 0.1.',
    'For m: Σ_x′ P(y | m, x′) P(x′) = 0.6 × 0.5 + 0.4 × 0.5 = 0.5.',
    'For ¬m: 0.3 × 0.5 + 0.1 × 0.5 = 0.2.',
    'Weight by P(m | x): 0.9 × 0.5 + 0.1 × 0.2 = 0.45 + 0.02.',
    eq('P(y | do(x)) = 0.47')])}
''', kw=['back door formula', 'front door formula', 'inverse probability weighting', 'average causal effect'])

K.lesson('compare', 'Ways to learn what causes what', f'''
{versus('Getting causal answers', ['', 'Randomised trial', 'Back door adjustment', 'Front door adjustment', 'Instrumental variables', 'Causal discovery from data'], [
    ['Needs', 'the power to assign treatment', 'all confounders measured', 'a mediator that carries the whole effect', 'a variable that moves T but affects R only through T', 'assumptions such as faithfulness'],
    ['Gives', 'P(r | do(t)) directly', 'P(r | do(t)) from observations', 'P(r | do(t)) even with a hidden confounder', 'the effect under linear or monotone models', 'a set of possible graphs'],
    ['Weak when', 'costly, slow or unethical', 'a confounder is missed', 'the mediator has other causes shared with T', 'the instrument is weak', 'data are few or variables hidden'],
    ['Example', 'drug trials', 'kidney stones', 'smoking, tar and cancer', 'distance to a hospital as an instrument', 'the PC algorithm (Spirtes and Glymour, 1991)']],
    'run an experiment when you can. When you cannot, draw the causal graph first, then pick the formula the graph allows.')}
{scene('Causal reasoning in practice', '<p>Medical guidelines rest on randomised trials because they cut every arrow into the treatment. Online companies run A/B tests, which are small randomised trials, before changing a web page. Economists won the 2021 Nobel prize (Card, Angrist and Imbens) for natural experiments and instrumental variables. In AI, causal models help with fairness (would the decision change if only the protected attribute changed) and with robustness, since causal links stay the same when the data distribution shifts.</p>')}
''', kw=['comparison', 'randomised trial', 'instrumental variables', 'causal discovery', 'PC algorithm', 'A/B test', 'fairness'])

K.lesson('levels', 'From intuition to research', f'''
{ladder(
    '<p>Seeing two things together does not mean one causes the other. To find out, change one thing yourself and watch what happens to the other.</p>',
    '<p>A causal network adds meaning to the arrows. do(x) cuts the arrows into X. The truncated product, the back door adjustment and Simpson’s paradox follow from this.</p>',
    '<p>The do calculus is complete for identification. Counterfactuals need structural equations, not just CPTs. Markov equivalent graphs differ in causal meaning, so data alone cannot always fix the arrows.</p>',
    '<p>Research: causal representation learning (finding causal variables in raw data such as images), causal reinforcement learning, invariant risk minimisation, and testing whether large language models can reason about interventions and counterfactuals.</p>')}
''', kw=['do calculus', 'causal representation learning', 'causal reinforcement learning', 'invariance'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Three rungs: seeing P(y | x), doing P(y | do(x)), imagining counterfactuals.',
    'do(x) cuts the arrows into X. The truncated product drops the table of X. Seeing and doing agree for root causes.',
    'Back door adjustment: P(r | do(t)) = Σ_z P(r | t, z) P(z) when Z blocks every back door path and is not caused by T.',
    'Simpson’s paradox: kidney stone treatment A looks worse overall (78 against 83 percent) but is better in each group, and better under do (83.3 against 77.9 percent).',
    'Counterfactuals: abduction, action, prediction on a structural causal model.'],
    'step 10 moves from beliefs to decisions over time: Markov decision processes and reinforcement learning.')}
{nbcard('causality', 'Compare seeing and doing in the sprinkler network and adjust the kidney stone data, then write the observed rate, the back door adjustment and a do query with graph surgery yourself.')}
''', kw=['summary', 'recap'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'P(y | do(x)) means', ['the chance of y among cases where x was seen', 'the chance of y if we set X to x ourselves', 'the chance of x given y', 'the same as P(x, y)'], 1,
       'Doing, not seeing.', 'The do operator is an action.')
K.quiz('e', 'In the graph, do(X = x)', ['adds arrows into X', 'removes every arrow into X', 'removes X’s children', 'reverses all arrows'], 1,
       'Graph surgery.', 'The cause of X is now our hand.')
K.quiz('e', 'A confounder is', ['a common effect of T and R', 'a common cause of T and R', 'a step between T and R', 'noise'], 1,
       'T ← Z → R.', 'It opens a back door path.')
K.quiz('e', 'A randomised controlled trial works because', ['it has many patients', 'chance decides the treatment, so nothing else causes it', 'patients choose', 'doctors know best'], 1,
       'It performs do(T).', 'Every arrow into the treatment is cut.')
K.quiz('m', 'In the sprinkler network, P(Rain | do(Sprinkler = true)) equals', ['P(Rain | Sprinkler = true) = 0.3', 'P(Rain) = 0.5', '1', '0'], 1,
       'Setting the sprinkler says nothing about the clouds.', 'Rain keeps its own distribution.')
K.quiz('m', 'The back door adjustment weights each group z by', ['P(z | t)', 'P(z)', 'P(t | z)', 'P(r | z)'], 1,
       'Population share.', 'Seeing uses P(z | t), doing uses P(z).')
K.quiz('m', 'Should you adjust for a mediator T → M → R when you want the total effect of T?', ['Yes', 'No, it blocks part of the effect you want to measure', 'Only if M is binary', 'Always'], 1,
       'Mediator.', 'Adjusting gives only the direct part.')
K.quiz('m', "Berkson's paradox comes from", ['conditioning on a common cause', 'conditioning on a common effect (collider)', 'randomising', 'small samples'], 1,
       'Colliders.', 'Two independent causes become linked once their common effect is selected.')
K.quiz('h', 'The three steps of a counterfactual are', ['seeing, doing, imagining', 'abduction, action, prediction', 'sample, weight, normalise', 'factor, multiply, sum'], 1,
       'Pearl, chapter 7.', 'Find U, change X, recompute Y.')
K.quiz('h', 'For a root variable X (no parents), P(y | do(x)) is', ['always 0', 'equal to P(y | x)', 'equal to P(y)', 'not defined'], 1,
       'Nothing to cut.', 'There is no back door.')
K.quiz('x', 'In the style of a Stanford causal inference exam: which set satisfies the back door criterion for T → R in the graph Z → T, Z → R, T → M → R?', ['{M}', '{Z}', '{Z, M}', 'the empty set'], 1,
       'Block T ← Z → R, do not touch descendants of T.', 'M is a descendant of T, so it must not be used.')
K.quiz('x', 'In the style of a Berkeley CS188 exam: the do calculus is complete, which means', ['every effect can be computed', 'if its rules cannot remove do, no method can identify the effect from the same observational data and graph', 'it never needs data', 'it equals Bayes’ rule'], 1,
       'Shpitser and Pearl 2006.', 'Completeness is about identification.')

# ---------------------------------------------------------------- calc
K.calc('e', 'Kidney stones: observed recovery rate with treatment A (273 of 350).', '0.78', '273 ÷ 350.',
       ['Recovered with A: 81 + 192 = 273.', 'Treated with A: 87 + 263 = 350.', eq('0.78')], check=0.78, tol=0.0005)
K.calc('e', 'Kidney stones: observed recovery rate with treatment B, to 3 decimals.', '0.826', '289 ÷ 350.',
       ['Recovered with B: 234 + 55 = 289.', 'Treated with B: 270 + 80 = 350.', eq('289 ÷ 350 ≈ 0.826')], check=0.826, tol=0.0005)
K.calc('e', 'Kidney stones: share of patients with small stones, P(small).', '0.51', '357 ÷ 700.',
       ['Small: 87 + 270 = 357.', 'All: 700.', eq('0.51')], check=0.51, tol=0.0005)
K.calc('m', 'P(recovery | do(A)), to 3 decimals.', '0.833', '0.931 × 0.51 + 0.730 × 0.49.',
       ['P(r | A, small) = 81 ÷ 87 ≈ 0.931. P(r | A, large) = 192 ÷ 263 ≈ 0.730.', '0.931 × 0.51 ≈ 0.475. 0.730 × 0.49 ≈ 0.358.', eq('≈ 0.833')], check=0.833, tol=0.001)
K.calc('m', 'P(recovery | do(B)), to 3 decimals.', '0.779', '0.867 × 0.51 + 0.6875 × 0.49.',
       ['P(r | B, small) = 234 ÷ 270 ≈ 0.867. P(r | B, large) = 55 ÷ 80 = 0.6875.', '0.867 × 0.51 ≈ 0.442. 0.6875 × 0.49 ≈ 0.337.', eq('≈ 0.779')], check=0.779, tol=0.001)
K.calc('m', 'Average causal effect of A over B, to 3 decimals.', '0.054', '0.833 − 0.779.',
       ['P(r | do(A)) ≈ 0.8326.', 'P(r | do(B)) ≈ 0.7789.', eq('≈ 0.054')], check=0.054, tol=0.001)
K.calc('m', 'Sprinkler network: P(Rain | Sprinkler = true), seeing.', '0.3', '0.09 ÷ 0.3.',
       ['Top: 0.5 × 0.1 × 0.8 + 0.5 × 0.5 × 0.2 = 0.04 + 0.05 = 0.09.', 'Bottom: 0.5 × 0.1 + 0.5 × 0.5 = 0.3.', eq('0.3')], check=0.3, tol=0.0005)
K.calc('h', 'Sprinkler network: P(WetGrass | do(Sprinkler = true)), to 3 decimals.', '0.945', 'Rain keeps P(r) = 0.5.',
       ['P(Rain) = 0.5 after the cut.', 'P(w | s, r) = 0.99, P(w | s, ¬r) = 0.90.', eq('0.5 × 0.99 + 0.5 × 0.90 = 0.945')], check=0.945, tol=0.0005)
K.calc('h', 'SCM Y = 2X + U. We saw X = 1, Y = 3. What would Y have been with X = 0?', '1', 'Abduction, action, prediction.',
       ['U = 3 − 2 = 1.', 'Set X = 0.', eq('Y = 0 + 1 = 1')], check=1)
K.calc('x', 'Front door: P(x) = 0.5, P(m | x) = 0.9, P(y | m, x) = 0.6, P(y | m, ¬x) = 0.4, P(y | ¬m, x) = 0.3, P(y | ¬m, ¬x) = 0.1. Find P(y | do(x)).', '0.47', 'Σ_m P(m | x) Σ_x′ P(y | m, x′) P(x′).',
       ['m: 0.6 × 0.5 + 0.4 × 0.5 = 0.5.', '¬m: 0.3 × 0.5 + 0.1 × 0.5 = 0.2.', eq('0.9 × 0.5 + 0.1 × 0.2 = 0.47')], check=0.47, tol=0.0005)

# ---------------------------------------------------------------- assignments
DATA = '''DATA = [("small", "A", 81, 87), ("small", "B", 234, 270),
        ("large", "A", 192, 263), ("large", "B", 55, 80)]   # (group, treatment, recovered, total)
EVEN = [("small", "A", 90, 100), ("small", "B", 80, 100),
        ("large", "A", 60, 100), ("large", "B", 50, 100)]
'''
K.assign('observe', 'e', 'The observed recovery rate',
         '<p>Write <code>observed(data, t)</code> that returns recovered ÷ total over all rows with treatment t.</p>',
         DATA + '''
def observed(data, t):
    # your code here
    pass
''', [("round(observed(DATA, 'A'), 3)", 0.78), ("round(observed(DATA, 'B'), 3)", 0.826), ("round(observed(EVEN, 'A'), 3)", 0.75)],
         DATA + '''
def observed(data, t):
    k = 0
    n = 0
    for group, treat, rec, tot in data:
        if treat == t:
            k = k + rec
            n = n + tot
    return k / n
''', 'Add recovered and totals for rows with this treatment, then divide.', '<p>Overall B looks better: 0.826 against 0.78.</p>')
K.assign('adjust', 'm', 'The back door adjustment',
         '<p>Write <code>adjusted(data, t)</code> = Σ over groups z of P(recovery | t, z) × P(z), where P(z) is the share of all patients in group z.</p>',
         DATA + '''
def adjusted(data, t):
    # your code here
    pass
''', [("round(adjusted(DATA, 'A'), 3)", 0.833), ("round(adjusted(DATA, 'B'), 3)", 0.779), ("round(adjusted(EVEN, 'A'), 3)", 0.75)],
         DATA + '''
def adjusted(data, t):
    everyone = 0
    for group, treat, rec, tot in data:
        everyone = everyone + tot
    groups = []
    for group, treat, rec, tot in data:
        if group not in groups:
            groups.append(group)
    result = 0
    for z in groups:
        size = 0
        for group, treat, rec, tot in data:
            if group == z:
                size = size + tot
        for group, treat, rec, tot in data:
            if group == z and treat == t:
                result = result + (rec / tot) * (size / everyone)
    return result
''', 'First find the share of each group among all patients. Then add rate × share for the rows with treatment t.', '<p>Test 3: with even groups, seeing and doing give the same 0.75.</p>')
SPR = '''P_C = 0.5
P_S = {True: 0.1, False: 0.5}
P_R = {True: 0.8, False: 0.2}
P_W = {(True, True): 0.99, (True, False): 0.90, (False, True): 0.90, (False, False): 0.0}
'''
K.assign('doquery', 'h', 'A do query by graph surgery',
         '<p>For the sprinkler network, write <code>wet_do(s)</code> = P(WetGrass = True | do(Sprinkler = s)) and <code>wet_see(s)</code> = P(WetGrass = True | Sprinkler = s). Sum over Cloudy and Rain. For do, leave P(s | c) out of the product.</p>',
         SPR + '''
def wet_do(s):
    # your code here
    pass

def wet_see(s):
    # your code here
    pass
''', [("round(wet_do(True), 3)", 0.945), ("round(wet_see(True), 3)", 0.927), ("round(wet_do(False), 3)", 0.45), ("round(wet_see(False), 3)", 0.527)],
         SPR + '''
def wet_do(s):
    total = 0
    for c in [True, False]:
        pc = P_C if c else 1 - P_C
        for r in [True, False]:
            pr = P_R[c] if r else 1 - P_R[c]
            total = total + pc * pr * P_W[(s, r)]
    return total

def wet_see(s):
    top = 0
    bottom = 0
    for c in [True, False]:
        pc = P_C if c else 1 - P_C
        ps = P_S[c] if s else 1 - P_S[c]
        bottom = bottom + pc * ps
        for r in [True, False]:
            pr = P_R[c] if r else 1 - P_R[c]
            top = top + pc * ps * pr * P_W[(s, r)]
    return top / bottom
''', 'Both are sums over c and r. Seeing keeps the factor P(s | c) and divides by P(s). Doing drops it.', '<p>Turning the sprinkler off ourselves leaves rain as the only cause: 0.5 × 0.9 = 0.45. Seeing it off suggests clouds, so rain is more likely (0.586), and the grass is wet with chance 0.586 × 0.9 ≈ 0.527.</p>')

K.must('Ladder', 'Seeing P(y | x), doing P(y | do(x)), imagining counterfactuals.')
K.must('do operator', 'Cut arrows into X, drop its CPT (truncated product). Root X: do equals see.')
K.must('Back door', 'Z has no descendant of T and blocks all T ← ... paths: P(r | do(t)) = Σ_z P(r | t, z) P(z).')
K.must("Simpson's paradox", 'Kidney stones: seeing A 0.78 < B 0.826, doing A 0.833 > B 0.779. Adjust for confounders, not mediators or colliders.')
K.must('Counterfactual', 'Abduction (find U), action (set X), prediction (recompute Y). Front door: Σ_m P(m | x) Σ_x′ P(y | m, x′) P(x′).')
K.must('Sprinkler', 'P(Rain | s) = 0.3 but P(Rain | do(s)) = 0.5. P(WetGrass | do(s)) = 0.945.')

T = K.topic(
    slug='causality', topic='causality', step=STEP9,
    title='Causality: seeing, doing and imagining', short='Causality', badge='9.4', minutes=50,
    lead='Tell correlation from cause. Use the do operator and graph surgery for actions, the back door adjustment to undo confounding (and explain Simpson’s paradox), and structural causal models for counterfactual questions.',
    desc='Causal networks, the ladder of causation, the do operator and graph surgery, the truncated factorisation, average causal effects, randomised controlled trials, confounders, mediators and colliders, the back door criterion and adjustment formula, Simpson’s paradox with the kidney stone data, Berkson’s paradox, structural causal models and counterfactuals, the front door adjustment and the do calculus.',
    summary='Causal networks, the do operator, back door adjustment, Simpson’s paradox and counterfactuals.',
    keywords=['causality', 'do operator', 'intervention', 'confounder', 'back door criterion', 'adjustment formula', "Simpson's paradox", 'counterfactual', 'structural causal model', 'front door'],
    recap='<p>do(x) cuts arrows into X. Adjust for confounders with Σ_z P(r | t, z) P(z). Counterfactuals: abduction, action, prediction.</p>',
    nb={'surgery': 'Seeing versus doing in the sprinkler network', 'simpson': 'Simpson’s paradox and the back door adjustment'})
