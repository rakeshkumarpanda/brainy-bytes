from kit import *

FILE = 'white-box-testing.html'

SECTIONS = [
    sec('mcdc-mutation', '🧬', 'Stronger coverage: MC/DC and mutation testing', f'''
<p>Statement and branch coverage show that code ran. Two stronger ideas check whether the tests would really notice a mistake.</p>
<h3>MC/DC: modified condition and decision coverage</h3>
<p>Take the rule: <b>allow the transfer if the user is verified AND (the amount is within the limit OR the payee is trusted)</b>. MC/DC asks for tests where <b>each single condition</b>, on its own, flips the final decision. That proves every condition really matters. Aviation software standards (DO-178C, the highest level) require it.</p>
{table(['Test', 'Verified', 'Within limit', 'Trusted payee', 'Allowed', 'Shows that'],
       ['1', 'Yes', 'Yes', 'No', 'Yes', 'Baseline'],
       ['2', 'No', 'Yes', 'No', 'No', '"Verified" alone flips it (compare with 1)'],
       ['3', 'Yes', 'No', 'No', 'No', '"Within limit" alone flips it (compare with 1)'],
       ['4', 'Yes', 'No', 'Yes', 'Yes', '"Trusted payee" alone flips it (compare with 3)'])}
<p>Four tests instead of all eight combinations. For n conditions, MC/DC usually needs about n + 1 tests.</p>
<h3>Mutation testing: testing the tests</h3>
<p>A tool makes many small deliberate changes to the code, called <b>mutants</b>: it turns &gt; into &gt;=, + into −, true into false. Then it runs the test suite against every mutant. If a test fails, the mutant is <b>killed</b>, which is good. If every test still passes, the mutant <b>survived</b>, which means the tests would not notice that mistake.</p>
{flow('mutation')}
{tip('Tools such as PIT (Java), Stryker (JavaScript and C#) and mutmut (Python) do this automatically. A surviving mutant usually points to a missing boundary test, which manual testers know well from boundary value analysis.')}
''', say(
        'MC/DC asks for tests where each single condition on its own flips the final decision, proving every condition matters. It usually needs about n plus one tests for n conditions and is required for the most critical aviation software. Mutation testing makes small deliberate changes to the code and checks that the tests fail. A mutant that survives shows a gap in the tests.',
        'MC/DC ऐसे tests माँगता है जिनमें हर condition अकेले final decision पलट दे, यह साबित करता है कि हर condition मायने रखती है। n conditions के लिए लगभग n plus one tests चाहिए, और सबसे critical aviation software में यह ज़रूरी है। Mutation testing code में छोटे जानबूझकर बदलाव करके देखती है कि tests fail हों। बचा हुआ mutant tests में कमी दिखाता है।',
        'MC/DC ಪ್ರತಿ condition ಒಂಟಿಯಾಗಿ decision ಬದಲಿಸುವ tests. n conditions ಗೆ ಸುಮಾರು n + 1 tests. Mutation testing code ನಲ್ಲಿ ಸಣ್ಣ ಬದಲಾವಣೆ, tests fail ಆಗಬೇಕು. ಉಳಿದ mutant ಕೊರತೆ ತೋರಿಸುತ್ತದೆ.',
        'MC/DC ପ୍ରତି condition ଏକା decision ବଦଳାଉଥିବା tests। n conditions ପାଇଁ ପ୍ରାୟ n + 1 tests। Mutation testing code ରେ ଛୋଟ ପରିବର୍ତ୍ତନ, tests fail ହେବା ଉଚିତ। ବଞ୍ଚିଥିବା mutant ଅଭାବ ଦେଖାଏ।',
        'تطلب تغطية MC/DC اختبارات يقلب فيها كل شرط بمفرده القرار النهائي، مما يثبت أهمية كل شرط. وتحتاج عادة نحو n زائد واحد من الاختبارات لعدد n من الشروط، وهي مطلوبة لأكثر برمجيات الطيران حرجًا. واختبار الطفرات يجري تغييرات صغيرة متعمدة في الشيفرة ويتحقق من فشل الاختبارات. والطفرة الناجية تكشف ثغرة في الاختبارات.',
        'MC/DC verlangt Tests, in denen jede einzelne Bedingung allein die Entscheidung umkehrt, und beweist so, dass jede Bedingung zählt. Meist braucht es etwa n plus eins Tests für n Bedingungen, und die kritischste Luftfahrtsoftware verlangt es. Mutationstests ändern den Code absichtlich ein wenig und prüfen, ob Tests fehlschlagen. Ein überlebender Mutant zeigt eine Testlücke.')),
]

QUIZ = [
    Qz('m', 'What does it mean when a mutant survives?', ['The code is perfect', 'The tests did not notice that change, so a test is missing', 'The tool crashed', 'The build failed'], 1, 'Survived means nobody caught it.', 'A surviving mutant shows a mistake that the current tests would let through.'),
    Qz('h', 'A decision has 3 conditions. About how many tests does MC/DC usually need?', ['3', '4', '8', '16'], 1, 'n + 1.', 'MC/DC usually needs about n + 1 tests, here 4, instead of all 2³ = 8 combinations.'),
]

CALC = [
    Calc('m', 'A mutation tool creates 120 mutants and the tests kill 96. What is the mutation score?', '80', '96 * 100 / 120', 'Killed × 100 ÷ total.', [eq(f'{fr("96 × 100", "120")} = 80%')], unit='%'),
    Calc('h', 'A decision has 4 independent conditions. How many combinations would full testing need, and how many tests does MC/DC usually need? Give full testing minus MC/DC.', '11', '2 ** 4 - (4 + 1)', '2ⁿ against n + 1.', [eq('2<sup>4</sup> = 16') + ' combinations', eq('4 + 1 = 5') + ' MC/DC tests', eq('16 − 5 = 11') + ' tests saved']),
]

DG = {
    "mutation": {"t": "Mutation testing checks the tests themselves", "w": 840, "h": 250,
        "n": [["code", 10, 90, 150, 70, "Original code", {"c": 2, "sub": "amount > 5000"}],
              ["m1", 230, 20, 170, 60, "Mutant 1", {"c": 0, "sub": "amount >= 5000"}],
              ["m2", 230, 170, 170, 60, "Mutant 2", {"c": 0, "sub": "amount < 5000"}],
              ["suite", 460, 90, 150, 70, "Run all tests", {"c": 3, "ic": "🧪"}],
              ["k", 670, 170, 160, 60, "Killed: a test failed", {"c": 1, "sh": "pill"}],
              ["s", 670, 20, 160, 60, "Survived: all passed", {"c": 6, "sh": "pill"}]],
        "e": [["code", "m1", {}], ["code", "m2", {}], ["m1", "suite", {}], ["m2", "suite", {}], ["suite", "s", {"t": "mutant 1"}], ["suite", "k", {"t": "mutant 2"}]],
        "st": [[["code"], "The real code blocks amounts above 5,000."],
               [["m1", "m2", "code>m1", "code>m2"], "The tool creates small mutants: one changes > to >=, another flips it to <."],
               [["suite", "m1>suite", "m2>suite"], "The full test suite runs against each mutant."],
               [["k", "suite>k"], "Mutant 2 breaks many tests, so it is killed. Good."],
               [["s", "suite>s"], "Mutant 1 survives: no test uses exactly 5,000. Add the boundary test and the mutant dies."]]},
}
