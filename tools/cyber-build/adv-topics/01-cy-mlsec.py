# Advanced 1.1: machine learning for security. Checked against Denning, "An Intrusion-Detection Model" (IEEE TSE
# 1987), Graham, "A Plan for Spam" (2002), Axelsson, "The Base-Rate Fallacy and the Difficulty of Intrusion
# Detection" (ACM CCS 1999, TISSEC 2000), McHugh's critique of the DARPA and KDD Cup 99 data (2000), Tavallaee et al.
# on NSL-KDD (2009), Sommer and Paxson, "Outside the Closed World" (IEEE S&P 2010), Liu, Ting and Zhou, "Isolation
# Forest" (ICDM 2008), Iglewicz and Hoaglin on the modified z score (1993), Anderson and Roth, the EMBER dataset (2018),
# the Google blog on TensorFlow in Gmail (February 2019), APWG phishing activity trends reports (2017 to 2021), and
# Lundberg and Lee on SHAP (NeurIPS 2017).
import math

from cvkit import Kit, fx, fxs, ladder, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow
from cykit import talk

chapter('cy-mlsec')
K = Kit()

K.code('spam_bayes', r'''
# Naive Bayes phishing filter, the idea behind Paul Graham's "A Plan for Spam" (2002)
import math

train = [
    ("verify your account password now", "phish"),
    ("urgent your account is suspended click here", "phish"),
    ("click here to claim your prize now", "phish"),
    ("update payment details urgent", "phish"),
    ("meeting moved to friday afternoon", "ham"),
    ("lunch tomorrow with the team", "ham"),
    ("here are the notes from the meeting", "ham"),
    ("your payment receipt for the course", "ham"),
]

counts = {"phish": {}, "ham": {}}
docs = {"phish": 0, "ham": 0}
for text, label in train:
    docs[label] += 1
    for w in text.split():
        counts[label][w] = counts[label].get(w, 0) + 1
vocab = set(counts["phish"]) | set(counts["ham"])
total = {c: sum(counts[c].values()) for c in counts}

def word_prob(w, c):
    # Laplace smoothing: add 1 so an unseen word never gives probability 0
    return (counts[c].get(w, 0) + 1) / (total[c] + len(vocab))

def log_odds(text):
    score = math.log(docs["phish"] / docs["ham"])
    for w in text.split():
        if w in vocab:
            score += math.log(word_prob(w, "phish") / word_prob(w, "ham"))
    return score

for msg in ["urgent verify your password", "notes from friday meeting", "your course payment receipt"]:
    s = log_odds(msg)
    p = 1 / (1 + math.exp(-s))
    print(f"{msg:30} log odds {s:6.2f}  P(phish) = {p:.3f}  {'PHISH' if p > 0.5 else 'ok'}")
print("\nvocabulary size:", len(vocab), " words in phish:", total["phish"], " words in ham:", total["ham"])
''')

K.code('url_features', r'''
# Phishing URL detector: hand made features plus logistic regression trained by gradient descent
import math

def entropy(s):
    """Shannon entropy in bits per character: random looking strings score high."""
    n = len(s)
    return -sum(s.count(ch) / n * math.log2(s.count(ch) / n) for ch in set(s))

def features(url):
    host = url.split("//")[-1].split("/")[0]
    return [
        len(url) / 50,                                # long URLs hide the real domain
        host.count(".") / 3,                          # many subdomains: paypal.com.secure-login.xyz
        1.0 if "@" in url or "-" in host else 0.0,    # tricks that confuse readers
        0.0 if url.startswith("https") else 1.0,      # no TLS
        sum(ch.isdigit() for ch in host) / 5,         # digits in the host name
        entropy(host) / 4,                            # random looking host
    ]

data = [
    ("https://www.google.com", 0), ("https://github.com/login", 0), ("https://mail.yahoo.com", 0),
    ("https://www.irctc.co.in", 0), ("https://en.wikipedia.org/wiki/Cat", 0), ("https://www.sbi.co.in", 0),
    ("http://paypal.com.secure-login.xq7z.top/verify", 1), ("http://192.168.10.5/bank/login", 1),
    ("http://sbi-kyc-update.in-pay.net/form", 1), ("http://amaz0n-prize.win@evil.io/claim", 1),
    ("http://login.micr0soft.verify-acc.ru", 1), ("http://x9k2q7.top/apple-id", 1),
]

w, b, lr = [0.0] * 6, 0.0, 0.5
for epoch in range(300):
    for url, y in data:
        x = features(url)
        z = sum(wi * xi for wi, xi in zip(w, x)) + b
        p = 1 / (1 + math.exp(-z))
        for i in range(6):
            w[i] -= lr * (p - y) * x[i]                # gradient of the log loss
        b -= lr * (p - y)

names = ["length", "dots", "@ or -", "no https", "digits", "entropy"]
print("learned weights:", ", ".join(f"{n} {wi:+.2f}" for n, wi in zip(names, w)))
for url in ["https://www.amazon.in/orders", "https://paypa1.com-secure-verify.xyz/login",
            "http://hdfc-netbanking.secure-update.co/login", "http://45.33.12.9/paytm"]:
    z = sum(wi * xi for wi, xi in zip(w, features(url))) + b
    print(f"{url:48} P(phish) = {1 / (1 + math.exp(-z)):.3f}")
print("\nThe https phishing URL slips through: every phish in training used http, so the model leaned on 'no https'.")
''', long=True)

K.code('anomaly_z', r'''
# Anomaly detection for user behaviour: megabytes uploaded per day by one employee
import statistics as st

uploads = [120, 135, 110, 128, 140, 118, 125, 132, 900, 122, 130, 2400, 127, 119]

mean, sd = st.mean(uploads), st.pstdev(uploads)
med = st.median(uploads)
mad = st.median([abs(x - med) for x in uploads])     # median absolute deviation

print(f"mean {mean:.1f}  sd {sd:.1f}   median {med}  MAD {mad}")
print("day  MB     z     robust z")
for day, x in enumerate(uploads, 1):
    z = (x - mean) / sd
    rz = 0.6745 * (x - med) / mad                     # Iglewicz and Hoaglin modified z score
    flag = "ALERT" if abs(rz) > 3.5 else ""
    print(f"{day:3} {x:5} {z:6.2f} {rz:9.2f}  {flag}")
print("\nThe plain z score passes 3 only on day 12: the two big days inflate the mean and sd and hide day 9.")
print("The median and MAD barely move, so the robust z score catches both.")
''')

