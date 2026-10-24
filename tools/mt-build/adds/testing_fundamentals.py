from kit import *

FILE = 'testing-fundamentals.html'
DESCRIPTION = 'What software is, what testing means, manual and automation testing, tools, programming and scripting languages, white, black and gray box testing, the seven testing principles, the cost of a late bug, QA versus QC, error, defect and failure, test oracles and the tester mindset.'

SECTIONS = [
    sec('qa-qc', '🏭', 'QA, QC and testing: three different jobs', f'''
<p>People often use these words as if they mean the same thing. They do not, and interviewers love to ask about the difference.</p>
{table(['', 'Quality assurance (QA)', 'Quality control (QC)', 'Testing'],
       ['Focus', 'The <b>process</b>: are we working in a way that prevents defects?', 'The <b>product</b>: does this product meet the standard?', 'A main activity inside QC: running and checking the product'],
       ['Goal', 'Prevent defects', 'Find defects', 'Find defects and give information about quality'],
       ['When', 'All through the project', 'When there is something to inspect', 'Whenever something can be checked'],
       ['Examples', 'Review templates, coding standards, training, audits, retrospectives', 'Reviews of the product, testing, inspections, sign off', 'Functional, integration, system and acceptance testing'],
       ['Owned by', 'Everyone, led by managers and the QA function', 'Testers and reviewers', 'Testers, and developers at unit level'])}
<p>A restaurant shows the difference. <b>QA</b> is the kitchen rules: wash hands, keep raw and cooked food apart, train new cooks. <b>QC</b> is the head chef tasting each plate before it leaves the kitchen. <b>Testing</b> is that tasting itself. Good rules mean fewer bad plates, but someone still tastes every one.</p>
<h3>Error, defect and failure</h3>
<p>A bug has a life story with three stages. ISTQB uses these words precisely:</p>
{flow('errchain')}
{table(['Word', 'Meaning', 'Example'],
       ['Error (mistake)', 'A human action that produces a wrong result', 'The developer reads "greater than 5,000" as "5,000 or more"'],
       ['Defect (bug, fault)', 'The flaw that the error leaves in a work product', 'The code says amount &gt;= 5000 instead of amount &gt; 5000'],
       ['Failure', 'What the user sees when the defect is executed', 'A transfer of exactly 5,000 goes through when it should be blocked'],
       ['Root cause', 'The deepest reason the error happened', 'The requirement used the word "above" without saying whether 5,000 is included'])}
{tip('Not every defect causes a failure. A defect in a screen nobody opens stays silent. And not every failure comes from a defect: a power cut or radiation can also cause one. That is why testers report failures and developers look for defects.')}
''', say(
        'Quality assurance improves the process to prevent defects. Quality control checks the product to find defects, and testing is the main activity of quality control. A bug has three stages. A person makes an error, the error leaves a defect in the code or document, and when that defect runs, the user sees a failure. The root cause is the deepest reason the error happened.',
        'Quality assurance defects रोकने के लिए process सुधारता है। Quality control defects ढूँढने के लिए product जाँचता है, और testing उसकी मुख्य activity है। Bug के तीन चरण हैं। इंसान error करता है, error code या document में defect छोड़ती है, और वह defect चलने पर user को failure दिखता है। Root cause error का सबसे गहरा कारण है।',
        'QA defects ತಡೆಯಲು process ಸುಧಾರಿಸುತ್ತದೆ. QC product ಪರೀಕ್ಷಿಸಿ defects ಹುಡುಕುತ್ತದೆ, testing ಅದರ ಮುಖ್ಯ ಭಾಗ. Error, defect, failure ಮೂರು ಹಂತ. Root cause ಆಳವಾದ ಕಾರಣ.',
        'QA defects ରୋକିବା ପାଇଁ process ସୁଧାରେ। QC product ଯାଞ୍ଚ କରି defects ଖୋଜେ, testing ତାର ମୁଖ୍ୟ ଅଂଶ। Error, defect, failure ତିନି ପର୍ଯ୍ୟାୟ। Root cause ଗଭୀର କାରଣ।',
        'ضمان الجودة يحسن العملية لمنع العيوب. ومراقبة الجودة تفحص المنتج لإيجاد العيوب، والاختبار نشاطها الرئيسي. للخطأ البرمجي ثلاث مراحل: يرتكب شخص خطأ، فيترك عيبًا في الشيفرة أو الوثيقة، وعند تنفيذ العيب يرى المستخدم إخفاقًا. والسبب الجذري هو أعمق سبب للخطأ.',
        'Qualitätssicherung verbessert den Prozess, um Fehler zu verhindern. Qualitätskontrolle prüft das Produkt, um Fehler zu finden, und Testen ist ihre Haupttätigkeit. Ein Bug hat drei Stufen: Ein Mensch macht einen Irrtum, dieser hinterlässt einen Defekt, und wird der Defekt ausgeführt, sieht der Nutzer einen Fehlschlag. Die Grundursache ist der tiefste Grund des Irrtums.')),

    sec('oracle-mindset', '🧠', 'Test oracles and the tester mindset', f'''
<p>To call something a bug, a tester must know what the right result is. Whatever tells you the right result is called a <b>test oracle</b>. The requirement is the main one, but it is never complete, so good testers use several:</p>
{table(['Oracle', 'Example question'],
       ['The requirement, user story or acceptance criteria', 'What does SRS 4.2 say should happen?'],
       ['A previous version of the product', 'Did the old app round this amount the same way?'],
       ['A comparable product', 'How do other banking apps show a failed transfer?'],
       ['Standards and laws', 'Does this meet WCAG contrast rules, or the RBI rule on OTP?'],
       ['A domain expert or the product owner', 'Should a holiday count as a working day for this rule?'],
       ['Consistency inside the product', 'Every other page says "Sign in". Why does this one say "Login"?'],
       ['User expectations and common sense', 'Would a real customer understand this message?'])}
{tip('When oracles disagree, for example the requirement says one thing and the old version did another, do not guess. Raise it as a question. Many important bugs are found exactly in these gaps.')}
<h3>Thinking like a tester</h3>
<p>The ISTQB syllabus describes the tester's mindset as curious, professionally pessimistic, critical, detail minded and keen to communicate well. In practice it means a few habits:</p>
{grid(box('🤔 Ask "what if?"', 'What if the user presses Back? What if two people do this at once? What if the network drops?'),
      box('🎯 Question assumptions', '"It always works" is a belief until it has been tested with odd data, slow networks and real users.'),
      box('🤝 Report without blame', 'A bug report describes the product, not the developer. Facts, steps and impact, calmly written.'),
      box('🧑‍🤝‍🧑 Respect the builder', 'Developers and testers want the same thing: a product users trust. Testers bring a different point of view, not an opposing team.'))}
{deep('confirmation bias and how to beat it', '<p>People tend to look for proof that they are right. A developer who tests their own code often tries the inputs they already expected to work. That is confirmation bias, and it is one reason independent testing finds more bugs. Testers fight their own bias too: plan negative tests on purpose, vary data, swap areas with a colleague, and use checklists so that tiredness does not decide what gets skipped.</p>')}
''', say(
        'A test oracle is whatever tells you the right result: the requirement, an older version, a similar product, standards and laws, a domain expert, consistency inside the product and common sense. When oracles disagree, raise a question instead of guessing. A tester\'s mindset is curious, professionally pessimistic and detail minded, and bugs are reported calmly without blame.',
        'Test oracle वह है जो सही result बताए: requirement, पुराना version, मिलता जुलता product, standards और कानून, domain expert, product के अंदर consistency और common sense। Oracles असहमत हों तो अनुमान न लगाएँ, सवाल उठाएँ। Tester का mindset जिज्ञासु, पेशेवर रूप से निराशावादी और detail पर ध्यान देने वाला है, और bugs बिना दोष दिए शांति से report होते हैं।',
        'Test oracle ಸರಿಯಾದ result ಹೇಳುವುದು: requirement, ಹಳೆಯ version, ಹೋಲುವ product, standards, expert, consistency, common sense. ಒಪ್ಪದಿದ್ದರೆ ಪ್ರಶ್ನೆ ಕೇಳಿ. Tester mindset ಕುತೂಹಲ, detail, ದೋಷಾರೋಪಣೆ ಇಲ್ಲದ reports.',
        'Test oracle ଠିକ୍ result କହେ: requirement, ପୁରୁଣା version, ସମାନ product, standards, expert, consistency, common sense। ମେଳ ନଖାଇଲେ ପ୍ରଶ୍ନ ପଚାରନ୍ତୁ। Tester mindset କୌତୂହଳ, detail, ଦୋଷ ବିନା reports।',
        'مرجع الاختبار هو كل ما يخبرك بالنتيجة الصحيحة: المتطلب، والإصدار السابق، والمنتج المشابه، والمعايير والقوانين، وخبير المجال، والاتساق داخل المنتج، والحس السليم. حين تختلف المراجع اطرح سؤالًا بدل التخمين. وعقلية المختبر فضولية ومتشائمة مهنيًا ودقيقة، وتبلغ عن الأخطاء بهدوء ودون لوم.',
        'Ein Testorakel ist alles, was das richtige Ergebnis sagt: Anforderung, ältere Version, ähnliches Produkt, Normen und Gesetze, Fachexperte, Konsistenz im Produkt und gesunder Menschenverstand. Widersprechen sich Orakel, stelle eine Frage statt zu raten. Die Haltung des Testers ist neugierig, professionell pessimistisch und detailgenau, und Fehler werden sachlich ohne Schuldzuweisung berichtet.')),
]

