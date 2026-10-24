# Chapter 9: chance and sample spaces, the addition and multiplication rules, counting, conditional
# probability, independence, Bayes' theorem, naive Bayes and Monte Carlo simulation.
from mkit import Kit, part, fx, fxs, trick, ml, life, frac, worked, table, code, viz, deep

K = Kit()

# ---------------------------------------------------------------- programs
K.code('counting', py=r'''
from math import comb, factorial, perm

print("ways to line up 5 friends: 5! =", factorial(5))
print("podium (gold, silver, bronze) from 10 runners: P(10, 3) =", perm(10, 3))
print("teams of 3 from 10 people: C(10, 3) =", comb(10, 3))
tickets = comb(49, 6)                     # choose 6 numbers from 49, order does not matter
print(f"lottery 6 from 49: 1 chance in {tickets}, that is {1 / tickets:.10f}")
print("four digit PIN codes:", 10 ** 4)
''', js=r'''
const factorial = n => (n <= 1 ? 1 : n * factorial(n - 1));
const perm = (n, k) => factorial(n) / factorial(n - k);
function comb(n, k) {                     // multiply and divide step by step to stay exact
  let r = 1;
  for (let i = 1; i <= k; i++) r = r * (n - k + i) / i;
  return Math.round(r);
}

console.log("ways to line up 5 friends: 5! =", factorial(5));
console.log("podium (gold, silver, bronze) from 10 runners: P(10, 3) =", perm(10, 3));
console.log("teams of 3 from 10 people: C(10, 3) =", comb(10, 3));
const tickets = comb(49, 6);              // choose 6 numbers from 49, order does not matter
console.log(`lottery 6 from 49: 1 chance in ${tickets}, that is ${(1 / tickets).toFixed(10)}`);
console.log("four digit PIN codes:", 10 ** 4);
''', ts=r'''
const factorial = (n: number): number => (n <= 1 ? 1 : n * factorial(n - 1));
const perm = (n: number, k: number): number => factorial(n) / factorial(n - k);
function comb(n: number, k: number): number {   // multiply and divide step by step to stay exact
  let r: number = 1;
  for (let i = 1; i <= k; i++) r = r * (n - k + i) / i;
  return Math.round(r);
}

console.log("ways to line up 5 friends: 5! =", factorial(5));
console.log("podium (gold, silver, bronze) from 10 runners: P(10, 3) =", perm(10, 3));
console.log("teams of 3 from 10 people: C(10, 3) =", comb(10, 3));
const tickets: number = comb(49, 6);      // choose 6 numbers from 49, order does not matter
console.log(`lottery 6 from 49: 1 chance in ${tickets}, that is ${(1 / tickets).toFixed(10)}`);
console.log("four digit PIN codes:", 10 ** 4);
''', java=r'''
public class Counting {
    static long factorial(int n) {
        return n <= 1 ? 1 : n * factorial(n - 1);
    }

    static long comb(int n, int k) {          // multiply and divide step by step to stay exact
        long r = 1;
        for (int i = 1; i <= k; i++) r = r * (n - k + i) / i;
        return r;
    }

    public static void main(String[] args) {
        System.out.println("ways to line up 5 friends: 5! = " + factorial(5));
        System.out.println("podium (gold, silver, bronze) from 10 runners: P(10, 3) = " + factorial(10) / factorial(7));
        System.out.println("teams of 3 from 10 people: C(10, 3) = " + comb(10, 3));
        long tickets = comb(49, 6);           // choose 6 numbers from 49, order does not matter
        System.out.println(String.format("lottery 6 from 49: 1 chance in %d, that is %.10f", tickets, 1.0 / tickets));
        System.out.println("four digit PIN codes: " + (int) Math.pow(10, 4));
    }
}
''')

K.code('conditional', py=r'''
# 200 students: did they study, and did they pass?
table = {("studied", "pass"): 90, ("studied", "fail"): 10,
         ("no study", "pass"): 40, ("no study", "fail"): 60}
total = sum(table.values())
passed = table[("studied", "pass")] + table[("no study", "pass")]
studied = table[("studied", "pass")] + table[("studied", "fail")]
print(f"P(pass)           = {passed}/{total} = {passed / total:.4f}")
print(f"P(pass | studied) = {table[('studied', 'pass')]}/{studied} = {table[('studied', 'pass')] / studied:.4f}")
print(f"P(pass | no study) = {table[('no study', 'pass')]}/{total - studied} = {table[('no study', 'pass')] / (total - studied):.4f}")
print(f"P(studied | pass) = {table[('studied', 'pass')]}/{passed} = {table[('studied', 'pass')] / passed:.4f}")
''', js=r'''
// 200 students: did they study, and did they pass?
const table = { "studied,pass": 90, "studied,fail": 10, "no study,pass": 40, "no study,fail": 60 };
const total = Object.values(table).reduce((s, v) => s + v, 0);
const passed = table["studied,pass"] + table["no study,pass"];
const studied = table["studied,pass"] + table["studied,fail"];
console.log(`P(pass)           = ${passed}/${total} = ${(passed / total).toFixed(4)}`);
console.log(`P(pass | studied) = ${table["studied,pass"]}/${studied} = ${(table["studied,pass"] / studied).toFixed(4)}`);
console.log(`P(pass | no study) = ${table["no study,pass"]}/${total - studied} = ${(table["no study,pass"] / (total - studied)).toFixed(4)}`);
console.log(`P(studied | pass) = ${table["studied,pass"]}/${passed} = ${(table["studied,pass"] / passed).toFixed(4)}`);
''', ts=r'''
// 200 students: did they study, and did they pass?
const table: Record<string, number> = { "studied,pass": 90, "studied,fail": 10, "no study,pass": 40, "no study,fail": 60 };
const total: number = Object.values(table).reduce((s, v) => s + v, 0);
const passed: number = table["studied,pass"] + table["no study,pass"];
const studied: number = table["studied,pass"] + table["studied,fail"];
console.log(`P(pass)           = ${passed}/${total} = ${(passed / total).toFixed(4)}`);
console.log(`P(pass | studied) = ${table["studied,pass"]}/${studied} = ${(table["studied,pass"] / studied).toFixed(4)}`);
console.log(`P(pass | no study) = ${table["no study,pass"]}/${total - studied} = ${(table["no study,pass"] / (total - studied)).toFixed(4)}`);
console.log(`P(studied | pass) = ${table["studied,pass"]}/${passed} = ${(table["studied,pass"] / passed).toFixed(4)}`);
''', java=r'''
import java.util.LinkedHashMap;
import java.util.Map;

public class Conditional {
    public static void main(String[] args) {
        // 200 students: did they study, and did they pass?
        Map<String, Integer> table = new LinkedHashMap<>();
        table.put("studied,pass", 90);
        table.put("studied,fail", 10);
        table.put("no study,pass", 40);
        table.put("no study,fail", 60);
        int total = 0;
        for (int v : table.values()) total += v;
        int passed = table.get("studied,pass") + table.get("no study,pass");
        int studied = table.get("studied,pass") + table.get("studied,fail");
        System.out.println(String.format("P(pass)           = %d/%d = %.4f", passed, total, (double) passed / total));
        System.out.println(String.format("P(pass | studied) = %d/%d = %.4f", table.get("studied,pass"), studied, (double) table.get("studied,pass") / studied));
        System.out.println(String.format("P(pass | no study) = %d/%d = %.4f", table.get("no study,pass"), total - studied, (double) table.get("no study,pass") / (total - studied)));
        System.out.println(String.format("P(studied | pass) = %d/%d = %.4f", table.get("studied,pass"), passed, (double) table.get("studied,pass") / passed));
    }
}
''')

K.code('bayes_test', py=r'''
prior = 0.01                              # 1 in 100 people have the disease
sensitivity = 0.99                        # P(positive | sick)
specificity = 0.95                        # P(negative | healthy)
p_pos = sensitivity * prior + (1 - specificity) * (1 - prior)   # all the ways to test positive
posterior = sensitivity * prior / p_pos   # Bayes: P(sick | positive)
print(f"P(positive)        = {p_pos:.4f}")
print(f"P(sick | positive) = {posterior:.4f}")
people = 10000                            # the same thing with whole people
sick = people * prior
print(f"of {people} people: {sick:.0f} sick, {sensitivity * sick:.0f} of them test positive")
print(f"{people - sick:.0f} healthy, {(1 - specificity) * (people - sick):.0f} of them test positive by mistake")
''', js=r'''
const prior = 0.01;                       // 1 in 100 people have the disease
const sensitivity = 0.99;                 // P(positive | sick)
const specificity = 0.95;                 // P(negative | healthy)
const pPos = sensitivity * prior + (1 - specificity) * (1 - prior);   // all the ways to test positive
const posterior = sensitivity * prior / pPos;   // Bayes: P(sick | positive)
console.log(`P(positive)        = ${pPos.toFixed(4)}`);
console.log(`P(sick | positive) = ${posterior.toFixed(4)}`);
const people = 10000;                     // the same thing with whole people
const sick = people * prior;
console.log(`of ${people} people: ${sick.toFixed(0)} sick, ${(sensitivity * sick).toFixed(0)} of them test positive`);
console.log(`${(people - sick).toFixed(0)} healthy, ${((1 - specificity) * (people - sick)).toFixed(0)} of them test positive by mistake`);
''', ts=r'''
const prior: number = 0.01;               // 1 in 100 people have the disease
const sensitivity: number = 0.99;         // P(positive | sick)
const specificity: number = 0.95;         // P(negative | healthy)
const pPos: number = sensitivity * prior + (1 - specificity) * (1 - prior);   // all the ways to test positive
const posterior: number = sensitivity * prior / pPos;   // Bayes: P(sick | positive)
console.log(`P(positive)        = ${pPos.toFixed(4)}`);
console.log(`P(sick | positive) = ${posterior.toFixed(4)}`);
const people: number = 10000;             // the same thing with whole people
const sick: number = people * prior;
console.log(`of ${people} people: ${sick.toFixed(0)} sick, ${(sensitivity * sick).toFixed(0)} of them test positive`);
console.log(`${(people - sick).toFixed(0)} healthy, ${((1 - specificity) * (people - sick)).toFixed(0)} of them test positive by mistake`);
''', java=r'''
public class BayesTest {
    public static void main(String[] args) {
        double prior = 0.01;                      // 1 in 100 people have the disease
        double sensitivity = 0.99;                // P(positive | sick)
        double specificity = 0.95;                // P(negative | healthy)
        double pPos = sensitivity * prior + (1 - specificity) * (1 - prior);   // all the ways to test positive
        double posterior = sensitivity * prior / pPos;   // Bayes: P(sick | positive)
        System.out.println(String.format("P(positive)        = %.4f", pPos));
        System.out.println(String.format("P(sick | positive) = %.4f", posterior));
        int people = 10000;                       // the same thing with whole people
        double sick = people * prior;
        System.out.println(String.format("of %d people: %.0f sick, %.0f of them test positive", people, sick, sensitivity * sick));
        System.out.println(String.format("%.0f healthy, %.0f of them test positive by mistake", people - sick, (1 - specificity) * (people - sick)));
    }
}
''')

