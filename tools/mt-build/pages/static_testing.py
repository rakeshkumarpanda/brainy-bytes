from kit import *

FILE = 'static-testing.html'
SLUG, TOPIC, PREFIX = 'mt-static', 'static-testing', 'mts'
TITLE = 'Static Testing and Reviews'
CRUMB = 'Static testing and reviews'
MODULE = '📝 Test design and defects'
EMOJI = '🔎'
DESCRIPTION = 'Testing without running the program: verification and validation, requirement reviews, the five step review process, review roles, informal reviews, walkthroughs, technical reviews and inspections, and static analysis tools.'
LEAD = 'Most bugs are born on paper, long before the first line of code. Static testing finds them there, by reading the requirement, the design or the code with a sharp eye. This page shows how a review works, who does what, and how to spot a requirement that cannot be tested.'
PREV = ('apps-environments.html', 'environments', '🖥️ Applications, Environments and Builds')
NEXT = ('test-design.html', 'test-design', '📝 Test Case Design and Documents')

TOP_SAY = say(
    'Welcome to static testing. Here we test without running anything. We read requirements, designs and code, and we catch mistakes while they are still words on a page, when fixing them costs almost nothing.',
    'Static testing में आपका स्वागत है। यहाँ हम कुछ भी run किए बिना test करते हैं। हम requirements, designs और code पढ़ते हैं, और गलतियाँ तभी पकड़ते हैं जब वे पन्ने पर शब्द ही हैं, जब उन्हें ठीक करना लगभग मुफ़्त है।',
    'Static testing ಗೆ ಸ್ವಾಗತ. ಇಲ್ಲಿ ಏನನ್ನೂ run ಮಾಡದೆ test ಮಾಡುತ್ತೇವೆ. Requirements, designs ಮತ್ತು code ಓದಿ, ತಪ್ಪುಗಳು ಇನ್ನೂ ಪುಟದ ಮೇಲಿನ ಪದಗಳಾಗಿರುವಾಗಲೇ ಹಿಡಿಯುತ್ತೇವೆ, ಆಗ ಸರಿಪಡಿಸಲು ಬಹುತೇಕ ಖರ್ಚಿಲ್ಲ.',
    'Static testing କୁ ସ୍ୱାଗତ। ଏଠାରେ କିଛି run ନକରି test କରାଯାଏ। Requirements, designs ଓ code ପଢ଼ି, ଭୁଲ ପୃଷ୍ଠାରେ ଶବ୍ଦ ଥିବା ବେଳେ ହିଁ ଧରାଯାଏ, ସେତେବେଳେ ସୁଧାରିବା ପ୍ରାୟ ମାଗଣା।',
    'مرحبًا بك في الاختبار الساكن. هنا نختبر دون تشغيل أي شيء. نقرأ المتطلبات والتصاميم والشيفرة، ونلتقط الأخطاء وهي ما تزال كلمات على الورق، حين يكون إصلاحها شبه مجاني.',
    'Willkommen beim statischen Testen. Hier testen wir, ohne etwas auszuführen. Wir lesen Anforderungen, Entwürfe und Code und finden Fehler, solange sie noch Worte auf Papier sind und ihre Behebung fast nichts kostet.')

