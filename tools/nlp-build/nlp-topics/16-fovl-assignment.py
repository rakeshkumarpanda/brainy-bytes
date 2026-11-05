# NLP section, chapter 5.2: the FoVL assignment on multilingual word embeddings for Indian languages, solved.
# The question paper (content/nlp/files/FOVL_assignment.pdf) asks for 300 dimensional embeddings trained from scratch
# on IndicCorpV2 only, evaluated with cosine similarity and Spearman correlation on the word similarity datasets of
# Akhtar et al. (2017) for Gujarati, Hindi, Marathi, Punjabi, Tamil, Telugu and Urdu, with OOV handling, a macro
# average score, a t-SNE plot of 100 words per language and an (N, 2, 300) .npy file per language.
# Every number on this page comes from the executed notebook (content/nlp/files/FOVL_word_embeddings_explained.ipynb):
# gensim FastText skip-gram per language, d = 300, window 8, min_count 1, n-grams 3 to 6, 10 negatives, 20 epochs,
# 100,000 n-gram buckets, one worker thread and seed 42, which makes the run reproducible.
from cvkit import Kit, fx, fxs, frac, scene, note, deep, table, steps, code, eq

K = Kit()

RHO = [('Gujarati', 163, 0.4603), ('Hindi', 235, 0.3226), ('Marathi', 104, 0.3974), ('Punjabi', 143, 0.3488),
       ('Tamil', 97, 0.3020), ('Telugu', 111, 0.2250), ('Urdu', 100, 0.2995)]
MACRO = 0.3365
COV = [('Gujarati', '201,036', '37,541', 221, 23, '89.6%', 23), ('Hindi', '279,852', '24,245', 318, 39, '87.7%', 57),
       ('Marathi', '202,624', '44,206', 337, 66, '80.4%', 70), ('Punjabi', '270,046', '25,454', 206, 22, '89.3%', 25),
       ('Tamil', '166,263', '53,943', 137, 37, '73.0%', 39), ('Telugu', '170,152', '46,596', 160, 48, '70.0%', 52),
       ('Urdu', '357,737', '28,674', 146, 25, '82.9%', 24)]
EXP = [('E1', 'Baseline: skip-gram, window 5, min_count 2, n-grams 3 to 6, 20 epochs', '0.2979'),
       ('E2', 'CBOW in place of skip-gram', '0.1642'),
       ('E3', 'Baseline with 40 epochs', '0.3026'),
       ('E4', 'Baseline with n-grams 2 to 5', '0.2725'),
       ('E5', 'Baseline with window 3', '0.2876'),
       ('E6', 'Baseline with window 8', '0.3041'),
       ('E7', 'Baseline with min_count 1', '0.3156'),
       ('E8', 'min_count 1 with subsampling 1e-4', '0.3179'),
       ('E9', 'min_count 1 with n-grams 3 to 5', '0.3184'),
       ('E10', 'min_count 1 with 5 negative samples', '0.3068'),
       ('E11', 'min_count 1 with seeds 1 and 2 (noise check)', '0.3195 and 0.3129'),
       ('E12', 'min_count 1 and window 8', '0.3314'),
       ('E13', 'min_count 1, window 8, 30 epochs', '0.3320'),
       ('E14', 'min_count 1, window 8, 100,000 n-gram buckets', '0.3335'),
       ('E15', 'One shared model for all 24 languages, Indic scripts mapped to Devanagari', '0.2189'),
       ('E16', 'Baseline plus removing the top 1, 2, 3 or 5 principal directions', '0.2646, 0.2613, 0.2624, 0.2429'),
       ('Final', 'E14 settings with one worker thread (reproducible)', '0.3365')]


def dl(href, kind, title, what):
    return (f'<div class="fv-dl"><div class="fv-dl-i">{kind}</div><div class="fv-dl-t"><b>{title}</b><span>{what}</span></div>'
            f'<a class="fv-dl-a" href="./files/{href}" download>Download {kind}</a></div>')


def solution(body):
    return (f'<details class="fv-sol"><summary><span class="fv-sol-btn">Solution</span>'
            f'<span class="fv-sol-tip">Press to show or hide the full worked solution</span></summary>'
            f'<div class="fv-sol-b">{body}</div></details>')


