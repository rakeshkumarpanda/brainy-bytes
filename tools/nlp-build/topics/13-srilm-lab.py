# Chapter 4.4: the SRILM toolkit and assignment 2. Source: lecture 8 (slides 78 to 85: the SRILM workflow, the count
# file and the ARPA file of the toy corpus, reading the -debug 2 output, the default Good-Turing and Katz smoothing,
# in-class activity 2 on the Brown corpus) and the submitted answers of assignment 2 (unk and addsmooth, five
# smoothing methods as bigram and trigram, punctuation and stop word removal, the search over k and lambda).
from cvkit import Kit, fx, fxs, frac, ladder, scene, note, deep, table, steps, code, viz, eq

K = Kit()

K.code('arpa', r'''
# Write the unigram part of an ARPA file by hand for the toy corpus (no smoothing)
from collections import Counter
from math import log10
corpus = ["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"]
c = Counter(w for line in corpus for w in line.split() + ["</s>"])
N = sum(c.values())

print("\\data\\")
print("ngram 1=" + str(len(c) + 2))           # + <s> and <unk>
print()
print("\\1-grams:")
print("-99\t<s>")                              # never predicted, so log 0
for w, n in sorted(c.items()):
    print(f"{log10(n / N):.7f}\t{w}")
print("-99\t<unk>")                            # count 0 without -addsmooth
''')

K.code('debug', r'''
# Read the per word lines of "ngram -ppl test.txt -debug 2" and add them up again
out = """p( Sam | <s> ) = [2gram] 0.6 [ -0.221849 ]
p( I | Sam ) = [2gram] 0.6 [ -0.221849 ]
p( do | I ) = [2gram] 0.2 [ -0.69897 ]
p( I | do ) = [2gram] 0.5 [ -0.30103 ]
p( like | I ) = [2gram] 0.4 [ -0.39794 ]
p( </s> | like ) = [2gram] 0.666667 [ -0.176091 ]"""

total = 0.0
for line in out.splitlines():
    total += float(line.split("[")[-1].split("]")[0])
words = 5
print("logprob =", round(total, 5))
print("ppl =", round(10 ** (-total / (words + 1)), 5), " ppl1 =", round(10 ** (-total / words), 5))
''')

K.code('compare', r'''
# Assignment 2: rank the five smoothing methods by bigram and trigram perplexity
rows = {"addsmooth 1": (2493.24, 3620.71), "absolute discounting": (391.85, 384.91),
        "Good-Turing": (642.33, 629.24), "Witten-Bell": (396.83, 385.06), "Kneser-Ney": (352.45, 340.18)}

for name, (bi, tri) in sorted(rows.items(), key=lambda kv: kv[1][0]):
    change = 100 * (tri - bi) / bi
    print(f"{name:22s} bigram {bi:8.2f}  trigram {tri:8.2f}  change {change:+.1f}%")
''')