SECTIONS = [
    sec('what-static', '📄', 'What static testing is', f'''
<p><b>Static testing means checking a work product without running it.</b> Nobody clicks a button or enters a value. People read the document, the design or the code, and tools scan it, looking for mistakes. <b>Dynamic testing</b> is the opposite: the program runs, and the tester watches what it does.</p>
<p>Think of a recipe. Before you cook, you read it and notice that it says "add salt" twice and never says how long to bake. That is static testing. Then you cook the dish and taste it. That is dynamic testing. Both catch problems, but reading the recipe is cheaper than throwing away a burnt cake.</p>
{flow('staticdyn')}
{table(['', 'Static testing', 'Dynamic testing'],
       ['Runs the program', 'No', 'Yes'],
       ['What it finds', 'The defect itself, for example a missing rule in the SRS', 'A failure, which is then traced back to the defect'],
       ['When it can start', 'As soon as anything is written, even day one', 'Only when a build is ready'],
       ['Typical methods', 'Reviews, walkthroughs, inspections, static analysis tools', 'Functional, integration, system and acceptance testing'],
       ['Cost to fix what it finds', 'Very low, the fix is a sentence or a line', 'Higher, the fix needs code, a new build and retesting'])}
<p>Static testing finds defects that running the program can <b>never</b> show. A requirement that is missing produces no failure, because nobody built it. Two requirements that contradict each other may both look fine on screen. Code that can never be reached never runs during a test.</p>
{rule('Static testing does not replace dynamic testing. It removes cheap defects early so dynamic testing can spend its time on the hard ones.')}
''', say(
        'Static testing checks a work product without running it. People read the requirement, design or code, and tools scan it. Dynamic testing runs the program and watches it. Static testing finds the defect itself, often before any code exists, and it finds problems running can never show, such as a missing requirement.',
        'Static testing किसी work product को run किए बिना जाँचना है। लोग requirement, design या code पढ़ते हैं और tools उसे scan करते हैं। Dynamic testing program चलाकर देखती है। Static testing सीधे defect पकड़ती है, अक्सर code बनने से पहले, और ऐसी समस्याएँ भी जो run करने से कभी नहीं दिखतीं, जैसे छूटी हुई requirement।',
        'Static testing ಎಂದರೆ work product ಅನ್ನು run ಮಾಡದೆ ಪರಿಶೀಲಿಸುವುದು. Requirement, design ಅಥವಾ code ಓದುತ್ತಾರೆ, tools scan ಮಾಡುತ್ತವೆ. Dynamic testing program run ಮಾಡಿ ನೋಡುತ್ತದೆ. Static testing ನೇರವಾಗಿ defect ಹಿಡಿಯುತ್ತದೆ, missing requirement ನಂತಹವನ್ನೂ.',
        'Static testing ମାନେ work product କୁ run ନକରି ଯାଞ୍ଚ। Requirement, design କିମ୍ବା code ପଢ଼ାଯାଏ, tools scan କରନ୍ତି। Dynamic testing program ଚଳାଇ ଦେଖେ। Static testing ସିଧା defect ଧରେ, missing requirement ଭଳି ସମସ୍ୟା ମଧ୍ୟ।',
        'الاختبار الساكن يفحص منتج العمل دون تشغيله. يقرأ الناس المتطلب أو التصميم أو الشيفرة، وتمسحه الأدوات. أما الاختبار الديناميكي فيشغل البرنامج ويراقبه. يجد الاختبار الساكن العيب نفسه، غالبًا قبل وجود أي شيفرة، ويجد مشكلات لا يظهرها التشغيل أبدًا، مثل متطلب مفقود.',
        'Statisches Testen prüft ein Arbeitsergebnis, ohne es auszuführen. Menschen lesen Anforderung, Entwurf oder Code, Werkzeuge scannen ihn. Dynamisches Testen führt das Programm aus. Statisches Testen findet den Fehler selbst, oft bevor Code existiert, auch Probleme, die eine Ausführung nie zeigt, etwa eine fehlende Anforderung.')),

    sec('what-review', '🗂️', 'What can be reviewed, and what reviews find', f'''
<p>Almost anything people write can be reviewed. If a person can read it and understand it, a person can check it.</p>
{grid(box('📋 Requirements', 'CRS, SRS, user stories and their acceptance criteria.'),
      box('🏗️ Designs', 'HLD and LLD diagrams, database designs, screen mock ups.'),
      box('💻 Code', 'Source code, configuration files, database scripts.'),
      box('🧪 Test work', 'Test plans, test scenarios, test cases and the RTM.'),
      box('📘 User material', 'Help pages, user guides, release notes and error messages.'),
      box('📜 Contracts', 'The agreement with the customer, the project plan and the schedule.'))}
<p>These are the defects reviews are best at catching:</p>
{table(['Where', 'Typical defect found by a review', 'Everyday example'],
       ['Requirement', 'Ambiguity, contradiction, something missing', 'Page 4 says the PIN has 4 digits, page 9 says 6 digits'],
       ['Requirement', 'Not testable', '"The app must be fast" has no number'],
       ['Design', 'Wrong or missing interface', 'The design sends the amount in rupees, the payment service expects paise'],
       ['Code', 'Unreachable code, unused variables, too complex', 'An if condition that can never be true'],
       ['Code', 'Security weakness', 'A password written in plain text in a config file'],
       ['Test case', 'Wrong expected result, missing negative case', 'The case expects a 6 letter username to be accepted'],
       ['Any', 'Gap in traceability', 'A requirement with no test case in the RTM'])}
{tip('A review finds defects, but it also spreads knowledge. After reading the SRS together, the developer and the tester understand the feature the same way. That alone prevents many bugs.')}
''', say(
        'Anything people write can be reviewed: requirements, user stories, designs, code, test cases, user guides and contracts. Reviews are best at finding ambiguity, contradictions, missing parts, untestable requirements, wrong interfaces, unreachable code and gaps in traceability. A review also helps everyone understand the feature the same way.',
        'लोग जो भी लिखते हैं उसका review हो सकता है: requirements, user stories, designs, code, test cases, user guides और contracts। Reviews ambiguity, विरोधाभास, छूटे हिस्से, untestable requirements, गलत interfaces, unreachable code और traceability की कमी पकड़ने में सबसे अच्छे हैं। Review से सबकी समझ भी एक जैसी होती है।',
        'ಜನ ಬರೆಯುವ ಎಲ್ಲವನ್ನೂ review ಮಾಡಬಹುದು: requirements, user stories, designs, code, test cases, guides ಮತ್ತು contracts. Ambiguity, ವಿರೋಧ, ಕಾಣೆಯಾದ ಭಾಗಗಳು, untestable requirements, unreachable code ಹಿಡಿಯಲು reviews ಉತ್ತಮ. ಎಲ್ಲರ ತಿಳುವಳಿಕೆಯೂ ಒಂದೇ ಆಗುತ್ತದೆ.',
        'ଲୋକେ ଯାହା ଲେଖନ୍ତି ସବୁର review ହୋଇପାରେ: requirements, user stories, designs, code, test cases, guides ଓ contracts। Ambiguity, ବିରୋଧ, ଛାଡ଼ିଯାଇଥିବା ଅଂଶ, untestable requirements, unreachable code ଧରିବାରେ reviews ଭଲ। ସମସ୍ତଙ୍କ ବୁଝାମଣା ମଧ୍ୟ ସମାନ ହୁଏ।',
        'يمكن مراجعة كل ما يكتبه الناس: المتطلبات وقصص المستخدم والتصاميم والشيفرة وحالات الاختبار والأدلة والعقود. تتفوق المراجعات في كشف الغموض والتناقض والنقص والمتطلبات غير القابلة للاختبار والواجهات الخاطئة والشيفرة غير القابلة للوصول وثغرات التتبع. كما توحد فهم الجميع للميزة.',
        'Alles Geschriebene lässt sich prüfen: Anforderungen, User Stories, Entwürfe, Code, Testfälle, Handbücher und Verträge. Reviews finden besonders gut Mehrdeutigkeit, Widersprüche, Lücken, nicht testbare Anforderungen, falsche Schnittstellen, unerreichbaren Code und fehlende Rückverfolgbarkeit. Außerdem verstehen danach alle die Funktion gleich.')),

    sec('verval', '✌️', 'Verification and validation', f'''
<p>These two words sound alike and appear in every interview. The classic way to remember them comes from Barry Boehm:</p>
{grid(box('🔍 Verification: are we building the product right?', 'Checking a work product against its specification. Did we follow the plan? Reviews and inspections are verification. Most static testing is verification.'),
      box('✅ Validation: are we building the right product?', 'Checking the product against what the user really needs. Does it solve their problem? User acceptance testing, beta testing and demos are validation.'))}
{flow('verval')}
<p>A tailor makes a suit. <b>Verification</b>: the tailor measures the finished suit against the order slip. Sleeves 62 cm, as written. <b>Validation</b>: the customer puts it on. If it was written down wrong, the suit matches the slip perfectly and still does not fit. Both checks are needed, because a product can be built exactly to a wrong specification.</p>
{table(['', 'Verification', 'Validation'],
       ['Question', 'Built right?', 'Right thing built?'],
       ['Compared with', 'The specification, design, standards', 'The user\'s real need'],
       ['Typical activity', 'Reviews, walkthroughs, inspections, static analysis', 'Executing the product, UAT, beta, usability sessions'],
       ['When', 'All through the project, from the first document', 'Mostly once something can be used'],
       ['Done by', 'Authors, reviewers, testers, QA', 'Testers, customers, real users'])}
{exam('In the V model, the left side (reviewing CRS, SRS, HLD and LLD) is mostly verification, and the right side (running the tests, ending with UAT) adds validation.')}
''', say(
        'Verification asks: are we building the product right? It checks a work product against its specification, mostly with reviews. Validation asks: are we building the right product? It checks the product against the user\'s real need, for example in user acceptance testing. A product can match a wrong specification perfectly, so both are needed.',
        'Verification पूछता है: क्या हम product सही तरीके से बना रहे हैं? यह work product को specification से मिलाता है, ज़्यादातर reviews से। Validation पूछता है: क्या हम सही product बना रहे हैं? यह product को user की असली ज़रूरत से मिलाता है, जैसे UAT में। Product गलत specification से भी पूरी तरह मेल खा सकता है, इसलिए दोनों ज़रूरी हैं।',
        'Verification ಕೇಳುತ್ತದೆ: product ಸರಿಯಾಗಿ ಕಟ್ಟುತ್ತಿದ್ದೇವಾ? Specification ಜೊತೆ ಹೋಲಿಸುತ್ತದೆ, ಹೆಚ್ಚಾಗಿ reviews ಮೂಲಕ. Validation ಕೇಳುತ್ತದೆ: ಸರಿಯಾದ product ಕಟ್ಟುತ್ತಿದ್ದೇವಾ? User ನ ನಿಜವಾದ ಅಗತ್ಯದ ಜೊತೆ, UAT ಯಲ್ಲಿ ಹಾಗೆ. ಎರಡೂ ಬೇಕು.',
        'Verification ପଚାରେ: product ଠିକ୍ ଭାବେ ତିଆରି ହେଉଛି କି? Specification ସହ ମିଳାଏ, ଅଧିକାଂଶ reviews ରେ। Validation ପଚାରେ: ଠିକ୍ product ତିଆରି ହେଉଛି କି? User ର ପ୍ରକୃତ ଆବଶ୍ୟକତା ସହ, ଯେପରି UAT ରେ। ଦୁହେଁ ଦରକାର।',
        'يسأل التحقق: هل نبني المنتج بشكل صحيح؟ ويقارن منتج العمل بمواصفاته، غالبًا عبر المراجعات. ويسأل الإثبات: هل نبني المنتج الصحيح؟ ويقارن المنتج بحاجة المستخدم الحقيقية، كما في اختبار القبول. قد يطابق المنتج مواصفة خاطئة تمامًا، لذا نحتاج الاثنين.',
        'Verifikation fragt: Bauen wir das Produkt richtig? Sie vergleicht ein Arbeitsergebnis mit seiner Spezifikation, meist durch Reviews. Validierung fragt: Bauen wir das richtige Produkt? Sie vergleicht das Produkt mit dem echten Bedarf der Nutzer, etwa im Abnahmetest. Ein Produkt kann eine falsche Spezifikation perfekt erfüllen, deshalb braucht man beides.')),

    sec('req-review', '🕵️', 'Reviewing a requirement like a tester', f'''
<p>A tester is often the first person who asks "how would I prove this works?" That question exposes weak requirements. A good requirement has these qualities:</p>
{table(['Quality', 'The question a reviewer asks', 'A bad example'],
       ['Clear (unambiguous)', 'Can it be read only one way?', '"Show recent orders" (recent means a day, a week or a month?)'],
       ['Complete', 'Is anything missing, such as errors or limits?', 'Login rules with nothing about a wrong password'],
       ['Consistent', 'Does it agree with every other requirement?', 'Max transfer 50,000 on one page and 1,00,000 on another'],
       ['Testable', 'Can I write a pass or fail check for it?', '"The screen should look modern"'],
       ['Feasible', 'Can it be built with the time and technology?', '"Works offline and always shows the live balance"'],
       ['Traceable', 'Does it have an id, and can tests point to it?', 'A rule given only in a phone call'],
       ['Prioritised', 'Do we know how important it is?', 'Fifty features all marked "must have"'])}
<p>Some words are warning signs. They feel clear, but two people picture different things: <b>fast, quick, user friendly, easy, modern, flexible, robust, appropriate, etc., and/or, some, many, usually, as needed, should, may</b>. Every such word becomes a question for the business analyst.</p>
{viz('ambiguity', 'search')}
{deep('a three question test for every requirement', '<p>Ask three questions. <b>1. What is the input?</b> If you cannot list the valid and invalid values, the requirement is incomplete. <b>2. What is the expected output?</b> If two people would expect different results, it is ambiguous. <b>3. How do I know it passed?</b> If there is no number, message or state to compare, it is not testable.</p><p>Write your questions in the review log with the requirement id, for example "SRS 4.2: what is the maximum number of search results per page?" A list of precise questions is one of the most valuable things a tester gives a project in its first week.</p>')}
''', say(
        'A good requirement is clear, complete, consistent, testable, feasible, traceable and prioritised. Warning words such as fast, user friendly, appropriate, etcetera, and should feel clear, but people imagine different things. Every such word becomes a question for the business analyst. Try to find all of them in the search requirement.',
        'अच्छी requirement clear, complete, consistent, testable, feasible, traceable और prioritised होती है। Fast, user friendly, appropriate, etc. और should जैसे warning शब्द clear लगते हैं, पर लोग अलग चीज़ें सोचते हैं। ऐसा हर शब्द business analyst के लिए सवाल बनता है। Search requirement में सब ढूँढिए।',
        'ಒಳ್ಳೆಯ requirement clear, complete, consistent, testable, feasible, traceable ಮತ್ತು prioritised. Fast, user friendly, appropriate, etc. ಮತ್ತು should ತರಹದ ಪದಗಳು clear ಅನಿಸುತ್ತವೆ, ಆದರೆ ಜನ ಬೇರೆ ಬೇರೆ ಯೋಚಿಸುತ್ತಾರೆ. ಪ್ರತಿ ಪದ business analyst ಗೆ ಪ್ರಶ್ನೆ.',
        'ଭଲ requirement clear, complete, consistent, testable, feasible, traceable ଓ prioritised। Fast, user friendly, appropriate, etc. ଓ should ଭଳି ଶବ୍ଦ clear ଲାଗେ, କିନ୍ତୁ ଲୋକେ ଅଲଗା ଭାବନ୍ତି। ପ୍ରତି ଶବ୍ଦ business analyst ପାଇଁ ପ୍ରଶ୍ନ।',
        'المتطلب الجيد واضح وكامل ومتسق وقابل للاختبار وممكن وقابل للتتبع ومرتب حسب الأولوية. كلمات التحذير مثل سريع وسهل الاستخدام ومناسب وإلخ وينبغي تبدو واضحة، لكن الناس يتخيلون أشياء مختلفة. كل كلمة كهذه تصبح سؤالًا لمحلل الأعمال.',
        'Eine gute Anforderung ist klar, vollständig, widerspruchsfrei, testbar, machbar, rückverfolgbar und priorisiert. Warnwörter wie schnell, benutzerfreundlich, angemessen, usw. und sollte wirken klar, aber jeder stellt sich etwas anderes vor. Jedes solche Wort wird eine Frage an den Business Analysten.')),

    sec('process', '🔁', 'The review process in five steps', f'''
<p>The ISTQB Foundation syllabus (version 4.0) describes a review as five activities. Small informal reviews squeeze them into a few minutes. A formal inspection follows every step and writes everything down.</p>
{flow('revproc')}
{table(['Step', 'What happens', 'Output'],
       ['1. Planning', 'Decide the scope, the goal, the people, the time, and the exit criteria', 'A short review plan'],
       ['2. Review initiation', 'Share the work product, the checklist and the rules', 'Everyone is ready to start'],
       ['3. Individual review', 'Each reviewer reads alone and notes anomalies', 'Personal issue notes'],
       ['4. Communication and analysis', 'Discuss each anomaly, decide if it is a defect, its owner and its severity, and decide if the work product passes', 'An agreed issue log and a review decision'],
       ['5. Fixing and reporting', 'The author fixes the defects, someone checks the fixes, results and metrics are reported', 'An updated work product and a review report'])}
{tip('Most defects are found in step 3, when each person reads alone with full attention. A meeting is for deciding, not for reading the document for the first time.')}
''', say(
        'A review has five steps. Planning sets the scope, people, time and exit criteria. Review initiation shares the material. In the individual review each reviewer reads alone and notes anomalies, and this is where most defects are found. In communication and analysis the group decides which anomalies are real defects. Finally the author fixes them and the results are reported.',
        'Review के पाँच steps हैं। Planning scope, लोग, समय और exit criteria तय करती है। Review initiation material बाँटती है। Individual review में हर reviewer अकेले पढ़ता है, और ज़्यादातर defects यहीं मिलते हैं। Communication and analysis में group तय करता है कि कौन से असली defects हैं। अंत में author ठीक करता है और results report होते हैं।',
        'Review ಗೆ ಐದು steps. Planning scope, ಜನ, ಸಮಯ, exit criteria. Review initiation material ಹಂಚುತ್ತದೆ. Individual review ನಲ್ಲಿ ಪ್ರತಿಯೊಬ್ಬರೂ ಒಬ್ಬರೇ ಓದುತ್ತಾರೆ, ಹೆಚ್ಚು defects ಇಲ್ಲೇ. Communication and analysis ನಲ್ಲಿ ನಿಜವಾದ defects ನಿರ್ಧಾರ. ಕೊನೆಗೆ author ಸರಿಪಡಿಸುತ್ತಾರೆ, report ಆಗುತ್ತದೆ.',
        'Review ର ପାଞ୍ଚ steps। Planning scope, ଲୋକ, ସମୟ, exit criteria। Review initiation material ବାଣ୍ଟେ। Individual review ରେ ପ୍ରତ୍ୟେକ ଏକା ପଢ଼ନ୍ତି, ଅଧିକ defects ଏଠି ମିଳେ। Communication and analysis ରେ ପ୍ରକୃତ defects ସ୍ଥିର ହୁଏ। ଶେଷରେ author ସୁଧାରନ୍ତି ଓ report ହୁଏ।',
        'للمراجعة خمس خطوات. التخطيط يحدد النطاق والأشخاص والوقت ومعايير الخروج. بدء المراجعة يوزع المواد. في المراجعة الفردية يقرأ كل مراجع وحده ويدون الملاحظات، وهنا توجد معظم العيوب. في التواصل والتحليل تقرر المجموعة أي الملاحظات عيوب حقيقية. وأخيرًا يصلحها المؤلف وترفع النتائج.',
        'Ein Review hat fünf Schritte. Die Planung legt Umfang, Personen, Zeit und Endekriterien fest. Der Review-Start verteilt das Material. Im Einzelreview liest jeder allein und notiert Auffälligkeiten, hier werden die meisten Fehler gefunden. In Kommunikation und Analyse entscheidet die Gruppe, was echte Fehler sind. Zuletzt behebt der Autor sie und die Ergebnisse werden berichtet.')),

    sec('roles', '👥', 'Who does what in a review', f'''
<p>One person can hold several roles in a small team. In a formal inspection each role is a different person. Tap a role in the diagram to read its job.</p>
{flow('revroles')}
{table(['Role', 'Main job'],
       ['Manager', 'Decides what is reviewed and provides the time and people'],
       ['Author', 'Created the work product and fixes the defects found in it'],
       ['Review leader', 'Takes overall responsibility, picks the people, organises when and where'],
       ['Moderator (facilitator)', 'Runs the meeting so it stays on time, calm and fair to everyone'],
       ['Scribe (recorder)', 'Collects the anomalies and writes down decisions and new findings from the meeting'],
       ['Reviewer', 'Reads the work product carefully and reports anomalies. Can be a tester, developer, BA, user or expert'])}
{warn('Criticise the work, never the person. "Requirement 4.2 has no maximum length" helps. "You forgot the maximum length again" makes the author defend the document instead of fixing it.')}
''', say(
        'A review has six roles. The manager gives time and people. The author wrote the work product and fixes it. The review leader is responsible overall and organises the review. The moderator keeps the meeting calm and on time. The scribe records anomalies and decisions. Reviewers read carefully and report anomalies. Always criticise the work, never the person.',
        'Review में छह roles हैं। Manager समय और लोग देता है। Author ने work product लिखा और वही ठीक करता है। Review leader पूरी ज़िम्मेदारी लेता है और review organise करता है। Moderator meeting शांत और समय पर रखता है। Scribe anomalies और फ़ैसले लिखता है। Reviewers ध्यान से पढ़ते हैं। हमेशा काम की आलोचना करें, इंसान की नहीं।',
        'Review ನಲ್ಲಿ ಆರು roles. Manager ಸಮಯ ಮತ್ತು ಜನ. Author ಬರೆದವರು, ಸರಿಪಡಿಸುವವರು. Review leader ಒಟ್ಟು ಜವಾಬ್ದಾರಿ. Moderator meeting ಶಾಂತವಾಗಿ ನಡೆಸುತ್ತಾರೆ. Scribe ದಾಖಲಿಸುತ್ತಾರೆ. Reviewers ಓದಿ anomalies ಹೇಳುತ್ತಾರೆ. ಕೆಲಸವನ್ನು ಟೀಕಿಸಿ, ವ್ಯಕ್ತಿಯನ್ನಲ್ಲ.',
        'Review ରେ ଛଅଟି roles। Manager ସମୟ ଓ ଲୋକ ଦିଅନ୍ତି। Author ଲେଖିଥିବା ଓ ସୁଧାରୁଥିବା। Review leader ସମୁଦାୟ ଦାୟିତ୍ୱ। Moderator meeting ଶାନ୍ତ ରଖନ୍ତି। Scribe ଲେଖନ୍ତି। Reviewers ପଢ଼ି anomalies କହନ୍ତି। କାମର ସମାଲୋଚନା କରନ୍ତୁ, ବ୍ୟକ୍ତିର ନୁହେଁ।',
        'للمراجعة ستة أدوار. المدير يوفر الوقت والأشخاص. المؤلف كتب منتج العمل ويصلحه. قائد المراجعة مسؤول عنها وينظمها. الميسر يبقي الاجتماع هادئًا وفي وقته. الكاتب يسجل الملاحظات والقرارات. المراجعون يقرؤون بعناية ويبلغون عن الملاحظات. انتقد العمل دائمًا، لا الشخص.',
        'Ein Review hat sechs Rollen. Der Manager stellt Zeit und Personen. Der Autor hat das Arbeitsergebnis erstellt und behebt Fehler. Der Review-Leiter trägt die Gesamtverantwortung. Der Moderator hält die Sitzung ruhig und pünktlich. Der Protokollant notiert Auffälligkeiten und Entscheidungen. Gutachter lesen sorgfältig. Kritisiere immer die Arbeit, nie die Person.')),

    sec('types', '🪜', 'Four types of review, from a chat to an inspection', f'''
<p>Reviews range from a quick look by a colleague to a strict, measured inspection. The more formal the review, the more it costs and the more defects it finds per page.</p>
{table(['Type', 'Led by', 'How formal', 'Main purpose', 'Example'],
       ['Informal review', 'Anyone', 'No process, no record needed', 'Find anomalies quickly and cheaply', 'A developer asks a tester to glance at a test case'],
       ['Walkthrough', 'The author', 'Some preparation, a meeting', 'Explain, teach, reach a shared understanding, find anomalies', 'The BA walks the team through the new payments story'],
       ['Technical review', 'A moderator', 'Defined process, records kept', 'Reach agreement on technical choices, find anomalies', 'Architects and senior developers review the HLD'],
       ['Inspection', 'A trained review leader (never the author)', 'The most formal, with entry and exit criteria and metrics', 'Find the most anomalies, measure and improve the process', 'The SRS of a medical device is inspected line by line'])}
{flow('revladder')}
{grid(box('🧑‍🤝‍🧑 Pair review', 'Two people look at the same screen and talk through it. Common in Agile teams for test cases and code (pull request reviews).'),
      box('🤝 Three amigos', 'A business person, a developer and a tester read a user story together before work starts. Each asks questions from their own point of view. It is an informal review that happens every sprint.'))}
{exam('Who leads a walkthrough? The author. Who must never lead an inspection? The author. This one pair of facts answers many exam questions.')}
''', say(
        'There are four review types. An informal review is a quick look with no process. A walkthrough is led by the author to explain and share understanding. A technical review is led by a moderator to agree on technical choices. An inspection is the most formal, led by a trained leader who is never the author, with entry and exit criteria and metrics. In Agile, the three amigos meeting is a regular informal review of each user story.',
        'Review के चार प्रकार हैं। Informal review बिना process के जल्दी देखना है। Walkthrough author चलाता है, समझाने के लिए। Technical review moderator चलाता है, technical फ़ैसलों पर सहमति के लिए। Inspection सबसे formal है, trained leader चलाता है जो कभी author नहीं होता, entry और exit criteria और metrics के साथ। Agile में three amigos हर user story का informal review है।',
        'ನಾಲ್ಕು review ಪ್ರಕಾರಗಳು. Informal review process ಇಲ್ಲದ ತ್ವರಿತ ನೋಟ. Walkthrough author ನಡೆಸುತ್ತಾರೆ. Technical review moderator ನಡೆಸುತ್ತಾರೆ. Inspection ಅತ್ಯಂತ formal, author ಅಲ್ಲದ trained leader, metrics ಜೊತೆ. Agile ನಲ್ಲಿ three amigos ಪ್ರತಿ story ಯ informal review.',
        'ଚାରି ପ୍ରକାର review। Informal review process ବିନା ଶୀଘ୍ର ଦେଖିବା। Walkthrough author ଚଳାନ୍ତି। Technical review moderator ଚଳାନ୍ତି। Inspection ସବୁଠୁ formal, author ନଥିବା trained leader, metrics ସହ। Agile ରେ three amigos ପ୍ରତି story ର informal review।',
        'هناك أربعة أنواع للمراجعة. المراجعة غير الرسمية نظرة سريعة بلا إجراءات. الجولة يقودها المؤلف للشرح وتوحيد الفهم. المراجعة الفنية يقودها ميسر للاتفاق على الخيارات التقنية. والتفتيش هو الأكثر رسمية، يقوده قائد مدرب ليس المؤلف أبدًا، مع معايير دخول وخروج ومقاييس. وفي أجايل، اجتماع الأصدقاء الثلاثة مراجعة غير رسمية لكل قصة.',
        'Es gibt vier Review-Arten. Ein informelles Review ist ein schneller Blick ohne Prozess. Ein Walkthrough wird vom Autor geleitet, um zu erklären. Ein technisches Review leitet ein Moderator, um technische Entscheidungen abzustimmen. Eine Inspektion ist am formalsten, geleitet von einem geschulten Leiter, nie dem Autor, mit Ein- und Endekriterien und Metriken. In Agile ist das Three-Amigos-Treffen ein regelmäßiges informelles Review jeder Story.')),

    sec('analysis', '🤖', 'Static analysis: tools that read for you', f'''
<p>Static analysis is static testing done by a tool. The tool reads the code or a document and reports problems, without running anything. Developers use it most, but testers read its reports and use similar tools on their own documents.</p>
{table(['Tool type', 'What it reports', 'Examples'],
       ['Linters and code analysers', 'Unused variables, unreachable code, risky patterns, broken coding rules', 'SonarQube, ESLint, Checkstyle, Pylint'],
       ['Security scanners (SAST)', 'Passwords in code, injection risks, weak encryption', 'SonarQube, Semgrep, GitHub CodeQL'],
       ['Dependency scanners', 'Libraries with known vulnerabilities or bad licences', 'Dependabot, Snyk, OWASP Dependency Check'],
       ['Complexity metrics', 'Cyclomatic complexity, very long functions, duplicated code', 'SonarQube, most IDEs'],
       ['Document checkers', 'Spelling, grammar, banned vague words, broken links', 'Spell checkers, link checkers, requirement quality tools'],
       ['Accessibility checkers', 'Missing alt text, missing labels, low contrast', 'axe, Lighthouse, WAVE'])}
<p>A tool is fast and never tired, but it only knows rules. It cannot tell that a business rule is wrong. A person can tell that "senior citizen means 60 and above" should be "65 and above" for this bank, and no tool will ever notice that.</p>
{tip('Many teams add static analysis to the CI pipeline as a quality gate: if the scan finds a new critical issue, the build is stopped before testers even receive it.')}
''', say(
        'Static analysis is static testing done by a tool. Linters, security scanners, dependency scanners, complexity metrics, document checkers and accessibility checkers read code or documents without running them. Tools are fast and tireless, but they only know rules. Only a person can notice that a business rule itself is wrong.',
        'Static analysis tool द्वारा की गई static testing है। Linters, security scanners, dependency scanners, complexity metrics, document checkers और accessibility checkers code या documents को run किए बिना पढ़ते हैं। Tools तेज़ और बिना थके काम करते हैं, पर सिर्फ़ rules जानते हैं। Business rule ही गलत है, यह सिर्फ़ इंसान देख सकता है।',
        'Static analysis ಎಂದರೆ tool ಮಾಡುವ static testing. Linters, security scanners, dependency scanners, complexity metrics, document ಮತ್ತು accessibility checkers run ಮಾಡದೆ ಓದುತ್ತವೆ. Tools ವೇಗ, ಆದರೆ rules ಮಾತ್ರ ಗೊತ್ತು. Business rule ತಪ್ಪು ಎಂದು ಮನುಷ್ಯ ಮಾತ್ರ ನೋಡಬಲ್ಲ.',
        'Static analysis ମାନେ tool କରୁଥିବା static testing। Linters, security scanners, dependency scanners, complexity metrics, document ଓ accessibility checkers run ନକରି ପଢ଼ନ୍ତି। Tools ଦ୍ରୁତ, କିନ୍ତୁ କେବଳ rules ଜାଣନ୍ତି। Business rule ଭୁଲ ବୋଲି କେବଳ ମଣିଷ ଦେଖିପାରେ।',
        'التحليل الساكن اختبار ساكن تقوم به أداة. أدوات التدقيق وماسحات الأمان وماسحات المكتبات ومقاييس التعقيد ومدققات الوثائق وإمكانية الوصول تقرأ الشيفرة أو الوثائق دون تشغيلها. الأدوات سريعة ولا تتعب، لكنها لا تعرف إلا القواعد. وحده الإنسان يلاحظ أن قاعدة العمل نفسها خاطئة.',
        'Statische Analyse ist statisches Testen durch ein Werkzeug. Linter, Sicherheitsscanner, Abhängigkeitsscanner, Komplexitätsmetriken, Dokument- und Barrierefreiheitsprüfer lesen Code oder Dokumente, ohne sie auszuführen. Werkzeuge sind schnell und unermüdlich, kennen aber nur Regeln. Nur ein Mensch bemerkt, dass eine Geschäftsregel selbst falsch ist.')),

    sec('success', '🌱', 'Making reviews work in a real team', f'''
<p>Reviews fail when they feel like an exam for the author or a waste of time for everyone else. These habits keep them useful:</p>
{grid(box('🎯 A clear goal', 'Say what the review is for: find defects, agree on a design, or train new people. The goal decides the type.'),
      box('🍰 Small pieces', 'Review 10 to 20 pages at a time. After about two hours attention drops and defects slip past.'),
      box('⏳ Time to prepare', 'Reviewers need time for the individual review. A meeting with unprepared people finds little.'),
      box('📋 Checklists', 'A checklist per document type (SRS, test case, code) guides the eye to common mistakes.'),
      box('🙂 A safe culture', 'Defects found in a review are a success, not a failure of the author. Never use review results to rate people.'),
      box('📈 Learn from numbers', 'Track defects found per page and per hour, and which kinds keep coming back, then improve templates and training.'))}
{deep('review numbers that managers ask for', '<p><b>Review rate</b> = pages reviewed ÷ hours spent. Inspections often go slowly, around 5 to 10 pages an hour, because speed hides defects.</p><p><b>Defect density of a document</b> = defects found ÷ pages. Compare it between documents to see which author or template needs help.</p><p><b>Savings</b>: if a requirement defect costs 1 unit to fix in review and around 100 units after release (the classic estimate shown in the fundamentals chapter), then 30 defects removed in one review save roughly 30 × 99 = 2,970 units. The real ratio changes from project to project, but the direction is always the same.</p>')}
{rule('The best compliment for a review: the author says "I am glad you found that now".')}
''', say(
        'Reviews work when they have a clear goal, small pieces of ten to twenty pages, time to prepare, checklists and a safe culture where a found defect is a success and never used to rate people. Track numbers like defects per page and review rate to improve templates and training over time.',
        'Reviews तब काम करते हैं जब उनका साफ़ लक्ष्य हो, दस से बीस pages के छोटे हिस्से, तैयारी का समय, checklists और सुरक्षित माहौल हो जहाँ मिला defect सफलता है और लोगों को rate करने में इस्तेमाल नहीं होता। Defects per page और review rate track करके templates और training सुधारें।',
        'Reviews ಕೆಲಸ ಮಾಡಲು ಸ್ಪಷ್ಟ ಗುರಿ, ಹತ್ತರಿಂದ ಇಪ್ಪತ್ತು pages ನ ಸಣ್ಣ ಭಾಗಗಳು, ತಯಾರಿ ಸಮಯ, checklists ಮತ್ತು ಸುರಕ್ಷಿತ ವಾತಾವರಣ ಬೇಕು. Defects per page ಮತ್ತು review rate track ಮಾಡಿ ಸುಧಾರಿಸಿ.',
        'Reviews ପାଇଁ ସ୍ପଷ୍ଟ ଲକ୍ଷ୍ୟ, ଦଶରୁ କୋଡ଼ିଏ pages ର ଛୋଟ ଅଂଶ, ପ୍ରସ୍ତୁତି ସମୟ, checklists ଓ ସୁରକ୍ଷିତ ପରିବେଶ ଦରକାର। Defects per page ଓ review rate track କରି ସୁଧାରନ୍ତୁ।',
        'تنجح المراجعات حين يكون لها هدف واضح، وأجزاء صغيرة من عشر إلى عشرين صفحة، ووقت للتحضير، وقوائم تحقق، وثقافة آمنة يعد فيها العيب المكتشف نجاحًا ولا يستخدم لتقييم الناس. تابع أرقامًا مثل العيوب لكل صفحة ومعدل المراجعة لتحسين القوالب والتدريب.',
        'Reviews funktionieren mit klarem Ziel, kleinen Stücken von zehn bis zwanzig Seiten, Vorbereitungszeit, Checklisten und einer sicheren Kultur, in der ein gefundener Fehler ein Erfolg ist und nie zur Bewertung von Menschen dient. Verfolge Zahlen wie Fehler pro Seite und Review-Rate, um Vorlagen und Schulungen zu verbessern.')),
]