K.code('ngrams', r'''
# FastText cuts a word into character n-grams with the marks < and >
def ngrams(word, lo, hi):
    s = "<" + word + ">"
    out = []
    for n in range(lo, hi + 1):
        for i in range(len(s) - n + 1):
            out.append(s[i:i + n])
    return out

for w in ["घर", "घरों", "बोर्ड"]:
    g = ngrams(w, 3, 6)
    print(w, len(g), g)

shared = set(ngrams("घर", 3, 6)) & set(ngrams("घरों", 3, 6))
print("pieces shared by घर and घरों:", shared)
''')

K.code('spearman', r'''
# Cosine scores of five test pairs against human scores, then Spearman by hand
human = [8.8, 7.4, 8.2, 3.2, 0.0]
model = [0.725, 0.480, 0.263, 0.726, 0.567]

def ranks(x):
    order = sorted(range(len(x)), key=lambda i: x[i])
    r = [0] * len(x)
    for pos, i in enumerate(order):
        r[i] = pos + 1
    return r

rh, rm = ranks(human), ranks(model)
d2 = sum((a - b) ** 2 for a, b in zip(rh, rm))
n = len(human)
print("human ranks", rh)
print("model ranks", rm)
print("sum d^2 =", d2, " rho =", round(1 - 6 * d2 / (n * (n * n - 1)), 4))
''')

K.code('macro', r'''
# The leaderboard score: the simple mean of the seven Spearman values
rho = {"Gujarati": 0.4603, "Hindi": 0.3226, "Marathi": 0.3974, "Punjabi": 0.3488,
       "Tamil": 0.3020, "Telugu": 0.2250, "Urdu": 0.2995}
macro = sum(rho.values()) / len(rho)
print("macro average =", round(macro, 4))
best = max(rho, key=rho.get)
print("best", best, rho[best], " lowest", min(rho, key=rho.get), min(rho.values()))
''')

rho_rows = [[n, p, f'{r:.4f}'] for n, p, r in RHO] + [['<b>Macro average</b>', '<b>953</b>', f'<b>{MACRO:.4f}</b>']]