K.lesson('workflow', 'SRILM in three commands', f'''
<p>SRILM, the SRI Language Modeling toolkit, is a set of C++ libraries and command line programs for building and applying statistical language models. It has been used for speech recognition, tagging, segmentation and machine translation. The lecture used it to check every hand calculation of the activity.</p>
{table(['Step', 'Command', 'What it does'], [
    ['1. Count', '<code>ngram-count -text train.txt -order 2 -write train.count</code>', 'Writes every n-gram with its count'],
    ['2. Estimate', '<code>ngram-count -text train.txt -order 2 -lm train.lm -addsmooth 0</code>', 'Turns counts into probabilities and backoff weights, saved as an ARPA file'],
    ['3. Test', '<code>ngram -lm train.lm -ppl test.txt -debug 2</code>', 'Prints each word\'s probability, then logprob, ppl and ppl1']])}
<p>The training file has one sentence per line and no tags. The toolkit adds &lt;s&gt; and &lt;/s&gt; to every line itself. Add <code>-unk</code> to both commands to keep an &lt;unk&gt; token and map unknown test words to it.</p>
<h3>The count file and the ARPA file</h3>
<p>The count file lists one n-gram per line with its count: &lt;s&gt; 5, &lt;s&gt; Sam 3, I 5, I am 2, the same numbers as chapter 4.1. The ARPA file, a format named after DARPA, starts with a header such as "ngram 1=8, ngram 2=14": 8 unigram entries including &lt;s&gt; and &lt;unk&gt;, and 14 different bigrams. Then each line holds a log₁₀ probability, the n-gram, and for lower orders a log₁₀ backoff weight.</p>
{table(['ARPA value', 'Check by hand'], [
    ['−0.6434527 for I, Sam and &lt;/s&gt;', 'log₁₀(5/22)'],
    ['−1.041393 for am and do', 'log₁₀(2/22)'],
    ['−0.8653014 for like', 'log₁₀(3/22)'],
    ['−0.2218488 for &lt;s&gt; Sam and Sam I', 'log₁₀(3/5)'],
    ['−0.1760913 for like &lt;/s&gt;', 'log₁₀(2/3)'],
    ['−99 for &lt;s&gt;', 'The ARPA stand in for log 0. &lt;s&gt; is never predicted.']])}
{code('arpa')}
<h3>Reading the test output</h3>
<p>For every token SRILM prints <code>p( word | context ) = [2gram] probability [ log10 ]</code>. "[2gram]" means the bigram was found. "[1gram]" would mean it backed off to the unigram. Each sentence ends with two lines: the number of words and OOVs, then zeroprobs, logprob, ppl and ppl1. The last two lines do the same for the whole file.</p>
{viz('ngramlm', test='Sam I do I like\nSam I am', view='srilm')}
{code('debug')}
{fxs(
    fx('Flags for smoothing', '-addsmooth k, &nbsp; -cdiscount d, &nbsp; -wbdiscount, &nbsp; -kndiscount, &nbsp; -interpolate', 'Add-k, absolute discounting, Witten-Bell, Kneser-Ney, and making a method interpolated instead of backoff.'),
    fx('Default', 'no flag = Good-Turing discounting with Katz backoff', 'Heard as "good viewing" in the lecture recording.'))}
{note('If SRILM cannot be installed, NLTK\'s nltk.lm module (MLE, Laplace, KneserNeyInterpolated) reproduces the toy numbers. Check its padding and its token count for perplexity against SRILM\'s ppl and ppl1 before trusting it.', 'tip')}
''', kw=['SRILM', 'ngram-count', 'ngram -ppl', 'debug 2', 'count file', 'ARPA format', 'backoff weight', '-99', 'addsmooth', 'unk flag'])

K.lesson('brown', 'From the toy corpus to the Brown corpus', f'''
<p>In-class activity 2 repeated the toy exercise on a real corpus. The Brown corpus has about one million words of American English published in 1961, spread over 15 genres: news, religion, lore, fiction, romance and others. The professor put it as "one class of text is fiction, another is fact". It is also tagged with parts of speech, which step 5 uses.</p>
<p>The data came split three ways: brown-train, brown-dev and brown-test. The task was to build unigram and bigram models with the commands from the tutorial, test on dev and test, report logprob, ppl, ppl1 and OOVs, then try smoothing. Asked whether Python was needed, the professor said no: the tutorial commands were enough and it was "hardly half an hour of work".</p>
{steps('A sensible order of work', [
    'Count and estimate on brown-train only. Never let dev or test text into the counts.',
    'Run an unsmoothed bigram on dev and read the OOV and zeroprob counts. They will be large.',
    'Add -unk so unknown words are scored, and a smoothing flag so unseen bigrams get probability.',
    'Compare methods and settings on dev. Pick the best.',
    'Run the chosen model once on test and report that number.'])}
{note('The professor asked students to do the coding activities with their own hands and not with a chatbot: "knowing is one thing, doing it with your hand is a different experience". The widgets in this chapter show the results so you can check yours, not replace them.', 'tip')}
''', kw=['Brown corpus', 'in-class activity 2', 'train dev test', 'genres', 'OOV', 'smoothing flags'])

