from kit import *

FILE = 'agile-devops-testing.html'
SLUG, TOPIC, PREFIX = 'mt-agile-devops', 'agile-devops', 'mtq'
TITLE = 'Agile, DevOps and Shift Left Testing'
CRUMB = 'Agile, DevOps and shift left'
MODULE = '🧭 Modern testing practice'
EMOJI = '🔄'
DESCRIPTION = 'How testers work in modern teams: the whole team approach, user stories and acceptance criteria, Given When Then and BDD, Definition of Ready and Done, the agile testing quadrants, the test pyramid, CI and CD pipelines with quality gates, shift left and shift right, canary releases, feature flags and monitoring.'
LEAD = 'In older projects testers waited at the end of the line for a finished build. Today a tester joins the conversation on day one, helps write the story, checks every small change within minutes through a pipeline, and keeps watching after release. This page explains that way of working, step by step.'
PREV = ('test-metrics.html', 'metrics', '📊 Test Estimation, Metrics and Reporting')
NEXT = ('ai-in-testing.html', 'ai-testing', '🤖 AI in Testing and Testing AI')

TOP_SAY = say(
    'Welcome. Modern teams release small changes often, sometimes many times a day. This chapter shows where a tester fits in: shaping the story, agreeing on acceptance criteria, guarding the pipeline, and watching real users after release.',
    'स्वागत है। आधुनिक teams छोटे बदलाव अक्सर release करती हैं, कभी दिन में कई बार। यह chapter बताता है कि tester कहाँ fit होता है: story बनाने में, acceptance criteria तय करने में, pipeline की रखवाली में, और release के बाद असली users को देखने में।',
    'ಸ್ವಾಗತ. ಆಧುನಿಕ teams ಸಣ್ಣ ಬದಲಾವಣೆಗಳನ್ನು ಆಗಾಗ release ಮಾಡುತ್ತವೆ. Tester ಎಲ್ಲಿ ಬರುತ್ತಾರೆ: story, acceptance criteria, pipeline, ಮತ್ತು release ನಂತರ ನಿಜವಾದ users.',
    'ସ୍ୱାଗତ। ଆଧୁନିକ teams ଛୋଟ ପରିବର୍ତ୍ତନ ବାରମ୍ବାର release କରନ୍ତି। Tester କେଉଁଠି: story, acceptance criteria, pipeline, ଓ release ପରେ ପ୍ରକୃତ users।',
    'مرحبًا. تطلق الفرق الحديثة تغييرات صغيرة كثيرًا، أحيانًا عدة مرات في اليوم. يوضح هذا الفصل مكان المختبر: صياغة القصة، والاتفاق على معايير القبول، وحراسة خط النشر، ومراقبة المستخدمين بعد الإطلاق.',
    'Willkommen. Moderne Teams liefern kleine Änderungen oft, manchmal mehrmals täglich. Dieses Kapitel zeigt, wo Tester hingehören: beim Formen der Story, bei Akzeptanzkriterien, an der Pipeline und beim Beobachten echter Nutzer nach dem Release.')