K.code('monte_carlo', py=r'''
seed = 2026


def rand():                               # a small repeatable random number maker (Park and Miller)
    global seed
    seed = seed * 16807 % 2147483647
    return seed / 2147483647


inside = 0
for i in range(1, 101):
    x, y = rand(), rand()                 # a random dart in the unit square
    if x * x + y * y <= 1:                # did it land inside the quarter circle?
        inside += 1
    if i in (10, 50, 100):
        print(f"{i:3} darts: {inside} inside, pi is about {4 * inside / i:.2f}")
''', js=r'''
let seed = 2026;

function rand() {                         // a small repeatable random number maker (Park and Miller)
  seed = seed * 16807 % 2147483647;
  return seed / 2147483647;
}

let inside = 0;
for (let i = 1; i <= 100; i++) {
  const x = rand(), y = rand();           // a random dart in the unit square
  if (x * x + y * y <= 1) {               // did it land inside the quarter circle?
    inside += 1;
  }
  if ([10, 50, 100].includes(i)) {
    console.log(`${String(i).padStart(3)} darts: ${inside} inside, pi is about ${(4 * inside / i).toFixed(2)}`);
  }
}
''', ts=r'''
let seed: number = 2026;

function rand(): number {                 // a small repeatable random number maker (Park and Miller)
  seed = seed * 16807 % 2147483647;
  return seed / 2147483647;
}

let inside: number = 0;
for (let i = 1; i <= 100; i++) {
  const x: number = rand(), y: number = rand();   // a random dart in the unit square
  if (x * x + y * y <= 1) {               // did it land inside the quarter circle?
    inside += 1;
  }
  if ([10, 50, 100].includes(i)) {
    console.log(`${String(i).padStart(3)} darts: ${inside} inside, pi is about ${(4 * inside / i).toFixed(2)}`);
  }
}
''', java=r'''
public class MonteCarlo {
    static long seed = 2026;

    static double rand() {                    // a small repeatable random number maker (Park and Miller)
        seed = seed * 16807 % 2147483647;
        return seed / 2147483647.0;
    }

    public static void main(String[] args) {
        int inside = 0;
        for (int i = 1; i <= 100; i++) {
            double x = rand(), y = rand();        // a random dart in the unit square
            if (x * x + y * y <= 1) {             // did it land inside the quarter circle?
                inside += 1;
            }
            if (i == 10 || i == 50 || i == 100) {
                System.out.println(String.format("%3d darts: %d inside, pi is about %.2f", i, inside, 4.0 * inside / i));
            }
        }
    }
}
''')

K.code('p_cards', py=r'''
from fractions import Fraction

deck = 52
aces, hearts, ace_of_hearts = 4, 13, 1
p_ace = Fraction(aces, deck)
p_heart = Fraction(hearts, deck)
p_both = Fraction(ace_of_hearts, deck)
p_either = p_ace + p_heart - p_both       # addition rule: do not count the ace of hearts twice
print("P(ace)         =", p_ace)
print("P(heart)       =", p_heart)
print("P(ace and heart) =", p_both, "=", p_ace * p_heart, "so they are independent")
print("P(ace or heart)  =", p_either)
''', js=r'''
const gcd = (a, b) => (b === 0 ? a : gcd(b, a % b));
const frac = (a, b) => { const g = gcd(a, b); return `${a / g}/${b / g}`; };

const deck = 52;
const aces = 4, hearts = 13, aceOfHearts = 1;
const either = aces + hearts - aceOfHearts;   // addition rule: do not count the ace of hearts twice
console.log("P(ace)         =", frac(aces, deck));
console.log("P(heart)       =", frac(hearts, deck));
console.log("P(ace and heart) =", frac(aceOfHearts, deck), "=", frac(aces * hearts, deck * deck), "so they are independent");
console.log("P(ace or heart)  =", frac(either, deck));
''', ts=r'''
const gcd = (a: number, b: number): number => (b === 0 ? a : gcd(b, a % b));
const frac = (a: number, b: number): string => { const g: number = gcd(a, b); return `${a / g}/${b / g}`; };

const deck: number = 52;
const aces: number = 4, hearts: number = 13, aceOfHearts: number = 1;
const either: number = aces + hearts - aceOfHearts;   // addition rule: do not count the ace of hearts twice
console.log("P(ace)         =", frac(aces, deck));
console.log("P(heart)       =", frac(hearts, deck));
console.log("P(ace and heart) =", frac(aceOfHearts, deck), "=", frac(aces * hearts, deck * deck), "so they are independent");
console.log("P(ace or heart)  =", frac(either, deck));
''', java=r'''
public class PracticeCards {
    static int gcd(int a, int b) {
        return b == 0 ? a : gcd(b, a % b);
    }

    static String frac(int a, int b) {
        int g = gcd(a, b);
        return (a / g) + "/" + (b / g);
    }

    public static void main(String[] args) {
        int deck = 52;
        int aces = 4, hearts = 13, aceOfHearts = 1;
        int either = aces + hearts - aceOfHearts;   // addition rule: do not count the ace of hearts twice
        System.out.println("P(ace)         = " + frac(aces, deck));
        System.out.println("P(heart)       = " + frac(hearts, deck));
        System.out.println("P(ace and heart) = " + frac(aceOfHearts, deck) + " = " + frac(aces * hearts, deck * deck) + " so they are independent");
        System.out.println("P(ace or heart)  = " + frac(either, deck));
    }
}
''')

K.code('p_birthday', py=r'''
p_all_different = 1.0
for k in range(50):                       # person k + 1 must miss the k birthdays already taken
    p_all_different *= (365 - k) / 365
    people = k + 1
    if people in (10, 23, 50):
        print(f"{people} people: P(at least two share a birthday) = {1 - p_all_different:.4f}")
''', js=r'''
let pAllDifferent = 1.0;
for (let k = 0; k < 50; k++) {            // person k + 1 must miss the k birthdays already taken
  pAllDifferent *= (365 - k) / 365;
  const people = k + 1;
  if ([10, 23, 50].includes(people)) {
    console.log(`${people} people: P(at least two share a birthday) = ${(1 - pAllDifferent).toFixed(4)}`);
  }
}
''', ts=r'''
let pAllDifferent: number = 1.0;
for (let k = 0; k < 50; k++) {            // person k + 1 must miss the k birthdays already taken
  pAllDifferent *= (365 - k) / 365;
  const people: number = k + 1;
  if ([10, 23, 50].includes(people)) {
    console.log(`${people} people: P(at least two share a birthday) = ${(1 - pAllDifferent).toFixed(4)}`);
  }
}
''', java=r'''
public class PracticeBirthday {
    public static void main(String[] args) {
        double pAllDifferent = 1.0;
        for (int k = 0; k < 50; k++) {        // person k + 1 must miss the k birthdays already taken
            pAllDifferent *= (365.0 - k) / 365;
            int people = k + 1;
            if (people == 10 || people == 23 || people == 50) {
                System.out.println(String.format("%d people: P(at least two share a birthday) = %.4f", people, 1 - pAllDifferent));
            }
        }
    }
}
''')

K.code('p_bayes_two', py=r'''
def update(prior, sens=0.99, spec=0.95):  # one positive test result
    return sens * prior / (sens * prior + (1 - spec) * (1 - prior))


belief = 0.01                             # before any test
for test in range(1, 4):
    belief = update(belief)               # today's posterior is tomorrow's prior
    print(f"after positive test {test}: P(sick) = {belief:.4f}")
''', js=r'''
function update(prior, sens = 0.99, spec = 0.95) {   // one positive test result
  return sens * prior / (sens * prior + (1 - spec) * (1 - prior));
}

let belief = 0.01;                        // before any test
for (let test = 1; test <= 3; test++) {
  belief = update(belief);                // today's posterior is tomorrow's prior
  console.log(`after positive test ${test}: P(sick) = ${belief.toFixed(4)}`);
}
''', ts=r'''
function update(prior: number, sens: number = 0.99, spec: number = 0.95): number {   // one positive test result
  return sens * prior / (sens * prior + (1 - spec) * (1 - prior));
}

let belief: number = 0.01;                // before any test
for (let test = 1; test <= 3; test++) {
  belief = update(belief);                // today's posterior is tomorrow's prior
  console.log(`after positive test ${test}: P(sick) = ${belief.toFixed(4)}`);
}
''', java=r'''
public class PracticeBayesTwo {
    static double update(double prior, double sens, double spec) {   // one positive test result
        return sens * prior / (sens * prior + (1 - spec) * (1 - prior));
    }

    public static void main(String[] args) {
        double belief = 0.01;                     // before any test
        for (int test = 1; test <= 3; test++) {
            belief = update(belief, 0.99, 0.95);  // today's posterior is tomorrow's prior
            System.out.println(String.format("after positive test %d: P(sick) = %.4f", test, belief));
        }
    }
}
''')

K.code('p_naive', py=r'''
# word counts from training messages (each class saw 12 words in total)
counts = {"spam": {"free": 6, "win": 4, "meeting": 1, "lunch": 1},
          "ham": {"free": 1, "win": 1, "meeting": 6, "lunch": 4}}
prior = {"spam": 0.4, "ham": 0.6}
vocab = 4


def p_word(word, label):                  # Laplace smoothing: add 1 so no word has chance 0
    return (counts[label][word] + 1) / (sum(counts[label].values()) + vocab)


for message in [["free", "lunch"], ["win", "free"]]:
    score = {}
    for label in ("spam", "ham"):
        s = prior[label]
        for word in message:
            s *= p_word(word, label)      # naive: multiply as if the words were independent
        score[label] = s
    p_spam = score["spam"] / (score["spam"] + score["ham"])
    print(f"{' '.join(message)}: spam score {score['spam']:.6f}, ham score {score['ham']:.6f}, P(spam) = {p_spam:.4f}")
''', js=r'''
// word counts from training messages (each class saw 12 words in total)
const counts = { spam: { free: 6, win: 4, meeting: 1, lunch: 1 },
                 ham: { free: 1, win: 1, meeting: 6, lunch: 4 } };
const prior = { spam: 0.4, ham: 0.6 };
const vocab = 4;

function pWord(word, label) {             // Laplace smoothing: add 1 so no word has chance 0
  const total = Object.values(counts[label]).reduce((s, v) => s + v, 0);
  return (counts[label][word] + 1) / (total + vocab);
}

for (const message of [["free", "lunch"], ["win", "free"]]) {
  const score = {};
  for (const label of ["spam", "ham"]) {
    let s = prior[label];
    for (const word of message) {
      s *= pWord(word, label);            // naive: multiply as if the words were independent
    }
    score[label] = s;
  }
  const pSpam = score.spam / (score.spam + score.ham);
  console.log(`${message.join(" ")}: spam score ${score.spam.toFixed(6)}, ham score ${score.ham.toFixed(6)}, P(spam) = ${pSpam.toFixed(4)}`);
}
''', ts=r'''
// word counts from training messages (each class saw 12 words in total)
type Label = "spam" | "ham";
const counts: Record<Label, Record<string, number>> = { spam: { free: 6, win: 4, meeting: 1, lunch: 1 },
                                                        ham: { free: 1, win: 1, meeting: 6, lunch: 4 } };
const prior: Record<Label, number> = { spam: 0.4, ham: 0.6 };
const vocab: number = 4;

function pWord(word: string, label: Label): number {   // Laplace smoothing: add 1 so no word has chance 0
  const total: number = Object.values(counts[label]).reduce((s, v) => s + v, 0);
  return (counts[label][word] + 1) / (total + vocab);
}

for (const message of [["free", "lunch"], ["win", "free"]]) {
  const score: Record<Label, number> = { spam: 0, ham: 0 };
  for (const label of ["spam", "ham"] as Label[]) {
    let s: number = prior[label];
    for (const word of message) {
      s *= pWord(word, label);            // naive: multiply as if the words were independent
    }
    score[label] = s;
  }
  const pSpam: number = score.spam / (score.spam + score.ham);
  console.log(`${message.join(" ")}: spam score ${score.spam.toFixed(6)}, ham score ${score.ham.toFixed(6)}, P(spam) = ${pSpam.toFixed(4)}`);
}
''', java=r'''
import java.util.Map;

public class PracticeNaive {
    // word counts from training messages (each class saw 12 words in total)
    static Map<String, Map<String, Integer>> counts = Map.of(
        "spam", Map.of("free", 6, "win", 4, "meeting", 1, "lunch", 1),
        "ham", Map.of("free", 1, "win", 1, "meeting", 6, "lunch", 4));
    static Map<String, Double> prior = Map.of("spam", 0.4, "ham", 0.6);
    static int vocab = 4;

    static double pWord(String word, String label) {   // Laplace smoothing: add 1 so no word has chance 0
        int total = 0;
        for (int v : counts.get(label).values()) total += v;
        return (counts.get(label).get(word) + 1.0) / (total + vocab);
    }

    public static void main(String[] args) {
        String[][] messages = {{"free", "lunch"}, {"win", "free"}};
        for (String[] message : messages) {
            double[] score = new double[2];
            String[] labels = {"spam", "ham"};
            for (int l = 0; l < 2; l++) {
                double s = prior.get(labels[l]);
                for (String word : message) {
                    s *= pWord(word, labels[l]);  // naive: multiply as if the words were independent
                }
                score[l] = s;
            }
            double pSpam = score[0] / (score[0] + score[1]);
            System.out.println(String.format("%s: spam score %.6f, ham score %.6f, P(spam) = %.4f", String.join(" ", message), score[0], score[1], pSpam));
        }
    }
}
''')

