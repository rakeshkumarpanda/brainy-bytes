# Cryptography 2.1: the number theory behind public key cryptography. Checked against Hoffstein, Pipher and
# Silverman, An Introduction to Mathematical Cryptography (2nd edition, chapters 1 and 3), Shoup, A Computational
# Introduction to Number Theory and Algebra, Menezes, van Oorschot and Vanstone, Handbook of Applied Cryptography
# (chapters 2 and 4), Agrawal, Kayal and Saxena, PRIMES is in P (2004), and the RSA-250 factoring announcement (2020).
from cvkit import Kit, fx, fxs, ladder, scene, note, deep, table, steps, viz, eq
from coreaikit import wwh, versus, recap, src
from pykit import chapter, run, files, grow, show, term
from cykit import talk, safe, attack

chapter('cy-numtheory')
K = Kit()

K.code('mod_basics', r'''
# Arithmetic modulo n: only the remainder matters
n = 7
print("17 mod 7 =", 17 % n)
print("-3 mod 7 =", -3 % n)                   # Python always gives 0 to n-1
print("(12 + 9) mod 7 =", (12 + 9) % n, "=", (12 % n + 9 % n) % n)
print("(12 x 9) mod 7 =", (12 * 9) % n, "=", (12 % n) * (9 % n) % n)

# Powers of 3 modulo 7 run through every non zero remainder: 3 is a generator
row = []
for k in range(1, 7):
    row.append(pow(3, k, n))
print("3^1 .. 3^6 mod 7:", row)

# Powers of 2 modulo 7 only reach three values
row = []
for k in range(1, 7):
    row.append(pow(2, k, n))
print("2^1 .. 2^6 mod 7:", row)
''')

K.code('euclid', r'''
# Euclid's algorithm, the extended version, and modular inverses
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def extended_gcd(a, b):
    # returns g, s, t with g = gcd(a, b) = s*a + t*b
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t

def inverse(a, n):
    g, s, t = extended_gcd(a, n)
    if g != 1:
        return None                     # no inverse when a and n share a factor
    return s % n

print("gcd(48, 18) =", gcd(48, 18))
g, s, t = extended_gcd(240, 46)
print("gcd(240, 46) =", g, "=", s, "* 240 +", t, "* 46")
print("inverse of 17 mod 3120 =", inverse(17, 3120))
print("check: 17 * 2753 mod 3120 =", 17 * 2753 % 3120)
print("inverse of 6 mod 9 =", inverse(6, 9))
print("Python 3.8+ can do it too:", pow(17, -1, 3120))
''')

K.code('square_multiply', r'''
# b^e mod n by square and multiply, compared with Python's pow
def power_mod(b, e, n):
    result = 1
    steps = 0
    for bit in bin(e)[2:]:              # the bits of e from left to right
        result = result * result % n    # square for every bit
        steps = steps + 1
        if bit == "1":
            result = result * b % n     # multiply when the bit is 1
            steps = steps + 1
    return result, steps

value, steps = power_mod(4, 13, 497)
print("4^13 mod 497 =", value, "in", steps, "steps")

big_n = 2 ** 127 - 1                    # a Mersenne prime with 39 digits
value, steps = power_mod(123456789, 65537, big_n)
print("123456789^65537 mod (2^127 - 1) found in", steps, "steps")
print("same as pow():", value == pow(123456789, 65537, big_n))
''', long=True)

K.code('fermat_euler', r'''
# Fermat's little theorem and Euler's theorem, checked by computer
from math import gcd

p = 101
ok = True
for a in range(1, p):
    if pow(a, p - 1, p) != 1:
        ok = False
print("a^100 mod 101 = 1 for every a from 1 to 100:", ok)

def phi_count(n):                       # count numbers below n that share no factor with n
    count = 0
    for k in range(1, n):
        if gcd(k, n) == 1:
            count = count + 1
    return count

def phi_formula(p, q):                  # for n = p * q with two different primes
    return (p - 1) * (q - 1)

print("phi(36) =", phi_count(36))
print("phi(143) by counting =", phi_count(143), " by formula =", phi_formula(11, 13))

n = 143
print("Euler: 7^phi(143) mod 143 =", pow(7, phi_formula(11, 13), n))
print("so 7^1000 mod 143 = 7^(1000 mod 120) mod 143 =", pow(7, 1000 % 120, n), "=", pow(7, 1000, n))
''', long=True)

K.code('crt', r'''
# The Chinese remainder theorem: rebuild x from its remainders
def crt(remainders, moduli):
    M = 1
    for m in moduli:
        M = M * m
    x = 0
    for a, m in zip(remainders, moduli):
        Mi = M // m
        yi = pow(Mi, -1, m)              # the inverse of Mi modulo m
        x = x + a * Mi * yi
    return x % M

print("Sun Zi's puzzle:", crt([2, 3, 2], [3, 5, 7]))

# RSA style: work modulo p and q separately, then join the answers
p, q = 61, 53
n = p * q
secret = 1234
mp, mq = secret % p, secret % q
print("1234 mod 61 =", mp, " 1234 mod 53 =", mq, " rebuilt:", crt([mp, mq], [p, q]))
''')

K.code('primes', r'''
# Primality testing: Fermat's test is fooled by Carmichael numbers, Miller-Rabin is not
import secrets

def fermat_test(n, a):
    return pow(a, n - 1, n) == 1

def miller_rabin(n, rounds=20):
    if n < 4:
        return n in (2, 3)
    if n % 2 == 0:
        return False
    d, s = n - 1, 0
    while d % 2 == 0:                    # write n - 1 = 2^s * d with d odd
        d, s = d // 2, s + 1
    for i in range(rounds):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for j in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False                 # a is a witness: n is surely composite
    return True                          # probably prime, error at most 4^-rounds

print("561 = 3 x 11 x 17 passes Fermat with a = 2:", fermat_test(561, 2))
print("Miller-Rabin says 561 is prime:", miller_rabin(561))
print("Miller-Rabin says 2^127 - 1 is prime:", miller_rabin(2 ** 127 - 1))

# Make a random 256 bit prime the way key generators do
tries = 0
while True:
    candidate = secrets.randbits(256) | (1 << 255) | 1   # top bit set (full size) and odd
    tries = tries + 1
    if miller_rabin(candidate):
        break
print("found a 256 bit prime after", tries, "odd candidates (about 89 expected)")
''', long=True)