SECTIONS = [
    sec('whole-team', '🤝', 'The whole team owns quality', f'''
<p>In Agile, quality is not one department's job. <b>The whole team</b>, developers, testers, the product owner and designers, is responsible for it. The tester is still the expert in finding risks, but now shares that skill with everyone, all the time.</p>
{table(['Old way (end of line testing)', 'Agile way (whole team)'],
       ['Testers get the build after weeks of coding', 'Testers join the story discussion before coding starts'],
       ['Big test phase at the end', 'Small checks every day, inside every sprint'],
       ['Bugs reported in a long list', 'Many problems fixed in a conversation the same day'],
       ['"Testing found 200 bugs"', '"The team prevented most bugs, and testing found the 20 that remained"'],
       ['Tester as gatekeeper', 'Tester as coach, explorer and risk advisor'])}
<p>A tester in an Agile team spends a typical sprint like this:</p>
{flow('sprintday')}
{tip('The Agile Manifesto (2001) values "individuals and interactions over processes and tools" and "responding to change over following a plan". For testers it means: talk early, adapt quickly, and keep the documentation that is truly useful.')}
''', say(
        'In Agile the whole team owns quality, not only the testers. Testers join the story discussion before coding starts, test small pieces every day inside the sprint, and fix many problems through conversation. The tester becomes a coach, explorer and risk advisor rather than a gatekeeper at the end.',
        'Agile में quality पूरी team की ज़िम्मेदारी है, सिर्फ़ testers की नहीं। Testers coding से पहले story की चर्चा में शामिल होते हैं, sprint में रोज़ छोटे हिस्से test करते हैं, और कई समस्याएँ बातचीत से ठीक होती हैं। Tester अंत का gatekeeper नहीं, coach, explorer और risk advisor बनता है।',
        'Agile ನಲ್ಲಿ quality ಇಡೀ team ನ ಜವಾಬ್ದಾರಿ. Testers coding ಮೊದಲೇ story ಚರ್ಚೆಯಲ್ಲಿ, sprint ನಲ್ಲಿ ಪ್ರತಿದಿನ ಸಣ್ಣ ಭಾಗಗಳ test. Tester coach, explorer, risk advisor.',
        'Agile ରେ quality ସମଗ୍ର team ର ଦାୟିତ୍ୱ। Testers coding ପୂର୍ବରୁ story ଆଲୋଚନାରେ, sprint ରେ ପ୍ରତିଦିନ ଛୋଟ test। Tester coach, explorer, risk advisor।',
        'في أجايل يتحمل الفريق كله مسؤولية الجودة، لا المختبرون وحدهم. ينضم المختبرون إلى نقاش القصة قبل البرمجة، ويختبرون أجزاء صغيرة كل يوم داخل السبرنت، وتحل مشكلات كثيرة بالحوار. يصبح المختبر مدربًا ومستكشفًا ومستشار مخاطر لا حارس بوابة في النهاية.',
        'In Agile trägt das ganze Team die Verantwortung für Qualität. Tester sind schon vor dem Programmieren bei der Story-Diskussion dabei, testen täglich kleine Stücke im Sprint und lösen viele Probleme im Gespräch. Der Tester wird Coach, Entdecker und Risikoberater statt Torwächter am Ende.')),

    sec('stories', '📝', 'User stories and acceptance criteria', f'''
<p>A <b>user story</b> is a small piece of value, written from the user's point of view:</p>
{rule('As a <b>bank customer</b>, I want to <b>set a daily transfer limit</b>, so that <b>a thief cannot empty my account in one day</b>.')}
<p>A story alone is too vague to test. <b>Acceptance criteria</b> turn it into clear, testable rules. A good story also passes the <b>INVEST</b> check:</p>
{table(['Letter', 'Means', 'Tester\'s question'],
       ['I', 'Independent', 'Can it be built and tested without waiting for another story?'],
       ['N', 'Negotiable', 'Are the details still open for discussion?'],
       ['V', 'Valuable', 'Does a user or the business get something real?'],
       ['E', 'Estimable', 'Do we understand it well enough to size it?'],
       ['S', 'Small', 'Does it fit in one sprint?'],
       ['T', 'Testable', 'Can we say exactly when it passes?'])}
<p>Many teams write acceptance criteria as <b>Given, When, Then</b> scenarios. This plain language style comes from BDD (behaviour driven development), and the format is called Gherkin. It is not code. Anyone in the business can read it:</p>
<div class="m2-gwt"><p><b>Scenario:</b> Transfer above the daily limit is blocked</p>
<p><b>Given</b> my daily limit is ₹20,000</p>
<p><b>And</b> I have already sent ₹15,000 today</p>
<p><b>When</b> I try to send ₹6,000</p>
<p><b>Then</b> the transfer is refused</p>
<p><b>And</b> I see "This transfer would go over your daily limit of ₹20,000"</p></div>
{flow('bddflow')}
{deep('ATDD, BDD and TDD in one table', table(['Practice', 'Who writes the examples', 'When', 'Main goal'],
       ['TDD (test driven development)', 'Developers', 'Before each small piece of code', 'Good code design, unit level checks'],
       ['ATDD (acceptance test driven development)', 'Business, developer and tester together', 'Before the story is built', 'Agree what done means for the user'],
       ['BDD (behaviour driven development)', 'The three amigos, in Given When Then', 'Before the story is built', 'Shared language, examples that can later be automated']) + '<p>A manual tester does not need to automate the scenarios. Writing sharp examples, especially the negative and boundary ones, is already the most valuable part.</p>')}
''', say(
        'A user story describes a small piece of value from the user\'s view: as a customer, I want something, so that I get a benefit. Acceptance criteria make it testable, often written as Given, When, Then scenarios in plain language. A good story is independent, negotiable, valuable, estimable, small and testable, which spells INVEST.',
        'User story user की नज़र से छोटा सा value बताती है: as a customer, I want कुछ, so that फ़ायदा। Acceptance criteria उसे testable बनाते हैं, अक्सर Given, When, Then की सरल भाषा में। अच्छी story independent, negotiable, valuable, estimable, small और testable होती है, यानी INVEST।',
        'User story user ದೃಷ್ಟಿಯ ಸಣ್ಣ value. Acceptance criteria ಅದನ್ನು testable ಮಾಡುತ್ತವೆ, Given, When, Then ಸರಳ ಭಾಷೆಯಲ್ಲಿ. ಒಳ್ಳೆಯ story INVEST: independent, negotiable, valuable, estimable, small, testable.',
        'User story user ଦୃଷ୍ଟିରୁ ଛୋଟ value। Acceptance criteria ତାକୁ testable କରେ, Given, When, Then ସରଳ ଭାଷାରେ। ଭଲ story INVEST: independent, negotiable, valuable, estimable, small, testable।',
        'قصة المستخدم تصف قيمة صغيرة من وجهة نظر المستخدم: بصفتي عميلًا أريد شيئًا كي أحصل على فائدة. معايير القبول تجعلها قابلة للاختبار، وتكتب غالبًا بصيغة بافتراض، عندما، إذن بلغة بسيطة. والقصة الجيدة مستقلة وقابلة للتفاوض وذات قيمة وقابلة للتقدير وصغيرة وقابلة للاختبار.',
        'Eine User Story beschreibt ein kleines Stück Nutzen aus Sicht des Nutzers. Akzeptanzkriterien machen sie testbar, oft als Gegeben, Wenn, Dann in einfacher Sprache. Eine gute Story ist unabhängig, verhandelbar, wertvoll, schätzbar, klein und testbar, kurz INVEST.')),

    sec('dor-dod', '✅', 'Definition of Ready and Definition of Done', f'''
<p>Two short checklists stop half baked work from entering or leaving a sprint.</p>
{grid(box('🚪 Definition of Ready (DoR)', 'A story may enter the sprint only when it is ready: acceptance criteria written, designs attached, dependencies known, test data identified, and the team has sized it.'),
      box('🏁 Definition of Done (DoD)', 'A story is done only when everything on the team\'s list is true: code reviewed, acceptance criteria pass, regression green, no open critical bugs, documentation and release notes updated.'))}
{table(['A sample Definition of Done', 'Who checks it'],
       ['Code reviewed by a second developer', 'Developers'],
       ['Unit tests written and passing in the pipeline', 'Developers'],
       ['Every acceptance criterion tested, including negative cases', 'Tester'],
       ['Exploratory session of at least 30 minutes on the story', 'Tester'],
       ['Automated regression suite green', 'Pipeline'],
       ['Accessibility quick check: keyboard, labels, contrast', 'Tester'],
       ['No open critical or major bugs for this story', 'Whole team'],
       ['Product owner has seen it and accepted it', 'Product owner'])}
{warn('"Done but not tested" does not exist. If testing is not finished, the story is not done, and it does not count in the sprint velocity.')}
''', say(
        'The Definition of Ready says when a story may enter a sprint: criteria written, designs and test data known, and sized. The Definition of Done says when it is truly finished: code reviewed, every acceptance criterion tested, regression green, no open critical bugs, and accepted by the product owner. Done but not tested does not exist.',
        'Definition of Ready बताती है कि story sprint में कब आ सकती है: criteria लिखे हों, designs और test data पता हों, और size तय हो। Definition of Done बताती है कि वह कब सच में पूरी है: code review, हर acceptance criterion test, regression green, कोई open critical bug नहीं, और product owner की स्वीकृति। Done but not tested जैसा कुछ नहीं होता।',
        'Definition of Ready story sprint ಗೆ ಯಾವಾಗ ಬರಬಹುದು ಎಂದು ಹೇಳುತ್ತದೆ. Definition of Done ನಿಜವಾಗಿ ಮುಗಿದಾಗ: code review, ಎಲ್ಲಾ criteria test, regression green, critical bugs ಇಲ್ಲ, product owner ಒಪ್ಪಿಗೆ.',
        'Definition of Ready story sprint କୁ କେବେ ଆସିପାରେ କହେ। Definition of Done ପ୍ରକୃତରେ ଶେଷ କେବେ: code review, ସବୁ criteria test, regression green, critical bugs ନାହିଁ, product owner ସ୍ୱୀକୃତି।',
        'تعريف الجاهزية يحدد متى تدخل القصة السبرنت: المعايير مكتوبة والتصاميم وبيانات الاختبار معروفة والحجم مقدر. وتعريف الإنجاز يحدد متى تنتهي فعلًا: مراجعة الشيفرة، واختبار كل معيار قبول، ونجاح الانحدار، وعدم وجود أخطاء حرجة مفتوحة، وقبول مالك المنتج.',
        'Die Definition of Ready sagt, wann eine Story in den Sprint darf: Kriterien geschrieben, Entwürfe und Testdaten bekannt, geschätzt. Die Definition of Done sagt, wann sie wirklich fertig ist: Code geprüft, jedes Kriterium getestet, Regression grün, keine offenen kritischen Fehler, vom Product Owner abgenommen.')),

    sec('quadrants', '🧭', 'The agile testing quadrants', f'''
<p>Brian Marick's <b>agile testing quadrants</b>, made popular by Lisa Crispin and Janet Gregory, sort every kind of test by two questions: does it face the <b>business</b> or the <b>technology</b>, and does it <b>guide the team</b> while building or <b>critique the product</b> after it is built?</p>
{flow('quadrants')}
{table(['Quadrant', 'Purpose', 'Examples', 'Usually'],
       ['Q1', 'Technology facing, guides the team', 'Unit tests, component tests', 'Automated'],
       ['Q2', 'Business facing, guides the team', 'Story examples, Given When Then, prototypes, functional tests', 'Manual and automated'],
       ['Q3', 'Business facing, critiques the product', 'Exploratory testing, usability testing, UAT, alpha and beta', 'Manual'],
       ['Q4', 'Technology facing, critiques the product', 'Performance, load, security, reliability testing', 'Tools'])}
{tip('Use the quadrants as a planning check. If a release plan has nothing in Q3 or Q4, ask who will explore the product and who will check performance and security.')}
''', say(
        'The agile testing quadrants sort tests by two questions: business or technology facing, and guiding the team or critiquing the product. Q1 holds unit tests. Q2 holds story examples and functional tests. Q3 holds exploratory, usability and acceptance testing. Q4 holds performance and security testing. A good plan covers all four.',
        'Agile testing quadrants tests को दो सवालों से बाँटते हैं: business या technology की ओर, और team को guide करना या product की आलोचना। Q1 में unit tests, Q2 में story examples और functional tests, Q3 में exploratory, usability और acceptance testing, Q4 में performance और security। अच्छी plan चारों cover करती है।',
        'Quadrants tests ಅನ್ನು business ಅಥವಾ technology, guide ಅಥವಾ critique ಎಂದು ವಿಂಗಡಿಸುತ್ತವೆ. Q1 unit, Q2 story examples, Q3 exploratory ಮತ್ತು usability, Q4 performance ಮತ್ತು security.',
        'Quadrants tests କୁ business କିମ୍ବା technology, guide କିମ୍ବା critique ଭାବେ ବାଣ୍ଟେ। Q1 unit, Q2 story examples, Q3 exploratory ଓ usability, Q4 performance ଓ security।',
        'تصنف أرباع الاختبار الرشيق الاختبارات بسؤالين: هل تواجه الأعمال أم التقنية، وهل توجه الفريق أم تنتقد المنتج. الربع الأول اختبارات الوحدات، والثاني أمثلة القصص والاختبارات الوظيفية، والثالث الاستكشافي وقابلية الاستخدام والقبول، والرابع الأداء والأمان.',
        'Die agilen Testquadranten ordnen Tests nach zwei Fragen: geschäfts- oder technikorientiert, und leiten sie das Team oder kritisieren sie das Produkt. Q1 Unit-Tests, Q2 Story-Beispiele und Funktionstests, Q3 exploratives Testen, Usability und Abnahme, Q4 Performance und Sicherheit.')),

    sec('pyramid', '🔺', 'The test pyramid', f'''
<p>Mike Cohn's <b>test pyramid</b> says how many checks to put at each level. Many small fast checks at the bottom, fewer slow checks through the screen at the top. The opposite shape, mostly slow screen tests and a few unit tests, is nicknamed the <b>ice cream cone</b>, and teams with it wait hours for results that often fail for no real reason.</p>
{viz('pyramid')}
{table(['Layer', 'Speed per check', 'Breaks when', 'Finds'],
       ['Unit', 'Milliseconds', 'The logic changes', 'Wrong calculations and conditions'],
       ['API or service', 'About a second', 'The contract between parts changes', 'Wrong data, wrong rules between services'],
       ['UI and end to end', 'Tens of seconds', 'Any button, text or layout moves', 'Broken user journeys across the whole system'],
       ['Manual exploratory (on top)', 'Minutes to hours', 'Never, a person adapts', 'Surprises nobody thought to check'])}
{tip('As a manual tester, use the pyramid when you suggest automation. "Please check the discount rule at the API level" gives a faster and steadier check than "please automate this through the browser".')}
''', say(
        'The test pyramid puts many fast unit checks at the bottom, fewer API checks in the middle and only a few slow user interface checks at the top, with manual exploratory testing above them. The upside down shape, called the ice cream cone, makes runs slow and full of false failures. Try both shapes in the lab.',
        'Test pyramid में नीचे बहुत से तेज़ unit checks, बीच में कम API checks और ऊपर कुछ ही धीमे UI checks होते हैं, उनके ऊपर manual exploratory testing। उल्टा आकार, ice cream cone, runs को धीमा और झूठी failures से भरा बनाता है। Lab में दोनों आकार आज़माइए।',
        'Test pyramid ಕೆಳಗೆ ಅನೇಕ ವೇಗದ unit checks, ಮಧ್ಯೆ API, ಮೇಲೆ ಕೆಲವೇ UI checks. ತಲೆಕೆಳಗಾದ ice cream cone ನಿಧಾನ ಮತ್ತು ಸುಳ್ಳು failures.',
        'Test pyramid ତଳେ ଅନେକ ଦ୍ରୁତ unit checks, ମଝିରେ API, ଉପରେ କେତୋଟି UI checks। ଓଲଟା ice cream cone ଧୀର ଓ ମିଛ failures।',
        'يضع هرم الاختبار فحوص وحدات سريعة كثيرة في القاعدة، وفحوص واجهات برمجية أقل في الوسط، وقليلًا من فحوص الواجهة البطيئة في القمة، وفوقها الاختبار الاستكشافي اليدوي. والشكل المقلوب، مخروط المثلجات، يجعل التشغيل بطيئًا ومليئًا بالإخفاقات الكاذبة.',
        'Die Testpyramide hat unten viele schnelle Unit-Checks, in der Mitte weniger API-Checks und oben nur wenige langsame UI-Checks, darüber exploratives Testen. Die umgedrehte Form, die Eistüte, macht Läufe langsam und voller falscher Fehlschläge.')),

    sec('cicd', '🚦', 'CI, CD and quality gates', f'''
<p><b>Continuous integration (CI)</b> means every change a developer pushes is built and checked automatically, many times a day. <b>Continuous delivery (CD)</b> means the product is always in a state that could be released with one click. <b>Continuous deployment</b> goes one step further: every change that passes the pipeline goes live by itself.</p>
{flow('pipeline')}
{table(['Pipeline stage', 'Typical checks', 'Where a manual tester helps'],
       ['Commit', 'Build, unit tests, static analysis, security scan', 'Reads the scan report for risky areas'],
       ['Test environment', 'API tests, UI smoke tests, contract tests', 'Explores the new story on this build within minutes'],
       ['Staging', 'Full regression, performance smoke, accessibility scan', 'UAT support, exploratory session on risky changes'],
       ['Production', 'Health checks, canary analysis, monitoring', 'Watches dashboards and user feedback, tests in production safely'])}
<p>A <b>quality gate</b> is a rule that stops the pipeline: "no new critical issues from the security scan", "all smoke tests green", "code coverage did not drop". It is the automatic version of the exit criteria you met in the test plan chapter.</p>
{tip('DevOps is the culture behind this: developers and operations people share responsibility for running the product. The DORA research measures DevOps teams with four numbers: how often they deploy, how long a change takes to reach users, how often a change fails, and how fast they recover. Testers influence all four.')}
''', say(
        'Continuous integration builds and checks every change automatically. Continuous delivery keeps the product always releasable, and continuous deployment releases every passing change by itself. Quality gates stop the pipeline when a rule fails, such as a critical security issue. Manual testers explore each new build within minutes and watch production after release.',
        'Continuous integration हर बदलाव को अपने आप build और check करता है। Continuous delivery product को हमेशा release योग्य रखता है, और continuous deployment हर pass बदलाव अपने आप release करता है। Quality gates rule fail होने पर pipeline रोकते हैं। Manual testers हर नया build मिनटों में explore करते हैं और release के बाद production देखते हैं।',
        'CI ಪ್ರತಿ ಬದಲಾವಣೆಯನ್ನು ಸ್ವಯಂ build ಮತ್ತು check ಮಾಡುತ್ತದೆ. CD product ಯಾವಾಗಲೂ release ಯೋಗ್ಯ. Quality gates rule fail ಆದರೆ pipeline ನಿಲ್ಲಿಸುತ್ತವೆ. Testers ಹೊಸ build ನಿಮಿಷಗಳಲ್ಲಿ explore ಮಾಡುತ್ತಾರೆ.',
        'CI ପ୍ରତି ପରିବର୍ତ୍ତନକୁ ସ୍ୱୟଂ build ଓ check କରେ। CD product ସବୁବେଳେ release ଯୋଗ୍ୟ। Quality gates rule fail ହେଲେ pipeline ରୋକେ। Testers ନୂଆ build ମିନିଟରେ explore କରନ୍ତି।',
        'التكامل المستمر يبني كل تغيير ويفحصه تلقائيًا. والتسليم المستمر يبقي المنتج جاهزًا للإطلاق دائمًا، والنشر المستمر يطلق كل تغيير ناجح بنفسه. بوابات الجودة توقف خط النشر عند فشل قاعدة، مثل مشكلة أمنية حرجة. ويستكشف المختبرون كل بناء جديد خلال دقائق.',
        'Continuous Integration baut und prüft jede Änderung automatisch. Continuous Delivery hält das Produkt jederzeit lieferbar, Continuous Deployment liefert jede bestandene Änderung selbst aus. Quality Gates stoppen die Pipeline, wenn eine Regel verletzt ist. Tester erkunden jeden neuen Build innerhalb von Minuten.')),

    sec('shift', '↔️', 'Shift left and shift right', f'''
<p><b>Shift left</b> means moving testing earlier: reviewing stories, writing examples before code, running checks on every commit. <b>Shift right</b> means continuing to learn after release, from real users in production. Modern teams do both.</p>
{grid(box('⬅️ Shift left', 'Three amigos, requirement reviews, acceptance criteria before coding, static analysis, unit and API tests in the pipeline, testers pairing with developers.'),
      box('➡️ Shift right', 'Canary releases, feature flags, A/B tests, monitoring and alerts, real user metrics, crash reports, reading app store reviews and support tickets.'))}
{table(['Technique', 'How it works', 'What the tester checks'],
       ['Feature flag', 'The new code is shipped switched off, then turned on for chosen users', 'Both states work, and switching does not break sessions'],
       ['Canary release', 'The new version serves 1%, then 5%, 25% and 100% of users while errors are watched', 'Error and speed metrics at each stage, and that rollback really works'],
       ['Blue green deployment', 'Two identical production environments, traffic switches from one to the other', 'The switch and the switch back'],
       ['A/B testing', 'Two versions shown to two groups to see which works better', 'Each user sees one version consistently, and the data is recorded right'],
       ['Synthetic monitoring', 'A robot runs a key journey, such as login and checkout, every few minutes in production', 'That the journey covers what matters and alerts reach a person'],
       ['Chaos engineering', 'Faults are injected on purpose, such as killing a server, to prove the system recovers', 'That recovery happens and users see a calm message'])}
{viz('canary')}
''', say(
        'Shift left moves testing earlier, with reviews, examples before code and checks on every commit. Shift right keeps learning after release from real users, with feature flags, canary releases, A/B tests, monitoring and chaos engineering. In a canary release the new version first serves a small share of users, and it is rolled back automatically if errors cross a limit.',
        'Shift left testing को पहले लाता है: reviews, code से पहले examples और हर commit पर checks। Shift right release के बाद असली users से सीखता रहता है: feature flags, canary releases, A/B tests, monitoring और chaos engineering। Canary release में नया version पहले थोड़े users को मिलता है, और errors सीमा पार करें तो अपने आप rollback होता है।',
        'Shift left testing ಮೊದಲೇ: reviews, examples, commit checks. Shift right release ನಂತರ users ಇಂದ ಕಲಿಕೆ: feature flags, canary, A/B, monitoring. Canary ನಲ್ಲಿ ಹೊಸ version ಸ್ವಲ್ಪ users ಗೆ, errors ಮಿತಿ ದಾಟಿದರೆ rollback.',
        'Shift left testing ଆଗରୁ: reviews, examples, commit checks। Shift right release ପରେ users ରୁ ଶିଖିବା: feature flags, canary, A/B, monitoring। Canary ରେ ନୂଆ version କିଛି users କୁ, errors ସୀମା ଟପିଲେ rollback।',
        'التحويل لليسار ينقل الاختبار إلى وقت أبكر عبر المراجعات والأمثلة قبل الشيفرة والفحص مع كل تعديل. والتحويل لليمين يواصل التعلم بعد الإطلاق من المستخدمين الحقيقيين عبر مفاتيح الميزات والإطلاق التدريجي واختبارات أ/ب والمراقبة. في الإطلاق التدريجي يخدم الإصدار الجديد نسبة صغيرة أولًا ويتراجع تلقائيًا إذا تجاوزت الأخطاء الحد.',
        'Shift Left verlegt Testen nach vorn: Reviews, Beispiele vor dem Code, Prüfungen bei jedem Commit. Shift Right lernt nach dem Release von echten Nutzern: Feature Flags, Canary Releases, A/B-Tests, Monitoring und Chaos Engineering. Beim Canary Release bedient die neue Version zuerst wenige Nutzer und wird automatisch zurückgerollt, wenn Fehler eine Grenze überschreiten.')),

    sec('sbtm', '🧭', 'Exploratory testing that the team can trust', f'''
<p>In fast moving teams, scripted test cases cannot keep up with every change. <b>Exploratory testing</b> fills the gap: the tester learns, designs and runs tests at the same time. To make it accountable, many teams use <b>session based test management (SBTM)</b>, created by Jonathan and James Bach.</p>
{table(['Part of a session', 'What it is', 'Example'],
       ['Charter', 'A one line mission', 'Explore the daily transfer limit with edge amounts and two devices to discover limit bypasses'],
       ['Time box', 'Usually 60 to 120 minutes, without interruptions', '90 minutes'],
       ['Notes', 'What was tried, what was seen, ideas for later', 'Tried ₹19,999 + ₹1 on two phones at the same second'],
       ['Bugs and issues', 'Problems found, and questions that block testing', 'Limit can be bypassed with two parallel transfers'],
       ['Debrief', 'A short talk with the lead about what was covered and what is left', '"Limits look solid for single device use. Parallel use needs a fix."'])}
{rule('A charter follows a simple pattern: <b>Explore</b> (a target) <b>with</b> (resources, data, tools) <b>to discover</b> (the kind of information you want).')}
''', say(
        'Exploratory testing means learning, designing and running tests at the same time. Session based test management makes it accountable. Each session has a charter, a time box of sixty to one hundred and twenty minutes, notes, bugs and a short debrief. A charter follows the pattern: explore a target, with some resources, to discover some information.',
        'Exploratory testing में सीखना, tests design करना और चलाना एक साथ होता है। Session based test management इसे जवाबदेह बनाता है। हर session में charter, साठ से एक सौ बीस मिनट का time box, notes, bugs और छोटा debrief होता है। Charter का pattern: explore लक्ष्य, with संसाधन, to discover जानकारी।',
        'Exploratory testing ಕಲಿಕೆ, design ಮತ್ತು run ಒಟ್ಟಿಗೆ. SBTM ನಲ್ಲಿ charter, time box, notes, bugs, debrief. Charter: explore target, with resources, to discover information.',
        'Exploratory testing ଶିଖିବା, design ଓ run ଏକାସାଙ୍ଗରେ। SBTM ରେ charter, time box, notes, bugs, debrief। Charter: explore target, with resources, to discover information।',
        'الاختبار الاستكشافي يعني التعلم والتصميم والتنفيذ في وقت واحد. وإدارة الاختبار القائمة على الجلسات تجعله قابلًا للمساءلة: لكل جلسة ميثاق ومدة محددة من ستين إلى مئة وعشرين دقيقة وملاحظات وأخطاء ومراجعة قصيرة. صيغة الميثاق: استكشف هدفًا، بموارد معينة، لتكتشف معلومة ما.',
        'Exploratives Testen heißt lernen, entwerfen und ausführen zugleich. Sessionbasiertes Testmanagement macht es nachvollziehbar: Jede Session hat eine Charter, ein Zeitfenster von sechzig bis hundertzwanzig Minuten, Notizen, Fehler und ein kurzes Debriefing. Muster der Charter: Erkunde ein Ziel, mit Ressourcen, um Informationen zu entdecken.')),
]