# ---------------------------------------------------------------- lesson text
PARTS = [
    part('basics', '🎲', 'Chance, outcomes and events', f'''
<p><b>Probability</b> is a number from 0 to 1 that says how likely something is. 0 means impossible, 1 means certain, and 0.5 means as likely as not. The list of everything that could happen is the <b>sample space</b>, and any group of outcomes you care about is an <b>event</b>.</p>
{fxs(fx('Equally likely outcomes', f'P(A) = {frac("number of outcomes in A", "total number of outcomes")}', 'A fair die: P(even) = 3/6 = 0.5.'),
         fx('Complement', 'P(not A) = 1 − P(A)', 'Often the easy way round: P(at least one six in 4 rolls) = 1 − (5/6)⁴ ≈ 0.518.'))}
{viz('dice')}
{table(['Experiment', 'Sample space', 'Event', 'Probability'], [
        ['toss a coin', '{{H, T}}', 'heads', '1/2'],
        ['roll a die', '{{1, 2, 3, 4, 5, 6}}', 'more than 4', '2/6 = 1/3'],
        ['roll two dice', '36 ordered pairs', 'sum is 7', '6/36 = 1/6'],
        ['pick a card', '52 cards', 'a king', '4/52 = 1/13'],
    ])}
<div class="tip">In the long run, the share of times an event happens settles near its probability. This is the <b>law of large numbers</b>, and the dice animation shows it: with 10 rolls the bars are uneven, with 1000 rolls they are nearly level.</div>
{life('A weather forecast of "70% chance of rain" means that on many days with conditions like today, about 7 in 10 had rain.')}
''', kw=['probability', 'sample space', 'event', 'outcome', 'complement', 'law of large numbers', 'dice']),

    part('rules', '➕', 'AND, OR and independence', f'''
<p>Two rules combine simple probabilities into bigger ones. OR means "at least one happens". AND means "both happen".</p>
{fxs(fx('Addition rule (OR)', 'P(A ∪ B) = P(A) + P(B) − P(A ∩ B)', 'Subtract the overlap so it is not counted twice. If A and B cannot happen together (mutually exclusive), the overlap is 0.'),
         fx('Multiplication rule (AND)', 'P(A ∩ B) = P(A) × P(B | A)', 'If A and B are independent, P(B | A) = P(B) and this becomes P(A) × P(B).'))}
{viz('venn')}
{table(['Words', 'Meaning', 'Example'], [
        ['mutually exclusive', 'cannot both happen, P(A ∩ B) = 0', 'rolling a 2 and rolling a 5 on one die'],
        ['independent', 'knowing one tells you nothing about the other', 'two separate coin tosses'],
        ['dependent', 'one changes the chance of the other', 'drawing two cards without putting the first back'],
    ])}
<div class="warn">Mutually exclusive events are NOT independent. If A happens, B cannot, so knowing A tells you a lot about B.</div>
{code('p_cards', 'Card probabilities with exact fractions')}
{trick('OR adds (then subtract the overlap). AND multiplies (when independent).')}
''', kw=['addition rule', 'multiplication rule', 'union', 'intersection', 'independent events', 'mutually exclusive', 'venn diagram']),

    part('counting', '🔢', 'Counting: permutations and combinations', f'''
<p>When outcomes are equally likely, probability is just counting. Three tools do most of the counting.</p>
{fxs(fx('Factorial', 'n! = n × (n − 1) × … × 2 × 1', 'Ways to arrange n different things in a row. 5! = 120. By agreement 0! = 1.'),
         fx('Permutations (order matters)', f'P(n, k) = {frac("n!", "(n − k)!")}', 'Gold, silver and bronze from 10 runners: 10 × 9 × 8 = 720.'),
         fx('Combinations (order does not matter)', f'C(n, k) = {frac("n!", "k! (n − k)!")}', 'A team of 3 from 10 people: 720 ÷ 3! = 120. Also written ⁿCₖ or "n choose k".'))}
{worked('What is the chance of winning a 6 from 49 lottery with one ticket?', [
        'Order does not matter, so count combinations: <span class="eq">C(49, 6) = (49 × 48 × 47 × 46 × 45 × 44) ÷ (6 × 5 × 4 × 3 × 2 × 1)</span>',
        'Top: <span class="eq">10068347520</span>. Bottom: <span class="eq">720</span>',
        'Divide: <span class="eq">13983816</span> possible tickets',
        'One ticket wins with probability <span class="eq">1 ÷ 13983816 ≈ 0.0000000715</span>'])}
{code('counting', 'Factorials, permutations, combinations and the lottery')}
{trick('Ask "does the order matter?" A podium, a PIN and a password are permutations. A team, a hand of cards and a lottery ticket are combinations.')}
{ml('Counting explains why brute force fails. A model choosing 10 features out of 100 has C(100, 10) ≈ 17 trillion subsets to try, which is why feature selection uses clever search instead.')}
''', kw=['factorial', 'permutation', 'combination', 'n choose k', 'counting', 'lottery odds']),

    part('conditional', '🔍', 'Conditional probability', f'''
<p>A <b>conditional probability</b> answers "how likely is A, now that I know B happened?" Knowing B shrinks the world down to just the outcomes where B is true.</p>
{fx('Conditional probability', f'P(A | B) = {frac("P(A ∩ B)", "P(B)")}', 'Read the bar | as "given". Out of the B world, what share is also A?')}
{table(['', 'Passed', 'Failed', 'Total'], [
        ['<b>Studied</b>', '90', '10', '100'],
        ['<b>Did not study</b>', '40', '60', '100'],
        ['<b>Total</b>', '130', '70', '200'],
    ])}
{worked('Reading the table', [
        'Overall pass rate: <span class="eq">P(pass) = 130 ÷ 200 = 0.65</span>',
        'Given studied, look only at that row: <span class="eq">P(pass | studied) = 90 ÷ 100 = 0.9</span>',
        'Given not studied: <span class="eq">P(pass | no study) = 40 ÷ 100 = 0.4</span>',
        'The other way round, look only at the Passed column: <span class="eq">P(studied | pass) = 90 ÷ 130 ≈ 0.692</span>',
        'P(pass | studied) ≠ P(pass), so passing and studying are <b>not</b> independent.'])}
{code('conditional', 'Conditional probabilities from a table')}
<div class="warn">P(A | B) and P(B | A) are different numbers. Most people who are fluent in French have been to France, but most people who have been to France are not fluent in French. Mixing them up is called the <b>prosecutor fallacy</b>.</div>
''', kw=['conditional probability', 'given', 'contingency table', 'P(A|B)', 'independence test', 'prosecutor fallacy']),

    part('bayes', '🔄', "Bayes' theorem: updating beliefs", f'''
<p><b>The theorem of Bayes</b> turns P(B | A) around into P(A | B). It is the rule for updating what you believe when new evidence arrives: start with a <b>prior</b>, see evidence, and get a <b>posterior</b>.</p>
{fx("Bayes' theorem", f'P(A | B) = {frac("P(B | A) × P(A)", "P(B)")} &nbsp;&nbsp; with &nbsp;&nbsp; P(B) = P(B | A)P(A) + P(B | not A)P(not A)', 'posterior = likelihood × prior ÷ evidence.')}
{viz('bayes')}
{worked('A disease affects 1% of people. A test catches 99% of sick people and wrongly flags 5% of healthy people. You test positive. How likely are you to be sick?', [
        'Prior: <span class="eq">P(sick) = 0.01</span>. Likelihoods: <span class="eq">P(+ | sick) = 0.99</span> and <span class="eq">P(+ | healthy) = 0.05</span>',
        'All ways to test positive: <span class="eq">P(+) = 0.99 × 0.01 + 0.05 × 0.99 = 0.0099 + 0.0495 = 0.0594</span>',
        'Bayes: <span class="eq">P(sick | +) = 0.0099 ÷ 0.0594 ≈ 0.167</span>',
        'Only about 1 in 6! In 10000 people: 99 sick people test positive, but so do 495 healthy people.',
        'A second independent positive test raises it to about 80%, because the posterior becomes the new prior.'])}
{code('bayes_test', "Bayes' theorem as a formula and as whole people")}
{trick('Think in whole people, not percentages. Draw 10000 people, split them into sick and healthy, then split each group by test result. The answer is just one count divided by another.')}
''', kw=["bayes theorem", 'prior', 'posterior', 'likelihood', 'evidence', 'base rate', 'false positive', 'medical test']),

    part('naive', '📧', 'Naive Bayes: a classifier from counting', f'''
<p><b>Naive Bayes</b> uses the theorem of Bayes to classify, for example spam or not spam. It makes one bold (naive) simplification: given the class, every word is independent of the others. That is rarely exactly true, yet the classifier works surprisingly well and trains in one pass of counting.</p>
{fxs(fx('Naive Bayes score', 'score(class) = P(class) × Π P(wordᵢ | class)', 'Compute it for every class and pick the biggest. Dividing by the total turns scores into probabilities.'),
         fx('Laplace (add one) smoothing', f'P(word | class) = {frac("count + 1", "total words in class + vocabulary size")}', 'Without the +1, one unseen word would make the whole product 0.'))}
{worked('Is "win free" spam? Spam saw free 6, win 4, meeting 1, lunch 1. Ham saw free 1, win 1, meeting 6, lunch 4. Priors 0.4 and 0.6.', [
        'Smoothed spam chances (12 words + 4 vocabulary = 16): <span class="eq">P(win | spam) = 5/16</span>, <span class="eq">P(free | spam) = 7/16</span>',
        'Smoothed ham chances: <span class="eq">P(win | ham) = 2/16</span>, <span class="eq">P(free | ham) = 2/16</span>',
        'Spam score: <span class="eq">0.4 × 5/16 × 7/16 = 0.4 × 35/256 ≈ 0.0547</span>',
        'Ham score: <span class="eq">0.6 × 2/16 × 2/16 = 0.6 × 4/256 ≈ 0.0094</span>',
        'P(spam) = <span class="eq">0.0547 ÷ (0.0547 + 0.0094) ≈ 0.854</span>. Flag it as spam.'])}
{code('p_naive', 'A tiny naive Bayes spam filter')}
{ml('Multiplying many small probabilities underflows to 0 on a computer. Real implementations add logarithms instead: log score = log P(class) + Σ log P(wordᵢ | class). The biggest log score still wins.')}
''', kw=['naive bayes', 'spam filter', 'laplace smoothing', 'text classification', 'conditional independence', 'log probabilities']),

    part('ml', '🤖', 'Probability inside machine learning', f'''
<p>Most models do not just say "cat". They say "cat with probability 0.92". Probability is how machine learning expresses uncertainty.</p>
{table(['Idea', 'Where it appears'], [
        ['Predicted probabilities', 'logistic regression and softmax outputs (Chapter 12)'],
        ['Likelihood', 'training often maximises P(data | weights), the maximum likelihood idea of Chapter 11'],
        ['Prior and posterior', 'Bayesian models and regularisation, where a prior belief keeps weights small'],
        ['Sampling', 'dropout, data augmentation, and how language models pick the next word'],
        ['Monte Carlo', 'estimating hard averages by simulating many random cases'],
        ['Calibration', 'checking that "90% sure" predictions are right about 90% of the time'],
    ])}
{fx('Monte Carlo estimate', f'average of f(random samples) → true average as samples grow', 'Throw random darts at a square: the share landing inside the quarter circle tends to π/4.')}
{code('monte_carlo', 'Estimating π with random darts')}
{code('p_birthday', 'The birthday surprise')}
{trick('When a probability is too hard to work out on paper, simulate it a million times and count.')}
''', kw=['monte carlo', 'simulation', 'predicted probability', 'calibration', 'likelihood', 'sampling', 'birthday problem']),
]