INFO = {"title": "Catch the bug while it is still a sentence", "panels": [
    {"s": [["e", "📄"], ["t", "SRS v1.2", {"b": 1}]], "h": "A document arrives", "t": "The requirement is shared with the team.", "more": "Nothing has been coded yet."},
    {"s": [["e", "🕵️"], ["t", "fast? all? etc.?", {"b": 1}]], "h": "Reviewers read alone", "t": "Each person notes what is unclear or missing.", "more": "Most defects are found in this quiet step."},
    {"s": [["e", "🤝"], ["t", "defect · not a defect · question", {"b": 1, "size": 12}]], "h": "The team decides", "t": "Every anomaly gets an owner and a decision.", "more": "Criticise the work, never the person."},
    {"s": [["e", "✅"], ["t", "SRS v1.3", {"b": 1}]], "h": "Fixed on paper", "t": "The author fixes it in minutes.", "more": "The same bug found after release could take weeks."}],
    "remember": "Static testing reads instead of runs. It finds the defect itself, very early, when a fix is only a sentence."}

REAL = [
    ["💌", "Proofreading a wedding card", "Before 500 cards are printed, the family reads the draft and spots a wrong date. Fixing the draft costs nothing. Reprinting 500 cards costs a lot. That is a review."],
    ["🏗️", "Checking the blueprint", "A builder who finds that the staircase in the drawing hits a beam fixes the drawing. Finding it after the concrete is poured means breaking walls."],
    ["✈️", "Pilot and co pilot", "Before take off one pilot reads the checklist aloud and the other confirms each item. Two pairs of eyes on the same list catch what one pair misses."]]