INFO = {"title": "Testing that never waits at the end", "panels": [
    {"s": [["e", "🤝"], ["t", "PO · dev · tester", {"b": 1}]], "h": "Before code", "t": "Three amigos agree on examples.", "more": "Given, When, Then in plain words."},
    {"s": [["e", "🚦"], ["t", "build · test · gate", {"b": 1}]], "h": "Every commit", "t": "The pipeline checks each change.", "more": "A quality gate stops bad builds."},
    {"s": [["e", "🐤"], ["t", "1% → 5% → 25%", {"b": 1}]], "h": "Careful release", "t": "A canary meets a few users first.", "more": "Errors over the limit mean rollback."},
    {"s": [["e", "📈"], ["t", "errors · speed · feedback", {"b": 1, "size": 12}]], "h": "After release", "t": "The team keeps watching real users.", "more": "Shift left and shift right together."}],
    "remember": "Modern testing starts before the code and continues after the release. The whole team owns quality, and the tester leads on risk."}

REAL = [
    ["🍽️", "A restaurant kitchen", "The chef tastes the sauce while cooking, not only when the plate reaches the customer. Checking small steps early is shift left."],
    ["🐤", "A canary in a coal mine", "Miners once carried a canary because it reacted to gas before people did. A canary release lets a few users meet a problem first, so most never do."],
    ["🚗", "A car's dashboard", "Warning lights keep checking the engine while you drive. Production monitoring is the dashboard of a live product."]]

