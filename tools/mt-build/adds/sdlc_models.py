from kit import *

FILE = 'sdlc-models.html'

SECTIONS = [
    sec('kanban-devops', '♾️', 'Kanban, scaled Agile and DevOps', f'''
<p>Scrum is not the only Agile way of working. Three more names appear in almost every job description today.</p>
{grid(box('🗂️ Kanban', 'Work flows across a board (To do, In progress, Testing, Done) without fixed sprints. Each column has a <b>WIP limit</b> (work in progress), for example at most 3 cards in Testing. When the limit is reached, people help finish work instead of starting new work.'),
      box('🏢 Scaled Agile (SAFe, LeSS)', 'Ways to run many Scrum teams on one big product. Teams plan together every few sprints (a "programme increment" in SAFe) and integrate often, so system level testing does not wait for the end.'),
      box('♾️ DevOps', 'Developers and operations share responsibility for building and running the product. Automation carries every change from commit to production, and monitoring feeds learning back to the team.'),
      box('🧪 What changes for testers', 'Smaller pieces tested more often, testing inside the pipeline, and watching production. The Agile, DevOps and Shift Left chapter goes deep into this.'))}
{flow('devopsloop')}
{table(['', 'Scrum', 'Kanban'],
       ['Rhythm', 'Fixed sprints of 1 to 4 weeks', 'Continuous flow'],
       ['Roles', 'Product owner, Scrum master, developers', 'No required roles'],
       ['Limit on work', 'What fits in the sprint', 'WIP limit per column'],
       ['Change during the cycle', 'Avoided inside a sprint', 'Allowed any time, if WIP allows'],
       ['Good for', 'New product features', 'Support, maintenance, bug fixing, operations'])}
{tip('A WIP limit on the Testing column is a quality tool. If testing is full, developers help test or fix bugs, instead of piling more half tested stories in front of the testers.')}
''', say(
        'Kanban moves work across a board without fixed sprints, with a work in progress limit for each column. Scaled Agile frameworks such as SAFe coordinate many Scrum teams on one product. DevOps makes developers and operations share responsibility, with automation from commit to production and monitoring that feeds learning back. For testers it means smaller pieces tested more often.',
        'Kanban बिना fixed sprints के board पर काम आगे बढ़ाता है, हर column की work in progress limit के साथ। SAFe जैसे scaled Agile frameworks एक product पर कई Scrum teams को जोड़ते हैं। DevOps में developers और operations ज़िम्मेदारी बाँटते हैं, commit से production तक automation और monitoring से सीख वापस आती है। Testers के लिए छोटे हिस्से, ज़्यादा बार test।',
        'Kanban fixed sprints ಇಲ್ಲದೆ board ಮೇಲೆ ಕೆಲಸ, ಪ್ರತಿ column ಗೆ WIP limit. SAFe ಅನೇಕ teams ಜೋಡಿಸುತ್ತದೆ. DevOps developers ಮತ್ತು operations ಜವಾಬ್ದಾರಿ ಹಂಚಿಕೆ, automation, monitoring.',
        'Kanban fixed sprints ବିନା board ରେ କାମ, ପ୍ରତି column ପାଇଁ WIP limit। SAFe ଅନେକ teams ଯୋଡ଼େ। DevOps developers ଓ operations ଦାୟିତ୍ୱ ବାଣ୍ଟନ୍ତି, automation, monitoring।',
        'كانبان ينقل العمل على لوحة دون سبرنتات ثابتة، مع حد للعمل الجاري لكل عمود. وأطر أجايل الموسعة مثل SAFe تنسق فرق سكرم كثيرة على منتج واحد. وديف أوبس يجعل المطورين والتشغيل يتقاسمون المسؤولية، مع أتمتة من التعديل إلى الإنتاج ومراقبة تعيد التعلم إلى الفريق.',
        'Kanban bewegt Arbeit ohne feste Sprints über ein Board, mit einer WIP-Grenze je Spalte. Skalierte Agile-Frameworks wie SAFe koordinieren viele Scrum-Teams an einem Produkt. DevOps lässt Entwicklung und Betrieb Verantwortung teilen, mit Automatisierung vom Commit bis zur Produktion und Monitoring als Rückmeldung.')),

    sec('testing-per-model', '🧪', 'Where testing happens in each model', f'''
<p>Every model tests, but at different moments and in different amounts. Knowing this helps a tester plan, and it is a common interview question.</p>
{table(['Model', 'When testing starts', 'How often the product is tested', 'Main testing risk'],
       ['Waterfall', 'After all coding is finished', 'Once, in one long phase', 'Requirement defects found very late and very expensive'],
       ['V model', 'Test documents are written from day one, execution after coding', 'Once per level, in order', 'Still slow to react to changes'],
       ['Spiral', 'In every cycle, module by module', 'Every cycle, with growing regression', 'Regression effort grows quickly'],
       ['Prototype', 'The prototype itself is reviewed and tested with the customer', 'Prototype rounds, then normal testing', 'Customers mistake the prototype for the real thing'],
       ['Scrum', 'Day one of each sprint', 'Every sprint, small pieces', 'Not enough time for regression without automation'],
       ['Kanban and DevOps', 'With every change', 'Continuously, through the pipeline', 'Over trust in automation, flaky tests, gaps in exploratory testing'])}
{flow('changecost')}
''', say(
        'Every model tests, but at different times. In waterfall testing starts after all coding, so requirement defects are found late. The V model writes test documents from day one. Spiral and Scrum test every cycle or sprint, which makes regression grow. Kanban and DevOps test with every change through the pipeline. The later a change arrives, the more it costs.',
        'हर model test करता है, पर अलग समय पर। Waterfall में testing सारी coding के बाद शुरू होती है, इसलिए requirement defects देर से मिलते हैं। V model पहले दिन से test documents लिखता है। Spiral और Scrum हर cycle या sprint में test करते हैं, जिससे regression बढ़ता है। Kanban और DevOps हर बदलाव पर pipeline से test करते हैं। बदलाव जितनी देर से आए, उतना महँगा।',
        'ಪ್ರತಿ model test ಮಾಡುತ್ತದೆ, ಬೇರೆ ಸಮಯದಲ್ಲಿ. Waterfall ಕೊನೆಯಲ್ಲಿ, V model ಮೊದಲ ದಿನದಿಂದ documents, Spiral ಮತ್ತು Scrum ಪ್ರತಿ cycle, DevOps ಪ್ರತಿ ಬದಲಾವಣೆ. ತಡವಾದ ಬದಲಾವಣೆ ದುಬಾರಿ.',
        'ପ୍ରତି model test କରେ, ଅଲଗା ସମୟରେ। Waterfall ଶେଷରେ, V model ପ୍ରଥମ ଦିନରୁ documents, Spiral ଓ Scrum ପ୍ରତି cycle, DevOps ପ୍ରତି ପରିବର୍ତ୍ତନ। ବିଳମ୍ବ ପରିବର୍ତ୍ତନ ମହଙ୍ଗା।',
        'كل نموذج يختبر، لكن في أوقات مختلفة. في الشلال يبدأ الاختبار بعد كل البرمجة فتكتشف عيوب المتطلبات متأخرة. ونموذج V يكتب وثائق الاختبار من اليوم الأول. والحلزوني وسكرم يختبران كل دورة أو سبرنت فيكبر الانحدار. وكانبان وديف أوبس يختبران مع كل تغيير. وكلما تأخر التغيير زادت تكلفته.',
        'Jedes Modell testet, aber zu anderen Zeiten. Im Wasserfall beginnt Testen nach dem gesamten Programmieren, Anforderungsfehler werden spät gefunden. Das V-Modell schreibt Testdokumente ab Tag eins. Spirale und Scrum testen jeden Zyklus oder Sprint, wodurch Regression wächst. Kanban und DevOps testen jede Änderung über die Pipeline. Je später eine Änderung, desto teurer.')),
]

