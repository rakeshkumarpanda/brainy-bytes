# MLOps 3.3: explainability and fairness. Checked against Breiman, Random forests (2001) for permutation importance,
# Strobl and colleagues, Bias in random forest variable importance measures (2007), Shapley, A value for n-person games
# (1953), Lundberg and Lee, A unified approach to interpreting model predictions (NeurIPS 2017), Hardt, Price and Srebro,
# Equality of opportunity in supervised learning (NeurIPS 2016), Chouldechova, Fair prediction with disparate impact
# (2017), Kleinberg, Mullainathan and Raghavan, Inherent trade-offs in the fair determination of risk scores (2017),
# Mitchell and colleagues, Model cards for model reporting (2019), the scikit-learn permutation_importance, SHAP and
# Fairlearn documentation, and the US EEOC Uniform Guidelines (1978) for the four fifths rule.
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, local, files, grow, term, show, leet_items
from mlkit import link, ossteps

chapter('mlops-explain-fair')
K = Kit()
K.code('importance', r'''
# Which features does the model really use? Impurity importance against permutation importance.
# We add a column of random ID numbers that has nothing to do with the label.
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

data = load_breast_cancer()
keep = ['worst radius', 'worst concave points', 'mean texture', 'worst smoothness']
X = data.data[:, [list(data.feature_names).index(k) for k in keep]]
rng = np.random.default_rng(0)
X = np.column_stack([X, rng.integers(0, 100000, len(X))])            # random_id: pure noise, many values
names = keep + ['random_id']
X_train, X_test, y_train, y_test = train_test_split(X, data.target, test_size=0.3, random_state=0, stratify=data.target)

forest = RandomForestClassifier(n_estimators=300, random_state=0).fit(X_train, y_train)
print('test accuracy', round(forest.score(X_test, y_test), 3))
perm = permutation_importance(forest, X_test, y_test, n_repeats=20, random_state=0)
print(f'{"feature":22s} {"impurity":>9s} {"permutation (test)":>19s}')
for i in np.argsort(-perm.importances_mean):
    print(f'{names[i]:22s} {forest.feature_importances_[i]:9.3f} {perm.importances_mean[i]:12.3f} +- {perm.importances_std[i]:.3f}')
print('Impurity importance gives the random ID a share because it offers many split points on training data.')
print('Permutation importance on test data shows that shuffling it changes nothing.')
''', long=True)

K.code('shapley', r'''
# Exact Shapley values for one prediction, by trying every order of adding the features.
# This is what the SHAP library estimates quickly for big models.
from itertools import permutations
from math import factorial

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier

rng = np.random.default_rng(0)
n = 3000
income = rng.normal(50, 15, n)                                      # thousands per year
debt = rng.uniform(0, 1, n)                                         # debt to income ratio
age = rng.integers(21, 70, n)
logit = 0.08 * (income - 50) - 4 * (debt - 0.5) + 0.02 * (age - 45)
y = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(int)          # 1 = loan repaid
X = np.column_stack([income, debt, age])
names = ['income', 'debt_ratio', 'age']
model = GradientBoostingClassifier(random_state=0).fit(X, y)
background = X[rng.choice(n, 200, replace=False)]                   # stands for "a typical applicant"


def value(subset, x):
    """Average prediction when the features in subset take x's values and the rest come from the background."""
    Z = background.copy()
    for j in subset:
        Z[:, j] = x[j]
    return model.predict_proba(Z)[:, 1].mean()


def shapley(x):
    k = len(x)
    phi = np.zeros(k)
    for order in permutations(range(k)):                            # 3 features: 6 orders
        seen = []
        for j in order:
            phi[j] += value(seen + [j], x) - value(seen, x)         # what j adds when it joins
            seen.append(j)
    return phi / factorial(k)


x = np.array([38.0, 0.82, 29])                                      # one applicant
base, pred = value([], x), model.predict_proba([x])[0, 1]
phi = shapley(x)
print(f'Average prediction (base value): {base:.3f}')
for name, v, p in zip(names, x, phi):
    print(f'  {name:10s} = {v:6.2f}   contribution {p:+.3f}')
print(f'base + contributions = {base + phi.sum():.3f}   model says {pred:.3f}')
print('The contributions always add up exactly from the base value to the prediction.')
''', long=True)