QUIZ = [
    Qz('e', 'Who owns quality in an Agile team?', ['Only testers', 'Only the product owner', 'The whole team', 'The customer'], 2, 'Not one department.', 'Agile teams share responsibility for quality. Testers lead on risk and testing skills.'),
    Qz('e', 'What does the T in INVEST stand for?', ['Timely', 'Testable', 'Technical', 'Tracked'], 1, 'A tester cares about this letter most.', 'A story must be testable: it should be clear when it passes.'),
    Qz('e', 'What is a feature flag?', ['A bug label', 'A switch that turns new code on or off without a new release', 'A test case id', 'A type of quality gate'], 1, 'Ship it switched off.', 'Feature flags separate deploying code from releasing a feature to users.'),
    Qz('m', 'Exploratory testing and usability testing sit in which agile testing quadrant?', ['Q1', 'Q2', 'Q3', 'Q4'], 2, 'Business facing, critiquing the product.', 'Q3 holds business facing tests that critique the product: exploratory, usability, UAT, alpha and beta.'),
    Qz('m', 'Which shape of test suite is called the ice cream cone?', ['Mostly unit tests', 'Mostly UI end to end tests and few unit tests', 'Equal numbers on every layer', 'Only manual tests'], 1, 'Wide at the top.', 'The cone is top heavy: many slow, fragile UI tests and few fast unit tests.'),
    Qz('m', 'A story is coded and reviewed but not tested. Is it done?', ['Yes, testing is separate', 'No, testing is part of the Definition of Done', 'Yes, if the developer says so', 'Only in the last sprint'], 1, 'Done but not tested does not exist.', 'A story counts as done only when every item of the Definition of Done is met, including testing.'),
    Qz('m', 'In a canary release, what happens if the error rate of the new version crosses the agreed limit?', ['The release continues to 100%', 'Traffic is moved back to the old version', 'The users are told to restart', 'Nothing'], 1, 'The canary warns early.', 'Automatic rollback limits the damage to the small share of users who were on the new version.'),
    Qz('h', 'Which practice is an example of shift right?', ['Requirement review', 'Unit tests on every commit', 'Monitoring error rates of real users after release', 'Three amigos meeting'], 2, 'Right means after release.', 'Shift right learns from production: monitoring, canary analysis, A/B tests and feedback.'),
    Qz('h', 'What is a quality gate in a CI pipeline?', ['A meeting with the manager', 'An automatic rule that stops the pipeline when it fails', 'A physical door to the server room', 'A manual sign off sheet'], 1, 'The automatic version of exit criteria.', 'Examples: no new critical security issues, smoke tests green, coverage not reduced.'),
    Qz('h', 'Which charter follows the SBTM pattern best?', ['Test the transfer page', 'Explore the transfer limit with edge amounts and two phones to discover limit bypasses', 'Run all 400 regression cases', 'Check everything carefully'], 1, 'Explore, with, to discover.', 'A charter names a target, the resources and the information the session should discover.'),
    Qz('x', 'Which pair correctly matches TDD and BDD?', ['TDD: business examples in Given When Then, BDD: unit tests first', 'TDD: developers write a unit test before the code, BDD: the team writes behaviour examples in plain language', 'They are the same', 'Both are only for testers'], 1, 'Driven by tests, driven by behaviour.', 'TDD is a developer practice at unit level. BDD uses shared Given When Then examples of behaviour.'),
    Qz('x', 'A Given When Then scenario says "Then the transfer is refused". What makes it a strong acceptance criterion?', ['It mentions a button colour', 'It gives a clear observable result that passes or fails', 'It is long', 'It names the developer'], 1, 'Testable means observable.', 'A good Then step describes an outcome anyone can observe and check, such as a refusal and a specific message.'),
]