SOL = f'''
<h3>Step 0. Read the paper and make a plan</h3>
<p>The paper fixes four hard rules: only IndicCorpV2 for training, exactly 300 dimensions, no pre-trained vectors, and no pair may be dropped because of an unseen word. The test sets of Akhtar et al. (2017) exist for 7 languages, so the models must cover Gujarati, Hindi, Marathi, Punjabi, Tamil, Telugu and Urdu. The plan was: look at the data, pick a model that can build vectors for unseen words, tune it on the public sets, then write the files in the exact submission format.</p>
{table(['Rule in the paper', 'How the solution meets it'], [
    ['Train only on IndicCorpV2', 'Only data.parquet of rony000013/indiccorpV2-5k is read for training'],
    ['Dimension exactly 300', 'vector_size = 300, every saved array ends in 300'],
    ['No pre-trained vectors or outside text', 'Every model starts from random numbers'],
    ['OOV words must get a meaningful vector', 'FastText character n-grams build a vector for any word'],
    ['Report Spearman per language and the macro average', 'Step 8 of the notebook prints all eight numbers'],
    ['Shape (N, 2, 300), original pair order', 'One .npy file per language, checked in the notebook'],
    ['Human scores never used for training', 'They are read only to compute Spearman']])}

<h3>Step 1. Look at the data</h3>
<p>IndicCorpV2-5k holds 118,243 lines in 24 languages, 5,000 lines each (Kashmiri has 3,243). After cleaning, each of our 7 languages has between 166,263 and 357,737 word tokens. That is tiny next to the billions of words used for published embeddings, so every choice below aims at squeezing meaning out of little text.</p>
{note('The Hindi test file is comma separated, the others are tab separated with Windows line ends. In the Marathi file 149 of the 253 pairs have no human score. They are kept in the .npy file (the paper asks for every pair in order) but Spearman for Marathi uses the 104 scored pairs. The Tamil file has one blank word.', 'warn')}

<h3>Step 2. Clean the text</h3>
<p>Each line is put in Unicode NFC form so that one letter is always stored one way, then every punctuation mark, symbol, separator, digit and ASCII character becomes a space, and the line is split on spaces.</p>
{note('The regular expression <code>\\w</code> looks natural for splitting words, but it does not count the vowel signs of Indian scripts (ा, ि, ो) as word characters. It cut किताब into pieces and gave Hindi only 5,426 word types. Checking the Unicode category of each character gave 24,245 real word types.', 'warn')}

<h3>Step 3. Choose the model: FastText skip-gram</h3>
<p>Word2Vec and GloVe give no vector at all to a word they never saw, and between 10 and 30 percent of the test words never appear in our small corpus. FastText (Bojanowski et al., 2017) learns a vector for every character n-gram as well as for every word, so it can build a vector for any word from its pieces.</p>
{fxs(fx('FastText word vector', 'v<sub>w</sub> = z<sub>w</sub> + ∑<sub>g ∈ G(w)</sub> z<sub>g</sub>', 'G(w) is the set of character n-grams of w with the marks &lt; and &gt;, here n = 3 to 6.', key=True),
     fx('Skip-gram with negative sampling', 'J = −log σ(v<sub>w</sub>·u<sub>c</sub>) − ∑<sub>k=1..K</sub> log σ(−v<sub>w</sub>·u<sub>n<sub>k</sub></sub>)', 'c is a real context word, n<sub>k</sub> are K = 10 random words.'),
     fx('Cosine similarity', 's(w<sub>i</sub>, w<sub>j</sub>) = ' + frac('v<sub>i</sub> · v<sub>j</sub>', '‖v<sub>i</sub>‖ ‖v<sub>j</sub>‖'), '1 means the same direction, 0 means unrelated.'),
     fx('Macro average', 'S<sub>macro</sub> = ' + frac('1', '|L|') + ' ∑<sub>ℓ ∈ L</sub> ρ<sub>ℓ</sub>', 'Each language counts the same, whatever its number of pairs.'))}
{code('ngrams')}

<h3>Step 4. OOV handling</h3>
<p>The function get_vector never drops a word. A word in the vocabulary uses its trained vector. An unseen word gets the sum of its n-gram vectors, which were learned from other words with the same pieces. A test entry with two words, such as कुटुंब नियोजन (family planning), is cleaned like the training text and the word vectors are averaged.</p>
{scene('a word the model never read', '<p>कीबोर्ड (keyboard) does not occur in the 5,000 Hindi lines. Its pieces such as बोर्ड and र्ड&gt; do. FastText adds them up and the nearest words of the new vector are बिलबोर्ड (billboard), डेशबोर्ड (dashboard) and बोर्ड (board). The meaning "some kind of board" survives even though the word itself was never seen.</p>')}

<h3>Step 5. Tune the settings</h3>
<p>Each experiment trained all 7 models and recorded the macro Spearman on the public sets, which the paper allows for development. Runs E1 to E16 used 4 threads, so a rerun moves by about 0.01 (E11). The final model uses 1 thread so the notebook gives the same numbers every time.</p>
{table(['Run', 'Setting', 'Macro ρ'], [list(r) for r in EXP])}
<p>Three lessons came out of the table. Skip-gram beats CBOW by a wide margin, because it gives every rare word its own updates. Keeping every word (min_count 1) and a wider window (8) both help a small corpus. One shared model for all languages, even with every Indic script mapped to Devanagari so that cognates share pieces, was clearly worse, because short pieces mean different things in different languages.</p>

<h3>Step 6. Results on the public benchmark</h3>
{table(['Language', 'Pairs used', 'Spearman ρ'], rho_rows)}
{code('macro')}

<h3>Step 7. Vocabulary coverage and OOV statistics</h3>
{table(['Language', 'Corpus tokens', 'Model vocabulary', 'Test words', 'OOV words', 'Coverage', 'Pairs with an OOV word'], [list(r) for r in COV])}
<p>Telugu and Tamil have the lowest coverage. Both glue many suffixes onto a stem, so one word has many forms and each form is rare in 5,000 lines. They also have the lowest scores, which shows how much the small corpus limits the result.</p>

<h3>Step 8. t-SNE pictures</h3>
<p>The first 100 different test words of each language go from 300 numbers to 2 with t-SNE (perplexity 15, PCA start, random_state 42). Words with the same stem or the same loan word sit together, for example the computer words in Hindi and Punjabi. Some groups share spelling more than meaning, which is the weak side of n-grams. The seven pictures are in the notebook and the report.</p>

<h3>Step 9. Error analysis</h3>
<p>Both scores are turned into ranks between 0 and 1. A small gap between the human rank and the model rank means the model agrees with people.</p>
{table(['Language', 'Pair', 'Meaning', 'Human', 'Cosine', 'Verdict'], [
    ['Hindi', 'कंप्यूटर, सॉफ्टवेयर', 'computer, software', '8.8', '0.725', 'right'],
    ['Tamil', 'மாணவர், பேராசிரியர்', 'student, professor', '8.75', '0.651', 'right'],
    ['Gujarati', 'ડૉક્ટર, નર્સ', 'doctor, nurse', '9.0', '0.614', 'right'],
    ['Urdu', 'یروشلم, اسرائیل', 'Jerusalem, Israel', '9.0', '0.516', 'right'],
    ['Hindi', 'पैसे, बैंक', 'money, bank', '8.2', '0.263', 'too low'],
    ['Punjabi', 'ਕਿਤਾਬ, ਪੇਪਰ', 'book, paper', '8.0', '0.226', 'too low'],
    ['Telugu', 'గ్రహం, స్టార్', 'planet, star', '8.0', '0.197', 'too low'],
    ['Punjabi', 'ਲੋਬਸਟਰ, ਵਾਈਨ', 'lobster, wine', '1.0', '0.586', 'too high'],
    ['Marathi', 'अराफात, जॅक्सन', 'Arafat, Jackson', '0.0', '0.724', 'too high'],
    ['Tamil', 'சகோதரர், துறவி', 'brother, monk', '1.125', '0.810', 'too high']])}
<p>Pairs that occur together in news text are scored well. Pairs that people link through world knowledge (money and bank, planet and star) rarely share a sentence in 5,000 lines, so they come out too low. Two unseen loan words or names (lobster and wine, Arafat and Jackson) are built only from transliterated pieces that look alike, so they come out too high.</p>
{code('spearman')}

<h3>Step 10. The submission files</h3>
{table(['File', 'What it holds'], [
    ['&lt;Language&gt;-WS-embeddings.npy', 'float32 array (N, 2, 300) in the original pair order'],
    ['&lt;Language&gt;-vocabulary.txt and &lt;Language&gt;-vocab-embeddings.npy', 'every test word with its index, and its vector in the same row'],
    ['&lt;Language&gt;-fasttext.model plus its .npy parts', 'the trained model, needed to embed new and OOV words in the private test (about 1.4 GB for all 7)'],
    ['FOVL_word_embeddings.ipynb', 'the code, including embed_file for any new pair file'],
    ['Report PDF', 'sections 1 to 8 as the paper asks']])}

<h3>Step 11. Limitations</h3>
<ul>
<li>5,000 lines per language is the main limit. A larger slice of IndicCorpV2 would raise every score.</li>
<li>The test sets have only 97 to 235 pairs, so one pair can move Spearman noticeably, and the private test may differ.</li>
<li>N-gram vectors capture spelling as well as meaning, which misleads on names and loan words.</li>
<li>Choosing settings on the public sets can overfit them a little. The settings are general (window, min_count) rather than fitted per pair, which limits that risk.</li>
</ul>
'''

