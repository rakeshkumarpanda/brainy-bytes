from kit import *

FILE = 'test-plan.html'

SECTIONS = [
    sec('strategy', '♟️', 'Test strategy and test approaches', f'''
<p>A <b>test strategy</b> is the general way an organisation or a programme tests: which levels, which kinds of testing, which tools, and how risk is handled. A <b>test plan</b> applies that strategy to one project or release, with dates, names and scope.</p>
{table(['', 'Test strategy', 'Test plan'],
       ['Scope', 'The whole organisation or a large programme', 'One project, release or level'],
       ['Changes', 'Rarely', 'Often, as the project changes'],
       ['Written by', 'Test manager or head of QA', 'Test lead or test manager'],
       ['Answers', 'How do we test here, in general?', 'What, when, who and how much for this release?'])}
<p>A strategy usually combines several <b>test approaches</b>:</p>
{table(['Approach', 'Testing is driven by', 'Example'],
       ['Risk based (analytical)', 'The risks of the product', 'Payments get the most tests because a bug there costs the most'],
       ['Requirements based', 'Every requirement in the SRS', 'Each requirement has test cases in the RTM'],
       ['Model based', 'A model such as a state diagram or a user flow', 'Tests generated from the order status diagram'],
       ['Methodical', 'A standard checklist or quality model', 'ISO 25010 used as a checklist'],
       ['Regression averse', 'Protecting what already works', 'A large automated regression suite'],
       ['Reactive (dynamic)', 'What the product shows while testing', 'Exploratory sessions on each new build'],
       ['Consultative', 'Advice from experts or users', 'Users choose which devices to test'])}
''', say(
        'A test strategy is the general way an organisation tests and changes rarely. A test plan applies it to one release, with dates, names and scope. Strategies combine approaches: risk based, requirements based, model based, methodical, regression averse, reactive such as exploratory testing, and consultative.',
        'Test strategy organisation के test करने का सामान्य तरीका है और कम बदलती है। Test plan उसे एक release पर लागू करता है, तारीखों, नामों और scope के साथ। Strategies कई approaches जोड़ती हैं: risk based, requirements based, model based, methodical, regression averse, reactive जैसे exploratory testing, और consultative।',
        'Test strategy ಸಂಸ್ಥೆಯ ಸಾಮಾನ್ಯ ವಿಧಾನ, ಅಪರೂಪವಾಗಿ ಬದಲು. Test plan ಒಂದು release ಗೆ. Approaches: risk, requirements, model, methodical, regression averse, reactive, consultative.',
        'Test strategy ସଂସ୍ଥାର ସାଧାରଣ ପଦ୍ଧତି, କମ୍ ବଦଳେ। Test plan ଗୋଟିଏ release ପାଇଁ। Approaches: risk, requirements, model, methodical, regression averse, reactive, consultative।',
        'استراتيجية الاختبار هي الطريقة العامة التي تختبر بها المؤسسة ونادرًا ما تتغير. وخطة الاختبار تطبقها على إصدار واحد بالتواريخ والأسماء والنطاق. وتجمع الاستراتيجيات مناهج عدة: القائم على المخاطر، والقائم على المتطلبات، والقائم على النماذج، والمنهجي، ومقاوم الانحدار، والتفاعلي مثل الاختبار الاستكشافي، والاستشاري.',
        'Eine Teststrategie ist die allgemeine Art, wie eine Organisation testet, und ändert sich selten. Ein Testplan wendet sie auf ein Release an, mit Terminen, Namen und Umfang. Strategien kombinieren Ansätze: risikobasiert, anforderungsbasiert, modellbasiert, methodisch, regressionsvermeidend, reaktiv wie exploratives Testen und beratend.')),

    sec('risk-based', '🎯', 'Risk based testing in practice', f'''
<p>Time is always short. <b>Risk based testing</b> spends it where failure would hurt most. Each risk gets a <b>likelihood</b> (how probable a defect is) and an <b>impact</b> (how bad a failure would be), usually from 1 to 5. Their product is the <b>risk level</b>.</p>
{eq('risk level = likelihood × impact')}
{flow('rbt')}
{table(['Area', 'Likelihood', 'Impact', 'Risk level', 'Test depth'],
       ['Fund transfer (new code, complex rules)', '4', '5', '20', 'Deep: all techniques, exploratory sessions, regression automated'],
       ['Loan calculator (changed formula)', '4', '4', '16', 'Deep on calculations and boundaries'],
       ['Profile photo upload', '3', '2', '6', 'Main cases and a few negatives'],
       ['Help pages', '1', '1', '1', 'Quick check, links work'])}
{tip('Likelihood rises with new or changed code, complex logic, many integrations, new developers and areas with past bugs (defect clustering). Impact rises with money, safety, legal duties, number of users and reputation.')}
''', say(
        'Risk based testing spends limited time where failure would hurt most. Each area gets a likelihood and an impact, usually from one to five, and the risk level is their product. High risk areas such as fund transfer get deep testing with many techniques, while low risk areas such as help pages get a quick check.',
        'Risk based testing सीमित समय वहाँ लगाती है जहाँ failure सबसे ज़्यादा नुकसान करे। हर area को likelihood और impact मिलता है, आमतौर पर एक से पाँच, और risk level उनका गुणनफल है। Fund transfer जैसे high risk areas को कई techniques से गहरी testing मिलती है, help pages जैसे low risk areas को जल्दी check।',
        'Risk based testing ಹೆಚ್ಚು ಹಾನಿ ಆಗುವಲ್ಲಿ ಸಮಯ. Likelihood × impact = risk level. Fund transfer ಆಳವಾದ testing, help pages ತ್ವರಿತ check.',
        'Risk based testing ଅଧିକ କ୍ଷତି ହେଉଥିବା ସ୍ଥାନରେ ସମୟ। Likelihood × impact = risk level। Fund transfer ଗଭୀର testing, help pages ଶୀଘ୍ର check।',
        'الاختبار القائم على المخاطر ينفق الوقت المحدود حيث يكون الإخفاق أشد ضررًا. يحصل كل مجال على احتمال وأثر، عادة من واحد إلى خمسة، ومستوى المخاطرة هو حاصل ضربهما. المجالات عالية المخاطر مثل تحويل الأموال تختبر بعمق، والمنخفضة مثل صفحات المساعدة تفحص سريعًا.',
        'Risikobasiertes Testen setzt knappe Zeit dort ein, wo ein Ausfall am meisten schadet. Jeder Bereich erhält Wahrscheinlichkeit und Auswirkung, meist von eins bis fünf, das Risikoniveau ist ihr Produkt. Hochrisikobereiche wie Überweisungen werden tief getestet, Hilfeseiten nur kurz geprüft.')),
]