K.code('detector_metrics', r'''
# Judging a detector: confusion matrix, precision, recall, F1 and ROC AUC on imbalanced data
scores = [0.95, 0.91, 0.88, 0.80, 0.72, 0.65, 0.61, 0.55, 0.43, 0.40, 0.33, 0.30, 0.22, 0.18, 0.10, 0.05]
labels = [1,    1,    0,    1,    0,    1,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0]
# 1 = real attack, 0 = normal

def confusion(threshold):
    tp = fp = fn = tn = 0
    for s, y in zip(scores, labels):
        alert = s >= threshold
        if alert and y == 1:
            tp += 1
        elif alert and y == 0:
            fp += 1
        elif not alert and y == 1:
            fn += 1
        else:
            tn += 1
    return tp, fp, fn, tn

print("thresh  TP FP FN TN  precision recall   F1    FPR")
for t in (0.9, 0.7, 0.5, 0.3):
    tp, fp, fn, tn = confusion(t)
    prec = tp / (tp + fp)
    rec = tp / (tp + fn)
    f1 = 2 * prec * rec / (prec + rec)
    print(f" {t:.1f}    {tp:2} {fp:2} {fn:2} {tn:2}    {prec:.3f}   {rec:.3f}  {f1:.3f}  {fp / (fp + tn):.3f}")

# AUC = chance that a random attack scores higher than a random normal event
pos = [s for s, y in zip(scores, labels) if y == 1]
neg = [s for s, y in zip(scores, labels) if y == 0]
wins = sum(1 for p in pos for n in neg if p > n)
print(f"\nROC AUC = {wins} / {len(pos) * len(neg)} = {wins / (len(pos) * len(neg)):.3f}")
print("Accuracy of 'never alert':", f"{len(neg) / len(labels):.3f}", " high, yet it catches nothing.")
''')

K.code('malware_similar', r'''
# Malware family by behaviour: Jaccard similarity of the API calls seen in a sandbox, then nearest neighbour
known = {
    "ransomware A": {"FindFirstFile", "CryptEncrypt", "WriteFile", "DeleteFile", "vssadmin"},
    "ransomware B": {"FindFirstFile", "CryptGenKey", "CryptEncrypt", "WriteFile", "MoveFile"},
    "keylogger":    {"SetWindowsHookEx", "GetAsyncKeyState", "WriteFile", "InternetOpen"},
    "downloader":   {"InternetOpen", "URLDownloadToFile", "CreateProcess", "RegSetValue"},
    "text editor":  {"CreateWindow", "ReadFile", "WriteFile", "GetOpenFileName"},
}

def jaccard(a, b):
    return len(a & b) / len(a | b)

samples = {
    "sample 1": {"FindFirstFile", "CryptEncrypt", "WriteFile", "vssadmin"},
    "sample 2": {"InternetOpen", "URLDownloadToFile", "CreateProcess", "WriteFile"},
    "sample 3": {"CreateWindow", "ReadFile", "WriteFile", "GetSaveFileName"},
}
for name, calls in samples.items():
    ranked = sorted(known.items(), key=lambda kv: -jaccard(calls, kv[1]))
    best, sim = ranked[0][0], jaccard(calls, ranked[0][1])
    print(f"{name}: closest = {best:13} similarity {sim:.2f}   next = {ranked[1][0]} {jaccard(calls, ranked[1][1]):.2f}")
''')

K.code('drift_psi', r'''
# Is the world changing under the model? Population stability index (PSI) between training and today
import math

bins = ["< 1 KB", "1 to 10 KB", "10 to 100 KB", "100 KB to 1 MB", "> 1 MB"]
train = [0.10, 0.30, 0.35, 0.20, 0.05]      # share of email attachments in each size bin when the model was trained
week1 = [0.11, 0.29, 0.34, 0.21, 0.05]
week9 = [0.05, 0.15, 0.30, 0.30, 0.20]      # attackers moved to big ISO and ZIP files

def psi(expected, actual):
    total = 0
    for e, a in zip(expected, actual):
        total += (a - e) * math.log(a / e)
    return total

def verdict(v):
    return "stable" if v < 0.1 else "watch it" if v < 0.25 else "retrain now"

for name, now in [("week 1", week1), ("week 9", week9)]:
    v = psi(train, now)
    print(f"{name}: PSI = {v:.4f}  {verdict(v)}")
print("\nper bin for week 9:")
for b, e, a in zip(bins, train, week9):
    print(f"  {b:15} {e:.2f} -> {a:.2f}  adds {(a - e) * math.log(a / e):.4f}")
''')