K.lesson('paper', 'The question paper', f'''
<p>This chapter is the FoVL assignment on word embeddings for Indian languages, with a complete worked solution. Download the question paper first and read it once.</p>
{dl('FOVL_assignment.pdf', 'PDF', 'FOVL assignment question paper', 'Objective, training data, tasks, scoring and what to submit.')}
<h3>The question in short</h3>
{table(['Part', 'What the paper asks'], [
    ['Objective', 'Train word embeddings that capture meaning in Indian languages'],
    ['Training data', 'Only IndicCorpV2 (the 5,000 line per language subset on Hugging Face)'],
    ['Model', 'Any model, such as GloVe, Word2Vec or FastText, trained from scratch, dimension exactly 300'],
    ['Evaluation', 'Word similarity datasets of Akhtar et al. (2017): cosine similarity, then Spearman per language'],
    ['OOV', 'Unseen words must still get a meaningful vector. Dropping pairs is not allowed'],
    ['Score', 'Macro average of Spearman over all evaluated languages, final ranking on a private test'],
    ['Submit', '(N, 2, 300) .npy per language, vocabulary file, PDF report, one .ipynb that can embed any word']])}
{note('The public word similarity sets cover Gujarati, Hindi, Marathi, Punjabi, Tamil, Telugu and Urdu, so these are the 7 languages every model must cover.', 'exam')}
''', kw=['FOVL assignment', 'question paper', 'IndicCorpV2', 'word similarity', 'Indian languages'])