K.lesson('idea', 'Why public key cryptography needs number theory', f'''
{talk('Symmetric ciphers have one big problem: both sides must already share a secret key. How do you share a key with a website you have never visited, over a network that anyone can watch? For thousands of years there was no answer. Then in 1976 Whitfield Diffie and Martin Hellman published New Directions in Cryptography, and in 1977 Ron Rivest, Adi Shamir and Leonard Adleman at MIT published RSA. We now know that James Ellis, Clifford Cocks and Malcolm Williamson at the British agency GCHQ had found the same ideas a few years earlier, in secret. All of these schemes rest on number theory, the study of whole numbers, which the great mathematician G. H. Hardy proudly called useless in 1940, because no one had found a military use for it. The key idea is a one way function with a trapdoor: something easy to compute, very hard to undo, unless you know a secret. Multiplying two large primes is easy. Splitting the product back into its primes seems to be extremely hard. Raising a number to a power modulo n is easy. Undoing it is hard, unless you know the trapdoor. This chapter gives you every tool you need to understand RSA, Diffie-Hellman and elliptic curves completely.')}
{src('Hoffstein, Pipher and Silverman, An Introduction to Mathematical Cryptography, Shoup, A Computational Introduction to Number Theory and Algebra, Menezes et al., Handbook of Applied Cryptography, Agrawal, Kayal and Saxena (2004).')}
{wwh('<b>Public key cryptography</b> uses a pair of keys: a public key anyone may know and a private key kept secret. Its security rests on <b>hard problems</b> from number theory, such as factoring large numbers and computing discrete logarithms.',
     'It solves key exchange over open networks and makes digital signatures possible. Every HTTPS connection, software update and online payment depends on it.',
     'We need fast operations (modular multiplication, powers, inverses) for the honest users and a problem that seems impossibly slow for everyone else (factoring n = pq, or finding x from g<sup>x</sup> mod p).')}
{table(['Tool', 'What it gives', 'Used in'], [
    ['Modular arithmetic', 'Calculations that wrap round, numbers stay small', 'Everything'],
    ['Euclid and its extension', 'gcd, and inverses modulo n', 'RSA key generation'],
    ['Square and multiply', 'Fast powers b<sup>e</sup> mod n', 'RSA, Diffie-Hellman, signatures'],
    ['Fermat and Euler', 'Why decryption undoes encryption', 'RSA correctness'],
    ['Chinese remainder theorem', 'Split work mod p and mod q', 'Fast RSA decryption'],
    ['Primality tests', 'Find large primes quickly', 'Key generation'],
    ['Hard problems', 'Factoring and discrete log are slow', 'Security of RSA and DH']])}
''', kw=['public key cryptography', 'number theory', 'one way function', 'trapdoor', 'Diffie-Hellman', 'RSA', 'GCHQ', 'Hardy', 'hard problems'])

K.lesson('modular', 'Modular arithmetic', f'''
{talk('You already do modular arithmetic every day with a clock. Five hours after nine o’clock is two o’clock, not fourteen, because the clock wraps round at twelve. Mathematicians write this as 14 is congruent to 2 modulo 12. Carl Friedrich Gauss introduced this notation in 1801, in his book Disquisitiones Arithmeticae, which he wrote at the age of 21. Modular arithmetic has a wonderful property: you can take the remainder at any moment during a calculation and still get the right final remainder. That means even a computation with numbers of millions of digits can be done by keeping only small remainders along the way. Addition, subtraction and multiplication all work. Division is the tricky one, and it only works when the number you divide by shares no factor with the modulus. Powers have patterns too: the powers of 3 modulo 7 cycle through every non zero remainder before returning to 1, which makes 3 a generator. Generators are the heart of Diffie-Hellman key exchange.')}
{wwh('<b>a mod n</b> is the remainder of a divided by n, from 0 to n &minus; 1. Two numbers are <b>congruent</b>, a &equiv; b (mod n), when n divides a &minus; b.',
     'Public key schemes work on huge numbers, but only remainders modulo n matter, so all values stay at a fixed size.',
     'Reduce after every step: (a + b) mod n = ((a mod n) + (b mod n)) mod n, and the same for multiplication. In Python, % always returns a value from 0 to n &minus; 1, even for negative numbers.')}
{run('mod_basics')}
{fxs(fx('Congruence', 'a &equiv; b (mod n) &hArr; n | (a &minus; b)', '14 &equiv; 2 (mod 12) because 12 divides 12.', key=True),
     fx('Rules', '(a + b) mod n = ((a mod n) + (b mod n)) mod n, (a &middot; b) mod n = ((a mod n)(b mod n)) mod n', 'Reduce early and often.', key=True),
     fx('Generator', 'g is a generator mod p if g<sup>1</sup>, g<sup>2</sup>, ..., g<sup>p&minus;1</sup> are all different', '3 is a generator mod 7: 3, 2, 6, 4, 5, 1. 2 is not: 2, 4, 1, 2, 4, 1.'))}
{note('Negative numbers trip up many programmers: in Python, &minus;3 % 7 is 4, but in C, Java and JavaScript, &minus;3 % 7 is &minus;3. Crypto code written in those languages must add n back.', 'exam')}
''', kw=['modular arithmetic', 'congruence', 'mod', 'remainder', 'Gauss', 'clock arithmetic', 'generator', 'cyclic group'])