K.lesson('idea', 'Why security teams use machine learning', f'''
{talk('Security teams face more data than people can read. A medium sized company can log billions of events a day, receive millions of emails, and see hundreds of thousands of new malware files every day around the world. Machine learning, or ML, means letting a program learn patterns from examples instead of writing every rule by hand. The idea is old in security. In 1987 Dorothy Denning published a model for intrusion detection that learned each user’s normal behaviour and flagged big changes, and the IDES system at SRI was built on it. In 2002 Paul Graham’s essay A Plan for Spam showed that a simple Bayesian filter could catch more than 99 percent of his spam with very few mistakes, and spam filters everywhere adopted the idea. In 2019 Google said its TensorFlow models were blocking an extra 100 million spam messages a day in Gmail. Today ML sits inside email filters, antivirus and endpoint detection, fraud checks on card payments, user behaviour analytics in the SOC, and tools that rank which vulnerabilities to patch first. But security is a hard place for ML. Attacks are rare, so even a small false alarm rate floods analysts. Labels are expensive and often wrong. And the other side adapts: attackers change their emails and malware to slip past whatever the model learned. Robin Sommer and Vern Paxson warned in 2010 that most of the hard work is in the data, the labels and honest testing. This chapter builds small versions of the main ideas so you can see both the power and the limits.')}
{src('Denning (1987), Graham (2002), Axelsson (1999 and 2000), McHugh (2000), Tavallaee et al. (2009), Sommer and Paxson (2010), Liu, Ting and Zhou (2008), Iglewicz and Hoaglin (1993), Anderson and Roth, EMBER (2018), Google blog on Gmail and TensorFlow (2019), APWG reports, Lundberg and Lee, SHAP (2017).')}
{wwh('<b>Machine learning for security</b> means training models on examples of normal activity and attacks so they can score new emails, files, logins or network flows as suspicious or safe.',
     'There is too much data for people and fixed rules alone, attackers change small details to dodge signatures, and models can spot patterns across thousands of signals at once.',
     'Collect data, label it or learn what normal looks like, turn raw data into features, train and test honestly, pick a threshold, put the model in front of analysts, take their feedback, and retrain as the world drifts.')}
{viz('cymlpipe')}
{table(['Security task', 'Typical ML approach', 'Main difficulty'], [
    ['Spam and phishing email', 'Supervised text classifiers (naive Bayes, boosted trees, transformers)', 'Attackers change words, images and links every week'],
    ['Malware detection', 'Supervised models on file features and sandbox behaviour', 'Packing and obfuscation hide features, new families keep appearing'],
    ['Intrusion and network anomaly detection', 'Unsupervised baselines, isolation forest, autoencoders', 'Normal traffic is very varied, so false alarms are common'],
    ['Card and payment fraud', 'Supervised models on transaction features', 'Fraud is rare and labels arrive weeks later after chargebacks'],
    ['User behaviour analytics (UEBA)', 'Per user baselines, peer group comparison', 'Jobs, travel and tools change what is normal'],
    ['Vulnerability triage', 'Models that predict which bugs will be exploited (for example EPSS)', 'Exploits depend on attacker choices that change']])}
''', kw=['machine learning', 'security analytics', 'Denning 1987', 'IDES', 'Paul Graham', 'A Plan for Spam', 'Gmail TensorFlow', 'UEBA', 'EPSS', 'Sommer and Paxson', 'pipeline'])

K.lesson('bayes', 'Naive Bayes: the classic spam and phishing filter', f'''
{talk('Naive Bayes is the simplest useful text classifier and still a strong baseline. It comes straight from Bayes rule, which you met in the foundations maths chapter. We want the probability that an email is phishing given its words. Bayes rule turns that around: it is proportional to the prior chance of phishing times the chance of seeing those words in phishing mail. The naive part is the assumption that words appear independently once we know the class. That is clearly false, because urgent and verify often appear together, but the method still ranks emails well. Multiplying many small probabilities underflows to zero on a computer, so we add logarithms instead, and we compare phishing against safe mail as a log odds score. A word never seen in phishing would give a probability of zero and wipe out all other evidence, so we use Laplace smoothing, which adds one to every count. Paul Graham’s 2002 filter and SpamAssassin’s Bayes module worked this way, and the user’s own Report spam clicks became the training labels. Attackers answered with tricks such as Bayesian poisoning, padding spam with innocent words, and putting the text inside images, which pushed filters to add image analysis and sender reputation. The animation walks one email through word by word, and the program trains the same tiny filter.')}
{viz('cybayes')}
{run('spam_bayes')}
{fxs(fx('Bayes rule for a class given the words', 'P(phish | words) &prop; P(phish) &times; &Pi; P(w<sub>i</sub> | phish)', 'The product runs over the words of the email, assumed independent given the class.', key=True),
     fx('Log odds score', 'score = log(P(phish) / P(safe)) + &Sigma; log(P(w<sub>i</sub> | phish) / P(w<sub>i</sub> | safe))', 'score above 0 means phishing is more likely, and P(phish) = 1 / (1 + e<sup>&minus;score</sup>).', key=True),
     fx('Laplace smoothing', 'P(w | c) = (count(w, c) + 1) / (N<sub>c</sub> + |V|)', '"urgent" twice in 23 phish words with 31 words in the vocabulary: 3 / 54 &asymp; 0.0556.', key=True))}
{deep('Why the log and why smoothing', '<p>Fifty words with probabilities near 0.01 multiply to about 10<sup>&minus;100</sup>, close to the limit of floating point numbers, while their logs simply add to about &minus;230. Smoothing is a prior belief that every word is possible in every class. With add one smoothing the estimate is the mean of a Beta (or Dirichlet) posterior with a uniform prior, which links this trick to Bayesian statistics.</p>')}
''', kw=['naive Bayes', 'Bayes rule', 'log odds', 'Laplace smoothing', 'add one smoothing', 'SpamAssassin', 'Bayesian poisoning', 'image spam', 'baseline'])

K.lesson('features', 'Features and logistic regression for phishing links', f'''
{talk('A model cannot read a web address the way you do. It needs numbers, called features, that capture what an expert would notice. For a phishing link those include the length of the address, how many dots and subdomains it has, whether it uses an at sign or hyphens that confuse readers, whether it uses HTTPS, digits in the host name, and how random the host name looks, measured by Shannon entropy. Logistic regression is the standard first model for this. It multiplies each feature by a weight, adds them up with a bias, and squashes the total into a probability with the sigmoid function. Training adjusts the weights a little after each example in the direction that lowers the log loss, which is called gradient descent. The program below trains on twelve made up addresses. Look at what it learns. Every phishing address in our training set used plain HTTP, so the model leans heavily on the no HTTPS feature, and a phishing address with HTTPS slips through. This is called shortcut learning. It happened in real life too. In 2017 the Anti Phishing Working Group found under a third of phishing sites used HTTPS, and by 2021 the share was over 80 percent, because free certificates made it easy. A model trained on old data would fail in exactly this way. Good teams check what features a model relies on, train on recent data, and add features attackers find hard to fake, such as the age of the domain and its registration details.')}
{run('url_features')}
{fxs(fx('Logistic regression', 'p = &sigma;(z) = 1 / (1 + e<sup>&minus;z</sup>), z = w &middot; x + b', 'z = 2 gives p &asymp; 0.881, z = 0 gives p = 0.5.', key=True),
     fx('Log loss and its gradient', 'L = &minus;[y log p + (1 &minus; y) log(1 &minus; p)], &part;L/&part;w<sub>i</sub> = (p &minus; y) x<sub>i</sub>', 'p = 0.8 for a phish (y = 1) and feature 0.5: gradient (0.8 &minus; 1) &times; 0.5 = &minus;0.1, so the weight grows.', key=True),
     fx('Shannon entropy of a string', 'H = &minus;&Sigma; p<sub>c</sub> log<sub>2</sub> p<sub>c</sub>', '"aabb": two letters each with p = 0.5, so H = 1 bit per character.'))}
{note('Shortcut learning is one of the most common failures of security ML. A model can score 99% on a test set drawn from the same old data and still fail on next month’s attacks. Always test on data collected after the training data.', 'warn')}
''', kw=['features', 'feature engineering', 'logistic regression', 'sigmoid', 'gradient descent', 'log loss', 'Shannon entropy', 'phishing URL', 'shortcut learning', 'APWG', 'domain age'])