QUIZ = [
    Qz('e', 'What makes testing "static"?', ['It is done by a tool', 'The work product is checked without being run', 'It is done only once', 'It uses fixed test data'], 1, 'Static means not moving.', 'Static testing examines a document or code without executing it. Dynamic testing runs the program.'),
    Qz('e', 'Which of these can be reviewed?', ['Only code', 'Only requirements', 'Any work product people can read, such as requirements, designs, code and test cases', 'Only the running application'], 2, 'If a person can read it, a person can check it.', 'Reviews apply to requirements, user stories, designs, code, test cases, guides and contracts.'),
    Qz('e', 'Who leads a walkthrough?', ['The moderator', 'The author', 'The manager', 'The customer'], 1, 'The person who knows the document best explains it.', 'In a walkthrough the author guides the group through the work product.'),
    Qz('e', 'Verification asks which question?', ['Are we building the right product?', 'Are we building the product right?', 'Is the user happy?', 'Is the server fast?'], 1, 'Right way, against the spec.', 'Verification checks a work product against its specification. Validation checks the product against the real user need.'),
    Qz('m', 'In which review step are most defects usually found?', ['Planning', 'Review initiation', 'Individual review', 'Fixing and reporting'], 2, 'The quiet step with full attention.', 'Each reviewer reads alone with a checklist. The meeting decides about anomalies already found.'),
    Qz('m', 'Which requirement is testable?', ['The app must be fast', 'The app must be user friendly', 'The first 20 results appear within 2 seconds for 95% of searches', 'The app should work on all devices'], 2, 'Look for a number you can measure.', 'Only that requirement gives a measurable pass or fail condition.'),
    Qz('m', 'Which defect can static testing find that dynamic testing cannot?', ['A slow page', 'A missing requirement that was never built', 'A crash on submit', 'A wrong colour on screen'], 1, 'You cannot see a failure for a feature nobody built.', 'A missing requirement causes no failure when running the program, but a reviewer notices the gap.'),
    Qz('m', 'Who must never be the review leader of an inspection?', ['A tester', 'The author', 'A trained moderator', 'A senior developer'], 1, 'Independence matters in the most formal review.', 'In an inspection the author cannot lead or act as scribe, so the review stays independent.'),
    Qz('h', 'A team reviews 120 pages in one 2 hour meeting and finds 3 defects. What is the most likely problem?', ['The document is perfect', 'The review went too fast and reviewers were not prepared', 'There were too many reviewers', 'The scribe was absent'], 1, 'Think about review rate.', '60 pages an hour is far too fast for careful review. Reviews work best with small pieces and individual preparation.'),
    Qz('h', 'Which statement about static analysis tools is correct?', ['They can prove the business rules are right', 'They find rule based problems like unused variables without running code', 'They replace all reviews', 'They need the application installed on a server'], 1, 'Tools know rules, not the business.', 'Static analysis finds rule breaks in code or documents. Only people can judge whether a business rule is correct.'),
    Qz('x', 'A suit matches the order slip exactly, but the slip had the wrong sleeve length. Which check failed?', ['Verification', 'Validation', 'Both', 'Neither'], 1, 'The product was built right, but was it the right product?', 'Verification passed because the suit matches the specification. Validation failed because it does not meet the real need.'),
    Qz('x', 'In a three amigos meeting the tester asks "what happens if two people buy the last item at the same moment?". What is the tester doing?', ['Dynamic testing', 'Exploratory testing of the build', 'Static testing through an informal review of the story', 'Performance testing'], 2, 'Nothing is running yet.', 'The story is being reviewed before any code exists. Asking about a missing case is static testing.'),
]