K.lesson('solution', 'The worked solution', f'''
<p>The full solution follows the order in which the work was done: plan, data, cleaning, model, OOV handling, tuning, results, coverage, pictures, error analysis, files and limits. Press the button to open it.</p>
<p>Final answer: one FastText skip-gram model per language, 300 dimensions, with a macro average Spearman of <b>{MACRO:.4f}</b> on the public sets.</p>
{solution(SOL)}
''', kw=['solution', 'FastText', 'OOV', 'Spearman', 'macro average', 't-SNE', 'error analysis'])

K.lesson('notebook', 'The notebook', f'''
<p>The notebook below runs the whole solution from the raw files to the submission files. Every code cell has a note above it that says what the step does, why it is needed and how the code does it. It already holds the outputs of a full run.</p>
{dl('FOVL_word_embeddings_explained.ipynb', 'ipynb', 'FOVL word embeddings, explained notebook', 'Twelve steps from loading IndicCorpV2 to the files for the private test.')}
{table(['Step', 'What happens'], [
    ['1 and 2', 'Load IndicCorpV2 and clean every line into words'],
    ['3', 'Load the 7 word similarity files'],
    ['4 and 5', 'Train and save one FastText model per language'],
    ['6', 'get_vector for any word, including OOV words'],
    ['7', 'Coverage and OOV statistics'],
    ['8', 'Cosine, Spearman per language and the macro average'],
    ['9', 'Save the (N, 2, 300) arrays and the vocabulary files'],
    ['10', 't-SNE of 100 words per language'],
    ['11', 'Right and wrong pairs'],
    ['12', 'embed_file for the private test']])}
{note('Put fovl_data/data.parquet and the folder Word-Similarity-Datasets-for-Indian-Languages next to the notebook. Training uses one thread on purpose so the numbers match the report, and takes about 35 minutes on a laptop.', 'tip')}
''', kw=['notebook', 'ipynb', 'download', 'gensim'])

# ---------------------------------------------------------------- quiz
K.quiz('e', 'Which words must still get a vector under the assignment rules?', ['only words in the corpus', 'every test word, including words never seen in training', 'only words with a human score', 'only Hindi words'], 1, 'OOV handling.', 'Dropping pairs with unseen words is not allowed.')
K.quiz('e', 'The saved array for a language with N pairs has shape', ['(N, 300)', '(2, N, 300)', '(N, 2, 300)', '(300, N)'], 2, 'Pairs, two words, dimension.', 'N pairs, 2 words per pair, 300 numbers per word.')
K.quiz('e', 'The leaderboard score is', ['the Spearman of the largest language', 'the mean Spearman over the languages', 'the cosine of all pairs', 'the number of OOV words'], 1, 'Macro.', 'Each language counts the same.')
K.quiz('m', 'Why FastText instead of Word2Vec here?', ['it trains faster', 'it builds vectors for unseen words from character n-grams', 'it needs no corpus', 'it is pre-trained'], 1, 'Subwords.', 'Word2Vec has no vector for an unseen word.')
K.quiz('m', 'What went wrong when words were split with the regex <code>\\w</code>?', ['nothing', 'vowel signs were treated as breaks, so words were cut into pieces', 'Urdu was removed', 'numbers were kept'], 1, 'Matras.', 'Hindi dropped to 5,426 fake word types.')
K.quiz('m', 'Which change lowered the macro score to 0.219?', ['window 8', 'min_count 1', 'one shared model for all 24 languages', '100,000 buckets'], 2, 'Experiment E15.', 'Pieces mean different things in different languages.')
K.quiz('m', 'CBOW against skip-gram on this small corpus', ['CBOW was much better', 'about the same', 'skip-gram was much better', 'CBOW could not train'], 2, '0.30 against 0.16.', 'Skip-gram gives rare words more updates.')
K.quiz('h', 'Why can lobster and wine get a high cosine in Punjabi?', ['they co-occur often', 'both are unseen loan words built from similar transliterated pieces', 'the human score is high', 'they are the same word'], 1, 'OOV vectors.', 'Their n-grams look alike.')
K.quiz('h', 'How were the Marathi pairs without a human score handled?', ['deleted', 'given a score of 0', 'kept in the .npy file but left out of Spearman', 'filled with the mean score'], 2, 'Order must be kept.', 'Spearman needs a human score.')
K.quiz('h', 'Why train the final model with one worker thread?', ['it is faster', 'it makes the run reproducible', 'gensim needs it', 'it raises the score'], 1, 'The paper asks for reproducible results.', 'Several threads change the update order.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'Hindi has 235 pairs. How many float32 numbers are in its (N, 2, 300) array?', '141000', 'N × 2 × 300.',
       ['N = 235.', '235 × 2 = 470.', eq('470 × 300 = 141,000')], check=141000, tol=0.5)