K.lesson('anomaly', 'Anomaly detection: learning what normal looks like', f'''
{talk('Supervised learning needs labelled attacks, and new attacks have no labels yet. Anomaly detection takes the other road: learn what normal looks like and flag what is far from it. This was Denning’s 1987 idea, and it powers user and entity behaviour analytics today. The simplest version is a z score: how many standard deviations a value is from the mean. But attacks themselves pull the mean and standard deviation, which can hide them. The program shows this with an employee’s daily uploads. Two huge days inflate the standard deviation so much that one of them looks normal. The fix is robust statistics: use the median and the median absolute deviation, called MAD, which barely move when a few values are extreme. Boris Iglewicz and David Hoaglin suggested flagging a modified z score above 3.5. For many features at once, a popular method is the isolation forest, from Fei Tony Liu, Kai Ming Ting and Zhi-Hua Zhou in 2008. Instead of describing normal data, it tries to isolate each point with random cuts. Odd points sit alone in empty space, so a few cuts separate them, while normal points need many. Averaging the number of cuts over many random trees gives an anomaly score. The weakness of all anomaly detection is that unusual is not the same as malicious. A finance team closing the books, a new backup job, or staff working from a new city all look odd. So anomaly scores are usually combined with context and sent to analysts as leads, not as proof.')}
{viz('cyiforest')}
{run('anomaly_z')}
{fxs(fx('z score', 'z = (x &minus; &mu;) / &sigma;', 'x = 2400, &mu; = 343.3, &sigma; = 604.1: z &asymp; 3.40.', key=True),
     fx('Modified (robust) z score', 'M = 0.6745 (x &minus; median) / MAD, flag when |M| &gt; 3.5', 'x = 900, median 127.5, MAD 7.5: M &asymp; 69.5, a clear outlier.', key=True),
     fx('Isolation forest score', 's(x, n) = 2<sup>&minus;E[h(x)] / c(n)</sup>, c(n) = 2H(n &minus; 1) &minus; 2(n &minus; 1)/n', 'H(i) &asymp; ln i + 0.5772. n = 256: c &asymp; 10.24. E[h] = 2 gives s &asymp; 0.87, an anomaly.'))}
{deep('Why 0.6745', '<p>For normally distributed data the MAD is about 0.6745 times the standard deviation, because 0.6745 is the 75th percentile of the standard normal distribution. Multiplying by 0.6745 puts the robust score on the same scale as an ordinary z score, so 3.5 means roughly the same thing.</p>')}
''', kw=['anomaly detection', 'z score', 'robust statistics', 'median', 'MAD', 'modified z score', 'Iglewicz and Hoaglin', 'isolation forest', 'path length', 'UEBA', 'baseline'])

K.lesson('metrics', 'Measuring a detector honestly', f'''
{talk('Accuracy is the wrong number for security. If one event in a thousand is an attack, a detector that never alerts is 99.9 percent accurate and useless. Instead we use the confusion matrix: true positives are attacks caught, false positives are false alarms, false negatives are attacks missed, and true negatives are normal events left alone. Precision is the share of alerts that are real, which decides how much analyst time is wasted. Recall, also called the true positive rate or detection rate, is the share of attacks caught. F1 is their harmonic mean. Every threshold trades one for the other. The ROC curve plots the true positive rate against the false positive rate for every threshold, and the area under it, AUC, is the chance that a random attack scores higher than a random normal event. Stefan Axelsson showed in 1999 why intrusion detection is so hard: because attacks are so rare, even a one percent false positive rate means most alerts are false. Testing also needs care. The famous KDD Cup 1999 intrusion dataset was criticised by John McHugh in 2000 and by later researchers for duplicate records and traffic that did not look like real networks, and NSL-KDD in 2009 removed the duplicates. Models that score near perfectly on such data often fail on real networks. Test on recent data from your own environment, split by time rather than at random, and report precision at the alert volume your team can really handle.')}
{viz('cyroc')}
{viz('cybaserate')}
{run('detector_metrics')}
{fxs(fx('Precision and recall', 'precision = TP / (TP + FP), recall = TP / (TP + FN)', 'TP 3, FP 2, FN 2: precision 0.6, recall 0.6.', key=True),
     fx('F1 score', 'F1 = 2 &times; precision &times; recall / (precision + recall)', 'precision 0.5, recall 0.8: F1 = 0.8 / 1.3 &asymp; 0.615.', key=True),
     fx('False positive rate', 'FPR = FP / (FP + TN)', 'FP 4, TN 7: 4 / 11 &asymp; 0.364.', key=True),
     fx('AUC as a ranking chance', 'AUC = P(score of a random attack &gt; score of a random normal event)', '47 winning pairs out of 5 &times; 11 = 55: AUC &asymp; 0.855.'),
     fx('Precision from the base rate (Bayes)', 'precision = r &middot; TPR / (r &middot; TPR + (1 &minus; r) &middot; FPR)', 'r = 0.0001, TPR = 0.99, FPR = 0.01: precision &asymp; 0.0098, under 1%.', key=True))}
{table(['Measure', 'Question it answers', 'Who cares most'], [
    ['Precision', 'Of the alerts, how many are real?', 'SOC analysts, because false alarms waste their time'],
    ['Recall (TPR)', 'Of the attacks, how many did we catch?', 'The CISO, because missed attacks cause breaches'],
    ['FPR', 'Of normal events, how many did we flag?', 'Users whose email or files get blocked'],
    ['ROC AUC', 'How well does the score rank attacks above normal events overall?', 'Model builders comparing models'],
    ['PR AUC', 'Precision and recall together across thresholds', 'Anyone with very rare attacks, where ROC AUC can look too good']])}
''', kw=['confusion matrix', 'precision', 'recall', 'true positive rate', 'false positive rate', 'F1', 'ROC curve', 'AUC', 'PR curve', 'base rate fallacy', 'Axelsson', 'KDD Cup 99', 'NSL-KDD', 'time split'])