K.lesson('gcd', 'Euclid’s algorithm and the extended version', f'''
{talk('Euclid wrote down his algorithm for the greatest common divisor around 300 BC, in the Elements, which makes it one of the oldest algorithms still in daily use. The idea is short: the gcd of two numbers does not change if you replace the larger by its remainder after dividing by the smaller. Repeat until the remainder is zero, and the last non zero remainder is the gcd. It is astonishingly fast. In 1844, Gabriel Lamé proved that the number of steps is at most five times the number of digits of the smaller number, and the worst case happens for consecutive Fibonacci numbers. That was one of the first results in the analysis of algorithms. The extended version, which keeps track of how each remainder is built from the two starting numbers, gives something even more useful: two whole numbers s and t with s times a plus t times b equal to the gcd. This is Bézout’s identity. When the gcd is 1, it hands us the inverse of b modulo a, which is exactly how RSA computes its private key.')}
{wwh('<b>Euclid’s algorithm</b> computes gcd(a, b) by repeated division with remainder. The <b>extended</b> algorithm also finds s and t with s&middot;a + t&middot;b = gcd(a, b).',
     'gcd tells whether two numbers share a factor, and the extended version gives modular inverses, needed to make RSA private keys and in many other places.',
     'Keep rows (r, s, t). Start with (a, 1, 0) and (b, 0, 1). Each new row is the row two above minus q times the row above, with q = floor(r<sub>old</sub> / r). Stop at r = 0. The row before holds the gcd and its s and t.')}
{viz('cyeuclid')}
{run('euclid')}
{fxs(fx('Euclid', 'gcd(a, b) = gcd(b, a mod b), gcd(a, 0) = a', 'gcd(48, 18) = gcd(18, 12) = gcd(12, 6) = gcd(6, 0) = 6.', key=True),
     fx('Bézout’s identity', 's&middot;a + t&middot;b = gcd(a, b) for some whole numbers s, t', '(&minus;9)&middot;240 + 47&middot;46 = 2.', key=True),
     fx('Lamé’s bound', 'steps &le; 5 &times; (number of decimal digits of the smaller number)', 'So a 600 digit RSA number needs at most about 3,000 steps, in practice far fewer.'))}
{note('Exam favourite: "Find d with 17d &equiv; 1 (mod 3120)". Run the extended algorithm on 3120 and 17. The answer, 2753, comes from the textbook RSA example with p = 61 and q = 53.', 'exam')}
''', kw=['gcd', 'Euclid algorithm', 'extended Euclidean algorithm', 'Bezout identity', 'Lame theorem', 'Fibonacci', 'modular inverse'])

K.lesson('inverse', 'Modular inverses and when they exist', f'''
{talk('In ordinary arithmetic, dividing by 3 is the same as multiplying by one third. In modular arithmetic there are no fractions, but there can still be a number that acts like one third. Modulo 11, the number 4 does the job, because 3 times 4 is 12, which is 1 modulo 11. So 4 is the inverse of 3 modulo 11. Not every number has an inverse, though. Modulo 9, the number 6 has none, because 6 times anything is a multiple of 3, and no multiple of 3 can leave a remainder of 1 when divided by 9. The rule is clean: a has an inverse modulo n exactly when a and n share no common factor, which means gcd of a and n is 1. When n is a prime, every number from 1 to n minus 1 has an inverse, which is why so much cryptography works modulo primes. RSA relies on this in two places: the public exponent must share no factor with Euler’s phi of n, and the private exponent is its inverse.')}
{wwh('The <b>inverse</b> of a modulo n is the number x with a&middot;x &equiv; 1 (mod n). It exists exactly when gcd(a, n) = 1.',
     'Inverses let us "divide" in modular arithmetic. RSA’s private exponent d is the inverse of e modulo &phi;(n), and the Chinese remainder theorem needs inverses too.',
     'Run the extended Euclidean algorithm on a and n. If the gcd is 1, then s&middot;a + t&middot;n = 1, so s&middot;a &equiv; 1 (mod n), and s mod n is the inverse. In Python 3.8 and later, <code>pow(a, -1, n)</code> does this.')}
{fxs(fx('Inverse', 'a &middot; a<sup>&minus;1</sup> &equiv; 1 (mod n), exists &hArr; gcd(a, n) = 1', '3<sup>&minus;1</sup> mod 11 = 4. 17<sup>&minus;1</sup> mod 3120 = 2753. 6 has no inverse mod 9.', key=True),
     fx('Units', 'the numbers with inverses mod n form the group Z<sub>n</sub><sup>*</sup>, of size &phi;(n)', 'For a prime p, Z<sub>p</sub><sup>*</sup> = {{1, ..., p &minus; 1}}.'))}
{table(['n', 'Numbers with an inverse', 'Count'], [
    ['7 (prime)', '1, 2, 3, 4, 5, 6', '6 = 7 &minus; 1'],
    ['9', '1, 2, 4, 5, 7, 8', '6 = &phi;(9)'],
    ['10', '1, 3, 7, 9', '4 = &phi;(10)'],
    ['15', '1, 2, 4, 7, 8, 11, 13, 14', '8 = &phi;(15) = 2 &times; 4']])}
''', kw=['modular inverse', 'gcd 1', 'coprime', 'pow(a, -1, n)', 'units', 'Z_n star', 'group'])

K.lesson('powmod', 'Fast powers: square and multiply', f'''
{talk('RSA raises a message to a power such as 65537, modulo a number with more than six hundred digits, and decryption uses an exponent with just as many digits. Multiplying the message by itself 65,536 times would already be slow, and multiplying it by itself a number of times with six hundred digits would take longer than the age of the universe. The trick, known for centuries and described in Indian mathematics as early as the Chandah Sutra of Pingala, is to use the binary form of the exponent. Squaring doubles the exponent, and multiplying by the base adds one. So reading the exponent’s bits from left to right, you square at every bit and also multiply when the bit is 1. The number of steps is about twice the number of bits, so a 2048 bit exponent needs only about 3,000 multiplications. And because we reduce modulo n after every step, the numbers never grow beyond twice the size of n. One warning: if the time of each step depends on whether a bit is 0 or 1, a careful attacker who measures the time can read the secret exponent. Paul Kocher showed this timing attack in 1996, so real libraries use constant time methods.')}
{wwh('<b>Square and multiply</b> computes b<sup>e</sup> mod n with about 2 log<sub>2</sub> e multiplications by reading e in binary.',
     'Without it, RSA, Diffie-Hellman and every signature would be far too slow to use.',
     'Start with r = 1. For each bit of e from the left: r = r<sup>2</sup> mod n, and if the bit is 1, r = r &middot; b mod n. Python’s three argument <code>pow(b, e, n)</code> does this in fast C code.')}
{viz('cypowmod')}
{run('square_multiply')}
{fxs(fx('Cost', 'multiplications &le; 2 &lfloor;log<sub>2</sub> e&rfloor;', 'e = 13 = 1101<sub>2</sub>: after the first bit, 3 squarings + 2 multiplications. e = 65537 = 2<sup>16</sup> + 1: 16 squarings + 1 multiplication = 17.', key=True),
     fx('Why it works', 'b<sup>2k</sup> = (b<sup>k</sup>)<sup>2</sup> and b<sup>2k+1</sup> = (b<sup>k</sup>)<sup>2</sup> &middot; b', 'Each bit doubles the exponent read so far, and a 1 bit adds one.'))}
{note('A naive implementation leaks the key: a 1 bit costs an extra multiplication, which shows up in timing and power traces. Libraries use constant time techniques such as the Montgomery ladder, which does the same work for every bit.', 'warn')}
''', kw=['square and multiply', 'modular exponentiation', 'binary exponentiation', 'pow', 'timing attack', 'Kocher', 'Montgomery ladder', '65537'])