QUIZ = [
    Qz('e', 'What does a WIP limit on the Testing column of a Kanban board do?', ['Limits the number of testers', 'Limits how many cards can be in Testing at once', 'Limits bugs per story', 'Limits the sprint length'], 1, 'Work in progress.', 'When the column is full, the team finishes testing before starting new work.'),
    Qz('m', 'Which model usually finds requirement defects the latest?', ['Scrum', 'Kanban', 'Waterfall', 'Prototype'], 2, 'Testing starts after all coding.', 'In waterfall the first execution happens after the whole product is built, so requirement defects surface late.'),
    Qz('h', 'Which statement about DevOps is correct?', ['It removes the need for testers', 'Developers and operations share responsibility, with automation and monitoring from commit to production', 'It is a programming language', 'It means releasing once a year'], 1, 'Dev plus Ops.', 'DevOps is a culture and set of practices, supported by automated pipelines and monitoring.'),
    Qz('x', 'A support team receives urgent fixes at random times every day. Which approach fits best?', ['Waterfall', 'Scrum with 4 week sprints', 'Kanban with WIP limits', 'The V model'], 2, 'No fixed rhythm.', 'Kanban handles a continuous flow of unpredictable work, while WIP limits keep quality in check.'),
]

CALC = [
    Calc('m', 'A Kanban Testing column has a WIP limit of 4 and holds 3 cards. A developer finishes 2 more stories. How many can move into Testing now?', '1', 'min(2, 4 - 3)', 'Free places = limit − cards.', [eq('4 − 3 = 1') + ' free place', 'The second story waits, and its developer helps test or fix.']),
]