K.lesson('malware', 'Classifying malware by what it does', f'''
{talk('Antivirus started with signatures: exact byte patterns or file hashes of known malware. They are precise but miss anything new, and changing one byte changes the hash. Machine learning adds two kinds of features. Static features come from the file without running it: the size of each section of a Windows program, the libraries and functions it imports, printable strings, and the entropy of each section, where very high entropy suggests the code is packed or encrypted. Dynamic features come from running the file in a sandbox and recording its behaviour: which files it opens, which registry keys it changes, which network addresses it contacts, and which Windows API calls it makes. Ransomware, for example, tends to list files, encrypt them, write new copies and delete shadow copies with vssadmin. The program compares the API calls of new samples with known families using Jaccard similarity, the size of the overlap divided by the size of the union, and picks the nearest neighbour. In 2018 Hyrum Anderson and Phil Roth released EMBER, a public set of features from 1.1 million Windows programs, so researchers could compare models fairly. Malware authors respond with packing, delaying behaviour until the sandbox gives up, and checking whether they are inside a virtual machine. So real products combine signatures, static ML, behaviour monitoring on the endpoint and cloud reputation, and every model verdict on an unknown file is backed by a way to undo damage.')}
{run('malware_similar')}
{fxs(fx('Jaccard similarity', 'J(A, B) = |A &cap; B| / |A &cup; B|', '4 calls shared, 5 calls in total: J = 0.8.', key=True),
     fx('Entropy of a file section', 'H = &minus;&Sigma; p<sub>b</sub> log<sub>2</sub> p<sub>b</sub>, at most 8 bits per byte', 'Plain code is often near 5 to 6 bits per byte. Above about 7.2 suggests packing or encryption.'))}
{versus('Static and dynamic malware features', ['', 'Static analysis', 'Dynamic analysis'], [
    ['How', 'Read the file without running it', 'Run it in a sandbox and record behaviour'],
    ['Features', 'Imports, section sizes and entropy, strings, headers', 'API calls, files, registry, network, processes'],
    ['Speed', 'Milliseconds, fine for every file', 'Minutes per file, so used for unknown files only'],
    ['Weakness', 'Packing and obfuscation hide the real code', 'Sandbox checks and long sleeps hide the behaviour'],
    ['Safe practice', 'Safe to run on any machine', 'Only inside an isolated sandbox with no access to real networks']],
    'Use both. Static models filter most files instantly, and dynamic analysis looks deeper at the few unknown ones.')}
''', kw=['malware classification', 'signatures', 'static features', 'dynamic features', 'sandbox', 'API calls', 'Jaccard similarity', 'nearest neighbour', 'section entropy', 'packing', 'EMBER', 'evasion'])

K.lesson('drift', 'Drift, adaptive attackers and explaining the model', f'''
{talk('A security model starts to go stale the day it is deployed. Data drift means the inputs change, for example attackers switching from small Word attachments to large ISO and ZIP files, which happened in 2022 after Microsoft started blocking macros in files from the internet by default. Concept drift means the link between inputs and labels changes, so the same features now mean something different. In security much of the drift is deliberate, because attackers test their emails and malware against popular products before they send them. Teams watch for drift with simple statistics. The population stability index, PSI, compares the share of data in each bin today with the share at training time. A common rule of thumb says below 0.1 is stable, 0.1 to 0.25 needs watching, and above 0.25 needs action. Analysts also need to know why a model flagged something, both to trust it and to act fast. Methods such as SHAP, by Scott Lundberg and Su-In Lee in 2017, split a score into the contribution of each feature, so an alert can say this login was flagged mainly because of the new country and the 3 AM hour. Finally, a model can itself be attacked: poisoned through its training data, fooled by carefully changed inputs, copied, or made to leak its training data. That is the subject of the next chapter.')}
{run('drift_psi')}
{fxs(fx('Population stability index', 'PSI = &Sigma; (a<sub>i</sub> &minus; e<sub>i</sub>) ln(a<sub>i</sub> / e<sub>i</sub>)', 'One bin from 0.05 to 0.20: (0.15) ln 4 &asymp; 0.208. Below 0.1 stable, above 0.25 retrain.', key=True))}
{table(['Kind of change', 'Example', 'What to do'], [
    ['Data drift', 'Attachments move to ISO and ZIP after macros are blocked', 'Watch PSI per feature, retrain on recent data'],
    ['Concept drift', 'A once rare login country becomes normal after a new office opens', 'Refresh labels and baselines, review rules'],
    ['Adversarial adaptation', 'Phishers test emails against filters before sending', 'Retrain often, use features costly to fake, layer defences'],
    ['Label delay', 'Card fraud confirmed only after a chargeback weeks later', 'Train on matured labels, watch early proxy signals']])}
''', kw=['data drift', 'concept drift', 'population stability index', 'PSI', 'adversarial adaptation', 'macros blocked 2022', 'explainability', 'SHAP', 'human in the loop', 'retraining'])