CALC = [
    Calc('e', 'A team of 6 delivers 42 story points over 3 sprints. What is the average velocity per sprint?', '14', '42 / 3', 'Total points ÷ sprints.', [eq(f'{fr("42", "3")} = 14') + ' points per sprint']),
    Calc('e', 'A canary stage sends 5% of 200,000 users to the new version. How many users is that?', '10000', '200000 * 5 / 100', 'Users × percent ÷ 100.', [eq('200,000 × 5 ÷ 100 = 10,000')]),
    Calc('m', 'In that 5% stage, 0.4% of requests fail. If each of the 10,000 users makes one request, how many see an error?', '40', '10000 * 0.4 / 100', 'Users × error rate.', [eq('10,000 × 0.4 ÷ 100 = 40')]),
    Calc('m', 'A suite has 900 unit tests at 0.02 s, 120 API tests at 1.5 s and 20 UI tests at 45 s. How many minutes does a full run take?', '18.3', '(900 * 0.02 + 120 * 1.5 + 20 * 45) / 60', 'Add the seconds, then divide by 60.', [eq('900 × 0.02 + 120 × 1.5 + 20 × 45 = 18 + 180 + 900 = 1,098 s'), eq(f'{fr("1,098", "60")} ≈ 18.3') + ' minutes']),
    Calc('h', 'A team deploys 3 times a day for 20 working days, and 6 deployments cause a problem in production. What is the change failure rate in percent?', '10', '6 * 100 / (3 * 20)', 'Failed changes × 100 ÷ all changes.', [eq('3 × 20 = 60') + ' deployments', eq(f'{fr("6 × 100", "60")} = 10%')], unit='%'),
    Calc('x', 'A flaky UI test fails at random 3% of the time. A pipeline runs 20 such independent tests. What is the chance, in percent, that at least one fails at random? Round to one decimal.', '45.6', '(1 - 0.97 ** 20) * 100', '1 − (chance all pass).', [eq('0.97<sup>20</sup> ≈ 0.544'), eq('1 − 0.544 = 0.456 ≈ 45.6%'), 'Almost every second run is red for no real reason. That is why flaky tests destroy trust.']),
]