DG = {
    "devopsloop": {"t": "The DevOps loop", "w": 860, "h": 250,
        "n": [["plan", 20, 30, 120, 56, "Plan", {"c": 3, "ic": "🗓️"}], ["code", 170, 30, 120, 56, "Code", {"c": 2, "ic": "💻"}],
              ["build", 320, 30, 120, 56, "Build", {"c": 2, "ic": "⚙️"}], ["test", 470, 30, 120, 56, "Test", {"c": 0, "ic": "🧪"}],
              ["rel", 620, 30, 120, 56, "Release", {"c": 1, "ic": "🚀"}], ["dep", 620, 170, 120, 56, "Deploy", {"c": 1, "ic": "📦"}],
              ["op", 470, 170, 120, 56, "Operate", {"c": 7, "ic": "🖥️"}], ["mon", 320, 170, 120, 56, "Monitor", {"c": 5, "ic": "📈"}],
              ["fb", 120, 170, 150, 56, "Feedback", {"c": 4, "ic": "💬", "sub": "users, alerts"}]],
        "e": [["plan", "code", {}], ["code", "build", {}], ["build", "test", {}], ["test", "rel", {}], ["rel", "dep", {}], ["dep", "op", {}], ["op", "mon", {}], ["mon", "fb", {}], ["fb", "plan", {}]],
        "st": [[["plan", "code", "plan>code"], "The team plans a small change and writes the code."],
               [["build", "test", "code>build", "build>test"], "The pipeline builds it and runs automated checks. Testers explore the change on a test environment."],
               [["rel", "dep", "test>rel", "rel>dep"], "The change is released and deployed, often to a few users first."],
               [["op", "mon", "dep>op", "op>mon"], "Operations keep it running, and monitoring watches errors, speed and usage."],
               [["fb", "mon>fb", "fb>plan"], "What the team learns from users and alerts goes straight into the next plan. The loop never stops."]]},
    "changecost": {"t": "The later a requirement changes, the more it costs", "w": 820, "h": 240,
        "n": [["r", 20, 150, 120, 50, "Requirements", {"c": 1, "sub": "×1"}], ["d", 175, 120, 120, 80, "Design", {"c": 1, "sub": "×3 to ×6"}],
              ["c", 330, 90, 120, 110, "Coding", {"c": 0, "sub": "×10"}], ["t", 485, 60, 120, 140, "Testing", {"c": 6, "sub": "×15 to ×40"}],
              ["p", 640, 20, 160, 180, "After release", {"c": 6, "sub": "×30 to ×100 or more"}]],
        "e": [["r", "d", {}], ["d", "c", {}], ["c", "t", {}], ["t", "p", {}]],
        "tx": [[410, 225, "Relative cost to fix the same defect (classic estimates, they vary by project)", {"s": 11}]],
        "st": [[["r"], "A wrong rule fixed in the requirement costs one sentence."],
               [["d", "r>d"], "Fixed in design, a few diagrams must change too."],
               [["c", "d>c"], "Fixed during coding, code that already exists must be rewritten."],
               [["t", "c>t"], "Found in testing, the fix needs new code, a new build, retesting and regression."],
               [["p", "t>p"], "Found by users, add support calls, hot fixes, data repair and lost trust. That is why every model tries to test earlier."]]},
}