K.code('fairness_audit', r'''
# A fairness audit of a loan model, by group. The model never sees the group, but a postcode score is a proxy for it.
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(42)
n = 20000
group = np.where(rng.random(n) < 0.6, 'A', 'B')
income = rng.normal(np.where(group == 'A', 55, 45), 12)            # recorded income differs between groups
postcode = rng.normal(np.where(group == 'A', 0.6, 0.4), 0.1)       # a proxy: says a lot about the group
skill = rng.normal(0, 1, n)                                         # what really drives repayment, hidden
repaid = (0.05 * (income - 50) + skill + rng.normal(0, 0.8, n) > 0).astype(int)

X = np.column_stack([income, postcode])                             # no group column
X_tr, X_te, y_tr, y_te, g_tr, g_te = train_test_split(X, repaid, group, test_size=0.5, random_state=0)
score = LogisticRegression().fit(X_tr, y_tr).predict_proba(X_te)[:, 1]


def rates(approve, y, g):
    out = {}
    for name in ['A', 'B']:
        m = g == name
        out[name] = {'selection': approve[m].mean(), 'TPR': approve[m & (y == 1)].mean(),
                     'FPR': approve[m & (y == 0)].mean(), 'base rate': y[m].mean()}
    return out


def report(title, approve):
    r = rates(approve, y_te, g_te)
    print(title, f'(accuracy {np.mean(approve == y_te):.3f})')
    for name in ['A', 'B']:
        print(f'  group {name}: repaid {r[name]["base rate"]:.2f}  approved {r[name]["selection"]:.2f}  TPR {r[name]["TPR"]:.2f}  FPR {r[name]["FPR"]:.2f}')
    print(f'  disparate impact (B approved / A approved) {r["B"]["selection"] / r["A"]["selection"]:.2f}   '
          f'equal opportunity gap (TPR A - TPR B) {r["A"]["TPR"] - r["B"]["TPR"]:+.2f}')


report('One threshold of 0.5 for everyone', score >= 0.5)

# Equal opportunity: pick group B's threshold so that its TPR matches group A's
target = rates(score >= 0.5, y_te, g_te)['A']['TPR']
pos_b = np.sort(score[(g_te == 'B') & (y_te == 1)])
t_b = pos_b[int((1 - target) * len(pos_b))]
report(f'Group B threshold lowered to {t_b:.2f} (equal opportunity)', np.where(g_te == 'A', score >= 0.5, score >= t_b))
''', long=True)

K.code('shap_fairlearn', r'''
# The same two checks with the standard libraries: SHAP for explanations, Fairlearn for a fairness audit.
# Install first:  pip install shap fairlearn scikit-learn
import numpy as np
import pandas as pd
import shap
from fairlearn.metrics import MetricFrame, demographic_parity_ratio, equal_opportunity_difference, selection_rate
from fairlearn.postprocessing import ThresholdOptimizer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, recall_score
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(42)
n = 20000
group = np.where(rng.random(n) < 0.6, 'A', 'B')
income = rng.normal(np.where(group == 'A', 55, 45), 12)
postcode = rng.normal(np.where(group == 'A', 0.6, 0.4), 0.1)
debt = rng.uniform(0, 1, n)
skill = rng.normal(0, 1, n)
repaid = (0.05 * (income - 50) - 1.5 * (debt - 0.5) + skill + rng.normal(0, 0.8, n) > 0).astype(int)
X = np.column_stack([income, postcode, debt])
names = ['income', 'postcode', 'debt_ratio']
X_tr, X_te, y_tr, y_te, g_tr, g_te = train_test_split(X, repaid, group, test_size=0.5, random_state=0)
g_tr, g_te = pd.Series(g_tr, name='group'), pd.Series(g_te, name='group')
model = GradientBoostingClassifier(random_state=0).fit(X_tr, y_tr)

# 1. SHAP: TreeExplainer computes exact Shapley values for tree models in milliseconds
explainer = shap.TreeExplainer(model)
sv = explainer(X_te[:1000])                                        # values are in log odds for this model
print('Mean |SHAP| per feature (global importance, log odds):')
for name, v in sorted(zip(names, np.abs(sv.values).mean(axis=0)), key=lambda t: -t[1]):
    print(f'  {name:10s} {v:.3f}')
row = sv[0]
print('First applicant: base', round(float(row.base_values), 3), '+',
      ' + '.join(f'{name} {v:+.3f}' for name, v in zip(names, row.values)),
      '=', round(float(row.base_values + row.values.sum()), 3),
      ' model log odds', round(float(model.decision_function(X_te[:1])[0]), 3))

# 2. Fairlearn: metrics by group, then a post-processing fix with one threshold per group
pred = model.predict(X_te)
frame = MetricFrame(metrics={'accuracy': accuracy_score, 'selection': selection_rate, 'TPR': recall_score},
                    y_true=y_te, y_pred=pred, sensitive_features=g_te)
print(frame.by_group.round(3))
print('overall accuracy', round(accuracy_score(y_te, pred), 3))
print('demographic parity ratio', round(demographic_parity_ratio(y_te, pred, sensitive_features=g_te), 3),
      '  equal opportunity difference', round(equal_opportunity_difference(y_te, pred, sensitive_features=g_te), 3))

fixer = ThresholdOptimizer(estimator=model, constraints='true_positive_rate_parity', prefit=True, predict_method='predict_proba')
fixer.fit(X_tr, y_tr, sensitive_features=g_tr)
fair = fixer.predict(X_te, sensitive_features=g_te, random_state=0)
print('After ThresholdOptimizer: accuracy', round(accuracy_score(y_te, fair), 3),
      '  equal opportunity difference', round(equal_opportunity_difference(y_te, fair, sensitive_features=g_te), 3))
''', long=True)

WHY_LIBS = 'It needs the shap and fairlearn packages, which the browser version of Python cannot install.'
PLOTS = '''import matplotlib
matplotlib.use("Agg")                     # draw into files, no window needed
import matplotlib.pyplot as plt

sv.feature_names = names
shap.plots.beeswarm(sv, show=False)       # every applicant, every feature
plt.savefig("shap_beeswarm.png", dpi=150, bbox_inches="tight")
plt.close()
shap.plots.waterfall(sv[0], show=False)   # one applicant, base value to prediction
plt.savefig("shap_waterfall.png", dpi=150, bbox_inches="tight")'''
CHECK = 'python -c "import shap, fairlearn; print(shap.__version__, fairlearn.__version__)"'