QUIZ = [
    Qz('e', 'Which activity is quality assurance rather than quality control?', ['Executing system test cases', 'Introducing a review checklist for every SRS', 'Logging a bug', 'Running a smoke test'], 1, 'QA improves the process.', 'A checklist changes how everyone works, so it prevents defects. Executing tests is quality control.'),
    Qz('m', 'A developer misunderstands "above 5,000". The code accepts 5,000. A user transfers 5,000 and it goes through. What is the failure?', ['The misunderstanding', 'The wrong comparison in the code', 'The transfer of 5,000 going through', 'The requirement wording'], 2, 'The failure is what the user sees.', 'The misunderstanding is the error, the comparison is the defect, the visible wrong behaviour is the failure, and the vague wording is the root cause.'),
    Qz('h', 'The SRS is silent about rounding, and the old version rounded paise up. Which oracle helps most?', ['A comparable product only', 'The previous version, then confirm with the product owner', 'Guess what feels right', 'Ignore rounding'], 1, 'Use what exists, then confirm.', 'The old version is a strong oracle, and a gap in the SRS must be confirmed with the product owner.'),
    Qz('x', 'Why do independent testers usually find more defects than authors testing their own work?', ['They are smarter', 'Authors suffer from confirmation bias and test what they expect to work', 'Authors have no tools', 'Independent testers work longer hours'], 1, 'Think about bias.', 'People look for proof that they are right. An independent view tries what the author never thought of.'),
]