INFO = {
    'title': 'Probability measures how likely, Bayes updates it',
    'panels': [
        {'s': [['e', '🎲'], ['t', 'P = favourable ÷ total', {'b': 1}]], 'h': 'Chance', 't': 'A number from 0 to 1.', 'more': 'P(not A) = 1 − P(A).'},
        {'s': [['e', '➕'], ['t', 'OR adds, AND multiplies', {'b': 1}]], 'h': 'Rules', 't': 'Subtract the overlap.', 'more': 'Multiply only when independent.'},
        {'s': [['e', '🔍'], ['t', 'P(A|B) = P(A∩B) ÷ P(B)', {'b': 1}]], 'h': 'Given', 't': 'Shrink the world to B.', 'more': 'P(A|B) is not P(B|A).'},
        {'s': [['e', '🔄'], ['t', 'posterior ∝ likelihood × prior', {'b': 1}]], 'h': 'Bayes', 't': 'Update with evidence.', 'more': 'Rare diseases make most positives false.'},
    ],
    'remember': 'Probability runs from 0 to 1. The addition rule subtracts the overlap, the multiplication rule multiplies (directly only for independent events). Count with factorials, permutations and combinations. P(A | B) = P(A ∩ B) ÷ P(B). Bayes turns P(B | A) into P(A | B), and the base rate matters hugely.',
}

REAL = [
    ['🩺', 'Medical screening', 'Doctors follow a positive screening result with a second test, because with a rare condition most first positives are false alarms, exactly as Bayes predicts.'],
    ['📧', 'Spam filters', 'Early email spam filters were naive Bayes classifiers that learned word chances from messages users marked as spam.'],
    ['🎰', 'Lotteries and games', 'Casinos and lotteries set prizes using exact counts of outcomes, so the house keeps an edge on average.'],
]

K.say('top', 'Welcome',
      'Probability is the maths of uncertainty. You will roll virtual dice, combine chances with AND and OR, count with combinations, and use Bayes theorem to update beliefs when evidence arrives. Then you will build a tiny spam filter from counting alone.',
      'Probability अनिश्चितता का गणित है। आप virtual dice फेंकेंगे, AND और OR से संभावनाएँ जोड़ेंगे, combinations से गिनेंगे, और Bayes theorem से नए सबूत पर विश्वास बदलेंगे। फिर गिनती से एक छोटा spam filter बनाएँगे।',
      'Probability ಅನಿಶ್ಚಿತತೆಯ ಗಣಿತ. Dice, AND ಮತ್ತು OR, combinations ಮತ್ತು Bayes theorem ಕಲಿತು spam filter ಮಾಡುತ್ತೀರಿ.',
      'Probability ଅନିଶ୍ଚିତତାର ଗଣିତ। Dice, AND ଓ OR, combinations ଓ Bayes theorem ଶିଖି spam filter ତିଆରି କରିବେ।',
      'الاحتمال هو رياضيات عدم اليقين. سترمي نردًا افتراضيًا، وتجمع الاحتمالات بـ و وأو، وتعد بالتوافيق، وتستخدم مبرهنة بايز لتحديث القناعات عند ظهور دليل، ثم تبني مرشح رسائل مزعجة صغيرًا من العد وحده.',
      'Wahrscheinlichkeit ist die Mathematik der Unsicherheit. Du würfelst virtuell, verknüpfst Chancen mit UND und ODER, zählst mit Kombinationen und nutzt den Satz von Bayes, um Annahmen bei neuen Belegen anzupassen. Dann baust du nur durch Zählen einen kleinen Spamfilter.')
K.say('basics', 'Chance',
      'A probability is a number from zero to one. With equally likely outcomes it is the favourable outcomes divided by all outcomes. Roll the dice many times and the shares settle near the true chances. That is the law of large numbers.',
      'Probability शून्य से एक के बीच की संख्या है। बराबर संभावना वाले परिणामों में यह अनुकूल परिणाम बटा कुल परिणाम है। Dice बार बार फेंकें तो हिस्से असली संभावना के पास आ जाते हैं।',
      'Probability ಸೊನ್ನೆಯಿಂದ ಒಂದರವರೆಗಿನ ಸಂಖ್ಯೆ. ಅನುಕೂಲ ಫಲಿತಾಂಶ ಭಾಗಿಸು ಒಟ್ಟು. ಹೆಚ್ಚು ಬಾರಿ ಎಸೆದರೆ ನಿಜ ಸಂಭವನೀಯತೆಗೆ ಹತ್ತಿರ.',
      'Probability ଶୂନରୁ ଏକ ମଧ୍ୟରେ ସଂଖ୍ୟା। ଅନୁକୂଳ ଫଳାଫଳ ଭାଗ ମୋଟ। ଅଧିକ ଥର ଫିଙ୍ଗିଲେ ପ୍ରକୃତ ସମ୍ଭାବନା ପାଖକୁ ଆସେ।',
      'الاحتمال عدد بين صفر وواحد. عند تساوي فرص النتائج يكون عدد النتائج المواتية على العدد الكلي. ارم النرد مرات كثيرة فتستقر النسب قرب الاحتمالات الحقيقية، وهذا قانون الأعداد الكبيرة.',
      'Eine Wahrscheinlichkeit ist eine Zahl von null bis eins. Bei gleich wahrscheinlichen Ergebnissen ist sie günstige durch alle Ergebnisse. Würfle oft, und die Anteile pendeln sich bei den wahren Chancen ein. Das ist das Gesetz der großen Zahlen.')
K.say('rules', 'AND and OR',
      'For OR, add the two chances and subtract the overlap. For AND, multiply, but only directly when the events are independent. Mutually exclusive events cannot both happen, and they are not independent.',
      'OR के लिए दोनों संभावनाएँ जोड़ें और overlap घटाएँ। AND के लिए गुणा करें, पर सीधे तभी जब events independent हों। Mutually exclusive events साथ नहीं हो सकते, और वे independent नहीं हैं।',
      'OR ಗೆ ಕೂಡಿಸಿ overlap ಕಳೆಯಿರಿ. AND ಗೆ ಗುಣಿಸಿ, independent ಆದಾಗ ಮಾತ್ರ ನೇರವಾಗಿ.',
      'OR ପାଇଁ ଯୋଗ କରି overlap ବିୟୋଗ କରନ୍ତୁ। AND ପାଇଁ ଗୁଣନ, independent ହେଲେ ହିଁ ସିଧାସଳଖ।',
      'لـ أو اجمع الاحتمالين واطرح التداخل. ولـ و اضرب، لكن مباشرة فقط حين تكون الأحداث مستقلة. والأحداث المتنافية لا تقع معًا وليست مستقلة.',
      'Für ODER addierst du beide Chancen und ziehst die Überschneidung ab. Für UND multiplizierst du, direkt aber nur bei unabhängigen Ereignissen. Unvereinbare Ereignisse können nicht zusammen eintreten und sind nicht unabhängig.')
K.say('counting', 'Counting',
      'Factorials count arrangements. Permutations count ordered choices and combinations count unordered ones. Ask whether the order matters. A lottery ticket is a combination, so six from forty nine gives almost fourteen million possible tickets.',
      'Factorial क्रम गिनता है। Permutations क्रम वाले चुनाव और combinations बिना क्रम वाले। पूछें क्या क्रम मायने रखता है। Lottery ticket combination है।',
      'Factorial ಜೋಡಣೆ ಎಣಿಸುತ್ತದೆ. Permutation ಕ್ರಮ ಸಹಿತ, combination ಕ್ರಮ ರಹಿತ. Lottery ticket combination.',
      'Factorial ସଜ୍ଜା ଗଣେ। Permutation କ୍ରମ ସହିତ, combination କ୍ରମ ବିନା। Lottery ticket combination।',
      'المضروب يعد الترتيبات، والتباديل تعد الاختيارات المرتبة، والتوافيق غير المرتبة. اسأل هل الترتيب مهم. تذكرة اليانصيب توفيقة، فستة من تسعة وأربعين تعطي نحو أربعة عشر مليون تذكرة.',
      'Fakultäten zählen Anordnungen, Permutationen geordnete und Kombinationen ungeordnete Auswahlen. Frage, ob die Reihenfolge zählt. Ein Lottoschein ist eine Kombination, sechs aus neunundvierzig ergibt fast vierzehn Millionen Scheine.')
K.say('conditional', 'Conditional probability',
      'P of A given B is the chance of A once you know B happened. Shrink the world to B, then ask what share is also A. Be careful, P of A given B is usually different from P of B given A.',
      'P of A given B वह संभावना है जब पता हो कि B हुआ। दुनिया को B तक छोटा करें, फिर देखें कितना हिस्सा A भी है। ध्यान दें, यह P of B given A से अलग होता है।',
      'P of A given B ಎಂದರೆ B ಸಂಭವಿಸಿದೆ ಎಂದು ತಿಳಿದಾಗ A ಸಾಧ್ಯತೆ. ಇದು P of B given A ಗಿಂತ ಬೇರೆ.',
      'P of A given B ମାନେ B ଘଟିଛି ଜାଣିଲେ A ର ସମ୍ଭାବନା। ଏହା P of B given A ଠାରୁ ଭିନ୍ନ।',
      'احتمال A بشرط B هو فرصة A بعد أن تعرف أن B وقع. صغّر العالم إلى B ثم اسأل كم منه هو A أيضًا. وانتبه، فهو عادة يختلف عن احتمال B بشرط A.',
      'P von A gegeben B ist die Chance für A, wenn du weißt, dass B eingetreten ist. Verkleinere die Welt auf B und frage, welcher Anteil auch A ist. Achtung, das ist meist etwas anderes als P von B gegeben A.')
K.say('bayes', 'Bayes theorem',
      'Bayes theorem updates a prior belief into a posterior using the evidence. With a rare disease, even a good test gives mostly false positives, because there are so many more healthy people. Change the sliders and count the coloured people.',
      'Bayes theorem सबूत से prior विश्वास को posterior में बदलता है। दुर्लभ बीमारी में अच्छा test भी ज़्यादातर false positives देता है, क्योंकि स्वस्थ लोग बहुत ज़्यादा हैं। Sliders बदलकर रंगीन लोग गिनें।',
      'Bayes theorem ಸಾಕ್ಷ್ಯದಿಂದ prior ಅನ್ನು posterior ಮಾಡುತ್ತದೆ. ಅಪರೂಪದ ರೋಗದಲ್ಲಿ ಹೆಚ್ಚು false positives.',
      'Bayes theorem ପ୍ରମାଣରୁ prior କୁ posterior କରେ। ବିରଳ ରୋଗରେ ଅଧିକାଂଶ false positives।',
      'مبرهنة بايز تحول القناعة المسبقة إلى لاحقة باستخدام الدليل. مع مرض نادر يعطي حتى الفحص الجيد إيجابيات كاذبة في الغالب، لأن الأصحاء أكثر بكثير. غيّر المنزلقات وعد الأشخاص الملونين.',
      'Der Satz von Bayes macht aus einer Vorannahme mit Hilfe der Belege eine Nachannahme. Bei einer seltenen Krankheit liefert selbst ein guter Test meist falsch positive Ergebnisse, weil es so viel mehr Gesunde gibt. Ändere die Regler und zähle die farbigen Personen.')