K.lesson('versus', 'Rules, supervised and unsupervised detection compared', f'''
{talk('No single method wins. Rules written by experts are precise and easy to explain but only catch what someone thought of. Supervised models learn from labelled examples and generalise to variants of known attacks. Unsupervised anomaly detection can find new things but raises many false alarms. Mature teams layer all three and let analysts decide.')}
{versus('Three ways to detect attacks', ['', 'Rules and signatures', 'Supervised ML', 'Unsupervised anomaly detection'], [
    ['Learns from', 'Expert knowledge', 'Labelled attacks and normal data', 'Normal data only'],
    ['Catches', 'Known attacks exactly', 'Known attacks and close variants', 'Anything unusual, including new attacks'],
    ['False alarms', 'Low when well written', 'Medium, set by the threshold', 'High, since unusual is not always bad'],
    ['Explains itself', 'Yes, the rule is the reason', 'Needs tools such as SHAP', 'Partly, by showing what was unusual'],
    ['Breaks when', 'Attackers change a detail', 'Data drifts or labels are poor', 'Normal behaviour changes']],
    'Start with rules for known bad, add supervised models where you have good labels, and use anomaly scores as leads for analysts to investigate.')}
''', kw=['rules versus ML', 'signatures', 'supervised', 'unsupervised', 'layered detection'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('A beginner knows that spam filters and antivirus learn from examples. A student can build a naive Bayes filter, train logistic regression, compute robust z scores and judge a detector with precision, recall and AUC. A professional runs these models in production with honest evaluation, drift monitoring and analyst feedback. Experts research robust and explainable security models and how attackers adapt to them.')}
{ladder(
    '<p>Your email app learns which messages are spam from millions of examples, and antivirus learns what bad programs look like.</p>',
    '<p>Naive Bayes with log odds and smoothing, logistic regression and gradient descent, robust z scores and isolation forest, precision, recall, F1, ROC AUC and the base rate, Jaccard similarity, PSI.</p>',
    '<p>Build detection models with time split evaluation, tune thresholds to analyst capacity, monitor drift, explain alerts with SHAP, and run feedback loops with the SOC.</p>',
    '<p>Research robustness to adaptive attackers, learning with few and noisy labels, graph and sequence models for intrusion detection, and language models as SOC assistants with their new risks.</p>')}
{grow('Explain how a spam filter learns from examples.',
      'Build and fairly measure small detectors for phishing, anomalies and malware.',
      'Run ML detection in production with feedback, drift checks and explanations.')}
''', kw=['beginner', 'expert', 'SOC assistant', 'research'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    '<b>Why ML</b>: too much data and adaptive attackers. Denning 1987, Graham 2002. The loop: data, labels, features, train, validate, threshold, feedback, drift.',
    '<b>Naive Bayes</b>: score = log prior ratio + &Sigma; log(P(w | phish) / P(w | safe)), Laplace (count + 1) / (N + |V|), P = &sigma;(score).',
    '<b>Logistic regression</b>: p = &sigma;(w &middot; x + b), gradient (p &minus; y) x. Watch for shortcut learning (HTTPS phishing).',
    '<b>Anomalies</b>: z score is hidden by outliers, robust z = 0.6745 (x &minus; median) / MAD &gt; 3.5. Isolation forest s = 2<sup>&minus;E[h]/c(n)</sup>.',
    '<b>Metrics</b>: precision, recall, F1, FPR, ROC AUC as a ranking chance, the base rate fallacy (Axelsson). Time split testing.',
    '<b>Malware and drift</b>: static and dynamic features, Jaccard nearest neighbour, EMBER. PSI below 0.1 stable, above 0.25 retrain. SHAP for explanations.'],
    'Advanced 1.2: attacks on machine learning models and how to defend them.')}
{files('Three tasks: an F1 score, robust outlier detection with the median and MAD, and the population stability index.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'Why is accuracy a poor measure for an intrusion detector?', ['It is hard to compute', 'Attacks are rare, so never alerting already scores very high', 'It ignores the threshold', 'It only works for images'], 1, 'Think of 1 attack in 1000 events.', 'Never alerting is 99.9% accurate and catches nothing. Use precision and recall.')
K.quiz('e', 'What does Laplace smoothing do in a naive Bayes filter?', ['Removes stop words', 'Adds one to every word count so unseen words do not give probability zero', 'Makes emails shorter', 'Sorts the vocabulary'], 1, 'Add one.', 'One zero probability would wipe out all other evidence.')
K.quiz('e', 'Anomaly detection learns mainly from', ['Labelled attacks only', 'What normal activity looks like', 'Attacker forums', 'Firewall rules'], 1, 'Unusual compared to what?', 'It flags points far from normal, which may or may not be malicious.')
K.quiz('e', 'Precision answers which question?', ['How many attacks did we catch?', 'Of our alerts, how many were real attacks?', 'How fast is the model?', 'How big is the dataset?'], 1, 'TP over all alerts.', 'Recall is the share of attacks caught.')
K.quiz('m', 'Why does a naive Bayes filter add logarithms instead of multiplying probabilities?', ['Logs are more accurate in theory', 'Multiplying many small probabilities underflows to zero on a computer', 'Bayes rule needs logs', 'To make it slower'], 1, 'Fifty factors of 0.01.', 'The product is about 10<sup>&minus;100</sup>, the log sum about &minus;230.')
K.quiz('m', 'A phishing URL model trained only on HTTP phishing misses HTTPS phishing. This is called', ['Overfitting to noise', 'Shortcut learning', 'Underfitting', 'Data augmentation'], 1, 'It relied on an easy clue.', 'The clue stopped working once free certificates spread.')
K.quiz('m', 'Why use the median and MAD instead of the mean and standard deviation for anomaly detection?', ['They are faster', 'Outliers barely move them, so attacks cannot hide themselves', 'They need labels', 'They work only on text'], 1, 'Robust statistics.', 'Big outliers inflate the standard deviation and hide other outliers.')
K.quiz('m', 'In an isolation forest, an anomaly has', ['A long average path length', 'A short average path length', 'No path', 'The same path as every point'], 1, 'Few cuts isolate it.', 'Score 2<sup>&minus;E[h]/c(n)</sup> is near 1 when E[h] is small.')
K.quiz('m', 'Which malware features need the file to be run in a sandbox?', ['Imported functions', 'Section entropy', 'API calls made while running', 'File size'], 2, 'Dynamic.', 'The others are static features read from the file.')
K.quiz('h', 'A detector has TPR 99% and FPR 1%, and 1 in 10000 events is an attack. About what share of alerts are real?', ['99%', 'About 50%', 'About 1%', '0%'], 2, 'Bayes with the base rate.', '0.0001 &times; 0.99 / (0.0001 &times; 0.99 + 0.9999 &times; 0.01) &asymp; 0.0098.')
K.quiz('h', 'What does an ROC AUC of 0.5 mean?', ['A perfect model', 'No better than random ranking', 'Half the attacks blocked', 'The threshold is 0.5'], 1, 'The diagonal.', 'AUC is the chance a random attack scores above a random normal event.')
K.quiz('h', 'A feature’s PSI between training and this month is 0.39. What should the team do?', ['Nothing, it is stable', 'Investigate and retrain, the data has shifted a lot', 'Delete the feature', 'Lower the threshold to 0'], 1, 'Above 0.25.', 'Rule of thumb: below 0.1 stable, 0.1 to 0.25 watch, above 0.25 act.')
K.quiz('h', 'Why was the KDD Cup 1999 dataset criticised?', ['It was too small', 'Duplicate records and traffic unlike real networks gave misleading results', 'It had no attacks', 'It was encrypted'], 1, 'McHugh 2000, NSL-KDD 2009.', 'Near perfect scores on it often fail on real networks.')
K.quiz('x', 'In the style of a CMU machine learning for security exam: why should a security model be tested with a time based split rather than a random split?', ['Random splits are illegal', 'Real use predicts future data, and random splits leak future patterns into training', 'Time splits make training faster', 'There is no difference'], 1, 'Think of deployment.', 'A random split lets the model see later variants of the same campaign, which inflates scores.')
K.quiz('x', 'In the style of an IIT information security viva: what is the isolation forest score when E[h] equals c(n)?', ['1', '0.5', '0', '2'], 1, '2 to the power &minus;1.', 'Points with average path length are scored 0.5, neither clearly anomalous nor clearly normal.')

K.calc('e', 'TP = 3, FP = 2. Precision?', '0.6', 'TP / (TP + FP).', ['Alerts = 3 + 2 = 5.', '3 / 5.', eq('0.6')], check=0.6)
K.calc('e', 'TP = 4, FN = 1. Recall?', '0.8', 'TP / (TP + FN).', ['Attacks = 4 + 1 = 5.', '4 / 5.', eq('0.8')], check=0.8)
K.calc('e', 'Laplace smoothing: "urgent" appears 2 times in 23 phish words, vocabulary 31. P(urgent | phish)? Round to 4 decimals.', '0.0556', '(count + 1) / (N + |V|).', ['2 + 1 = 3.', '23 + 31 = 54.', eq('3 / 54 &asymp; 0.0556')], check=round(3 / 54, 4))
K.calc('m', 'Precision 0.5 and recall 0.8. F1? Round to 4 decimals.', '0.6154', 'Harmonic mean.', ['2 &times; 0.5 &times; 0.8 = 0.8.', '0.5 + 0.8 = 1.3.', eq('0.8 / 1.3 &asymp; 0.6154')], check=round(0.8 / 1.3, 4))
K.calc('m', 'A log odds score of 3.18. P(phish)? Round to 3 decimals.', '0.96', 'Sigmoid.', ['e<sup>&minus;3.18</sup> &asymp; 0.0416.', '1 / 1.0416.', eq('&asymp; 0.960')], check=round(1 / (1 + math.exp(-3.18)), 3))
K.calc('m', '"urgent" seen 2 times in phish and 0 in safe mail, both classes with 23 words and vocabulary 31. Its log ratio? Round to 4 decimals.', '1.0986', 'Smoothed counts 3 and 1.', ['P(urgent | phish) = 3 / 54, P(urgent | safe) = 1 / 54.', 'Ratio = 3.', eq('ln 3 &asymp; 1.0986')], check=round(math.log(3), 4))
K.calc('m', 'x = 900, median 127.5, MAD 7.5. Modified z score? Round to 2 decimals.', '69.47', '0.6745 (x &minus; median) / MAD.', ['900 &minus; 127.5 = 772.5.', '772.5 / 7.5 = 103.', eq('0.6745 &times; 103 &asymp; 69.47')], check=round(0.6745 * 772.5 / 7.5, 2))
K.calc('m', 'FP = 4, TN = 7. False positive rate? Round to 3 decimals.', '0.364', 'FP / (FP + TN).', ['Normal events = 11.', '4 / 11.', eq('&asymp; 0.364')], check=round(4 / 11, 3))
K.calc('h', 'Base rate 0.0001, TPR 0.99, FPR 0.01. Precision? Round to 4 decimals.', '0.0098', 'Bayes rule.', ['True alerts: 0.0001 &times; 0.99 = 0.000099.', 'False alarms: 0.9999 &times; 0.01 = 0.009999.', eq('0.000099 / 0.010098 &asymp; 0.0098')], check=round(0.0001 * 0.99 / (0.0001 * 0.99 + 0.9999 * 0.01), 4))
K.calc('h', 'API call sets share 4 calls, and together have 5 different calls. Jaccard similarity?', '0.8', 'Intersection over union.', ['|A &cap; B| = 4.', '|A &cup; B| = 5.', eq('4 / 5 = 0.8')], check=0.8)
K.calc('h', 'PSI term for one bin: expected 0.05, actual 0.20. Round to 4 decimals.', '0.2079', '(a &minus; e) ln(a / e).', ['a &minus; e = 0.15.', 'ln(0.20 / 0.05) = ln 4 &asymp; 1.3863.', eq('0.15 &times; 1.3863 &asymp; 0.2079')], check=round(0.15 * math.log(4), 4))
K.calc('h', 'Entropy of the string "aabb" in bits per character?', '1', 'Two letters, each half the time.', ['p(a) = p(b) = 0.5.', '&minus;2 &times; 0.5 log<sub>2</sub> 0.5.', eq('= 1')], check=1)
K.calc('x', 'Isolation forest with n = 256: c(n) = 2(ln 255 + 0.5772) &minus; 2 &times; 255 / 256. Round to 2 decimals.', '10.24', 'Harmonic number approximation.', ['ln 255 &asymp; 5.5413, plus 0.5772 = 6.1185.', '2 &times; 6.1185 = 12.2370, and 2 &times; 255 / 256 = 1.9922.', eq('12.2370 &minus; 1.9922 &asymp; 10.24')], check=round(2 * (math.log(255) + 0.5772156649) - 2 * 255 / 256, 2))
K.calc('x', 'With c(n) = 10.24, a point has average path length 2. Anomaly score? Round to 3 decimals.', '0.873', '2<sup>&minus;E[h]/c</sup>.', ['2 / 10.24 &asymp; 0.1953.', '2<sup>&minus;0.1953</sup>.', eq('&asymp; 0.873')], check=round(2 ** (-2 / 10.24), 3))

K.assign('f1_score', 'e', 'F1 score from counts',
         '<p>Write <code>f1_score(tp, fp, fn)</code> that returns the F1 score rounded to 4 decimals. Return <code>0.0</code> when there are no true positives.</p>',
         '''
def f1_score(tp, fp, fn):
    # your code here
    pass
''', [('f1_score(3, 2, 2)', 0.6), ('f1_score(4, 4, 1)', 0.6154), ('f1_score(0, 5, 5)', 0.0), ('f1_score(10, 0, 0)', 1.0)],
         '''
def f1_score(tp, fp, fn):
    if tp == 0:
        return 0.0
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    return round(2 * precision * recall / (precision + recall), 4)
''', 'Compute precision and recall first, then the harmonic mean.', '<p>F1 treats a missed attack and a false alarm as equally bad. When they cost different amounts, compare models on cost instead, or use an F beta score.</p>')
K.assign('robust_outliers', 'm', 'Robust outliers with the median and MAD',
         '<p>Write <code>robust_outliers(values)</code> that returns the list of indices (from 0) whose modified z score 0.6745 (x &minus; median) / MAD has an absolute value above 3.5. Use <code>statistics.median</code>.</p>',
         '''
import statistics

def robust_outliers(values):
    # your code here
    pass
''', [('robust_outliers([120, 135, 110, 128, 140, 118, 125, 132, 900, 122, 130, 2400, 127, 119])', [8, 11]),
      ('robust_outliers([10, 11, 9, 10, 12, 10])', []),
      ('robust_outliers([5, 6, 5, 7, 6, 50, 5, 6])', [5])],
         '''
import statistics

def robust_outliers(values):
    med = statistics.median(values)
    mad = statistics.median([abs(x - med) for x in values])
    out = []
    for i, x in enumerate(values):
        if abs(0.6745 * (x - med) / mad) > 3.5:
            out.append(i)
    return out
''', 'Find the median, then the median of the distances from it, then score each value.', '<p>If more than half the values are identical the MAD is 0 and the score is undefined. Real code then falls back to the mean absolute deviation.</p>')
K.assign('psi_value', 'h', 'Population stability index',
         '<p>Write <code>psi_value(expected, actual)</code> for two lists of bin shares that returns &Sigma; (a &minus; e) ln(a / e) rounded to 4 decimals.</p>',
         '''
import math

def psi_value(expected, actual):
    # your code here
    pass
''', [('psi_value([0.10, 0.30, 0.35, 0.20, 0.05], [0.05, 0.15, 0.30, 0.30, 0.20])', 0.3948),
      ('psi_value([0.5, 0.5], [0.5, 0.5])', 0.0),
      ('psi_value([0.25, 0.75], [0.5, 0.5])', 0.2747)],
         '''
import math

def psi_value(expected, actual):
    total = 0.0
    for e, a in zip(expected, actual):
        total += (a - e) * math.log(a / e)
    return round(total, 4)
''', 'Loop over the bins together with zip and add each term.', '<p>PSI is a symmetric form of the Kullback Leibler divergence: KL(a || e) + KL(e || a). Empty bins make it infinite, so real code adds a tiny value to each share.</p>')

K.must('The ML loop', 'Collect, label (or learn normal), features, train, validate on later data, deploy with a threshold, analyst feedback, watch drift, retrain. Denning 1987 anomaly model, Graham 2002 Bayes spam filter. Most work is data, labels and evaluation (Sommer and Paxson 2010).')
K.must('Naive Bayes', 'score = log(P(phish) / P(safe)) + &Sigma; log(P(w | phish) / P(w | safe)). Laplace P(w | c) = (count + 1) / (N<sub>c</sub> + |V|). P = 1 / (1 + e<sup>&minus;score</sup>). Logs avoid underflow.')
K.must('Logistic regression', 'p = &sigma;(w &middot; x + b), log loss, gradient (p &minus; y) x<sub>i</sub>. Features: length, dots, @ or hyphen, HTTPS, digits, entropy. Beware shortcut learning, test on newer data.')
K.must('Anomalies', 'z = (x &minus; &mu;) / &sigma; is fooled by outliers. Robust M = 0.6745 (x &minus; median) / MAD, flag above 3.5. Isolation forest: s = 2<sup>&minus;E[h]/c(n)</sup>, near 1 anomaly, 0.5 average. Unusual is not proof of malicious.')
K.must('Metrics', 'Precision TP/(TP+FP), recall TP/(TP+FN), F1, FPR FP/(FP+TN). ROC AUC = chance an attack outranks a normal event. Base rate: precision = r TPR / (r TPR + (1 &minus; r) FPR). KDD 99 flaws, use time splits.')
K.must('Malware and drift', 'Static (imports, entropy above about 7.2 suggests packing) and dynamic (sandbox API calls) features. Jaccard |A &cap; B| / |A &cup; B|. EMBER 2018. PSI = &Sigma; (a &minus; e) ln(a/e): below 0.1 stable, above 0.25 act. SHAP explains alerts.')

T = K.topic(
    slug='cy-mlsec', topic='cy-mlsec', step=(1, 'Machine learning and security', 'cy-a1', 'Using machine learning to find attacks, and protecting machine learning systems from attackers.', 'Advanced'),
    title='Machine learning for security', short='ML for security', badge='1.1', minutes=80,
    lead='How security teams use machine learning and where it fails: the detection loop, a naive Bayes phishing filter, features and logistic regression for links, anomaly detection with robust statistics and isolation forests, honest metrics with ROC, AUC and the base rate, malware similarity, drift with PSI, and explaining alerts.',
    desc='machine learning for security, detection pipeline, naive Bayes, spam filter, phishing, Laplace smoothing, log odds, logistic regression, gradient descent, feature engineering, URL features, entropy, shortcut learning, anomaly detection, z score, robust z score, MAD, isolation forest, UEBA, precision, recall, F1, ROC curve, AUC, base rate fallacy, KDD Cup 99, NSL-KDD, malware classification, static analysis, dynamic analysis, sandbox, Jaccard similarity, EMBER, concept drift, data drift, population stability index, PSI, SHAP, explainability',
    summary='Detection loop, naive Bayes filter, phishing link features with logistic regression, robust anomaly detection and isolation forest, ROC and the base rate, malware similarity, drift and explanations.',
    keywords=['machine learning', 'naive Bayes', 'logistic regression', 'anomaly detection', 'isolation forest', 'ROC AUC', 'precision', 'recall', 'malware', 'drift', 'PSI'],
    recap='<p>Learn from data, measure with precision and recall at the real base rate, test on newer data, watch for drift, and keep analysts in the loop.</p>',
    added='2026-11-15')