LIB_MAC = ('<ol><li>Activate your project environment. Both packages publish ready built wheels for Apple Silicon and Intel Macs, so no compiler is needed. If pip starts compiling shap from source, your pip is old: upgrade it and try again.</li>'
           '<li>Run the program. This page was built with shap 0.54.1 and fairlearn 0.15.0.</li>'
           '<li>To keep the plots, add the lines shown below the panels. Open the PNG files with Preview.</li></ol>'
           + term(['source .venv/bin/activate', 'python -m pip install --upgrade pip', 'pip install shap fairlearn scikit-learn matplotlib', CHECK, 'python shap_fairlearn.py'], 'Terminal (macOS)'))
LIB_WIN = ('<ol><li>Activate the environment in PowerShell. Use <code>python -m pip</code> so the packages go into the active environment and not into another Python on the path.</li>'
           '<li>An error that mentions Microsoft Visual C++ 14.0 means pip found no wheel for your Python version and tried to compile. Use a Python version that shap lists on its PyPI page, or install the Microsoft C++ Build Tools.</li>'
           '<li>Plots saved with the lines below open in the Photos app.</li></ol>'
           + term(['.venv\\Scripts\\Activate.ps1', 'python -m pip install --upgrade pip', 'python -m pip install shap fairlearn scikit-learn matplotlib', CHECK, 'python shap_fairlearn.py'], 'PowerShell (Windows)'))
LIB_LINUX = ('<p>The same as macOS. On a server with no screen, matplotlib cannot open a window, so keep the <code>matplotlib.use("Agg")</code> line from the snippet below or set <code>MPLBACKEND=Agg</code> before running.</p>'
             + term(['source .venv/bin/activate', 'pip install shap fairlearn scikit-learn matplotlib', CHECK, 'MPLBACKEND=Agg python shap_fairlearn.py'], 'Terminal (Linux)'))
LIB_CHROME = ('<p>Install inside the Linux development environment. The saved PNG files appear in the Files app under Linux files, where you can open them with the ChromeOS image viewer.</p>'
              + term(['source .venv/bin/activate', 'uv pip install shap fairlearn scikit-learn matplotlib', CHECK, 'python shap_fairlearn.py'], 'Terminal (ChromeOS Linux)'))

K.lesson('global', 'Which features does the model use?', f'''
{src('Breiman, Random forests (2001), Strobl and colleagues, Bias in random forest variable importance measures (2007), and scikit-learn, Permutation feature importance.')}
{wwh('<b>Global importance</b> ranks the features by how much the whole model relies on them. <b>Impurity importance</b> (feature_importances_ in a tree model) adds up how much each feature reduced impurity in the training splits. <b>Permutation importance</b> shuffles one column of held out data and measures how much the score drops.',
     'Teams, auditors and regulators ask what drives a model. Importance also finds bugs: a model that leans on an ID column or a leaked target is wrong, however good its score looks.',
     'Prefer permutation importance on test data. Shuffle each feature several times, report the mean drop and its spread, and treat two strongly correlated features with care, because shuffling one leaves the other to carry the same information.')}
{run('importance')}
{note('Impurity importance always adds up to 1 and gives worst radius 0.442. On test data, shuffling worst radius costs 0.170 accuracy, the real dependence. The random ID column, pure noise, still got 0.018 of the impurity credit because its many distinct values offer many split points on training data. Shuffling it changed the test score by &minus;0.008, which is just noise.', 'exam')}
{fxs(fx('Permutation importance', 'I<sub>j</sub> = s &minus; (1/K) &Sigma;<sub>k</sub> s<sub>k,j</sub>', 's is the test score, s<sub>k,j</sub> the score after the k-th shuffle of feature j.', key=True),
     fx('Impurity importance', 'I<sub>j</sub> = &Sigma;<sub>splits on j</sub> (n<sub>node</sub>/n) &Delta;impurity', 'Measured on training data, biased towards features with many values.'))}
{table(['Method', 'Data it uses', 'Strength', 'Weakness'], [
    ['Impurity (tree models)', 'Training', 'Free, instant', 'Favours many valued features, says nothing about test data'],
    ['Permutation', 'Test', 'Any model, measures real dependence', 'Correlated features share or hide credit'],
    ['Mean |SHAP|', 'Any', 'Consistent with local explanations', 'Slower for non tree models']])}
''', kw=['feature importance', 'impurity importance', 'permutation importance', 'Gini importance', 'correlated features', 'leakage'])