K.say('naive', 'Naive Bayes',
      'Naive Bayes multiplies the prior of each class by the chance of every word given that class, as if the words were independent. Add one to every count so unseen words do not wipe out the product. The biggest score wins.',
      'Naive Bayes हर class के prior को हर शब्द की संभावना से गुणा करता है, जैसे शब्द independent हों। हर count में एक जोड़ें ताकि नए शब्द गुणनफल को शून्य न करें। सबसे बड़ा score जीतता है।',
      'Naive Bayes ಪ್ರತಿ class ನ prior ಅನ್ನು ಪ್ರತಿ ಪದದ ಸಾಧ್ಯತೆಯಿಂದ ಗುಣಿಸುತ್ತದೆ. ಪ್ರತಿ count ಗೆ ಒಂದು ಸೇರಿಸಿ.',
      'Naive Bayes ପ୍ରତ୍ୟେକ class ର prior କୁ ପ୍ରତ୍ୟେକ ଶବ୍ଦର ସମ୍ଭାବନାରେ ଗୁଣନ କରେ। ପ୍ରତ୍ୟେକ count ରେ ଏକ ଯୋଗ କରନ୍ତୁ।',
      'بايز الساذج يضرب الاحتمال المسبق لكل فئة في احتمال كل كلمة ضمن تلك الفئة كأن الكلمات مستقلة. أضف واحدًا لكل عدّ حتى لا تصفّر الكلمات غير المرئية الناتج. وأكبر درجة تفوز.',
      'Naive Bayes multipliziert die Vorannahme jeder Klasse mit der Chance jedes Wortes in dieser Klasse, als wären die Wörter unabhängig. Addiere eins zu jeder Zählung, damit ungesehene Wörter das Produkt nicht auslöschen. Die größte Punktzahl gewinnt.')
K.say('ml', 'Probability in machine learning',
      'Models give probabilities, training maximises likelihood, priors act as regularisers, and Monte Carlo simulation estimates hard averages by sampling. Random darts can even estimate pi.',
      'Models probabilities देते हैं, training likelihood बढ़ाती है, priors regularisers का काम करते हैं, और Monte Carlo sampling से कठिन औसत निकालता है। Random darts से pi भी निकल सकता है।',
      'Models probabilities ಕೊಡುತ್ತವೆ, Monte Carlo sampling ನಿಂದ ಕಠಿಣ ಸರಾಸರಿ. Random darts ನಿಂದ pi.',
      'Models probabilities ଦିଏ, Monte Carlo sampling ରେ କଠିନ ହାରାହାରି। Random darts ରେ pi।',
      'النماذج تعطي احتمالات، والتدريب يعظم الأرجحية، والقناعات المسبقة تعمل كتنظيم، ومحاكاة مونت كارلو تقدر المتوسطات الصعبة بأخذ العينات، حتى إن السهام العشوائية تقدر باي.',
      'Modelle liefern Wahrscheinlichkeiten, Training maximiert die Likelihood, Vorannahmen wirken als Regularisierung, und Monte Carlo schätzt schwierige Mittelwerte durch Stichproben. Zufällige Pfeile können sogar Pi schätzen.')
K.say('practice', 'Practice',
      'Practice time. Work out card chances, the birthday surprise, repeated medical tests, and a naive Bayes spam score.',
      'अभ्यास का समय। Cards की संभावना, birthday surprise, बार बार medical test, और naive Bayes spam score निकालें।',
      'ಅಭ್ಯಾಸದ ಸಮಯ. Cards, birthday, medical tests ಮತ್ತು naive Bayes.',
      'ଅଭ୍ୟାସ ସମୟ। Cards, birthday, medical tests ଓ naive Bayes।',
      'وقت التدريب. احسب احتمالات الأوراق، ومفاجأة أعياد الميلاد، والفحوص الطبية المتكررة، ودرجة رسالة مزعجة ببايز الساذج.',
      'Zeit zum Üben. Berechne Kartenchancen, die Geburtstagsüberraschung, wiederholte medizinische Tests und einen Naive Bayes Spamwert.')

# ---------------------------------------------------------------- practice
K.practice('cards', 'e', 'Aces and hearts', 'p_cards',
           '<p>One card is drawn from a full deck of 52. Find P(ace), P(heart), P(ace and heart) and P(ace or heart). Are "ace" and "heart" independent?</p>',
           'P(ace)         = 1/13\nP(heart)       = 1/4\nP(ace and heart) = 1/52 = 1/52 so they are independent\nP(ace or heart)  = 4/13',
           'There is exactly one ace of hearts. Use the addition rule for OR.',
           '<p>P(ace) = 4/52 = 1/13 and P(heart) = 13/52 = 1/4. Only one card is both, so P(ace and heart) = 1/52, which equals 1/13 × 1/4. That is the test for independence: knowing the card is a heart does not change the chance it is an ace. For OR, 4 + 13 − 1 = 16 cards qualify, so 16/52 = 4/13.</p>',
           'O(1)', 'O(1)')
K.practice('birthday', 'm', 'The birthday surprise', 'p_birthday',
           '<p>How many people must be in a room before there is a better than even chance that two share a birthday? Ignore leap years.</p>',
           '10 people: P(at least two share a birthday) = 0.1169\n23 people: P(at least two share a birthday) = 0.5073\n50 people: P(at least two share a birthday) = 0.9704',
           'Use the complement: work out P(all different) and subtract from 1.',
           '<p>The first person can have any birthday. The second must avoid one day: 364/365. The third must avoid two: 363/365, and so on. Multiply these and subtract from 1. With only 23 people the chance passes 50%, because there are C(23, 2) = 253 pairs of people, each a chance for a match. The same counting explains hash collisions in computer science.</p>',
           'O(n)', 'O(1)')
K.practice('bayes-two', 'h', 'Testing positive again', 'p_bayes_two',
           '<p>Using the disease test from the lesson (1% prior, 99% sensitivity, 95% specificity), find P(sick) after one, two and three independent positive tests.</p>',
           'after positive test 1: P(sick) = 0.1667\nafter positive test 2: P(sick) = 0.7984\nafter positive test 3: P(sick) = 0.9874',
           'The posterior after one test becomes the prior for the next.',
           '<p>After one positive test, P(sick) = 0.0099 ÷ 0.0594 ≈ 0.167. Use 0.167 as the new prior: 0.99 × 0.167 ÷ (0.99 × 0.167 + 0.05 × 0.833) ≈ 0.798. A third positive pushes it to about 0.987. Each positive test multiplies the odds of being sick by 0.99 ÷ 0.05 = 19.8, the "likelihood ratio". This is why doctors confirm with a second test.</p>',
           'O(tests)', 'O(1)')
K.practice('naive', 'x', 'A naive Bayes spam score', 'p_naive',
           '<p>With the word counts and priors from the lesson, compute the spam probability of the messages "free lunch" and "win free" using Laplace smoothing.</p>',
           'free lunch: spam score 0.021875, ham score 0.023438, P(spam) = 0.4828\nwin free: spam score 0.054688, ham score 0.009375, P(spam) = 0.8537',
           'Each class saw 12 words and the vocabulary has 4 words, so every smoothed chance is (count + 1) ÷ 16.',
           '<p>For "free lunch", spam: 0.4 × 7/16 × 2/16 = 0.021875 and ham: 0.6 × 2/16 × 5/16 ≈ 0.023438. Ham wins narrowly (P(spam) ≈ 0.48) because "lunch" is a ham word and the ham prior is higher. For "win free", both words lean spam, giving P(spam) ≈ 0.85. Real filters use thousands of words and add log probabilities instead of multiplying.</p>',
           'O(words × classes)', 'O(vocabulary × classes)')

# ---------------------------------------------------------------- quiz
K.quiz('e', 'What is the probability of an impossible event?', ['0', '0.5', '1', '−1'], 0, 'The bottom of the scale.', 'Probabilities run from 0 (impossible) to 1 (certain).')
K.quiz('e', 'A fair die is rolled. What is P(even)?', ['1/6', '1/3', '1/2', '2/3'], 2, 'Even faces: 2, 4, 6.', '3 favourable out of 6: 1/2.')
K.quiz('e', 'P(rain) = 0.3. What is P(no rain)?', ['0.3', '0.7', '1.3', '0'], 1, 'Complement.', '1 − 0.3 = 0.7.')
K.quiz('e', 'Two fair coins are tossed. What is P(two heads)?', ['1/2', '1/3', '1/4', '1/8'], 2, 'Independent, so multiply.', '1/2 × 1/2 = 1/4.')
K.quiz('m', 'How many ways can 3 books be arranged on a shelf?', ['3', '6', '9', '27'], 1, '3!.', '3 × 2 × 1 = 6.')
K.quiz('m', 'C(6, 2) equals…', ['12', '15', '30', '36'], 1, '6!/(2! 4!).', '(6 × 5) ÷ 2 = 15.')
K.quiz('m', 'P(A) = 0.5, P(B) = 0.4 and P(A ∩ B) = 0.2. What is P(A ∪ B)?', ['0.9', '0.7', '0.2', '0.1'], 1, 'Add, then subtract the overlap.', '0.5 + 0.4 − 0.2 = 0.7.')
K.quiz('m', 'Events A and B are independent when…', ['P(A ∩ B) = 0', 'P(A ∩ B) = P(A) × P(B)', 'P(A) = P(B)', 'P(A ∪ B) = 1'], 1, 'Knowing one does not change the other.', 'Equivalently P(A | B) = P(A).')
K.quiz('m', 'Which is the formula for P(A | B)?', ['P(A) × P(B)', 'P(A ∩ B) ÷ P(B)', 'P(A ∩ B) ÷ P(A)', 'P(B | A)'], 1, 'Shrink to the B world.', 'Out of the B outcomes, the share that are also A.')
K.quiz('h', 'A rare disease (1%) and a 99% sensitive, 95% specific test. Roughly what is P(sick | positive)?', ['99%', '95%', 'about 17%', '1%'], 2, 'Count false positives among 9900 healthy people.', '99 true positives against 495 false positives: 99 ÷ 594 ≈ 17%.')
K.quiz('h', 'Why does naive Bayes use Laplace smoothing?', ['to speed it up', 'so a word never seen in a class does not make the whole product zero', 'to make probabilities add to 2', 'to remove stop words'], 1, 'Multiplying by 0.', 'Adding 1 to every count keeps every word chance above 0.')
K.quiz('h', 'What is "naive" about naive Bayes?', ['it ignores priors', 'it assumes the features are independent given the class', 'it uses only one feature', 'it never learns'], 1, 'It multiplies word chances.', 'Words are treated as conditionally independent given the class.')
K.quiz('h', 'P(at least one six in 4 rolls of a die) is closest to…', ['0.67', '0.52', '0.25', '0.40'], 1, 'Complement: 1 − (5/6)⁴.', '1 − 0.482 ≈ 0.518.')
K.quiz('x', 'In Bayes\' theorem, what is P(B) in the denominator often called?', ['the prior', 'the evidence (or marginal likelihood)', 'the posterior', 'the likelihood ratio'], 1, 'It normalises the posterior.', 'P(B) = Σ P(B | Aᵢ)P(Aᵢ), the total chance of seeing the evidence.')
K.quiz('x', 'Why do naive Bayes implementations add log probabilities?', ['logs are more accurate for big numbers', 'multiplying many tiny probabilities underflows to 0 on a computer', 'it changes the winner', 'logs remove the prior'], 1, 'Floating point limits.', 'Sums of logs stay in range, and the class with the biggest log score is still the winner.')