K.lesson('euler', 'Fermat’s little theorem, Euler’s phi and Euler’s theorem', f'''
{talk('In 1640, Pierre de Fermat wrote in a letter that if p is a prime and a is not a multiple of p, then a raised to the power p minus 1 leaves a remainder of 1 when divided by p. As often with Fermat, he did not include a proof. Leonhard Euler proved it in 1736, and in 1763 he went further. He defined a function, now written with the Greek letter phi, that counts how many numbers from 1 to n share no factor with n, and he proved that a raised to the power phi of n is 1 modulo n, whenever a shares no factor with n. For a prime p, phi of p is p minus 1, which gives back Fermat’s theorem. For a product of two different primes, phi of p times q is p minus 1 times q minus 1. This is the single most important fact behind RSA. It means exponents can be reduced modulo phi of n, so raising to e and then to d, where e times d is 1 more than a multiple of phi of n, brings every message back to itself. Anyone who knows p and q can compute phi of n easily. Anyone who only knows n seems to need to factor it first.')}
{wwh('<b>Fermat’s little theorem</b>: a<sup>p&minus;1</sup> &equiv; 1 (mod p) for a prime p and p &#8740; a. <b>Euler’s phi</b> &phi;(n) counts 1 &le; k &le; n with gcd(k, n) = 1. <b>Euler’s theorem</b>: a<sup>&phi;(n)</sup> &equiv; 1 (mod n) when gcd(a, n) = 1.',
     'Euler’s theorem is why RSA decryption works, why exponents can be reduced, and why knowing &phi;(n) (that is, knowing p and q) is the trapdoor.',
     'For n = p q with primes p &ne; q, &phi;(n) = (p &minus; 1)(q &minus; 1). Then a<sup>k&phi;(n)+1</sup> &equiv; a (mod n), so choosing e d &equiv; 1 (mod &phi;(n)) makes (a<sup>e</sup>)<sup>d</sup> &equiv; a.')}
{run('fermat_euler')}
{fxs(fx('Fermat', 'a<sup>p&minus;1</sup> &equiv; 1 (mod p)', '2<sup>10</sup> = 1024 = 93 &times; 11 + 1, so 2<sup>10</sup> &equiv; 1 (mod 11).', key=True),
     fx('Euler’s phi', '&phi;(p<sup>k</sup>) = p<sup>k</sup> &minus; p<sup>k&minus;1</sup>, &phi;(m n) = &phi;(m) &phi;(n) when gcd(m, n) = 1', '&phi;(36) = &phi;(4)&phi;(9) = 2 &times; 6 = 12. &phi;(143) = 10 &times; 12 = 120.', key=True),
     fx('Euler’s theorem', 'a<sup>&phi;(n)</sup> &equiv; 1 (mod n)', 'So a<sup>x</sup> &equiv; a<sup>x mod &phi;(n)</sup>. 7<sup>222</sup> mod 11 = 7<sup>2</sup> mod 11 = 5.', key=True),
     fx('Carmichael function', '&lambda;(pq) = lcm(p &minus; 1, q &minus; 1)', 'The smallest exponent that works for every a. Modern RSA standards compute d modulo &lambda;(n).'))}
{deep('Proof of Euler’s theorem in four lines', '<p>Let r<sub>1</sub>, ..., r<sub>k</sub> be the k = &phi;(n) numbers from 1 to n that are coprime to n. Multiply each by a (with gcd(a, n) = 1). The products a r<sub>1</sub>, ..., a r<sub>k</sub> are again coprime to n and all different mod n (if a r<sub>i</sub> &equiv; a r<sub>j</sub>, multiply by a<sup>&minus;1</sup>). So they are the same numbers in a different order. Multiply all of them: a<sup>k</sup> r<sub>1</sub>...r<sub>k</sub> &equiv; r<sub>1</sub>...r<sub>k</sub> (mod n). The product of the r<sub>i</sub> is coprime to n, so cancel it: a<sup>k</sup> &equiv; 1 (mod n). For n = p prime, k = p &minus; 1, which is Fermat’s little theorem.</p>')}
''', kw=['Fermat little theorem', 'Euler phi', 'totient', 'Euler theorem', 'Carmichael function', 'lambda', 'reduce exponents', 'RSA correctness'])

K.lesson('crt', 'The Chinese remainder theorem', f'''
{talk('Around the fourth century, the Chinese mathematician Sun Zi posed a puzzle in his Mathematical Manual: there is an unknown number of things. Counted by threes, two are left over. By fives, three are left over. By sevens, two are left over. How many things are there? The answer is 23, and the general method behind it is the Chinese remainder theorem. It says that if the divisors share no common factors, then the remainders fix the number uniquely, up to the product of the divisors. Think of it as a coordinate system: knowing a number modulo 3, 5 and 7 is the same as knowing it modulo 105. In cryptography this lets us split one big calculation into several smaller ones and join the results. RSA decryption, done modulo p and modulo q separately and then recombined, runs about four times faster than working modulo n directly. The same idea also creates danger: in 1997 Boneh, DeMillo and Lipton showed that if a hardware fault spoils just one of the two halves, a single faulty signature reveals the factors of n.')}
{wwh('The <b>Chinese remainder theorem</b> (CRT): if m<sub>1</sub>, ..., m<sub>k</sub> are pairwise coprime and M is their product, then for any remainders a<sub>i</sub> there is exactly one x from 0 to M &minus; 1 with x &equiv; a<sub>i</sub> (mod m<sub>i</sub>) for every i.',
     'It lets computations mod n = pq be done mod p and mod q separately, which speeds up RSA decryption and signing by about 4 times, and it appears in many attacks.',
     'Compute M<sub>i</sub> = M / m<sub>i</sub> and y<sub>i</sub> = M<sub>i</sub><sup>&minus;1</sup> mod m<sub>i</sub>. Then x = &Sigma; a<sub>i</sub> M<sub>i</sub> y<sub>i</sub> mod M. Each term is a<sub>i</sub> modulo its own m<sub>i</sub> and 0 modulo the others.')}
{viz('cycrt')}
{run('crt')}
{fx('CRT solution', 'x = &Sigma;<sub>i</sub> a<sub>i</sub> M<sub>i</sub> y<sub>i</sub> mod M, with M<sub>i</sub> = M / m<sub>i</sub> and M<sub>i</sub> y<sub>i</sub> &equiv; 1 (mod m<sub>i</sub>)', 'Sun Zi: M = 105. 2&middot;35&middot;2 + 3&middot;21&middot;1 + 2&middot;15&middot;1 = 140 + 63 + 30 = 233 &equiv; 23 (mod 105).', key=True)}
{attack([
    ['Causes a glitch during one half of an RSA-CRT signature (Bellcore attack)', 'Verify every signature before releasing it'],
    ['Collects the same message encrypted with e = 3 to three people', 'Use random padding (OAEP), so the messages differ'],
    ['Times the CRT steps to learn p', 'Constant time code and blinding']])}
''', kw=['Chinese remainder theorem', 'CRT', 'Sun Zi', 'pairwise coprime', 'RSA-CRT', 'Bellcore attack', 'fault attack', 'Garner'])