K.lesson('shap', 'Shapley values: why this one prediction?', f'''
{src('Shapley, A value for n-person games (1953), and Lundberg and Lee, A unified approach to interpreting model predictions (2017).')}
{viz('mlshapley')}
{wwh('A <b>Shapley value</b> splits one prediction among the features. Start from the <b>base value</b>, the average prediction. Add the features one at a time and record what each adds. Average that over every order of adding them. <b>SHAP</b> is the family of fast methods that compute or estimate these values for real models.',
     'A loan applicant who is refused is owed a reason, and a data scientist debugging one strange prediction needs to see which inputs pushed it. Shapley values are the only way of splitting a prediction that is fair in a precise sense: contributions add up exactly, identical features get equal credit and an unused feature gets zero.',
     'For a few features, try every order, as the program does. For tree models use SHAP&rsquo;s TreeExplainer, which is exact and fast. For any other model use a sampling explainer with a background set of a few hundred typical rows.')}
{run('shapley')}
{note('The base value is 0.450, the average predicted chance of repaying. This applicant&rsquo;s debt ratio of 0.82 pulls the prediction down by 0.194, the low income by 0.121 and the young age by 0.052, ending at 0.083. The three contributions add up exactly from 0.450 to 0.083, which is the efficiency property.', 'exam')}
{fxs(fx('Shapley value', '&phi;<sub>j</sub> = &Sigma;<sub>S &sube; F &setminus; j</sub> [ |S|! (|F| &minus; |S| &minus; 1)! / |F|! ] &middot; [ v(S &cup; j) &minus; v(S) ]', 'v(S) is the average prediction when only the features in S are known.', key=True),
     fx('Efficiency', 'f(x) = &phi;<sub>0</sub> + &Sigma;<sub>j</sub> &phi;<sub>j</sub>', '&phi;<sub>0</sub> is the base value, the average prediction.', key=True),
     fx('Cost of the exact sum', '2<sup>|F|</sup> coalitions', '3 features need 8, 20 features already need 1,048,576.'))}
{deep('Explanations are not causes', '<p>A Shapley value says how the model used a feature, not what would happen in the world if the feature changed. With correlated features the credit is split in ways that depend on the background data. Report explanations together with the background you used, and never read them as advice such as &ldquo;lower your age&rdquo;. For actionable advice, counterfactual explanations search for the smallest change to changeable features that flips the decision.</p>')}
''', kw=['Shapley value', 'SHAP', 'base value', 'efficiency property', 'TreeExplainer', 'local explanation', 'counterfactual explanation'])

K.lesson('fair', 'Is the model fair to every group?', f'''
{src('Hardt, Price and Srebro, Equality of opportunity in supervised learning (2016), US EEOC Uniform Guidelines on Employee Selection Procedures (1978), and Barocas, Hardt and Narayanan, Fairness and Machine Learning (2023).')}
{viz('mlthreshold')}
{wwh('A <b>fairness audit</b> computes the same rates separately for each group of people, such as sex, age band or ethnicity, and compares them. <b>Demographic parity</b> asks for equal approval rates. <b>Equal opportunity</b> asks for equal true positive rates: people who would repay are approved equally often in every group. <b>Equalized odds</b> also asks for equal false positive rates.',
     'Leaving the group column out does not make a model fair. Other features such as postcode or income carry the same information, a proxy, and the model learns the old pattern from them. Lending, hiring and housing laws in many countries forbid unjustified differences between groups.',
     'Keep the group labels aside for auditing, even when the model may not use them. Compute selection rate, TPR and FPR per group on test data, compare them with a chosen rule, and repeat the audit whenever the model or the data changes.')}
{run('fairness_audit')}
{note('With one threshold of 0.5 group B is approved 33 percent of the time against 64 percent for group A, a disparate impact of 0.52, far below the four fifths rule of 0.8. Among people who did repay, B was approved 48 percent of the time and A 75 percent. Lowering B&rsquo;s threshold to 0.38 closed the TPR gap, raised the ratio to 0.92 and cost only 0.010 accuracy (0.647 to 0.637).', 'exam')}
{fxs(fx('Disparate impact ratio', 'DI = P(&ycirc; = 1 | B) / P(&ycirc; = 1 | A)', 'The four fifths rule flags DI below 0.8.', key=True),
     fx('Equal opportunity gap', 'TPR<sub>A</sub> &minus; TPR<sub>B</sub>, with TPR = P(&ycirc; = 1 | y = 1)', 'Zero means qualified people are treated alike.', key=True),
     fx('Equalized odds', 'TPR<sub>A</sub> = TPR<sub>B</sub> and FPR<sub>A</sub> = FPR<sub>B</sub>', 'Both kinds of error are shared equally.'))}
''', kw=['fairness audit', 'demographic parity', 'disparate impact', 'four fifths rule', 'equal opportunity', 'equalized odds', 'proxy feature', 'sensitive attribute'])

K.lesson('tools', 'SHAP and Fairlearn on your own computer', f'''
{src('SHAP documentation (TreeExplainer, plots), and Fairlearn documentation (MetricFrame, ThresholdOptimizer).')}
{wwh('<b>SHAP</b> is the standard Python library for Shapley explanations. <b>Fairlearn</b> computes metrics by group with MetricFrame and offers mitigation methods such as ThresholdOptimizer, which picks a threshold per group to meet a fairness rule.',
     'Hand written loops teach the idea, but real projects need tested, fast tools whose numbers others can reproduce. Both libraries are open source and work with any scikit-learn model.',
     'Install both packages, run the program, then add the plot lines to save a beeswarm chart (every row, every feature) and a waterfall chart (one row, from base value to prediction).')}
{local('shap_fairlearn', WHY_LIBS)}
{note('TreeExplainer works in log odds for this model, and for the first applicant 0.027 + 0.489 + 0.027 + 0.401 = 0.943, exactly the model&rsquo;s own log odds. Postcode gets a small mean |SHAP| of 0.055, yet the audit still shows a TPR gap of 0.196 between groups, because income also differs between groups. ThresholdOptimizer cut the gap to 0.018 while overall accuracy went from 0.672 to 0.665.', 'tip')}
{ossteps('Install SHAP and Fairlearn and run the program', LIB_MAC, LIB_WIN, LIB_LINUX, LIB_CHROME)}
{show('Add to the end of shap_fairlearn.py to save the plots', PLOTS, {2: 'The Agg backend writes image files and needs no screen, so it also works on servers and in CI.', 6: 'Each dot is one applicant, coloured by the feature value and placed by its SHAP value.', 9: 'One applicant, bar by bar from the base value to the final log odds.'})}
''', kw=['SHAP library', 'Fairlearn', 'MetricFrame', 'ThresholdOptimizer', 'beeswarm plot', 'waterfall plot', 'pip install'])