# ---------------------------------------------------------------- worked problems
K.calc('e', 'What is the probability of rolling a 5 on a fair die? Give 3 decimal places.', '0.167', 'One favourable face out of six.', [
    'Favourable outcomes: <span class="eq">1</span> (the face 5)',
    'Total outcomes: <span class="eq">6</span>',
    '<span class="eq">P = 1 ÷ 6 ≈ 0.167</span>',
], check=1 / 6, tol=0.001)
K.calc('e', 'What is the probability of NOT rolling a 6? Give 3 decimal places.', '0.833', 'Complement rule.', [
    '<span class="eq">P(6) = 1/6</span>',
    '<span class="eq">P(not 6) = 1 − 1/6 = 5/6</span>',
    '<span class="eq">5 ÷ 6 ≈ 0.833</span>',
], check=5 / 6, tol=0.001)
K.calc('e', 'Two fair coins are tossed. What is P(both heads)?', '0.25', 'The tosses are independent.', [
    '<span class="eq">P(H) = 0.5</span> for each coin',
    'Independent, so multiply: <span class="eq">0.5 × 0.5 = 0.25</span>',
    'Check by listing: HH, HT, TH, TT. One of four is HH. ✔',
], check=0.25)
K.calc('e', 'In how many orders can 5 different books be placed on a shelf?', '120', '5!.', [
    'First place: <span class="eq">5</span> choices. Second: <span class="eq">4</span>. Then 3, 2, 1.',
    'Multiply: <span class="eq">5 × 4 × 3 × 2 × 1</span>',
    '<span class="eq">= 120</span>',
], check=120)
K.calc('m', 'How many different pairs can be chosen from 5 people?', '10', 'Order does not matter: C(5, 2).', [
    'Ordered pairs: <span class="eq">5 × 4 = 20</span>',
    'Each pair was counted twice (AB and BA): divide by <span class="eq">2! = 2</span>',
    '<span class="eq">20 ÷ 2 = 10</span>',
], check=10)
K.calc('m', 'Two dice are rolled. What is P(sum = 7)? Give 4 decimal places.', '0.1667', 'Count the pairs that add to 7.', [
    'Pairs: <span class="eq">(1,6), (2,5), (3,4), (4,3), (5,2), (6,1)</span>, that is 6 pairs',
    'All pairs: <span class="eq">6 × 6 = 36</span>',
    '<span class="eq">6 ÷ 36 = 1/6 ≈ 0.1667</span>. 7 is the most likely sum.',
], check=1 / 6, tol=0.0001)
K.calc('m', 'P(A) = 0.5, P(B) = 0.4, P(A ∩ B) = 0.2. What is P(A ∪ B)?', '0.7', 'Addition rule.', [
    'Add: <span class="eq">0.5 + 0.4 = 0.9</span>',
    'The overlap was counted twice, subtract it once: <span class="eq">0.9 − 0.2 = 0.7</span>',
    'So <span class="eq">P(A ∪ B) = 0.7</span>',
], check=0.7)
K.calc('m', 'From the student table, what is P(pass | studied)?', '0.9', 'Look only at the Studied row.', [
    'Students who studied: <span class="eq">90 + 10 = 100</span>',
    'Of these, passed: <span class="eq">90</span>',
    '<span class="eq">90 ÷ 100 = 0.9</span>',
], check=0.9)
K.calc('h', 'Disease prevalence 1%, sensitivity 99%, false positive rate 5%. What is P(sick | positive) as a percentage? Give 1 decimal place.', '16.7', 'Bayes. Or use 10000 people.', [
    '10000 people: <span class="eq">100</span> sick, <span class="eq">9900</span> healthy',
    'True positives: <span class="eq">0.99 × 100 = 99</span>',
    'False positives: <span class="eq">0.05 × 9900 = 495</span>',
    '<span class="eq">99 ÷ (99 + 495) = 99 ÷ 594 ≈ 0.1667 = 16.7%</span>',
], check=99 / 594 * 100, tol=0.05, unit='%')
K.calc('h', 'What is P(at least one six in 4 rolls of a fair die)? Give 4 decimal places.', '0.5177', 'Complement: 1 − P(no six at all).', [
    'One roll with no six: <span class="eq">5/6</span>',
    'Four rolls with no six: <span class="eq">(5/6)⁴ = 625/1296 ≈ 0.4823</span>',
    'At least one six: <span class="eq">1 − 0.4823 = 0.5177</span>',
], check=1 - (5 / 6) ** 4, tol=0.0001)
K.calc('h', 'From the student table, what is P(studied | pass)? Give 3 decimal places.', '0.692', 'Look only at the Passed column.', [
    'Students who passed: <span class="eq">90 + 40 = 130</span>',
    'Of these, studied: <span class="eq">90</span>',
    '<span class="eq">90 ÷ 130 ≈ 0.692</span>. Different from P(pass | studied) = 0.9.',
], check=90 / 130, tol=0.001)
K.calc('x', 'Naive Bayes from the lesson: what is P(spam) for "win free"? Give 3 decimal places.', '0.854', 'Spam score 0.4 × 5/16 × 7/16, ham score 0.6 × 2/16 × 2/16.', [
    'Spam score: <span class="eq">0.4 × 35/256 = 14/256 ≈ 0.05469</span>',
    'Ham score: <span class="eq">0.6 × 4/256 = 2.4/256 ≈ 0.00938</span>',
    'Normalise: <span class="eq">14 ÷ (14 + 2.4) = 14 ÷ 16.4 ≈ 0.854</span>',
], check=14 / 16.4, tol=0.001)
K.calc('x', 'With 23 people, what is the probability that at least two share a birthday? Give 3 decimal places.', '0.507', 'Complement: 1 − (365/365)(364/365)…(343/365).', [
    'All different: <span class="eq">(365 × 364 × … × 343) ÷ 365²³</span>',
    'Multiplying the 23 fractions gives about <span class="eq">0.4927</span>',
    'At least one shared birthday: <span class="eq">1 − 0.4927 = 0.5073 ≈ 0.507</span>',
], check=0.5073, tol=0.001)