K.lesson('primes', 'Primes: how many there are and how to find them', f'''
{talk('RSA needs two random primes with about 300 digits each. Are there enough of them, and how do we find one? Euclid proved around 300 BC that there are infinitely many primes. The prime number theorem, proved in 1896 by Jacques Hadamard and Charles de la Vallée Poussin, tells us how common they are: near a number x, roughly one number in every natural log of x is prime. For 1024 bit numbers, that is about one in 710, or one in 355 if we only look at odd numbers. So we pick random odd numbers and test each one, and after a few hundred tries we have a prime. Testing must be fast, and dividing by every smaller number is hopeless. Fermat’s little theorem gives a quick test: if a to the n minus 1 is not 1 mod n, then n is certainly not prime. But some composite numbers, called Carmichael numbers, pass this test for every a. The smallest is 561. The Miller-Rabin test, from 1976 and 1980, fixes this and is wrong with probability at most one in four per round, so 64 rounds make an error less likely than a cosmic ray flipping a bit in your computer. In 2002, Manindra Agrawal and his students Neeraj Kayal and Nitin Saxena at IIT Kanpur proved that primality can be decided with certainty in polynomial time, a famous result, although Miller-Rabin is still used in practice because it is faster.')}
{wwh('A <b>prime</b> has exactly two divisors, 1 and itself. The <b>prime number theorem</b> says about x / ln x primes are below x. <b>Miller-Rabin</b> is a fast probabilistic primality test.',
     'Key generation needs random large primes. Bad primes or weak randomness have broken real keys: in 2012 researchers found that tens of thousands of devices on the internet shared prime factors because of poor randomness at boot.',
     'Pick a random odd number with the top bit set, test it with Miller-Rabin (after quick trial division by small primes), and repeat until one passes.')}
{run('primes')}
{fxs(fx('Prime number theorem', '&pi;(x) &sim; x / ln x', 'Density near x is about 1 / ln x. For x = 2<sup>1024</sup>: ln x = 1024 &times; ln 2 &asymp; 710.', key=True),
     fx('Expected tries', 'about ln(x) / 2 odd candidates', '1024 bit: about 355. 256 bit: ln(2<sup>256</sup>) / 2 &asymp; 89.', key=True),
     fx('Miller-Rabin error', 'P(composite passes k rounds) &le; 4<sup>&minus;k</sup>', '64 rounds: below 2<sup>&minus;128</sup>.'),
     fx('Fermat test fails on Carmichael numbers', '561 = 3 &times; 11 &times; 17, a<sup>560</sup> &equiv; 1 (mod 561) for all a coprime to 561', 'Korselt’s criterion: n is squarefree and p &minus; 1 divides n &minus; 1 for every prime p dividing n.'))}
{note('The 2012 study "Ron was wrong, Whit is right" (Lenstra and others) and "Mining your Ps and Qs" (Heninger and others) found RSA keys that shared a prime with another key. A simple gcd of the two public moduli then factors both instantly.', 'warn')}
''', kw=['prime', 'prime number theorem', 'Miller-Rabin', 'Fermat test', 'Carmichael number', '561', 'AKS', 'IIT Kanpur', 'prime generation', 'shared primes'])

K.lesson('hard', 'The hard problems: factoring and discrete logarithms', f'''
{talk('Public key cryptography is a bet that certain problems are hard. Multiplying two 1024 bit primes takes a computer a microsecond. Splitting their product back into the two primes has resisted mathematicians for centuries. The best known method, the general number field sieve, is much faster than trying divisors, but still grows too quickly for large numbers. In February 2020 a team factored RSA-250, a number of 829 bits, using about 2,700 years of computer core time. A 2048 bit RSA number is estimated to be harder by a factor of billions. The second hard problem is the discrete logarithm. Raising a generator g to a secret power x modulo a prime p is easy with square and multiply. Given the result, finding x seems just as hard as factoring. Diffie-Hellman and DSA rely on it, and elliptic curves rely on a version of it that is even harder. Neither problem is proven hard. And Peter Shor showed in 1994 that a large enough quantum computer would solve both quickly, which is why the world is now moving to post quantum cryptography, covered later in this section.')}
{wwh('<b>Factoring</b>: given n = pq, find p and q. <b>Discrete logarithm</b>: given g, p and h = g<sup>x</sup> mod p, find x. Both seem hard for large numbers on classical computers.',
     'RSA’s security rests on factoring, and Diffie-Hellman, DSA and elliptic curve schemes on discrete logarithms. Key sizes are chosen from the best known attacks.',
     'Trial division needs about &radic;n steps. The general number field sieve takes about exp(1.923 (ln n)<sup>1/3</sup> (ln ln n)<sup>2/3</sup>) steps, sub exponential but still enormous for 2048 bit n.')}
{fxs(fx('Trial division', 'about &radic;n divisions', 'For a 2048 bit n that is 2<sup>1024</sup>, hopeless.', key=True),
     fx('Number field sieve', 'L<sub>n</sub>[1/3, 1.923] = exp( 1.923 (ln n)<sup>1/3</sup> (ln ln n)<sup>2/3</sup> )', 'This is why RSA keys must be much longer than symmetric keys for the same security.', key=True),
     fx('Equivalent strength (NIST SP 800-57)', '128 bit symmetric &asymp; RSA 3072 &asymp; elliptic curve 256', '112 bit &asymp; RSA 2048. 256 bit &asymp; RSA 15360.'))}
{table(['Record', 'Year', 'Size', 'Effort'], [
    ['RSA-129 ("magic words are squeamish ossifrage")', '1994', '426 bits', '1,600 volunteer computers over 8 months'],
    ['RSA-768', '2009', '768 bits', 'About 2,000 core years'],
    ['RSA-240', '2019', '795 bits', 'About 900 core years'],
    ['RSA-250', '2020', '829 bits', 'About 2,700 core years'],
    ['RSA-2048', 'Not factored', '2048 bits', 'Far beyond current classical computers']])}
''', kw=['factoring', 'discrete logarithm', 'number field sieve', 'GNFS', 'RSA-250', 'key size', 'NIST SP 800-57', 'Shor', 'hardness assumption'])