QUIZ = [
    Qz('e', 'Which document changes more often?', ['Test strategy', 'Test plan', 'Both the same', 'Neither'], 1, 'Project level.', 'The plan follows one project and changes with it. The strategy is organisation wide and stable.'),
    Qz('m', 'Likelihood 3 and impact 5. What is the risk level?', ['8', '15', '2', '35'], 1, 'Multiply.', '3 × 5 = 15.'),
    Qz('h', 'Exploratory sessions planned on every new build are an example of which approach?', ['Methodical', 'Reactive (dynamic)', 'Regression averse', 'Model based'], 1, 'Driven by what the product shows.', 'Reactive approaches adapt to what the tester learns from the running product.'),
]

CALC = [
    Calc('m', 'Areas have risk levels 20, 16, 6 and 1. With 86 hours, effort is shared in proportion to risk. How many hours does the level 20 area get?', '40', '86 * 20 / (20 + 16 + 6 + 1)', 'Hours × its risk ÷ total risk.', [eq('20 + 16 + 6 + 1 = 43'), eq(f'86 × {fr("20", "43")} = 40') + ' hours']),
]

DG = {
    "rbt": {"t": "From risks to test depth", "w": 860, "h": 230,
        "n": [["id", 10, 80, 150, 70, "Identify risks", {"c": 3, "ic": "🔍", "sub": "workshop, history"}],
              ["sc", 200, 80, 160, 70, "Score", {"c": 0, "ic": "🧮", "sub": "likelihood × impact"}],
              ["pr", 400, 80, 150, 70, "Prioritise", {"c": 2, "ic": "📋", "sub": "highest first"}],
              ["dp", 590, 80, 120, 70, "Choose depth", {"c": 1, "ic": "🎚️"}],
              ["mon", 740, 80, 110, 70, "Monitor", {"c": 5, "ic": "📈"}],
              ["back", 400, 180, 310, 40, "New bugs and changes update the risks", {"c": 7, "sh": "pill"}]],
        "e": [["id", "sc", {}], ["sc", "pr", {}], ["pr", "dp", {}], ["dp", "mon", {}], ["mon", "back", {"d": 1}], ["back", "sc", {"d": 1, "via": [[280, 200]]}]],
        "st": [[["id"], "The team lists product risks together, using requirements, past bugs and experience."],
               [["sc", "id>sc"], "Each risk gets a likelihood and an impact from 1 to 5. Multiply them for the risk level."],
               [["pr", "sc>pr"], "Sort by risk level. The highest risks are tested first and most deeply."],
               [["dp", "pr>dp"], "Choose the depth: techniques, number of cases, reviews and automation for each level."],
               [["mon", "back", "dp>mon", "mon>back", "back>sc"], "During testing, new bugs and changes update the scores. Risk based testing never stops adjusting."]]},
}