DG = {
    "sprintday": {"t": "A tester's sprint", "w": 880, "h": 230,
        "n": [["plan", 10, 70, 150, 70, "Sprint planning", {"c": 0, "ic": "🗓️", "sub": "risks, test effort"}],
              ["amigo", 185, 70, 150, 70, "Three amigos", {"c": 3, "ic": "🤝", "sub": "examples per story"}],
              ["pair", 360, 70, 150, 70, "Test while built", {"c": 2, "ic": "🧪", "sub": "each small build"}],
              ["expl", 535, 70, 150, 70, "Explore and regress", {"c": 7, "ic": "🧭", "sub": "sessions, suite"}],
              ["demo", 710, 70, 160, 70, "Review and retro", {"c": 1, "ic": "🎉", "sub": "demo, improve"}],
              ["daily", 285, 170, 310, 44, "Daily stand up: blockers and test progress", {"c": 5, "sh": "pill"}]],
        "e": [["plan", "amigo", {}], ["amigo", "pair", {}], ["pair", "expl", {}], ["expl", "demo", {}], ["daily", "pair", {"d": 1}]],
        "st": [[["plan"], "In sprint planning the tester points out risky stories and makes sure testing time is part of every estimate."],
               [["amigo", "plan>amigo"], "Before coding, the product owner, a developer and the tester agree on examples and acceptance criteria for each story."],
               [["pair", "amigo>pair", "daily", "daily>pair"], "While the story is built, the tester checks each small build, often the same day. The daily stand up shares blockers and progress."],
               [["expl", "pair>expl"], "When a story is complete, the tester runs exploratory sessions and makes sure the regression suite is green."],
               [["demo", "expl>demo"], "In the sprint review the team shows working software. In the retrospective it improves how it works, including how it tests."]]},
    "bddflow": {"t": "From a conversation to a living check", "w": 860, "h": 210,
        "n": [["talk", 10, 60, 160, 76, "Conversation", {"c": 3, "ic": "💬", "sub": "three amigos"}],
              ["ex", 230, 60, 170, 76, "Examples", {"c": 5, "sh": "doc", "sub": "Given When Then"}],
              ["build", 460, 60, 160, 76, "Build the story", {"c": 2, "ic": "🛠️"}],
              ["check", 680, 60, 170, 76, "Examples pass", {"c": 1, "ic": "✅", "sub": "by hand or automated"}]],
        "e": [["talk", "ex", {}], ["ex", "build", {"t": "guides"}], ["build", "check", {}],
              ["check", "ex", {"id": "loop", "d": 1, "via": [[765, 180], [315, 180]], "t": "examples stay as documentation", "tx": 540, "ty": 180}]],
        "st": [[["talk"], "It starts with a conversation. The business explains the rule, the developer asks how, the tester asks what if."],
               [["ex", "talk>ex"], "The answers are captured as concrete examples in Given, When, Then form, including the unhappy paths."],
               [["build", "ex>build"], "The developer builds the story with the examples in front of them, so fewer misunderstandings reach testing."],
               [["check", "build>check"], "The examples are checked, by hand or by automation. A passing example means the rule really works."],
               [["loop"], "The examples stay as living documentation. When the rule changes, the example changes first."]]},
    "quadrants": {"t": "The agile testing quadrants", "w": 760, "h": 340,
        "n": [["q2", 120, 50, 250, 120, "Q2 · Functional examples", {"c": 2, "sub": "story tests, prototypes"}],
              ["q3", 390, 50, 250, 120, "Q3 · Explore and accept", {"c": 3, "sub": "exploratory, usability, UAT"}],
              ["q1", 120, 190, 250, 120, "Q1 · Unit and component", {"c": 1, "sub": "automated, developer owned"}],
              ["q4", 390, 190, 250, 120, "Q4 · Performance, security", {"c": 6, "sub": "load, security, reliability"}]],
        "tx": [[380, 22, "Business facing", {"b": 1, "c": 2}], [380, 330, "Technology facing", {"b": 1, "c": 2}], [60, 180, "Guide\nthe team", {"b": 1, "c": 1}], [700, 180, "Critique\nthe product", {"b": 1, "c": 3}]],
        "st": [[["q1"], "Q1: technology facing tests that guide the team. Unit and component tests, written by developers and run on every commit."],
               [["q2"], "Q2: business facing tests that guide the team. Story examples, acceptance criteria and functional checks, manual or automated."],
               [["q3"], "Q3: business facing tests that critique the product. Exploratory testing, usability, UAT, alpha and beta. Mostly manual and human."],
               [["q4"], "Q4: technology facing tests that critique the product. Performance, load, security and reliability, usually with special tools."]]},
    "pipeline": {"t": "A CI and CD pipeline with quality gates", "w": 880, "h": 250,
        "n": [["dev", 10, 80, 120, 70, "Commit", {"c": 3, "ic": "👩‍💻", "sub": "a small change"}],
              ["ci", 165, 80, 140, 70, "Build and unit", {"c": 2, "ic": "⚙️", "sub": "plus static scan"}],
              ["g1", 335, 90, 50, 50, "", {"c": 5, "sh": "diamond"}],
              ["qa", 415, 80, 140, 70, "Test env", {"c": 0, "ic": "🧪", "sub": "API, smoke, explore"}],
              ["g2", 585, 90, 50, 50, "", {"c": 5, "sh": "diamond"}],
              ["stg", 665, 80, 100, 70, "Staging", {"c": 7, "sub": "regression"}],
              ["prod", 790, 80, 80, 70, "Live", {"c": 1, "ic": "🌍"}],
              ["stop", 335, 190, 300, 44, "Gate fails: stop, report, fix", {"c": 6, "sh": "pill"}]],
        "e": [["dev", "ci", {}], ["ci", "g1", {}], ["g1", "qa", {}], ["qa", "g2", {}], ["g2", "stg", {}], ["stg", "prod", {}], ["g1", "stop", {"d": 1, "c": 6}], ["g2", "stop", {"d": 1, "c": 6}]],
        "tx": [[360, 70, "gate 1", {"s": 11}], [610, 70, "gate 2", {"s": 11}]],
        "st": [[["dev"], "A developer pushes a small change. Small changes are easy to test and easy to undo."],
               [["ci", "dev>ci"], "The pipeline builds it, runs the unit tests and a static and security scan within minutes."],
               [["g1", "ci>g1", "stop", "g1>stop"], "Gate 1: if any check fails, the pipeline stops and the developer is told at once. No tester time is wasted on a broken build."],
               [["qa", "g1>qa"], "The build is deployed to a test environment. API and smoke checks run, and the tester explores the new story."],
               [["g2", "qa>g2", "g2>stop"], "Gate 2: the smoke suite and agreed checks must be green before the build moves on."],
               [["stg", "g2>stg"], "In staging the full regression and other slower checks run on a production like copy."],
               [["prod", "stg>prod"], "The change goes live, often as a canary first, and monitoring keeps watching it."]]},
}

X = {}