K.lesson('levels', 'From beginner to expert', f'''
{talk('Number theory for cryptography is a ladder you can climb a long way. A beginner learns clock arithmetic and that a product of two primes is easy to make but hard to split. A college student can run the extended Euclidean algorithm by hand, compute phi, reduce big powers with Euler’s theorem, solve Chinese remainder problems and explain Miller-Rabin. A masters student studies groups, rings and finite fields properly, the structure of the multiplicative group modulo a prime, and the sub exponential algorithms: the quadratic sieve, the number field sieve, index calculus for discrete logarithms and Pollard’s rho and p minus 1 methods. At the research level, mathematicians study the exact complexity of these problems, lattice methods such as Coppersmith’s technique that find small roots and break RSA with partial information, and quantum algorithms such as Shor’s, together with careful estimates of how many qubits a real attack would need. In 2025, Craig Gidney of Google estimated that RSA-2048 could be factored with under a million noisy qubits in less than a week, far beyond today’s machines but closer than earlier estimates.')}
{ladder(
    '<p>Modular arithmetic is clock arithmetic. Multiplying two primes is easy, splitting the product is hard. That one sided difficulty is what public key cryptography is built on.</p>',
    '<p>Compute gcd and inverses with the extended Euclidean algorithm, powers with square and multiply, reduce exponents with Euler’s theorem, solve CRT systems, and test primes with Miller-Rabin.</p>',
    '<p>Group theory of Z<sub>n</sub><sup>*</sup>, Lagrange’s theorem, primitive roots, quadratic residues and the Legendre symbol, Pollard’s rho and p &minus; 1, the quadratic sieve and number field sieve, index calculus, and Pohlig-Hellman for discrete logs in groups of smooth order.</p>',
    '<p>Coppersmith’s method for small roots and partial key exposure, lattice reduction (LLL), rigorous analysis of factoring algorithms, Shor’s algorithm and resource estimates (Gidney, 2025: RSA-2048 with fewer than a million noisy qubits in under a week), and the search for problems hard even for quantum computers.</p>')}
{grow('Explain modular arithmetic and why factoring makes public keys possible.',
      'Use Euclid, inverses, fast powers, Euler’s theorem, CRT and Miller-Rabin confidently.',
      'Analyse factoring and discrete log algorithms, lattice attacks and quantum resource estimates.')}
''', kw=['beginner', 'expert', 'group theory', 'Lagrange theorem', 'primitive root', 'Pollard rho', 'quadratic sieve', 'index calculus', 'Coppersmith', 'LLL', 'Shor resource estimates'])

K.lesson('recap', 'Chapter summary', f'''
{recap([
    'Public key cryptography rests on <b>hard problems</b>: factoring n = pq and the discrete logarithm. Honest users need only fast modular operations.',
    'a &equiv; b (mod n) when n divides a &minus; b. Reduce after every step. 3 is a <b>generator</b> mod 7.',
    '<b>Euclid</b>: gcd(a, b) = gcd(b, a mod b). The <b>extended</b> version gives s&middot;a + t&middot;b = gcd (Bézout).',
    'a has an <b>inverse</b> mod n &hArr; gcd(a, n) = 1. 17<sup>&minus;1</sup> mod 3120 = 2753. Python: pow(a, &minus;1, n).',
    '<b>Square and multiply</b>: square every bit, multiply on 1 bits, about 2 log<sub>2</sub> e steps. 65537 needs 17. Use constant time code.',
    '<b>Fermat</b>: a<sup>p&minus;1</sup> &equiv; 1 (mod p). <b>Euler</b>: a<sup>&phi;(n)</sup> &equiv; 1 (mod n), &phi;(pq) = (p &minus; 1)(q &minus; 1). Exponents reduce mod &phi;(n).',
    '<b>CRT</b>: pairwise coprime moduli fix x mod M. x = &Sigma; a<sub>i</sub> M<sub>i</sub> y<sub>i</sub>. Sun Zi’s answer is 23. RSA-CRT is about 4 times faster.',
    'Primes: &pi;(x) &sim; x / ln x, about 355 odd tries for 1024 bits. <b>Miller-Rabin</b> error &le; 4<sup>&minus;k</sup>. 561 fools Fermat’s test.'],
    'Cryptography 2.2 puts these tools together into RSA: key generation, encryption, decryption, signatures, the proof that it works, and the attacks on careless use.')}
{files('Three tasks: a modular inverse, square and multiply without pow, and the Chinese remainder theorem.')}
''', kw=['summary', 'recap'])