K.lesson('a2', 'Assignment 2, question by question', f'''
<p>This lesson rebuilds the submitted answers of assignment 2 as interactive charts. The numbers are the ones SRILM printed on the Brown data.</p>
<h3>Question 1: why the unknown word breaks the model</h3>
<p>&lt;unk&gt; never appears in the training data. With <code>-addsmooth 0</code> nothing is smoothed, so P(&lt;unk&gt;) = 0 and its log is −∞, and bigrams that need it back off to zero as well. <code>-addsmooth 0</code> means a δ of 0, and <code>-unk</code> keeps an &lt;unk&gt; word in the model and maps OOV test words to it. The fix used was <code>-addsmooth 1 -unk</code>: then log₁₀ P(&lt;unk&gt;) = −5.428, with 0 OOVs and 0 zeroprobs.</p>
<h3>Questions 2 and 3: five ways to smooth</h3>
{viz('srilmtable')}
{table(['SRILM option', 'Bigram ppl', 'Bigram ppl1', 'Trigram ppl', 'Trigram ppl1', 'log₁₀ P(&lt;unk&gt;)'], [
    ['-addsmooth 1', '2493.24', '3600.57', '3620.71', '5321.27', '−5.428'],
    ['Absolute discounting', '391.85', '518.76', '384.91', '509.14', '−1.401'],
    ['Good-Turing', '642.33', '870.35', '629.24', '851.77', '−5.408'],
    ['Witten-Bell', '396.83', '525.66', '385.06', '509.35', '−1.298'],
    ['Kneser-Ney', '352.45', '464.28', '340.18', '447.38', '−0.878']])}
{code('compare')}
<p>Every discounting method beats add-one, and Kneser-Ney is best. A large part of the gap comes from how much probability each method keeps for &lt;unk&gt;: add-one and Good-Turing give it about 10<sup>−5.4</sup>, Kneser-Ney about 10<sup>−0.9</sup>. Moving from bigram to trigram lowers perplexity for the four discounting methods and raises it for add-one.</p>
<h3>Question 4: punctuation and stop words</h3>
{viz('stopwords')}
{table(['Data version', 'Test words', 'Model unigrams', 'ppl', 'ppl1'], [
    ['Original', '305,056', '40,607', '396.83', '525.66'],
    ['Punctuation tokens removed', '268,236', '40,590', '610.78', '859.35'],
    ['Punctuation and stop words removed', '148,503', '40,262', '3,234.52', '7,019.32']])}
<p>Perplexity rises after each removal. Since the vocabulary and token count change, this is a trend and not a strict comparison. Punctuation and stop words are frequent and easy to predict, so they pull the average down. Without them only the harder content words remain, words that were never neighbours become adjacent, and the bigram context weakens.</p>
<h3>Question 5: tuning k and λ together</h3>
{viz('addkgrid')}
{table(['-addsmooth k', '1', '0.1', '0.01', '0.001', '0.0001'], [['Best λ', '0.3', '0.6', '0.7', '0.7', '0.6'], ['Dev ppl', '1123.66', '833.51', '656.01', '581.03', '582.25']])}
<p>The minimum is k = 0.001 with λ = 0.7 and dev ppl 581.03. On the unseen test set this model gives ppl 681.35 and ppl1 925.77. The same two components alone gave 963.11 for the bigram and 1362.51 for the unigram. Kneser-Ney still did better than the tuned mixture.</p>
{scene('choosing a model for a support chatbot', '<p>A team must pick a language model to rank reply suggestions. They follow the assignment\'s recipe: train on old tickets, tune on last month\'s tickets, test once on this week\'s. They also keep the tokenisation fixed across all candidates, because the stop word experiment showed how much perplexity moves when the vocabulary changes.</p>')}
{ladder(
    '<p>A toolkit does the counting and the arithmetic, and you check that its numbers match what you can do by hand on a small example.</p>',
    '<p>ngram-count builds counts and an ARPA model, ngram -ppl scores text. Read OOVs and zeroprobs before trusting a ppl. On Brown, Kneser-Ney beats Witten-Bell, absolute discounting, Good-Turing and add-one.</p>',
    '<p>ARPA stores log₁₀ probabilities and backoff weights so that any n-gram probability is a short look up. The best method depends on how it shares mass with unseen events, which is visible in log P(&lt;unk&gt;). Grid search over k and λ is model selection on held out data.</p>',
    '<p>Modern toolkits such as KenLM build modified Kneser-Ney models over billions of words with quantised tries. n-gram models are still used as fast first pass scorers, for data filtering, and as baselines when measuring how much a neural model really gains.</p>')}
''', kw=['assignment 2', 'Brown', 'Kneser-Ney', 'Witten-Bell', 'Good-Turing', 'absolute discounting', 'stop words', 'punctuation', 'k and lambda search', 'unk probability'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which SRILM program scores a test file?', ['ngram-count', 'ngram', 'arpa', 'srilm-test'], 1,
       'ngram-count builds, the other applies.', 'ngram -lm model -ppl test.txt prints logprob, ppl and ppl1.')
K.quiz('e', 'Does the SRILM training file need &lt;s&gt; and &lt;/s&gt; tags?', ['Yes, on every line', 'No, the toolkit adds them', 'Only &lt;/s&gt;', 'Only for trigrams'], 1,
       'One sentence per line.', 'SRILM adds the tags to each line itself.')
K.quiz('e', 'What does −99 mean in an ARPA file?', ['A probability of 0.99', 'log 0, a probability of 0', 'An error', 'A count of 99'], 1,
       'It stands in for −∞.', 'For example P(&lt;s&gt;) = 0 because &lt;s&gt; is never predicted.')
K.quiz('e', 'Without any smoothing flag, SRILM uses', ['Add-one', 'Kneser-Ney', 'Good-Turing discounting with Katz backoff', 'No smoothing'], 2,
       'The default.', 'Good-Turing with Katz backoff is the default.')
K.quiz('m', 'In the -debug 2 output, "[1gram]" next to a bigram query means', ['The bigram was found', 'The model backed off to the unigram', 'The word is OOV', 'The probability is 1'], 1,
       'Which order answered.', '[2gram] means the bigram was found, [1gram] that it backed off.')
K.quiz('m', 'Why did -addsmooth 0 give −∞ for the Brown test?', ['The file was empty', '&lt;unk&gt; had count 0 and nothing was smoothed', 'Trigrams were missing', 'ppl1 was used'], 1,
       'Question 1.', 'Without smoothing an unseen token has probability 0.')
K.quiz('m', 'Which method gave the lowest bigram perplexity in assignment 2?', ['Witten-Bell', 'Absolute discounting', 'Kneser-Ney', 'Good-Turing'], 2,
       '352.45.', 'Kneser-Ney beat all the others, as Chen and Goodman found.')
K.quiz('m', 'Removing stop words raised perplexity from 396.83 to 3234.52. The safest conclusion is', ['The model got worse', 'The task got harder and the vocabulary changed, so it is a trend, not a fair comparison', 'Stop words are noise', 'SRILM failed'], 1,
       'Same vocabulary rule.', 'Different token sets make perplexities incomparable in the strict sense.')
K.quiz('h', 'Going from bigram to trigram, add-one perplexity rose from 2493 to 3621. Why?', ['Trigrams are always worse', 'Add-one spreads mass over far more unseen trigram histories', 'The test set changed', 'Underflow'], 1,
       'kV per history.', 'Each trigram history gets kV extra counts, so seen trigrams lose even more.')
K.quiz('h', 'Which number best explains why Kneser-Ney and Witten-Bell beat Good-Turing here?', ['The ARPA header', 'log₁₀ P(&lt;unk&gt;)', 'The number of genres', 'The order'], 1,
       'Look at the last column.', 'They keep far more probability for unknown words, and the test set has many.')
K.quiz('h', 'In question 5 the dev ppl was 581.03 but the test ppl 681.35. This is', ['A bug', 'Expected: the settings were chosen on dev, so the dev number is optimistic', 'Proof of overfitting to test', 'Caused by ppl1'], 1,
       'Selection bias.', 'The choice was made with dev, so dev looks better than unseen data.')
K.quiz('x', 'The ARPA header says ngram 1=8 for a six token vocabulary. The two extra entries are', ['Two typos', '&lt;s&gt; and &lt;unk&gt;', 'Two bigrams', '&lt;/s&gt; twice'], 1,
       'One is never predicted, one has count 0.', 'Both appear with −99 when nothing is smoothed.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Check the ARPA entry for like: log₁₀(3/22)? Seven decimals.', '−0.8653014', 'like occurs 3 times in N = 22.',
       ['P(like) = 3/22 = 0.136364.', 'log₁₀ 3 = 0.4771213, log₁₀ 22 = 1.3424227.', eq('0.4771213 − 1.3424227 = −0.8653014')], check=-0.8653014, tol=0.0000005)
K.calc('e', 'An SRILM line shows [ −0.69897 ]. What is the probability? One decimal.', '0.2', '10 to the power of the value.',
       ['SRILM prints log₁₀ p.', 'p = 10<sup>−0.69897</sup>.', eq('p = 0.2 = 1/5')], check=0.2, tol=0.0005)
K.calc('e', 'Kneser-Ney bigram ppl on Brown is 352.45. How many bits per word is that? Two decimals.', '8.46', 'log₂ PP.',
       ['Bits per word = log₂ PP.', 'ln 352.45 = 5.865, ln 2 = 0.693.', eq('log₂ 352.45 = 8.46 bits')], check=8.461298, tol=0.005)
K.calc('m', 'How many times higher is the add-one bigram ppl (2493.24) than Kneser-Ney (352.45)? Two decimals.', '7.07', 'Divide.',
       ['2493.24 ÷ 352.45.', '352.45 × 7 = 2467.15, leaving 26.09.', eq('Ratio ≈ 7.07')], check=2493.24 / 352.45, tol=0.005)
K.calc('m', 'Kneser-Ney: by what percentage does trigram ppl (340.18) improve on bigram (352.45)? Two decimals.', '3.48', '(old − new) ÷ old × 100.',
       ['Difference 352.45 − 340.18 = 12.27.', '12.27 ÷ 352.45 = 0.03481.', eq('About 3.48% lower')], check=100 * 12.27 / 352.45, tol=0.005)
K.calc('m', 'What probability does Kneser-Ney give &lt;unk&gt; if log₁₀ P = −0.878? Three decimals.', '0.132', '10<sup>−0.878</sup>.',
       ['p = 10<sup>−0.878</sup>.', '10<sup>0.122</sup> = 1.324, so p = 1.324 ÷ 10.', eq('p ≈ 0.132')], check=10 ** -0.878, tol=0.0005)
K.calc('m', 'How many orders of magnitude more does Kneser-Ney give &lt;unk&gt; than add-one (log₁₀ −5.428)? Three decimals.', '4.55', 'Subtract the logs.',
       ['Kneser-Ney: −0.878. Add-one: −5.428.', 'The ratio of probabilities is 10 to the difference of the logs.', eq('−0.878 − (−5.428) = 4.55 orders of magnitude')], check=4.55, tol=0.0005)
K.calc('h', 'Removing stop words cut test words from 268,236 to 148,503. What percentage of tokens were stop words? One decimal.', '44.6', '(before − after) ÷ before.',
       ['Removed 268,236 − 148,503 = 119,733 tokens.', '119,733 ÷ 268,236 = 0.4464.', eq('About 44.6% of the tokens')], check=100 * 119733 / 268236, tol=0.05)
K.calc('h', 'The tuned mixture scored dev ppl 581.03 and test ppl 681.35. By what percentage is test higher? One decimal.', '17.3', '(681.35 − 581.03) ÷ 581.03.',
       ['Difference 100.32.', '100.32 ÷ 581.03 = 0.1727.', eq('About 17.3% higher on unseen text')], check=100 * 100.32 / 581.03, tol=0.05)
K.calc('h', 'SRILM line: logprob = −4.23070 for 5 words, 0 OOVs, 1 sentence. What is ppl1? Four decimals.', '7.0168', 'ppl1 divides by the 5 words only.',
       ['ppl uses 5 + 1 = 6 tokens: 10<sup>4.2307/6</sup> = 10<sup>0.70512</sup>.', 'ppl1 uses 5: 10<sup>0.84614</sup>.', eq('ppl1 = 7.0168, against ppl = 5.0713')], check=10 ** (4.2307 / 5), tol=0.0005)
K.calc('x', 'A file has 2 sentences, 8 words, 1 OOV and logprob −3.0. What is ppl? Four decimals.', '2.1544', 'Tokens = words − OOVs + sentences.',
       ['Tokens counted: 8 − 1 + 2 = 9.', 'Exponent: 3.0 ÷ 9 = 0.3333.', eq('ppl = 10<sup>0.3333</sup> = 2.1544')], check=10 ** (3 / 9), tol=0.0005)

# ---------------------------------------------------------------- assignments
K.assign('parse', 'e', 'Read an SRILM result line',
         '<p>Write <code>parse_line(s)</code> for a line such as <code>0 zeroprobs, logprob= -2.01773 ppl= 2.16914 ppl1= 2.53248</code>. Return a dict with the keys zeroprobs (int), logprob, ppl and ppl1 (floats).</p>',
         '''
def parse_line(s):
    # your code here
    pass
''', [('parse_line("0 zeroprobs, logprob= -2.01773 ppl= 2.16914 ppl1= 2.53248")', {'zeroprobs': 0, 'logprob': -2.01773, 'ppl': 2.16914, 'ppl1': 2.53248}),
      ('parse_line("2 zeroprobs, logprob= -1.4437 ppl= 2.29571 ppl1= 3.02853")["zeroprobs"]', 2)],
         '''
def parse_line(s):
    t = s.replace(",", "").split()
    return {"zeroprobs": int(t[0]), "logprob": float(t[3]), "ppl": float(t[5]), "ppl1": float(t[7])}
''', 'Remove the comma, split on spaces, and pick the tokens after each "name=".', '<p>Scripts like this are how a whole grid of SRILM runs, as in question 5, is turned into a table.</p>')
K.assign('arpa', 'm', 'The unigram section of an ARPA file',
         '<p>Write <code>arpa_unigrams(corpus)</code> that returns a dict from token to its log₁₀ MLE probability rounded to 7 decimals, for every word and &lt;/s&gt;, plus "&lt;s&gt;" and "&lt;unk&gt;" mapped to -99.</p>',
         '''
from math import log10

def arpa_unigrams(corpus):
    # your code here
    pass
''', [('arpa_unigrams(["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"])["I"]', -0.6434527),
      ('arpa_unigrams(["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"])["like"]', -0.8653014),
      ('arpa_unigrams(["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"])["<s>"]', -99),
      ('len(arpa_unigrams(["I am Sam", "Sam I am", "Sam I like", "Sam I do like", "do I like Sam"]))', 8)],
         '''
from collections import Counter
from math import log10

def arpa_unigrams(corpus):
    c = Counter(w for line in corpus for w in line.split() + ["</s>"])
    N = sum(c.values())
    out = {w: round(log10(n / N), 7) for w, n in c.items()}
    out["<s>"] = -99
    out["<unk>"] = -99
    return out
''', 'N counts the words and one &lt;/s&gt; per line.', '<p>The length 8 matches the header "ngram 1=8" of the toy model.</p>')
K.assign('best', 'm', 'Pick the method on dev, report on test',
         '<p>Write <code>choose(dev, test)</code>. Both are dicts from method name to perplexity. Return a pair (name, test perplexity) where the name has the lowest dev perplexity. Never look at test to choose.</p>',
         '''
def choose(dev, test):
    # your code here
    pass
''', [('choose({"wb": 400, "kn": 350, "gt": 640}, {"wb": 390, "kn": 360, "gt": 600})', ('kn', 360)),
      ('choose({"a": 10, "b": 12}, {"a": 30, "b": 5})', ('a', 30))],
         '''
def choose(dev, test):
    name = min(dev, key=dev.get)
    return (name, test[name])
''', 'min with a key function finds the best dev entry.', '<p>The second test is the trap: b looks far better on test, but choosing it would be tuning on the test set.</p>')

K.must('Workflow', 'ngram-count -write (counts), ngram-count -lm (model), ngram -lm -ppl -debug 2 (scores). Add -unk to map unknown words.')
K.must('ARPA', 'log₁₀ probabilities and backoff weights. −99 = log 0. Toy header ngram 1=8, ngram 2=14. log₁₀(5/22) = −0.6434527.')
K.must('Default smoothing', 'Good-Turing with Katz backoff. Flags: -addsmooth k, -cdiscount, -wbdiscount, -kndiscount, -interpolate.')
K.must('Brown results', 'Bigram ppl: add-one 2493, GT 642, WB 397, absolute 392, KN 352. Trigram lowers all except add-one.')
K.must('Stop words and tuning', 'Removing punctuation and stop words raises ppl (397, 611, 3235), a trend only. Best k 0.001, λ 0.7, dev 581, test 681.')

T = K.topic(
    slug='srilm-lab', topic='srilm', step=(4, 'Language models', 'nlp-lm', 'Predict the next word with n-gram models, measure them with perplexity, smooth away the zeros and run the SRILM assignment.', 'College and masters'),
    title='The SRILM toolkit and assignment 2', short='SRILM and assignment 2', badge='4.4', minutes=40,
    lead='Match the toolkit to the hand calculation, read its count file, ARPA file and test output, and explore the Brown corpus results of assignment 2.',
    desc='The three SRILM commands, the count file and ARPA format of the toy model, reading the -debug 2 output, the default smoothing and its flags, in-class activity 2 on the Brown corpus, and assignment 2 rebuilt as charts: the unknown word problem, five smoothing methods as bigram and trigram, punctuation and stop word removal, and the joint search over k and λ.',
    summary='SRILM commands, count and ARPA files, test output, and the Brown corpus results of assignment 2.',
    keywords=['SRILM', 'ARPA', 'ngram-count', 'Brown corpus', 'assignment 2', 'Kneser-Ney', 'stop words', 'lambda search'],
    recap='<p>SRILM counts, estimates and scores in three commands, and every number it prints can be checked by hand on a small corpus. On the Brown corpus the discounting methods beat add-one by a factor of 4 to 7, with Kneser-Ney best, and settings must be chosen on dev before a single run on test.</p>')
