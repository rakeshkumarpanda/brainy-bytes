from kit import *

FILE = 'defect-management.html'

SECTIONS = [
    sec('triage', '🚑', 'The defect triage meeting', f'''
<p>When many bugs arrive at once, not all can be fixed at once. <b>Triage</b>, a word borrowed from hospital emergency rooms, means deciding quickly which bugs need attention first. Most teams hold a short triage meeting daily or a few times a week during a test cycle.</p>
{flow('triageflow')}
{table(['Who attends', 'Brings'],
       ['Test lead or tester', 'The new bugs, how to reproduce them, the impact on testing'],
       ['Development lead', 'How hard each fix is and who can take it'],
       ['Product owner or business analyst', 'How much each bug matters to users and the business'],
       ['Release or project manager', 'Dates, and what can still fit in this release'])}
{table(['Decision', 'When'],
       ['Fix now', 'Blockers and critical bugs, anything that stops testing or the release'],
       ['Fix in this release', 'Major bugs with real user impact'],
       ['Defer to a later release', 'Low impact, risky to fix late, a workaround exists'],
       ['Need more information', 'Cannot reproduce, unclear expected result'],
       ['Reject', 'Works as designed, duplicate, not a defect'])}
{tip('Come to triage prepared: one line per bug that says what breaks for the user. "Customers cannot pay with UPI on Android 14" decides faster than "Exception in PaymentActivity".')}
''', say(
        'Triage means deciding quickly which bugs need attention first. In a short meeting the tester, the development lead, the product owner and the manager look at new bugs and decide: fix now, fix in this release, defer, need more information, or reject. Come prepared with one line per bug that says what breaks for the user.',
        'Triage का मतलब जल्दी तय करना कि किन bugs पर पहले ध्यान चाहिए। छोटी meeting में tester, development lead, product owner और manager नए bugs देखकर तय करते हैं: अभी fix, इसी release में fix, बाद में, और जानकारी चाहिए, या reject। हर bug के लिए एक line तैयार रखें कि user के लिए क्या टूटता है।',
        'Triage ಯಾವ bugs ಮೊದಲು ಎಂದು ಬೇಗ ನಿರ್ಧಾರ. Tester, dev lead, product owner, manager: fix now, ಈ release, defer, ಮಾಹಿತಿ ಬೇಕು, reject. User ಗೆ ಏನು ಮುರಿಯುತ್ತದೆ ಎಂಬ ಒಂದು line.',
        'Triage କେଉଁ bugs ପ୍ରଥମେ ଶୀଘ୍ର ନିଷ୍ପତ୍ତି। Tester, dev lead, product owner, manager: fix now, ଏହି release, defer, ତଥ୍ୟ ଦରକାର, reject। User ପାଇଁ କଣ ଭାଙ୍ଗେ ଗୋଟିଏ line।',
        'الفرز يعني أن نقرر بسرعة أي الأخطاء تحتاج الاهتمام أولًا. في اجتماع قصير ينظر المختبر وقائد التطوير ومالك المنتج والمدير في الأخطاء الجديدة ويقررون: إصلاح الآن، أو في هذا الإصدار، أو التأجيل، أو طلب معلومات، أو الرفض. احضر بسطر واحد لكل خطأ يقول ما الذي يتعطل لدى المستخدم.',
        'Triage heißt schnell entscheiden, welche Fehler zuerst Aufmerksamkeit brauchen. In einem kurzen Treffen entscheiden Tester, Entwicklungsleitung, Product Owner und Manager: jetzt beheben, in diesem Release, verschieben, mehr Informationen nötig oder ablehnen. Komm vorbereitet mit einer Zeile je Fehler, was für den Nutzer kaputtgeht.')),

    sec('rca', '🌳', 'Root cause analysis: 5 whys and the fishbone', f'''
<p>Fixing a bug removes one defect. Finding its <b>root cause</b> stops the same kind of bug from coming back. Two simple techniques are used everywhere, from car factories to software teams.</p>
<h3>The 5 whys</h3>
<p>Ask "why?" again and again, about five times, until you reach a cause the team can change:</p>
{flow('fivewhys')}
<h3>The fishbone (Ishikawa) diagram</h3>
<p>Kaoru Ishikawa's diagram puts the problem at the head of a fish and groups possible causes along its bones. For software, common bones are <b>People, Process, Requirements, Tools, Environment and Data</b>.</p>
{flow('fishbone')}
{table(['Root cause found', 'Fix for this bug', 'Fix that prevents the next one'],
       ['Requirement said "above 5,000" without saying if 5,000 is included', 'Correct the comparison', 'Add boundary wording to the requirement review checklist'],
       ['No test for exactly 5,000', 'Add the test', 'Make boundary value analysis part of the Definition of Done'],
       ['Test data had no account at the limit', 'Create one', 'Keep standard edge accounts in every environment'])}
{rule('Root cause analysis looks for causes in the process, never for a person to blame. "Who did it?" stops learning. "What let it happen?" starts it.')}
''', say(
        'Root cause analysis stops the same kind of bug from coming back. The five whys asks why again and again until you reach a cause the team can change. The fishbone diagram groups possible causes such as people, process, requirements, tools, environment and data. Always look for what let it happen, never for a person to blame.',
        'Root cause analysis वैसे ही bug को दोबारा आने से रोकता है। Five whys बार बार क्यों पूछता है जब तक ऐसा कारण न मिले जिसे team बदल सके। Fishbone diagram संभावित कारणों को people, process, requirements, tools, environment और data में बाँटता है। हमेशा देखें कि किस चीज़ ने इसे होने दिया, किसी इंसान को दोष न दें।',
        'Root cause analysis ಅದೇ bug ಮತ್ತೆ ಬರದಂತೆ. Five whys ಮತ್ತೆ ಮತ್ತೆ ಏಕೆ. Fishbone people, process, requirements, tools, environment, data. ವ್ಯಕ್ತಿಯನ್ನು ದೂಷಿಸಬೇಡಿ.',
        'Root cause analysis ସମାନ bug ପୁଣି ନ ଆସିବା ପାଇଁ। Five whys ବାରମ୍ବାର କାହିଁକି। Fishbone people, process, requirements, tools, environment, data। ବ୍ୟକ୍ତିଙ୍କୁ ଦୋଷ ଦିଅନ୍ତୁ ନାହିଁ।',
        'تحليل السبب الجذري يمنع عودة النوع نفسه من الأخطاء. طريقة الأسئلة الخمسة تسأل لماذا مرارًا حتى تصل إلى سبب يستطيع الفريق تغييره. ومخطط عظم السمكة يجمع الأسباب المحتملة في الناس والعملية والمتطلبات والأدوات والبيئة والبيانات. ابحث دائمًا عما سمح بحدوثه، لا عن شخص تلومه.',
        'Ursachenanalyse verhindert, dass dieselbe Art Fehler wiederkommt. Die fünf Warum fragen immer wieder warum, bis eine Ursache erreicht ist, die das Team ändern kann. Das Fischgrätendiagramm gruppiert mögliche Ursachen nach Menschen, Prozess, Anforderungen, Werkzeugen, Umgebung und Daten. Suche immer, was es ermöglichte, nie einen Schuldigen.')),
]