K.lesson('tradeoff', 'Fixing unfairness, and why you cannot have every kind', f'''
{src('Chouldechova, Fair prediction with disparate impact (2017), and Kleinberg, Mullainathan and Raghavan, Inherent trade-offs in the fair determination of risk scores (2017).')}
{steps('Three places to mitigate bias', [
    'Before training (pre processing): fix the data. Collect more examples of the smaller group, reweight rows, or remove proxies that carry no real signal.',
    'During training (in processing): add a fairness constraint or penalty to the loss, for example Fairlearn&rsquo;s ExponentiatedGradient.',
    'After training (post processing): choose a threshold per group, as ThresholdOptimizer did. It needs the group at decision time, which some laws do not allow.',
    'Whatever you choose, measure accuracy and every fairness metric again on fresh test data, and record the decision and its reasons.'])}
{wwh('An <b>impossibility result</b> says that when the groups have different base rates (shares of real positives), no imperfect classifier can be calibrated and also have equal false positive and false negative rates in every group.',
     'Fairness is a choice between definitions that conflict, not a box you tick. Teams must pick the definition that fits the harm in their setting, and say so openly.',
     'Ask which error hurts people most. Refusing a good borrower points to equal opportunity. Wrongly flagging an innocent person points to equal false positive rates. Then document the choice in the model card.')}
{fxs(fx('Chouldechova&rsquo;s identity', 'FPR = [p / (1 &minus; p)] &middot; [(1 &minus; PPV) / PPV] &middot; (1 &minus; FNR)', 'p is the base rate. With equal PPV and FNR, different p forces different FPR.', key=True))}
{versus('Fairness rules compared', ['', 'Demographic parity', 'Equal opportunity', 'Equalized odds', 'Calibration by group'], [
    ['Asks for equal', 'Approval rate', 'TPR', 'TPR and FPR', 'Meaning of a score'],
    ['Uses true labels', 'No', 'Yes', 'Yes', 'Yes'],
    ['Fits when', 'Labels themselves are biased', 'Missing a qualified person is the main harm', 'Both errors harm people', 'Scores are read as probabilities'],
    ['Main cost', 'Can approve unqualified people', 'FPR may differ', 'Usually lowers accuracy most', 'Rates may differ between groups']],
    'With different base rates, calibration by group conflicts with equalized odds. Choose one and explain why.')}
''', kw=['bias mitigation', 'pre processing', 'in processing', 'post processing', 'impossibility theorem', 'calibration', 'base rate', 'ExponentiatedGradient'])

K.lesson('cards', 'Model cards and responsible release', f'''
{src('Mitchell and colleagues, Model cards for model reporting (2019), Gebru and colleagues, Datasheets for datasets (2021), the EU AI Act (Regulation 2024/1689) and GDPR Article 22.')}
{wwh('A <b>model card</b> is a short document shipped with every model version. It states what the model is for and not for, the training data, metrics overall and per group, fairness results, known limits and who to contact. A <b>datasheet</b> does the same for a dataset.',
     'People who reuse a model rarely know how it was built. Regulators increasingly ask for this record: the EU AI Act lists credit scoring and hiring among high risk uses that need documentation and human oversight, and GDPR Article 22 gives people rights around decisions made only by automated means.',
     'Generate the card from the tracking run and the audit, so the numbers cannot drift from the real model. Store it next to the model in the registry (MLOps 3.1) and make the promotion gate fail if the card or the fairness check is missing.')}
{table(['Model card section', 'Example for the loan model'], [
    ['Intended use', 'Rank loan applications for human review. Not for automatic refusal.'],
    ['Training data', '20,000 past applications, 2019 to 2024, one country'],
    ['Metrics', 'Accuracy 0.637 overall, reported per group'],
    ['Fairness', 'Equal opportunity gap 0.00 after group thresholds, disparate impact 0.92'],
    ['Explanations', 'SHAP top three reasons sent with every refusal'],
    ['Limits', 'Not tested on self employed applicants. Retrain if PSI of income passes 0.25 (MLOps 3.2).']])}
{note('Explainability and fairness checks belong in the same CI pipeline as accuracy tests (MLOps 2.3). A gate such as &ldquo;fail if disparate impact is below 0.8 or the TPR gap is above 0.05&rdquo; stops an unfair model from being promoted, in the same way as a failing unit test.', 'tip')}
''', kw=['model card', 'datasheet', 'EU AI Act', 'GDPR Article 22', 'human oversight', 'responsible AI', 'fairness gate'])