CALC = [
    Calc('e', 'A team reviews 30 pages in 4 hours. What is the review rate in pages per hour?', '7.5', '30 / 4', 'Pages ÷ hours.', [eq(f'{fr("30", "4")} = 7.5') + ' pages per hour']),
    Calc('e', 'A 40 page SRS review finds 18 defects. What is the defect density per page?', '0.45', '18 / 40', 'Defects ÷ pages.', [eq(f'{fr("18", "40")} = 0.45') + ' defects per page']),
    Calc('m', 'Fixing a requirement defect costs ₹500 in review and ₹50,000 after release. A review finds 12 defects. How much money does it save?', '594000', '12 * (50000 - 500)', 'Savings per defect × number of defects.', [eq('50,000 − 500 = 49,500') + ' saved per defect', eq('12 × 49,500 = 5,94,000')], unit='₹'),
    Calc('m', 'A review meeting has 5 people for 2 hours, and each person also prepared for 3 hours. How many person hours did the review cost?', '25', '5 * (2 + 3)', 'Add preparation and meeting time per person.', [eq('2 + 3 = 5') + ' hours per person', eq('5 × 5 = 25') + ' person hours']),
    Calc('h', 'Reviewer A finds 20 defects, reviewer B finds 15, and 10 of them are the same. How many different defects did they find together?', '25', '20 + 15 - 10', 'Do not count shared defects twice.', [eq('20 + 15 − 10 = 25')]),
    Calc('x', 'Using the estimate above (A found 20, B found 15, 10 shared), the capture recapture idea estimates the total defects as A × B ÷ shared. How many defects probably exist in the document?', '30', '20 * 15 / 10', 'A × B ÷ shared.', [eq(f'{fr("20 × 15", "10")} = 30'), 'So about 30 − 25 = 5 defects are probably still hiding.']),
]