CALC = [
    Calc('m', 'A review finds 12 requirement defects, testing finds 30 code defects, and users find 8 after release. What percentage of all defects were found before any code ran (in the review)? ', '24', '12 * 100 / (12 + 30 + 8)', 'Review defects × 100 ÷ all defects.', [eq('12 + 30 + 8 = 50'), eq(f'{fr("12 × 100", "50")} = 24%')], unit='%'),
]

DG = {
    "errchain": {"t": "From a human error to a failure the user sees", "w": 860, "h": 220,
        "n": [["rc", 10, 70, 160, 76, "Root cause", {"c": 5, "ic": "🌱", "sub": "vague word \"above\""}],
              ["err", 230, 70, 160, 76, "Error", {"c": 0, "ic": "🙋", "sub": "a person misreads it"}],
              ["def", 450, 70, 160, 76, "Defect", {"c": 6, "ic": "🐞", "sub": "amount >= 5000"}],
              ["fail", 670, 70, 180, 76, "Failure", {"c": 4, "ic": "💥", "sub": "5,000 is let through"}],
              ["sil", 450, 170, 160, 40, "Not run yet: silent", {"c": 7, "sh": "pill"}]],
        "e": [["rc", "err", {"t": "leads to"}], ["err", "def", {"t": "leaves"}], ["def", "fail", {"t": "when run"}], ["def", "sil", {"d": 1}]],
        "st": [[["rc"], "It starts with a root cause: the requirement says \"above 5,000\" without saying if 5,000 itself is allowed."],
               [["err", "rc>err"], "A developer reads it one way. That human mistake is the error."],
               [["def", "err>def"], "The error leaves a defect in the code: the comparison includes 5,000."],
               [["sil", "def>sil"], "Until someone transfers exactly 5,000, the defect stays silent. It exists, but nobody sees it."],
               [["fail", "def>fail"], "A user transfers exactly 5,000 and it goes through. That visible wrong behaviour is the failure the tester reports."]]},
}