# ---------------------------------------------------------------- animations
VIZ_JS = r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;
  let seed = 12345;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };

  /* ----- roll dice and watch the bars settle ----- */
  W.dice = el => {
    const b = shell(el, 'Roll the dice', 'Choose one die or the sum of two dice and how many rolls to make. Press Play to roll in growing batches and watch the bars (what happened) close in on the dashed marks (the true probability).');
    b.innerHTML = `<div class="vz-row">${seg('mode', [['one', 'One die'], ['two', 'Sum of two dice']], 'one')}</div>
      <div class="mv-wrap"><div class="dc-plot"></div><div class="mv-side">${slider('n', 'rolls', 10, 5000, 600, 10)}<div class="vz-ctl"><button type="button" class="dc-new">🎲 New random rolls</button></div><div class="mv-read dc-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let mode = 'one', N = 600, rolls = [];
    const STEPS = 12;
    const faces = () => (mode === 'one' ? [1, 2, 3, 4, 5, 6] : [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
    const truth = v => (mode === 'one' ? 1 / 6 : (6 - Math.abs(v - 7)) / 36);
    function roll() { rolls = Array.from({ length: N }, () => mode === 'one' ? 1 + Math.floor(rnd() * 6) : 2 + Math.floor(rnd() * 6) + Math.floor(rnd() * 6)); P.load(STEPS + 1, STEPS); }
    function show(t) {
      const k = Math.max(1, Math.round(N * Math.pow(t / STEPS, 2)));
      const used = t === 0 ? [] : rolls.slice(0, k), F = faces();
      const cnt = Object.fromEntries(F.map(v => [v, 0])); used.forEach(r => cnt[r]++);
      const G = MV.frame(440, 300, [F[0] - 0.7, F[F.length - 1] + 0.7], [0, mode === 'one' ? 0.35 : 0.25], 42);
      let s = MV.axes(G, { xstep: 1, ystep: 0.05 });
      F.forEach(v => {
        const p = used.length ? cnt[v] / used.length : 0, w = 0.36;
        s += `<rect class="mv-bar" x="${G.sx(v - w).toFixed(1)}" y="${G.sy(Math.min(G.yr[1], p)).toFixed(1)}" width="${(G.sx(v + w) - G.sx(v - w)).toFixed(1)}" height="${(G.sy(0) - G.sy(Math.min(G.yr[1], p))).toFixed(1)}"/>`;
        s += MV.line(G, v - w - 0.05, truth(v), v + w + 0.05, truth(v), 'mv-v o dash');
      });
      $('.dc-plot', b).innerHTML = MV.svg(G, s, 'Bar chart of dice results');
      const err = used.length ? Math.max(...F.map(v => Math.abs(cnt[v] / used.length - truth(v)))) : 0;
      $('.dc-out', b).innerHTML = `rolls so far: <b>${used.length}</b><br>` + (mode === 'one' ? `each face should be 1/6 ≈ 0.167<br>` : `7 should be 6/36 ≈ 0.167, 2 and 12 only 1/36 ≈ 0.028<br>`) +
        (used.length ? `biggest gap from the truth: ${MV.num(err, 3)}<br>${used.length < 100 ? 'Few rolls: the bars are bumpy.' : 'Many rolls: the bars hug the dashed lines. This is the law of large numbers.'}` : 'Press Play to start rolling.');
    }
    const P = Player($('.vz-p', b), show, 450);
    wireSeg(b, 'mode', v => { mode = v; roll(); });
    wireSlider(b, 'n', v => { N = v; roll(); });
    $('.dc-new', b).addEventListener('click', roll);
    roll();
  };

  /* ----- 100 outcomes, two events, and the rules ----- */
  W.venn = el => {
    const b = shell(el, 'Events as squares in a grid', 'Each of the 100 squares is one equally likely outcome. Set the sizes of events A and B and how much they overlap, then press Play to step through A, B, A and B, A or B, and A given B.');
    b.innerHTML = `<div class="vz-row">${slider('a', 'P(A) %', 5, 80, 50, 1)}${slider('b', 'P(B) %', 5, 80, 40, 1)}${slider('o', 'overlap %', 0, 40, 20, 1)}</div>
      <div class="mv-wrap"><div class="vn-grid"></div><div class="mv-side"><div class="mv-legend"><span><i></i>A only</span><span><i class="o"></i>B only</span><span><i class="p"></i>both</span></div><div class="mv-read vn-out" aria-live="polite"></div></div></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let A = 50, B = 40, O = 20;
    function cells() {
      O = Math.min(O, A, B, Math.max(0, A + B - 0) );
      if (A + B - O > 100) O = A + B - 100;
      const out = [];
      for (let i = 0; i < 100; i++) {
        const inA = i < A, inB = i >= A - O && i < A - O + B;
        out.push(inA && inB ? 'both' : inA ? 'a' : inB ? 'b' : 'none');
      }
      return out;
    }
    function show(t) {
      const C = cells(), nB = B, nO = O, nU = A + B - O;
      const hi = [k => true, k => k === 'a' || k === 'both', k => k === 'b' || k === 'both', k => k === 'both', k => k !== 'none', k => k === 'both'][t];
      const dim = t === 5 ? (k => k !== 'b' && k !== 'both') : (k => !hi(k));
      $('.vn-grid', b).innerHTML = `<div class="vn-g">${C.map(k => `<span class="vn-${k} ${dim(k) ? 'dim' : ''} ${t > 0 && hi(k) ? 'on' : ''}"></span>`).join('')}</div>`;
      $('.vz-msg', b).innerHTML = ['100 equally likely outcomes. Press Play.',
        `A covers ${A} squares: P(A) = ${A}/100 = ${MV.num(A / 100)}`,
        `B covers ${B} squares: P(B) = ${B}/100 = ${MV.num(B / 100)}`,
        `Both A and B: ${nO} squares, so P(A ∩ B) = ${MV.num(nO / 100)}`,
        `A or B (or both): ${A} + ${B} − ${nO} = ${nU} squares, so P(A ∪ B) = ${MV.num(nU / 100)}. The overlap is subtracted so it is not counted twice.`,
        `A given B: shrink the world to the ${nB} squares of B. ${nO} of them are also A, so P(A | B) = ${nO}/${nB} = ${MV.num(nB ? nO / nB : 0, 3)}`][t];
      const indep = Math.abs(nO / 100 - (A / 100) * (B / 100)) < 0.005;
      $('.vn-out', b).innerHTML = `P(A) × P(B) = ${MV.num(A * B / 10000, 4)}<br>P(A ∩ B) = ${MV.num(nO / 100, 4)}<br>${indep ? '✅ Equal: A and B are independent.' : nO === 0 ? '🚫 No overlap: mutually exclusive (and so not independent).' : 'Not equal: A and B are dependent.'}`;
    }
    const P = Player($('.vz-p', b), show, 1500);
    const sync = () => { $('[data-sl="o"]', b).value = O; $('[data-slv="o"]', b).textContent = O; };
    wireSlider(b, 'a', v => { A = v; cells(); sync(); show(P.i); });
    wireSlider(b, 'b', v => { B = v; cells(); sync(); show(P.i); });
    wireSlider(b, 'o', v => { O = v; cells(); sync(); show(P.i); });
    P.load(6, 0);
  };

  /* ----- Bayes with 500 people ----- */
  W.bayes = el => {
    const b = shell(el, 'Bayes with 500 people', 'Every square is a person. Set how common the disease is and how good the test is. Press Play to sort the people step by step and find the chance that a positive result really means sick.');
    b.innerHTML = `<div class="vz-row">${slider('prev', 'disease %', 0.5, 20, 2, 0.5)}${slider('sens', 'sensitivity %', 50, 100, 95, 1)}${slider('spec', 'specificity %', 50, 100, 90, 1)}</div>
      <div class="mv-people by-grid"></div><div class="mv-legend"><span><i class="r"></i>sick, positive</span><span><i style="background:color-mix(in srgb, var(--red) 35%, var(--surface))"></i>sick, missed</span><span><i class="o"></i>healthy, false alarm</span><span><i class="g"></i>healthy, negative</span></div>
      <div class="mv-read by-out" aria-live="polite"></div><div class="vz-msg" aria-live="polite"></div><div class="vz-p"></div>`;
    let prev = 2, sens = 95, spec = 90;
    const N = 500;
    function counts() {
      const sick = Math.round(N * prev / 100), tp = Math.round(sick * sens / 100), fn = sick - tp, healthy = N - sick, fp = Math.round(healthy * (100 - spec) / 100), tn = healthy - fp;
      return { sick, tp, fn, healthy, fp, tn };
    }
    function show(t) {
      const c = counts();
      const cls = [];
      for (let i = 0; i < N; i++) {
        if (t === 0) cls.push('');
        else if (t === 1) cls.push(i < c.sick ? 'tp' : '');
        else if (i < c.tp) cls.push('tp');
        else if (i < c.sick) cls.push('fn');
        else if (t >= 3 && i < c.sick + c.fp) cls.push('fp');
        else cls.push(t >= 3 ? 'tn' : '');
      }
      $('.by-grid', b).innerHTML = cls.map(k => `<span class="${k}"></span>`).join('');
      const pos = c.tp + c.fp, post = pos ? c.tp / pos : 0;
      $('.vz-msg', b).innerHTML = [`${N} people. Press Play to sort them.`,
        `Prior: ${prev}% are sick, that is ${c.sick} people (red).`,
        `The test catches ${sens}% of the sick: ${c.tp} test positive, ${c.fn} are missed (pale red).`,
        `The test wrongly flags ${100 - spec}% of the ${c.healthy} healthy people: ${c.fp} false alarms (orange).`,
        `Everyone with a positive result: ${c.tp} + ${c.fp} = ${pos}. Only ${c.tp} of them are sick, so P(sick | positive) = ${c.tp}/${pos} ≈ ${MV.num(100 * post, 1)}%.`][t];
      $('.by-out', b).innerHTML = `true positives ${c.tp}, false positives ${c.fp}<br>P(sick | positive) = <b>${MV.num(100 * post, 1)}%</b>` + (post < 0.5 && t === 4 ? '<br>Most positives are false alarms, because healthy people vastly outnumber sick ones.' : '');
    }
    const P = Player($('.vz-p', b), show, 1500);
    wireSlider(b, 'prev', v => { prev = v; show(P.i); });
    wireSlider(b, 'sens', v => { sens = v; show(P.i); });
    wireSlider(b, 'spec', v => { spec = v; show(P.i); });
    P.load(5, 0);
  };
})();
'''

CSS = r'''
.vn-g{display:grid; grid-template-columns:repeat(10, 1fr); gap:3px; max-width:320px; margin:auto}
.vn-g span{aspect-ratio:1; border-radius:4px; border:1px solid var(--line); background:var(--dimbox); transition:opacity .3s, transform .3s}
.vn-g .vn-a{background:color-mix(in srgb, var(--accent) 55%, var(--surface))}
.vn-g .vn-b{background:color-mix(in srgb, var(--orange) 55%, var(--surface))}
.vn-g .vn-both{background:color-mix(in srgb, var(--purple) 60%, var(--surface))}
.vn-g .dim{opacity:.18}
.vn-g .on{transform:scale(1.06)}
.dc-new{margin:6px 0}
'''

# ---------------------------------------------------------------- deeper explanations and extra animations
# Each lesson above gives the short version. DEEPER adds a slower, fuller explanation (and sometimes an
# animation) to the end of the lesson with the same id.
DEEPER = {
    'rules': deep('the birthday problem, where the complement rule shines', f'''
<p>How many people must be in a room before two of them probably share a birthday? Most people guess around 180. The real answer is 23. The trick is to work out the chance that <b>nobody</b> shares, using the AND rule, and then take the complement.</p>
{worked('Chance that at least two of 23 people share a birthday (365 equally likely days)', [
        'Person 1 can have any birthday: chance <span class="eq">365 ÷ 365</span>',
        'Person 2 must avoid that day: <span class="eq">364 ÷ 365</span>. Person 3 must avoid two days: <span class="eq">363 ÷ 365</span>',
        'Keep going to person 23, who must avoid 22 days: <span class="eq">343 ÷ 365</span>',
        'All different (AND, so multiply): <span class="eq">(365 × 364 × … × 343) ÷ 365²³ ≈ 0.493</span>',
        'At least one shared birthday (complement): <span class="eq">1 − 0.493 = 0.507</span>, just over half.'])}
<p>Why so few? With 23 people there are C(23, 2) = 253 different <b>pairs</b>, and each pair is a fresh chance of a match. Counting pairs, not people, is what intuition misses.</p>
{ml('The same maths decides how often two different items get the same hash code in a hash table or a data deduplication system. With about 1.2 × √N items you reach a 50% chance of at least one collision among N possible codes.')}
'''),
    'counting': deep('see permutations collapse into combinations', f'''
<p>Combinations are permutations with the order thrown away. Every group of k items can be lined up in k! different orders, so the list of permutations contains each combination exactly k! times. Dividing by k! removes the repeats.</p>
{viz('perm')}
{worked('Odds of a 6 from 49 lottery', [
        'Order does not matter, so count combinations: <span class="eq">C(49, 6) = 49! ÷ (6! × 43!)</span>',
        'Cancel the 43!: <span class="eq">(49 × 48 × 47 × 46 × 45 × 44) ÷ (6 × 5 × 4 × 3 × 2 × 1)</span>',
        'Top: <span class="eq">10068347520</span>. Bottom: <span class="eq">720</span>',
        '<span class="eq">10068347520 ÷ 720 = 13983816</span> possible tickets',
        'One ticket wins with chance about <span class="eq">1 in 14 million</span>.'])}
{trick('When working out C(n, k) by hand, cancel the bigger factorial first and multiply only k numbers on top. C(10, 3) = (10 × 9 × 8) ÷ (3 × 2 × 1) = 120.')}
'''),
    'conditional': deep('shrink the world and watch the probability change', f'''
<p>"Given B" means: throw away every outcome where B did not happen, and measure inside what is left. The grid below shows the 200 students from the table. Pick a "given" and the rest of the grid fades away. The probability is just a count of the bright dots divided by the size of the remaining world.</p>
{viz('condgrid')}
<p>A <b>probability tree</b> is another way to keep conditional probabilities straight. The first branches split on one question, the second branches on the next, and you multiply along a path.</p>
{worked('Probability tree for the study table', [
        'First branch: <span class="eq">P(studied) = 100 ÷ 200 = 0.5</span> and <span class="eq">P(did not) = 0.5</span>',
        'Second branch after studying: <span class="eq">P(pass | studied) = 0.9</span>. After not studying: <span class="eq">P(pass | not) = 0.4</span>',
        'Multiply along each path: studied and passed <span class="eq">0.5 × 0.9 = 0.45</span>, did not study and passed <span class="eq">0.5 × 0.4 = 0.2</span>',
        'Add the paths that end in "pass": <span class="eq">P(pass) = 0.45 + 0.2 = 0.65</span>, which matches 130 ÷ 200 ✓',
        'This last step has a name, the law of total probability, and it is the bottom of Bayes’ theorem.'])}
'''),
    'bayes': deep('the odds form of Bayes, the quickest way to update', f'''
<p>Bayes’ theorem has a second form that is easier to use in your head. Write beliefs as <b>odds</b> (chance for ÷ chance against) and each new piece of evidence multiplies the odds by a single number, the <b>likelihood ratio</b>.</p>
{fx('Bayes in odds form', 'posterior odds = prior odds × likelihood ratio', 'likelihood ratio = P(evidence | A) ÷ P(evidence | not A). Above 1 the evidence favours A, below 1 it favours not A.')}
{worked('A disease in 1 of 100 people, test sensitivity 90%, false positive rate 5%', [
        'Prior odds of being sick: <span class="eq">1 : 99</span>',
        'Likelihood ratio of a positive test: <span class="eq">0.90 ÷ 0.05 = 18</span>',
        'Posterior odds: <span class="eq">1 × 18 : 99 = 18 : 99</span>',
        'Back to a probability: <span class="eq">18 ÷ (18 + 99) = 18 ÷ 117 ≈ 0.154</span>, about 15%',
        'A second, independent positive test multiplies by 18 again: <span class="eq">324 : 99</span>, so about 77%.'])}
<p>The odds form shows clearly why a rare condition stays fairly unlikely after one positive test: the prior odds start very low, and one multiplication by 18 cannot make up all the difference. It also shows how evidence piles up, one multiplication per independent clue, which is exactly what naive Bayes does in the next lesson.</p>
'''),
    'naive': deep('what "naive" costs and the Gaussian version', f'''
<p>The naive assumption says that, once you know the class, the words do not influence each other. In real email "free" and "money" do travel together in spam. Naive Bayes then counts that evidence twice and becomes over confident: its probabilities are often pushed close to 0 or 1. Yet the <b>ranking</b> (which class has the bigger score) is usually still right, which is all a classifier needs to pick a label.</p>
{table(['Version', 'Features', 'P(feature | class) comes from'], [
        ['Multinomial', 'word counts', 'counting words in each class, with add one smoothing'],
        ['Bernoulli', 'word present or absent', 'the share of documents in each class that contain the word'],
        ['Gaussian', 'numbers such as height or blood pressure', 'a normal curve with the mean and SD of that feature in that class (Chapter 10)'],
    ])}
{worked('Gaussian naive Bayes with one feature', [
        'Class A heights: mean 160 cm, SD 10. Class B: mean 180 cm, SD 10. Equal priors.',
        'A new person is 172 cm. z under A: <span class="eq">(172 − 160) ÷ 10 = 1.2</span>. z under B: <span class="eq">(172 − 180) ÷ 10 = −0.8</span>',
        'The normal density is proportional to <span class="eq">e^(−z²/2)</span>: for A <span class="eq">e^(−0.72) ≈ 0.487</span>, for B <span class="eq">e^(−0.32) ≈ 0.726</span>',
        'Normalise: <span class="eq">P(B | 172) = 0.726 ÷ (0.487 + 0.726) ≈ 0.60</span>',
        'So class B, with 60% confidence. The boundary sits at 170 cm, halfway between the means, because the SDs are equal.'])}