DG = {
    "staticdyn": {"t": "Reading against running", "w": 820, "h": 280,
        "g": [[10, 10, 390, 258, "Static testing", 1], [420, 10, 390, 258, "Dynamic testing", 2]],
        "n": [["doc", 30, 60, 150, 76, "Work product", {"c": 5, "sh": "doc", "sub": "SRS, design, code"}],
              ["rev", 250, 40, 110, 120, "Reviewer", {"c": 3, "sh": "actor"}],
              ["sfix", 30, 194, 350, 56, "The defect itself is found", {"c": 1, "sh": "pill", "sub": "no program is run"}],
              ["app", 440, 60, 150, 76, "Running app", {"c": 2, "sh": "screen"}],
              ["te", 670, 40, 110, 120, "Tester", {"c": 3, "sh": "actor"}],
              ["dfix", 440, 194, 350, 56, "A failure is seen, then traced", {"c": 6, "sh": "pill", "sub": "the program must run"}]],
        "e": [["rev", "doc", {"t": "reads"}], ["rev", "sfix", {}], ["te", "app", {"t": "runs it"}], ["app", "dfix", {}]],
        "st": [[["g0", "doc"], "Static testing starts with something written: a requirement, a design or some code. Nothing needs to run."],
               [["rev", "rev>doc"], "A reviewer, or a tool, reads it carefully with a checklist."],
               [["sfix", "rev>sfix"], "The reviewer points straight at the defect: this sentence is missing a limit. The fix is a few words."],
               [["g1", "app", "te", "te>app"], "Dynamic testing needs a build. The tester runs the application with inputs."],
               [["dfix", "app>dfix"], "The tester sees a failure, such as a wrong message. Someone must then dig to find the defect behind it."]]},
    "verval": {"t": "Built right, and the right thing", "w": 720, "h": 250,
        "n": [["need", 20, 92, 150, 62, "User's real need", {"c": 0, "ic": "🙋"}],
              ["spec", 280, 18, 150, 64, "Specification", {"c": 5, "sh": "doc", "sub": "SRS, design"}],
              ["prod", 280, 160, 150, 64, "Product", {"c": 2, "sh": "screen"}]],
        "e": [["need", "spec", {"t": "written as"}], ["spec", "prod", {"t": "built from"}],
              ["prod", "spec", {"id": "ver", "t": "Verification: built right?", "via": [[560, 192], [560, 50]], "c": 2}],
              ["prod", "need", {"id": "val", "t": "Validation: right product?", "via": [[95, 192]], "c": 1}]],
        "st": [[["need"], "Everything starts with what the user really needs, for example paying a bill in under a minute."],
               [["spec", "need>spec"], "The need is written down as a specification. Mistakes can creep in right here."],
               [["prod", "spec>prod"], "The team builds the product from the specification."],
               [["ver"], "Verification compares the product, and every document on the way, with its specification. Reviews do most of this."],
               [["val"], "Validation goes back to the user. Does the product really solve their problem? UAT and beta testing answer this."]]},
    "revproc": {"t": "The five activities of a review", "w": 880, "h": 250,
        "n": [["plan", 10, 40, 150, 70, "1. Planning", {"c": 0, "sub": "scope, people, time"}],
              ["init", 185, 40, 150, 70, "2. Review initiation", {"c": 0, "sub": "share the material"}],
              ["ind", 360, 40, 150, 70, "3. Individual review", {"c": 3, "sub": "each person alone"}],
              ["comm", 535, 40, 150, 70, "4. Communication\nand analysis", {"c": 2}],
              ["fix", 710, 40, 160, 70, "5. Fixing and\nreporting", {"c": 1}],
              ["log", 360, 160, 150, 60, "Issue log", {"c": 5, "sh": "doc"}],
              ["upd", 710, 160, 160, 60, "Updated document", {"c": 1, "sh": "doc"}]],
        "e": [["plan", "init", {}], ["init", "ind", {}], ["ind", "comm", {}], ["comm", "fix", {}], ["ind", "log", {"t": "anomalies"}], ["log", "comm", {}], ["fix", "upd", {}]],
        "st": [[["plan"], "The review leader decides what is reviewed, why, by whom, how long it may take, and the exit criteria, such as no open major issues."],
               [["init", "plan>init"], "Everyone receives the work product, the checklist and the deadline. Newcomers are told how the review works."],
               [["ind", "init>ind"], "Each reviewer reads alone with a checklist and notes every anomaly: unclear, missing, wrong or inconsistent."],
               [["log", "ind>log"], "All anomalies are collected in one issue log, each with its place in the document and a suggested severity."],
               [["comm", "log>comm", "ind>comm"], "The group discusses each anomaly: a real defect, not a defect, or a question for someone else. It also decides whether the document passes."],
               [["fix", "comm>fix", "upd", "fix>upd"], "The author fixes the defects, the fixes are checked, and the results and numbers are reported."]]},
    "revroles": {"t": "Roles around one work product", "s": "Click a role to read what that person does.", "w": 760, "h": 300,
        "n": [["doc", 300, 115, 160, 70, "Work product", {"c": 5, "sh": "doc", "sub": "SRS v1.2"}],
              ["mgr", 20, 20, 170, 60, "Manager", {"c": 0, "ic": "💼", "i": "Decides what is reviewed and gives the review the time, money and people it needs."}],
              ["auth", 20, 120, 170, 60, "Author", {"c": 1, "ic": "✍️", "i": "Wrote the work product. Answers questions and fixes the defects that are found."}],
              ["lead", 20, 220, 170, 60, "Review leader", {"c": 2, "ic": "🧭", "i": "Takes overall responsibility, chooses the people, and organises when and where the review happens."}],
              ["mod", 570, 20, 170, 60, "Moderator", {"c": 3, "ic": "⚖️", "sub": "facilitator", "i": "Runs the meeting so it stays on time, calm and fair, and makes sure every voice is heard."}],
              ["scr", 570, 120, 170, 60, "Scribe", {"c": 4, "ic": "📝", "sub": "recorder", "i": "Collects anomalies from the reviewers and writes down every decision and new finding."}],
              ["rvw", 570, 220, 170, 60, "Reviewers", {"c": 7, "ic": "🕵️", "i": "Read carefully and report anomalies. Testers, developers, analysts, users and experts can all be reviewers."}]],
        "e": [["mgr", "doc", {"d": 1}], ["auth", "doc", {"d": 1}], ["lead", "doc", {"d": 1}], ["mod", "doc", {"d": 1}], ["scr", "doc", {"d": 1}], ["rvw", "doc", {"d": 1}]]},
    "revladder": {"t": "More formal, more cost, more defects per page", "w": 820, "h": 230,
        "n": [["inf", 10, 150, 180, 64, "Informal review", {"c": 1, "sub": "anyone, minutes"}],
              ["walk", 215, 110, 180, 64, "Walkthrough", {"c": 0, "sub": "led by the author"}],
              ["tech", 420, 70, 180, 64, "Technical review", {"c": 2, "sub": "led by a moderator"}],
              ["insp", 625, 30, 180, 64, "Inspection", {"c": 3, "sub": "trained leader, metrics"}]],
        "e": [["inf", "walk", {}], ["walk", "tech", {}], ["tech", "insp", {}]],
        "tx": [[110, 30, "Formality grows to the right", {"b": 1, "c": 2}]],
        "st": [[["inf"], "An informal review: a colleague looks at your test cases for ten minutes. No process, often no record."],
               [["walk", "inf>walk"], "A walkthrough: the author explains the document to a group, to teach and to agree, and the group asks questions."],
               [["tech", "walk>tech"], "A technical review: experts led by a moderator discuss a design and agree on the technical choices."],
               [["insp", "tech>insp"], "An inspection: trained people, checklists, entry and exit criteria, and numbers on every defect found. Used for safety critical documents."]]},
}