QUIZ = [
    Qz('e', 'What is the main goal of a triage meeting?', ['Writing test cases', 'Deciding quickly which bugs to fix first', 'Closing all bugs', 'Assigning blame'], 1, 'Borrowed from emergency rooms.', 'Triage sets priority and ownership for new bugs.'),
    Qz('m', 'Which category is NOT a usual bone of a software fishbone diagram?', ['Process', 'Requirements', 'Environment', 'The developer\'s name'], 3, 'Causes, not culprits.', 'Fishbone categories describe causes such as people skills, process, tools, environment and data, never individual names.'),
    Qz('h', 'Five whys ends at "the review checklist has no item for boundaries". Which action prevents similar bugs?', ['Fix only this bug', 'Add a boundary item to the review checklist', 'Punish the reviewer', 'Remove reviews'], 1, 'Change what let it happen.', 'Fixing the process cause stops the whole class of defects.'),
]

CALC = [
    Calc('m', 'A cycle logs 48 bugs. Triage marks 30 fix now or this release, 8 deferred, 4 need information and the rest rejected. How many are rejected?', '6', '48 - 30 - 8 - 4', 'Subtract the other groups.', [eq('48 − 30 − 8 − 4 = 6')]),
]

DG = {
    "triageflow": {"t": "A bug at the triage table", "w": 840, "h": 260,
        "n": [["new", 10, 100, 140, 64, "New bug", {"c": 6, "ic": "🐞"}],
              ["t", 200, 100, 160, 64, "Triage meeting", {"c": 3, "ic": "🧑‍⚖️", "sub": "QA, dev, PO, PM"}],
              ["now", 430, 10, 170, 44, "Fix now", {"c": 6, "sh": "pill"}],
              ["rel", 430, 64, 170, 44, "Fix this release", {"c": 0, "sh": "pill"}],
              ["def", 430, 118, 170, 44, "Defer", {"c": 5, "sh": "pill"}],
              ["inf", 430, 172, 170, 44, "Need more info", {"c": 2, "sh": "pill"}],
              ["rej", 650, 100, 170, 44, "Reject", {"c": 7, "sh": "pill", "sub": "as designed, duplicate"}]],
        "e": [["new", "t", {}], ["t", "now", {}], ["t", "rel", {}], ["t", "def", {}], ["t", "inf", {}], ["t", "rej", {"via": [[395, 230], [735, 230]]}]],
        "st": [[["new"], "A new bug arrives with steps, expected and actual results, severity and evidence."],
               [["t", "new>t"], "In triage the tester explains the impact, development says how hard the fix is, and the product owner says how much it matters."],
               [["now", "t>now"], "Blockers and criticals are fixed now, even if that interrupts other work."],
               [["rel", "def", "t>rel", "t>def"], "Major bugs are planned for this release. Low impact bugs with a workaround may be deferred."],
               [["inf", "rej", "t>inf", "t>rej"], "Unclear bugs go back for more information, and some are rejected as duplicates or as designed, always with a reason."]]},
    "fivewhys": {"t": "Five whys for one bug", "w": 860, "h": 300,
        "n": [["p", 10, 10, 840, 44, "Problem: a transfer of exactly ₹5,000 went through, but the limit should block it", {"c": 6, "sh": "pill"}],
              ["w1", 10, 80, 160, 90, "Why 1", {"c": 0, "sub": "code uses >= not >"}],
              ["w2", 180, 80, 160, 90, "Why 2", {"c": 0, "sub": "SRS said \"above\""}],
              ["w3", 350, 80, 160, 90, "Why 3", {"c": 0, "sub": "nobody asked if 5,000\nis included"}],
              ["w4", 520, 80, 160, 90, "Why 4", {"c": 0, "sub": "review had no\nboundary check"}],
              ["w5", 690, 80, 160, 90, "Why 5", {"c": 3, "sub": "checklist never\nupdated"}],
              ["fix", 260, 220, 340, 56, "Action: add boundaries to the review checklist", {"c": 1, "sh": "pill"}]],
        "e": [["w1", "w2", {}], ["w2", "w3", {}], ["w3", "w4", {}], ["w4", "w5", {}], ["w5", "fix", {}]],
        "st": [[["p"], "The problem, stated as a fact."],
               [["w1"], "Why did it go through? The code compares with >= instead of >."],
               [["w2", "w1>w2"], "Why? The requirement said \"above 5,000\" and the developer read it as 5,000 or more."],
               [["w3", "w2>w3"], "Why was that not caught? Nobody asked whether 5,000 itself is included."],
               [["w4", "w3>w4"], "Why? The requirement review had no check for boundary wording."],
               [["w5", "fix", "w4>w5", "w5>fix"], "Why? The checklist was never updated after similar bugs. That is a cause the team can change, so the action targets it."]]},
    "fishbone": {"t": "Fishbone: possible causes of a production bug", "w": 860, "h": 300,
        "n": [["head", 700, 120, 150, 60, "Wrong limit\nin production", {"c": 6}],
              ["c1", 40, 20, 170, 50, "Requirements", {"c": 5, "sub": "vague \"above\""}],
              ["c2", 260, 20, 170, 50, "Process", {"c": 3, "sub": "no boundary review"}],
              ["c3", 480, 20, 170, 50, "People", {"c": 2, "sub": "new to banking rules"}],
              ["c4", 40, 230, 170, 50, "Tools", {"c": 0, "sub": "no mutation testing"}],
              ["c5", 260, 230, 170, 50, "Data", {"c": 7, "sub": "no account at limit"}],
              ["c6", 480, 230, 170, 50, "Environment", {"c": 4, "sub": "limit config differs"}],
              ["spine", 20, 146, 670, 8, "", {"c": 2}]],
        "e": [["c1", "spine", {"d": 1}], ["c2", "spine", {"d": 1}], ["c3", "spine", {"d": 1}], ["c4", "spine", {"d": 1}], ["c5", "spine", {"d": 1}], ["c6", "spine", {"d": 1}], ["spine", "head", {}]],
        "st": [[["head", "spine", "spine>head"], "The problem sits at the head of the fish. The spine leads to it."],
               [["c1", "c2", "c3", "c1>spine", "c2>spine", "c3>spine"], "Upper bones: requirements, process and people. Each holds possible causes found by asking the team."],
               [["c4", "c5", "c6", "c4>spine", "c5>spine", "c6>spine"], "Lower bones: tools, data and environment. Several bones often contribute to one bug."]]},
}