K.quiz('e', 'What is 17 mod 5?', ['3', '2', '12', '0'], 1, '17 = 3 &times; 5 + ?', '17 = 3 &times; 5 + 2.')
K.quiz('e', 'What is gcd(48, 18)?', ['2', '3', '6', '9'], 2, '48 = 2 &times; 18 + 12.', 'gcd(48, 18) = gcd(18, 12) = gcd(12, 6) = 6.')
K.quiz('e', 'Which pair is coprime?', ['12 and 18', '14 and 21', '9 and 28', '10 and 25'], 2, 'No shared factor.', '9 = 3<sup>2</sup> and 28 = 2<sup>2</sup> &times; 7 share nothing.')
K.quiz('e', 'Python’s pow(3, 4, 5) gives', ['81', '1', '4', '0'], 1, '3<sup>4</sup> = 81.', '81 mod 5 = 1.')
K.quiz('m', 'When does a have an inverse modulo n?', ['Always', 'When a is prime', 'When gcd(a, n) = 1', 'When a &lt; n'], 2, 'Coprime.', 'The inverse exists exactly when a and n share no factor.')
K.quiz('m', 'What is &phi;(p q) for different primes p and q?', ['pq', '(p &minus; 1)(q &minus; 1)', 'p + q', 'pq &minus; 1'], 1, 'Remove multiples of p and of q.', '&phi;(pq) = pq &minus; p &minus; q + 1 = (p &minus; 1)(q &minus; 1).')
K.quiz('m', 'How many multiplications does square and multiply need for e = 65537?', ['65536', '17', '32', '8'], 1, '2<sup>16</sup> + 1.', '16 squarings and 1 multiplication.')
K.quiz('m', 'Fermat’s little theorem says that for a prime p not dividing a', ['a<sup>p</sup> &equiv; 0', 'a<sup>p&minus;1</sup> &equiv; 1 (mod p)', 'a<sup>2</sup> &equiv; 1', 'a &equiv; p'], 1, 'Exponent p &minus; 1.', 'a<sup>p&minus;1</sup> &equiv; 1 (mod p).')
K.quiz('m', 'Sun Zi: 2 mod 3, 3 mod 5, 2 mod 7. The answer below 105 is', ['8', '23', '52', '68'], 1, 'Check each.', '23 = 7&middot;3 + 2 = 4&middot;5 + 3 = 3&middot;7 + 2.')
K.quiz('h', 'Why does 561 matter in primality testing?', ['It is the largest known prime', 'It is a Carmichael number that passes Fermat’s test for every base coprime to it', 'It breaks Miller-Rabin', 'It is a Mersenne prime'], 1, '3 &times; 11 &times; 17.', 'Carmichael numbers fool the Fermat test, which is why Miller-Rabin is used.')
K.quiz('h', 'Compute 7<sup>222</sup> mod 11 with Euler’s theorem.', ['1', '5', '7', '3'], 1, '&phi;(11) = 10.', '222 mod 10 = 2, and 7<sup>2</sup> = 49 = 4 &times; 11 + 5.')
K.quiz('h', 'Two RSA moduli n1 and n2 accidentally share a prime. An attacker', ['Can do nothing', 'Computes gcd(n1, n2) to get the shared prime and factors both', 'Needs a quantum computer', 'Must factor each separately'], 1, 'Euclid is fast.', 'gcd(n1, n2) = p instantly, then q1 = n1 / p and q2 = n2 / p.')
K.quiz('x', 'In the style of a Stanford CS 255 exam: why is RSA-CRT decryption about 4 times faster than direct decryption mod n?', ['It uses smaller keys', 'Two exponentiations with half size numbers and half size exponents each cost about 1/8 of one full size exponentiation', 'It skips the exponent', 'It avoids modular reduction'], 1, 'Cost of one exponentiation grows like k<sup>3</sup> for k bit numbers.', 'Half the bits: multiplications are 4 times cheaper and there are half as many, so each is 1/8, and two of them give 1/4.')
K.quiz('x', 'In the style of an IIT Kanpur number theory question: the AKS test (2002) showed that primality is', ['Undecidable', 'Decidable in deterministic polynomial time', 'Only decidable with randomness', 'NP complete'], 1, 'PRIMES is in P.', 'Agrawal, Kayal and Saxena gave a deterministic polynomial time test, though Miller-Rabin is faster in practice.')

K.calc('e', 'What is 17 mod 5?', '2', 'Divide and keep the remainder.', ['17 = 3 &times; 5 + 2.', 'The remainder is 2.', eq('17 mod 5 = 2')], check=17 % 5)
K.calc('e', 'What is &minus;3 mod 7 (as a value from 0 to 6)?', '4', 'Add 7.', ['&minus;3 + 7 = 4.', '4 is between 0 and 6.', eq('&minus;3 mod 7 = 4')], check=-3 % 7)
K.calc('e', 'What is gcd(48, 18)?', '6', 'Euclid.', ['48 mod 18 = 12, 18 mod 12 = 6.', '12 mod 6 = 0.', eq('gcd = 6')], check=__import__('math').gcd(48, 18))
K.calc('m', 'What is the inverse of 3 modulo 11?', '4', 'Find x with 3x &equiv; 1.', ['3 &times; 4 = 12.', '12 mod 11 = 1.', eq('3<sup>&minus;1</sup> mod 11 = 4')], check=pow(3, -1, 11))
K.calc('m', 'What is &phi;(36)?', '12', '36 = 2<sup>2</sup> &times; 3<sup>2</sup>.', ['&phi;(4) = 2, &phi;(9) = 6.', 'Multiply (coprime parts).', eq('&phi;(36) = 2 &times; 6 = 12')], check=sum(1 for k in range(1, 36) if __import__('math').gcd(k, 36) == 1))
K.calc('m', 'What is 3<sup>5</sup> mod 7?', '5', '3<sup>5</sup> = 243.', ['243 = 34 &times; 7 + 5.', 'Or: 3, 2, 6, 4, 5.', eq('3<sup>5</sup> mod 7 = 5')], check=pow(3, 5, 7))
K.calc('m', 'For RSA with p = 11 and q = 13, what is &phi;(n)?', '120', '(p &minus; 1)(q &minus; 1).', ['p &minus; 1 = 10.', 'q &minus; 1 = 12.', eq('&phi;(143) = 120')], check=10 * 12)
K.calc('h', 'Compute 7<sup>222</sup> mod 11.', '5', 'Reduce the exponent mod &phi;(11) = 10.', ['222 mod 10 = 2.', '7<sup>2</sup> = 49.', eq('49 mod 11 = 5')], check=pow(7, 222, 11))
K.calc('h', 'Solve x &equiv; 2 (mod 3), x &equiv; 3 (mod 5), x &equiv; 2 (mod 7) with 0 &le; x &lt; 105.', '23', 'CRT.', ['M = 105, M<sub>i</sub> = 35, 21, 15, y<sub>i</sub> = 2, 1, 1.', '2&middot;35&middot;2 + 3&middot;21&middot;1 + 2&middot;15&middot;1 = 233.', eq('233 mod 105 = 23')], check=next(x for x in range(105) if x % 3 == 2 and x % 5 == 3 and x % 7 == 2))
K.calc('h', 'How many multiplications (squarings plus multiplies) does square and multiply use for e = 65537, not counting the first squaring of 1?', '17', '65537 = 2<sup>16</sup> + 1.', ['Binary: 1 followed by 15 zeros and a 1, 17 bits.', '16 squarings after the first bit, and 2 multiplies, but the first multiply is 1 &times; b.', eq('16 + 1 = 17 real multiplications')], check=16 + 1)
K.calc('x', 'In the style of an MIT 18.783 problem: by the prime number theorem, about one in how many random odd 1024 bit numbers is prime? Round to a whole number.', '355', 'Density 1 / ln x, doubled for odd numbers.', ['ln(2<sup>1024</sup>) = 1024 &times; 0.6931 &asymp; 709.8.', 'Only odd numbers: twice as dense.', eq('709.8 / 2 &asymp; 355')], check=round(1024 * __import__('math').log(2) / 2))