X = {"amb": {"search": {
    "t": "Spot the unclear words in this requirement",
    "req": "SRS 4.2 Product search. The search page must load [[fast|How fast? A tester needs a number, such as within 2 seconds for 95 out of 100 searches.]] and show [[all relevant|Relevant to whom? Matching the name only, or also the brand and the description?]] products. Results are [[sorted by price|Lowest first or highest first? And what happens when two items have the same price?]] and the user [[may|May means optional. Is the brand filter a must have or a nice to have?]] filter by brand. The page should be [[user friendly|Not measurable. Name the behaviour instead, such as keyboard support or a clear message for zero results.]] and work on [[all browsers|Which ones, and which versions? Nobody can test every browser ever made.]]. Errors are shown [[appropriately|Which errors, which messages, and where on the screen?]] [[etc.|Etcetera hides requirements. Every hidden item will be missed by someone.]]",
    "fix": "SRS 4.2 Product search. The first 20 results appear within 2 seconds for 95% of searches on a 4G connection. Results include every product whose name or brand contains the search word. Results are sorted by price, lowest first, and items with the same price are sorted by name. The user can filter by brand (must have). The page works on the latest two versions of Chrome, Safari, Edge and Firefox. When nothing matches, the page shows \"No products found for <word>\" and three suggestions."}}}