K.lesson('levels', 'From beginner to expert', f'''
{ladder(
    '<p>Ask which inputs a model relies on, and check whether it treats different groups of people alike.</p>',
    '<p>Compute permutation importance and Shapley values, audit selection rate, TPR and FPR per group, and apply the four fifths rule.</p>',
    '<p>Use SHAP and Fairlearn, choose and defend a fairness definition, mitigate bias before, during or after training, and write model cards.</p>',
    '<p>Explain models with correlated features and causal structure, prove trade-offs between fairness rules, and audit large language and vision models for bias.</p>')}
{grow('Ask what drives a model and who it affects.',
      'Explain single predictions and audit groups.',
      'Ship models with explanations, fairness gates and model cards.')}
{scene('A refused applicant asks why', '<p>A bank&rsquo;s model refuses a loan. The applicant asks for the reason. The team computes SHAP values for that one decision: debt ratio &minus;0.194, income &minus;0.121, age &minus;0.052. They send the two main reasons, debt ratio and income, in plain words. Because age is a protected attribute in many lending laws, the quarterly audit also checks that approval rates by age band pass the four fifths rule.</p>')}
''', kw=['beginner', 'expert', 'adverse action reasons'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Permutation importance</b> on test data measures real dependence (worst radius 0.170). Impurity importance is computed on training data and still credited a random ID with 0.018.',
    '<b>Shapley values</b> split one prediction exactly: base 0.450, then &minus;0.121, &minus;0.194 and &minus;0.052, ending at 0.083. TreeExplainer computes them exactly for trees.',
    'Dropping the group column does not remove bias, because proxies carry it. One threshold gave a disparate impact of 0.52 and a TPR gap of 0.28.',
    'A per group threshold closed the TPR gap for 0.010 accuracy. With different base rates, calibration and equal error rates cannot all hold.',
    'Install shap and fairlearn per OS, save plots with the Agg backend, and ship a model card with every version.'],
    'Coming next: designing a whole ML system end to end, and revising MLOps for interviews and exams.')}
{files('Three tasks: permutation importance from scores, exact Shapley values for two features, and a disparate impact ratio by group.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Permutation importance measures', ['The number of splits on a feature', 'How much the test score drops when one feature is shuffled', 'The correlation with the label', 'The training time'], 1, 'Shuffle and measure.', 'Worst radius: 0.170.')
K.quiz('e', 'The base value in a SHAP explanation is', ['Zero', 'The average prediction over the background data', 'The largest contribution', 'The true label'], 1, 'Where every explanation starts.', '0.450 in the loan example.')
K.quiz('e', 'Removing the group column from the features', ['Makes the model fair', 'Does not remove bias when other features act as proxies', 'Is illegal', 'Raises accuracy'], 1, 'Proxies.', 'Postcode and income carried it.')
K.quiz('e', 'The four fifths rule flags a disparate impact ratio below', ['0.5', '0.8', '0.95', '1.25'], 1, 'Four fifths is 0.8.', 'From the 1978 US EEOC guidelines.')
K.quiz('m', 'Why did the random ID column get impurity importance?', ['It predicts the label', 'Its many distinct values give many split points on training data', 'It was scaled', 'It is the first column'], 1, 'Bias of impurity importance.', 'Permutation importance showed &minus;0.008.')
K.quiz('m', 'The efficiency property of Shapley values says', ['They are always positive', 'Base value plus all contributions equals the prediction', 'They sum to one', 'Only one feature gets credit'], 1, 'Adds up exactly.', '0.450 &minus; 0.367 = 0.083.')
K.quiz('m', 'Equal opportunity asks for equal', ['Approval rates', 'True positive rates between groups', 'Accuracy', 'Group sizes'], 1, 'Qualified people treated alike.', 'P(approve | repaid) per group.')
K.quiz('m', 'Two features are strongly correlated. Shuffling one of them', ['Always gives it high importance', 'Can show little drop because the other still carries the information', 'Breaks the model', 'Has no effect on any model'], 1, 'Shared information.', 'Shuffle them as a group.')
K.quiz('m', 'On a Linux server without a screen, SHAP plots fail to open a window. The fix is', ['Install a desktop', 'Use the matplotlib Agg backend and save the plot to a file', 'Use fewer rows', 'Run as root'], 1, 'Write to files.', 'MPLBACKEND=Agg.')
K.quiz('h', 'ThresholdOptimizer needs the group at prediction time. Why can that be a problem?', ['It is slow', 'Some laws forbid using the protected attribute in the decision itself', 'It lowers TPR', 'It needs a GPU'], 1, 'Disparate treatment.', 'Then use pre or in processing.')
K.quiz('h', 'Groups have different base rates and a classifier is calibrated in both. Then', ['Equalized odds holds automatically', 'Equal false positive and false negative rates generally cannot both hold', 'Accuracy is 1', 'Demographic parity holds'], 1, 'Impossibility result.', 'Chouldechova, Kleinberg and colleagues.')
K.quiz('h', 'A SHAP value of &minus;0.05 for age means', ['Raising age by one year lowers the prediction by 0.05', 'In this model and with this background, age moved this prediction down by 0.05', 'Age causes default', 'Age is unimportant'], 1, 'Model use, not cause.', 'Not advice to change anything.')
K.quiz('x', 'In the style of a Stanford CS329S question: exact Shapley values for 20 features need the value of how many coalitions?', ['20', '400', '2<sup>20</sup> = 1,048,576', '20!'], 2, 'Every subset.', 'Hence sampling and TreeExplainer.')
K.quiz('x', 'In the style of an ML fairness interview: for a medical screening test where missing a sick patient is the main harm, the best first rule is', ['Demographic parity', 'Equal opportunity (equal TPR across groups)', 'Equal group sizes', 'No rule'], 1, 'Missed positives are the harm.', 'Then check FPR too.')

K.calc('e', 'Base value 0.45, contributions &minus;0.121, &minus;0.194 and &minus;0.052. Prediction?', '0.083', 'Efficiency property.', ['Sum of contributions: &minus;0.121 &minus; 0.194 &minus; 0.052 = &minus;0.367.', 'Add the base value.', eq('0.45 &minus; 0.367 = 0.083')], check=0.083, tol=0.0005)
K.calc('e', 'Group A is approved 64 percent of the time and group B 33 percent. Disparate impact ratio?', '0.5156', 'B over A.', ['DI = rate B / rate A.', '0.33 / 0.64.', eq('DI = 0.5156, below 0.8')], check=0.5156, tol=0.0005)
K.calc('e', 'Group A&rsquo;s approval rate is 0.50. The lowest rate for group B that passes the four fifths rule?', '0.4', '0.8 times A.', ['The rule: rate B / rate A &ge; 0.8.', 'So rate B &ge; 0.8 &times; 0.50.', eq('rate B &ge; 0.40')], check=0.4)
K.calc('m', 'Test accuracy is 0.936. After shuffling worst radius it is 0.766. Permutation importance?', '0.17', 'Score drop.', ['I = s &minus; s<sub>shuffled</sub>.', '0.936 &minus; 0.766.', eq('I = 0.170')], check=0.17, tol=0.0005)
K.calc('m', 'Two features with v(&empty;) = 0.4, v(1) = 0.6, v(2) = 0.5, v(1,2) = 0.9. Shapley value of feature 1?', '0.3', 'Average over the 2 orders.', ['Order 1 then 2: feature 1 adds 0.6 &minus; 0.4 = 0.2.', 'Order 2 then 1: feature 1 adds 0.9 &minus; 0.5 = 0.4.', eq('&phi;<sub>1</sub> = (0.2 + 0.4) / 2 = 0.3')], check=0.3)
K.calc('m', 'Group B has 400 people who repaid, and the model approved 192 of them. TPR of group B?', '0.48', 'Approved among real positives.', ['TPR = approved positives / all positives.', '192 / 400.', eq('TPR = 0.48')], check=0.48)
K.calc('m', 'TPR is 0.75 in group A and 0.48 in group B. Equal opportunity gap?', '0.27', 'A minus B.', ['Gap = TPR<sub>A</sub> &minus; TPR<sub>B</sub>.', '0.75 &minus; 0.48.', eq('gap = 0.27')], check=0.27, tol=0.0005)
K.calc('h', 'How many coalitions must be evaluated for exact Shapley values with 20 features?', '1048576', 'Every subset.', ['Each feature is in or out of a coalition: 2 choices.', '20 features give 2<sup>20</sup> subsets.', eq('2<sup>20</sup> = 1,048,576')], check=1048576)
K.calc('h', 'Accuracy fell from 0.647 to 0.637 after the fairness fix. Relative drop in percent?', '1.5456', 'Drop over the old value.', ['Drop: 0.647 &minus; 0.637 = 0.010.', '0.010 / 0.647 = 0.015456.', eq('0.015456 &times; 100 = 1.5456 percent')], check=1.5456, tol=0.0005)
K.calc('x', 'In the style of a fairness theory exam: PPV = 0.8 and FNR = 0.2 in both groups, and group B&rsquo;s base rate is 0.3. Use FPR = [p/(1 &minus; p)] &middot; [(1 &minus; PPV)/PPV] &middot; (1 &minus; FNR). FPR of group B?', '0.0857', 'Multiply the three factors.', ['p / (1 &minus; p) = 0.3 / 0.7 = 0.4286.', '(1 &minus; PPV) / PPV = 0.2 / 0.8 = 0.25, and 1 &minus; FNR = 0.8.', eq('0.4286 &times; 0.25 &times; 0.8 = 0.0857 (a group with p = 0.5 gets 0.2)')], check=0.0857, tol=0.0005)

K.assign('perm_importance', 'e', 'Permutation importance from scores',
         '<p>Write <code>perm_importance(base, shuffled)</code>. <code>base</code> is the test score of the model and <code>shuffled</code> a list of scores after shuffling one feature several times. Return the mean drop, base minus the mean of shuffled, rounded to 3 decimals.</p>',
         """
def perm_importance(base, shuffled):
    # your code here
    pass
""", [('perm_importance(0.9, [0.8, 0.7])', 0.15), ('perm_importance(0.9, [0.9, 0.9, 0.9])', 0.0), ('perm_importance(0.5, [0.6])', -0.1), ('perm_importance(0.936, [0.77, 0.76, 0.768])', 0.17)],
         """
def perm_importance(base, shuffled):
    return round(base - sum(shuffled) / len(shuffled) + 0.0, 3)
""", 'Average the shuffled scores, then subtract from the base score.', '<p>A negative result means shuffling made the score slightly better by chance, so the feature is useless. Real tools report the spread across shuffles too.</p>')
K.assign('shapley_two', 'm', 'Exact Shapley values for two features',
         '<p>Write <code>shapley_two(v0, v1, v2, v12)</code>. The arguments are the value with no features known, with only feature 1, with only feature 2, and with both. Return a tuple (&phi;<sub>1</sub>, &phi;<sub>2</sub>), each rounded to 4 decimals, by averaging what each feature adds over the two orders.</p>',
         """
def shapley_two(v0, v1, v2, v12):
    # your code here
    pass
""", [('shapley_two(0.4, 0.6, 0.5, 0.9)', (0.3, 0.2)), ('shapley_two(0, 1, 1, 2)', (1.0, 1.0)), ('shapley_two(0.5, 0.5, 0.5, 0.5)', (0.0, 0.0)), ('shapley_two(0.45, 0.3, 0.2, 0.1)', (-0.125, -0.225))],
         """
def shapley_two(v0, v1, v2, v12):
    phi1 = ((v1 - v0) + (v12 - v2)) / 2
    phi2 = ((v2 - v0) + (v12 - v1)) / 2
    return (round(phi1 + 0.0, 4), round(phi2 + 0.0, 4))
""", 'Feature 1 adds v1 &minus; v0 when it comes first and v12 &minus; v2 when it comes second.', '<p>Check the efficiency property: v0 + &phi;<sub>1</sub> + &phi;<sub>2</sub> always equals v12.</p>')
K.assign('disparate_impact', 'm', 'Disparate impact by group',
         '<p>Write <code>disparate_impact(approve, group)</code>. <code>approve</code> is a list of 0 and 1 decisions and <code>group</code> the group label of each person. Compute the approval rate of every group and return the lowest rate divided by the highest, rounded to 3 decimals.</p>',
         """
def disparate_impact(approve, group):
    # your code here
    pass
""", [("disparate_impact([1, 1, 0, 1, 0, 0], ['A', 'A', 'A', 'B', 'B', 'B'])", 0.5), ("disparate_impact([1, 0, 1, 0], ['A', 'A', 'B', 'B'])", 1.0), ("disparate_impact([1, 1, 1, 1, 0, 1, 0, 0], ['A', 'A', 'A', 'A', 'B', 'B', 'B', 'B'])", 0.25), ("disparate_impact([1, 0, 1, 1, 1, 0], ['A', 'A', 'B', 'B', 'C', 'C'])", 0.5)],
         """
def disparate_impact(approve, group):
    totals, yes = {}, {}
    for a, g in zip(approve, group):
        totals[g] = totals.get(g, 0) + 1
        yes[g] = yes.get(g, 0) + a
    rates = [yes[g] / totals[g] for g in totals]
    return round(min(rates) / max(rates), 3)
""", 'Count people and approvals per group in two dictionaries, then divide.', '<p>Taking the lowest over the highest rate works for any number of groups. A result below 0.8 fails the four fifths rule.</p>')

K.must('Global importance', 'Permutation on test data: I = s &minus; mean shuffled score. Impurity importance is computed on training data and favours many valued features.')
K.must('Shapley values', '&phi; averages what a feature adds over every order. Base + &Sigma;&phi; = prediction. 2<sup>|F|</sup> coalitions, so use TreeExplainer or sampling.')
K.must('Explanations', 'Show how the model used a feature, not a cause. They depend on the background data. Counterfactuals give actionable changes.')
K.must('Group metrics', 'Disparate impact = rate B / rate A, flag below 0.8. Equal opportunity: equal TPR. Equalized odds: equal TPR and FPR.')
K.must('Mitigation', 'Pre processing (data), in processing (constrained loss), post processing (group thresholds). Re-measure everything afterwards.')
K.must('Impossibility and documentation', 'Different base rates: calibration and equal error rates conflict. Pick a rule for the harm, write a model card, gate promotion on it.')

T = K.topic(
    slug='mlops-explain-fair', topic='mlops-explain-fair', step=(3, 'Operate and improve', 'mlops-s3', 'Track experiments, register model versions, watch for drift and decay, and explain and audit predictions.', 'Advanced'),
    title='Explainability and fairness', short='Explainability and fairness', badge='3.3', minutes=55,
    lead='Find which features a model really uses with permutation importance, explain single predictions with Shapley values and SHAP, audit a model for fairness by group, fix a gap with group thresholds, install SHAP and Fairlearn on every operating system, and document the result in a model card.',
    desc='Explainability, feature importance, impurity importance, permutation importance, Shapley values, SHAP, TreeExplainer, base value, counterfactual explanations, fairness, demographic parity, disparate impact, four fifths rule, equal opportunity, equalized odds, proxy features, ThresholdOptimizer, Fairlearn, bias mitigation, impossibility theorem, model cards, EU AI Act, GDPR Article 22.',
    summary='Permutation importance, Shapley values and SHAP, fairness metrics by group, mitigation, impossibility results and model cards.',
    keywords=['explainability', 'SHAP', 'Shapley values', 'permutation importance', 'fairness', 'disparate impact', 'equal opportunity', 'Fairlearn', 'model card'],
    recap='<p>Explain what drives a model and each of its decisions, measure how it treats every group, choose a fairness rule for the harm at stake, and ship the evidence in a model card.</p>',
    added='2026-11-14', leet=leet_items())