'''),
    'ml': deep('estimate π by throwing random darts', f'''
<p>Monte Carlo methods replace a hard calculation by a simple random experiment repeated many times. Here is the classic example. Throw darts uniformly at a 1 × 1 square. The quarter circle of radius 1 inside it has area π ÷ 4, so the share of darts that land inside should approach π ÷ 4. Multiply by 4 and you have an estimate of π.</p>
{viz('mcpi')}
<p>Watch how the estimate wobbles a lot at first and then settles. The error shrinks like 1 ÷ √n, the same rule as the standard error in Chapter 10: 100 times more darts gives about 10 times more accuracy. That slow but steady rule works in any number of dimensions, which is why Monte Carlo is the standard tool for the huge integrals of Bayesian machine learning (Chapter 15).</p>
{ml('Dropout in neural networks is a Monte Carlo idea too. During training, each neuron is switched off at random, so each mini batch trains a slightly different random sub network. At test time the network behaves like an average over all those sub networks.')}
'''),
}
for _p in PARTS:
    _p['html'] += DEEPER.get(_p['id'], '')

VIZ_JS += r'''
(() => {
  const { $, shell, seg, wireSeg, Player, slider, wireSlider } = VIZ.kit;
  const W = VIZ.widgets;

  /* ----- list permutations, then group them into combinations ----- */
  W.perm = el => {
    const b = shell(el, 'Permutations, then combinations', 'Choose k letters from A to E. Press Play: first every ordered arrangement appears, then arrangements with the same letters are grouped into one combination.');
    b.innerHTML = `<div class="mv-wrap"><div class="pm-host"></div><div class="mv-side">${slider('n', 'n letters', 3, 5, 4, 1)}${slider('k', 'k chosen', 1, 3, 2, 1)}<div class="mv-read pm-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    let n = 4, k = 2, perms = [];
    const fact = m => m <= 1 ? 1 : m * fact(m - 1);
    function plan() {
      k = Math.min(k, n);
      const L = 'ABCDE'.slice(0, n).split(''); perms = [];
      const rec = (cur, used) => { if (cur.length === k) { perms.push(cur.join('')); return; } L.forEach((c, i) => { if (!used[i]) { used[i] = 1; cur.push(c); rec(cur, used); cur.pop(); used[i] = 0; } }); };
      rec([], []);
      P.load(perms.length + 2, 0);
    }
    function show(t) {
      const grouped = t > perms.length;
      const key = s => s.split('').sort().join('');
      const groups = {}; perms.forEach(p => { (groups[key(p)] = groups[key(p)] || []).push(p); });
      const hue = Object.keys(groups);
      const cell = (p, on) => `<span class="pm-c${on ? '' : ' off'}" style="--h:${hue.indexOf(key(p)) * 47 % 360}">${p}</span>`;
      $('.pm-host', b).innerHTML = grouped
        ? `<div class="pm-groups">${hue.map(g => `<div class="pm-g">${groups[g].map(p => cell(p, true)).join('')}<b>→ {${g.split('').join(', ')}}</b></div>`).join('')}</div>`
        : `<div class="pm-list">${perms.map((p, i) => cell(p, i < t)).join('')}</div>`;
      const P1 = fact(n) / fact(n - k), C = P1 / fact(k);
      $('.pm-out', b).innerHTML = `ordered arrangements P(${n}, ${k}) = ${n}! ÷ ${n - k}! = <b>${P1}</b><br>` + (grouped ? `each group holds ${k}! = ${fact(k)} orders of the same letters<br>combinations C(${n}, ${k}) = ${P1} ÷ ${fact(k)} = <span class="big">${C}</span>` : `listed so far: <b>${Math.min(t, perms.length)}</b>`);
    }
    const P = Player($('.vz-p', b), show, 450);
    wireSlider(b, 'n', v => { n = v; plan(); });
    wireSlider(b, 'k', v => { k = v; plan(); });
    plan();
  };

  /* ----- conditional probability as a shrinking world of 200 students ----- */
  W.condgrid = el => {
    const b = shell(el, 'Given B: shrink the world', 'Each square is one of 200 students. Green = passed, grey = failed. A thick border means they studied. Pick what you are given and read the probability as bright squares divided by the remaining world.');
    b.innerHTML = `<div class="vz-row">${seg('g', [['all', 'Everyone'], ['st', 'Given studied'], ['ns', 'Given did not study'], ['pa', 'Given passed']], 'all')}</div><div class="cg-grid"></div><div class="mv-read cg-out" aria-live="polite"></div>`;
    const S = [];
    for (let i = 0; i < 200; i++) { const st = i < 100, pass = st ? i < 90 : i < 140; S.push({ st, pass }); }
    function draw(g) {
      const keep = s => g === 'all' || (g === 'st' && s.st) || (g === 'ns' && !s.st) || (g === 'pa' && s.pass);
      $('.cg-grid', b).innerHTML = S.map(s => `<span class="${s.pass ? 'p' : 'f'}${s.st ? ' s' : ''}${keep(s) ? '' : ' dim'}"></span>`).join('');
      const world = S.filter(keep), wp = world.filter(s => s.pass).length, ws = world.filter(s => s.st).length;
      const msg = {
        all: `P(pass) = 130 ÷ 200 = <b>0.65</b>`,
        st: `world = the ${world.length} who studied<br>P(pass | studied) = ${wp} ÷ ${world.length} = <b>${MV.num(wp / world.length, 3)}</b>`,
        ns: `world = the ${world.length} who did not study<br>P(pass | did not study) = ${wp} ÷ ${world.length} = <b>${MV.num(wp / world.length, 3)}</b>`,
        pa: `world = the ${world.length} who passed<br>P(studied | passed) = ${ws} ÷ ${world.length} = <b>${MV.num(ws / world.length, 3)}</b><br>Not the same as P(pass | studied) = 0.9. The order of the bar matters.`,
      }[g];
      $('.cg-out', b).innerHTML = msg;
    }
    wireSeg(b, 'g', draw);
    draw('all');
  };

  /* ----- Monte Carlo estimate of π ----- */
  W.mcpi = el => {
    const b = shell(el, 'Estimate π with random darts', 'Press Play to throw darts in batches. Orange darts land inside the quarter circle. The estimate is 4 × (inside ÷ total).');
    b.innerHTML = `<div class="mv-wrap"><div class="mc-plot"></div><div class="mv-side">${slider('seed', 'random seed', 1, 9, 3, 1)}<div class="mv-read mc-out" aria-live="polite"></div></div></div><div class="vz-p"></div>`;
    const G = MV.frame(360, 360, [0, 1], [0, 1], 16);
    const sizes = [0, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000];
    let pts = [], seed = 3;
    function plan() { let s = seed * 9973 + 1; const r = () => { s = (s * 16807) % 2147483647; return s / 2147483647; }; pts = []; for (let i = 0; i < 5000; i++) pts.push([r(), r()]); P.load(sizes.length, 0); }
    function show(t) {
      const n = sizes[t];
      let s = `<rect x="${G.sx(0)}" y="${G.sy(1)}" width="${G.sx(1) - G.sx(0)}" height="${G.sy(0) - G.sy(1)}" class="mv-poly" style="fill:none"/>` + MV.curve(G, x => Math.sqrt(Math.max(0, 1 - x * x)), 'c4', { n: 120 });
      let inside = 0;
      for (let i = 0; i < n; i++) { const [x, y] = pts[i], ok = x * x + y * y <= 1; if (ok) inside++; s += `<circle cx="${G.sx(x).toFixed(1)}" cy="${G.sy(y).toFixed(1)}" r="${n > 1000 ? 1.2 : 2.2}" class="mv-pt ${ok ? 'o' : 'k'}" style="stroke:none"/>`; }
      $('.mc-plot', b).innerHTML = MV.svg(G, s, 'Darts in a square');
      const est = n ? 4 * inside / n : 0;
      $('.mc-out', b).innerHTML = n ? `darts: <b>${n}</b><br>inside: <b>${inside}</b><br>estimate 4 × ${inside} ÷ ${n} = <span class="big">${est.toFixed(4)}</span><br>true π = 3.1416<br>error = ${Math.abs(est - Math.PI).toFixed(4)}<br>typical error ≈ 1.64 ÷ √n = ${(1.64 / Math.sqrt(n)).toFixed(4)}` : 'No darts yet. Press Play.';
    }
    const P = Player($('.vz-p', b), show, 900);
    wireSlider(b, 'seed', v => { seed = v; plan(); });
    plan();
  };
})();
'''
CSS += r'''
.pm-list,.pm-groups{display:flex; flex-wrap:wrap; gap:6px; align-content:flex-start}
.pm-g{display:flex; flex-wrap:wrap; gap:4px; align-items:center; padding:6px; border-radius:10px; border:1px solid var(--line); background:var(--surface2)}
.pm-g b{font-family:var(--font-mono); font-size:13px; margin-left:4px}
.pm-c{font-family:var(--font-mono); font-weight:800; padding:4px 8px; border-radius:8px; background:hsl(var(--h) 70% 60% / .25); border:1.5px solid hsl(var(--h) 60% 45% / .7); transition:opacity .3s}
.pm-c.off{opacity:.12}
.cg-grid{display:grid; grid-template-columns:repeat(20,1fr); gap:3px; margin:8px 0; max-width:520px}
.cg-grid span{aspect-ratio:1; border-radius:3px; border:1px solid var(--line); transition:opacity .3s}
.cg-grid span.p{background:color-mix(in srgb, var(--green) 60%, var(--surface))}
.cg-grid span.f{background:var(--dimbox)}
.cg-grid span.s{border:2px solid var(--ink)}
.cg-grid span.dim{opacity:.1}
.mc-plot .mv-svg{max-height:380px}
'''

T = K.topic(
    slug='probability', topic='probability', prefix='mm09', short='Probability', emoji='🎲',
    title="Probability and Bayes' Theorem",
    module=('🎲', 'Probability and statistics', 'probability', 'Chance, distributions and statistics: the maths that lets a model handle uncertainty and judge its own results.'),
    minutes=55,
    lead="Probability is the maths of uncertainty. Roll virtual dice, see the addition and multiplication rules on a grid of outcomes, count with permutations and combinations, read conditional probabilities from a table, and sort 500 people to understand Bayes' theorem before building a naive Bayes spam filter.",
    desc="Probability for machine learning: sample spaces and events, the addition and multiplication rules, independence, permutations and combinations, conditional probability, Bayes' theorem, naive Bayes and Monte Carlo simulation.",
    summary="Outcomes, events and the complement rule, the law of large numbers, AND and OR rules, independent versus mutually exclusive events, factorials, permutations and combinations, conditional probability from a table, Bayes' theorem and base rates, naive Bayes with Laplace smoothing, and Monte Carlo estimates.",
    keywords=['probability', 'sample space', 'event', 'addition rule', 'multiplication rule', 'independent events', 'mutually exclusive', 'permutation', 'combination', 'conditional probability', "bayes theorem", 'prior', 'posterior', 'naive bayes', 'monte carlo', 'birthday problem'],
    parts=PARTS, info=INFO, real=REAL, viz=VIZ_JS, css=CSS, allow_diff={},
)