K.calc('e', 'How many character n-grams of length 3 to 6 does the 2 letter word घर have with boundary marks?', '3', 'The marked word is 4 characters.',
       ['&lt;घर&gt; has 4 characters.', 'n = 3: 2, n = 4: 1, n = 5 and 6: none.', eq('2 + 1 = 3')], check=3, tol=1e-9)
K.calc('m', 'Macro average of the seven Spearman values 0.4603, 0.3226, 0.3974, 0.3488, 0.3020, 0.2250 and 0.2995 (four decimals).', '0.3365', 'Sum, then divide by 7.',
       ['Sum = 2.3556.', 'Divide by 7.', eq('0.3365')], check=2.3556 / 7, tol=5e-5)
K.calc('m', 'Telugu has 160 test words and 48 are OOV. Coverage in percent.', '70', '(160 − 48) ÷ 160.',
       ['160 − 48 = 112.', '112 ÷ 160 = 0.7.', eq('70 percent')], check=70, tol=1e-9)
K.calc('m', 'Human ranks 1, 2, 3, 4, 5 and model ranks 4, 3, 1, 5, 2 for five pairs. Spearman ρ.', '-0.2', '1 − 6∑d² ÷ n(n² − 1).',
       ['d = (−3, −1, 2, −1, 3), so ∑d² = 9 + 1 + 4 + 1 + 9 = 24.', 'n(n² − 1) = 5 × 24 = 120.', eq('ρ = 1 − 144 ÷ 120 = −0.2')], check=-0.2, tol=1e-9)
K.calc('h', 'Vectors a = (1, 2, 2) and b = (2, 1, 2). Cosine similarity (four decimals).', '0.8889', 'Dot product over lengths.',
       ['a · b = 2 + 2 + 4 = 8.', '‖a‖ = ‖b‖ = 3.', eq('8 ÷ 9 = 0.8889')], check=8 / 9, tol=5e-5)
K.calc('h', 'An n-gram table of 100,000 buckets with 300 float32 numbers each. Size in MB (10<sup>6</sup> bytes).', '120', '4 bytes per float32.',
       ['100,000 × 300 = 30,000,000 numbers.', 'Times 4 bytes.', eq('120,000,000 bytes = 120 MB')], check=120, tol=1e-9)

T = K.topic(
    slug='fovl-assignment', topic='nn-fovl-assignment', kind='revision',
    step=(5, 'Exam revision', 'nn-revision', 'Revise the neural NLP section by exam style, from school questions to IIT numericals, MCQ and MSQ papers with negative marking, and MIT and Cambridge style derivations.', 'All levels'),
    title='FoVL assignment: word embeddings for Indian languages', short='FoVL assignment solved', badge='5.2', minutes=45, added='2026-11-05',
    lead='The FoVL assignment on multilingual word embeddings, solved: download the question paper, open the worked solution, and download the explained notebook.',
    desc='Question paper download, the worked solution behind a Solution button (FastText skip-gram per language on IndicCorpV2, OOV handling with character n-grams, cosine and Spearman on the Akhtar et al. 2017 sets, 16 experiments, coverage, t-SNE and error analysis) and a notebook with what, why and how for every step.',
    summary='The FoVL word embedding assignment for 7 Indian languages with the question paper, a full worked solution and an explained notebook.',
    keywords=['FOVL assignment', 'word embeddings', 'FastText', 'IndicCorpV2', 'OOV', 'Spearman', 'Indian languages', 'Hindi', 'Tamil', 'Urdu'],
    recap='')