K.assign('modinv', 'e', 'A modular inverse',
         '<p>Write <code>modinv(a, n)</code> that returns the inverse of a modulo n (a number from 1 to n &minus; 1), or None if it does not exist. Use the extended Euclidean algorithm, not pow.</p>',
         '''
def modinv(a, n):
    # your code here
    pass
''', [('modinv(3, 11)', 4), ('modinv(17, 3120)', 2753), ('modinv(6, 9)', None), ('modinv(1, 7)', 1)],
         '''
def modinv(a, n):
    old_r, r = a, n
    old_s, s = 1, 0
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    if old_r != 1:
        return None
    return old_s % n
''', 'Track only r and s: at the end old_r is the gcd and old_s the coefficient of a.', '<p>17 and 3120 are the e and &phi;(n) of the classic RSA example with p = 61 and q = 53, so the answer 2753 is that example’s private exponent.</p>')
K.assign('powmod', 'm', 'Square and multiply',
         '<p>Write <code>power_mod(b, e, n)</code> that returns b<sup>e</sup> mod n using square and multiply over the bits of e. Do not use pow or **.</p>',
         '''
def power_mod(b, e, n):
    # your code here
    pass
''', [('power_mod(4, 13, 497)', 445), ('power_mod(2, 10, 1000)', 24), ('power_mod(7, 0, 13)', 1), ('power_mod(123456789, 65537, 1000003)', pow(123456789, 65537, 1000003))],
         '''
def power_mod(b, e, n):
    result = 1 % n
    for bit in bin(e)[2:]:
        result = result * result % n
        if bit == "1":
            result = result * b % n
    return result
''', 'Loop over bin(e)[2:]. Square every time, multiply by b when the bit is "1", and reduce mod n each time.', '<p>For e = 0, bin(0) is "0b0", so the loop squares 1 once and the answer is 1, which is correct.</p>')
K.assign('crt', 'm', 'The Chinese remainder theorem',
         '<p>Write <code>crt(remainders, moduli)</code> for pairwise coprime moduli. Return the x from 0 to M &minus; 1 that has every given remainder.</p>',
         '''
def crt(remainders, moduli):
    # your code here
    pass
''', [('crt([2, 3, 2], [3, 5, 7])', 23), ('crt([1, 2], [4, 9])', 29), ('crt([0, 0, 1], [2, 3, 5])', 6)],
         '''
def crt(remainders, moduli):
    M = 1
    for m in moduli:
        M = M * m
    x = 0
    for i in range(len(moduli)):
        m = moduli[i]
        Mi = M // m
        yi = pow(Mi, -1, m)
        x = x + remainders[i] * Mi * yi
    return x % M
''', 'Compute M, then add a<sub>i</sub> &middot; M<sub>i</sub> &middot; y<sub>i</sub> for each condition, where y<sub>i</sub> is the inverse of M<sub>i</sub> mod m<sub>i</sub>.', '<p>Each term is a<sub>i</sub> modulo its own m<sub>i</sub> and 0 modulo every other modulus, so the sum has all the right remainders at once.</p>')

K.must('Modular', 'a &equiv; b (mod n) &hArr; n | a &minus; b. Reduce after each step. Python % is 0 to n &minus; 1.')
K.must('Euclid', 'gcd(a, b) = gcd(b, a mod b). Extended: s&middot;a + t&middot;b = gcd. Lamé: steps &le; 5 &times; digits.')
K.must('Inverse', 'Exists &hArr; gcd(a, n) = 1. Extended Euclid or pow(a, &minus;1, n). 17<sup>&minus;1</sup> mod 3120 = 2753.')
K.must('Powers', 'Square and multiply, about 2 log<sub>2</sub> e. 65537 = 2<sup>16</sup> + 1 needs 17. Constant time against timing attacks.')
K.must('Fermat and Euler', 'a<sup>p&minus;1</sup> &equiv; 1 (mod p). a<sup>&phi;(n)</sup> &equiv; 1 (mod n). &phi;(pq) = (p &minus; 1)(q &minus; 1).')
K.must('CRT and primes', 'x = &Sigma; a<sub>i</sub>M<sub>i</sub>y<sub>i</sub> mod M. &pi;(x) &sim; x / ln x. Miller-Rabin &le; 4<sup>&minus;k</sup>. 561 is Carmichael.')

T = K.topic(
    slug='cy-numtheory', topic='cy-numtheory', step=(2, 'Public key cryptography and its maths', 'cy-c2', 'The number theory behind public keys, then RSA, Diffie-Hellman and elliptic curves, each with its proofs and its attacks.', 'Advanced'),
    title='Number theory for cryptography: modular arithmetic to primes', short='Number theory', badge='2.1', minutes=80,
    lead='Every tool RSA and Diffie-Hellman need: modular arithmetic and generators, Euclid’s algorithm and its extension, modular inverses, square and multiply, Fermat’s little theorem, Euler’s phi and theorem with a proof, the Chinese remainder theorem, the prime number theorem and Miller-Rabin, and the hard problems of factoring and discrete logarithms.',
    desc='number theory, modular arithmetic, congruence, generator, gcd, Euclid algorithm, extended Euclidean algorithm, Bezout, Lame, modular inverse, square and multiply, modular exponentiation, timing attack, Fermat little theorem, Euler phi, totient, Euler theorem, Carmichael function, Chinese remainder theorem, Sun Zi, RSA-CRT, Bellcore attack, prime number theorem, Miller-Rabin, Carmichael number 561, AKS, factoring, discrete logarithm, number field sieve, RSA-250',
    summary='modular arithmetic, Euclid and inverses, fast powers, Fermat and Euler, CRT, primes and Miller-Rabin, hard problems.',
    keywords=['modular arithmetic', 'gcd', 'extended Euclid', 'inverse', 'square and multiply', 'Euler phi', 'Fermat', 'CRT', 'Miller-Rabin', 'factoring'],
    recap='<p>Fast for the key holder, hopeless for everyone else: modular powers, inverses and Euler’s theorem are easy with the trapdoor, factoring and discrete logs are hard without it.</p>',
    added='2026-11-14')
