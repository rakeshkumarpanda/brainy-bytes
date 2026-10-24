from kit import *

FILE = 'test-metrics.html'
SLUG, TOPIC, PREFIX = 'mt-metrics', 'metrics', 'mtm'
TITLE = 'Test Estimation, Metrics and Reporting'
CRUMB = 'Estimation, metrics and reporting'
MODULE = '🗺️ Planning and closure'
EMOJI = '📊'
DESCRIPTION = 'How long testing will take and how to show where it stands: estimation techniques (work breakdown, three point, planning poker, Wideband Delphi), test progress metrics, defect metrics such as DRE, leakage and density, coverage, test status and completion reports, test closure, and the traps of measuring people.'
LEAD = '"How long will testing take?" and "Are we ready to release?" are the two questions every tester hears. Both need numbers, explained in plain words. This page shows how to estimate, which numbers to collect, how to read them, and how to report them honestly.'
PREV = ('test-plan.html', 'test-plan', '🗓️ The Test Plan')
NEXT = ('agile-devops-testing.html', 'agile-devops', '🔄 Agile, DevOps and Shift Left Testing')

TOP_SAY = say(
    'Welcome. Managers ask two questions again and again: how long will testing take, and are we ready to release? This chapter teaches you to estimate, to measure progress and defects, and to report the truth in a way anyone can understand.',
    'स्वागत है। Managers बार बार दो सवाल पूछते हैं: testing में कितना समय लगेगा, और क्या हम release के लिए तैयार हैं? यह chapter estimate करना, progress और defects मापना, और सच को सरल तरीके से report करना सिखाता है।',
    'ಸ್ವಾಗತ. Managers ಎರಡು ಪ್ರಶ್ನೆ ಕೇಳುತ್ತಾರೆ: testing ಎಷ್ಟು ಸಮಯ, release ಗೆ ಸಿದ್ಧವೇ? ಈ chapter estimate, progress ಮತ್ತು defects ಅಳತೆ, ಸತ್ಯವಾದ report ಕಲಿಸುತ್ತದೆ.',
    'ସ୍ୱାଗତ। Managers ଦୁଇଟି ପ୍ରଶ୍ନ ପଚାରନ୍ତି: testing କେତେ ସମୟ, release ପାଇଁ ପ୍ରସ୍ତୁତ କି? ଏହି chapter estimate, progress ଓ defects ମାପ, ସତ୍ୟ report ଶିଖାଏ।',
    'مرحبًا. يسأل المديرون سؤالين مرارًا: كم سيستغرق الاختبار، وهل نحن جاهزون للإطلاق؟ يعلمك هذا الفصل التقدير وقياس التقدم والعيوب وكتابة تقرير صادق يفهمه الجميع.',
    'Willkommen. Manager fragen immer wieder zwei Dinge: Wie lange dauert das Testen, und sind wir bereit für das Release? Dieses Kapitel lehrt Schätzen, das Messen von Fortschritt und Fehlern und ehrliches, verständliches Berichten.')

SECTIONS = [
    sec('why-measure', '🎯', 'Why testers measure', f'''
<p>A number is useful only if it helps someone decide something. "We ran 4,000 test cases" sounds busy, but it does not say whether the product is safe to release. "All 38 high risk requirements pass, and 2 major bugs are open in payments" does.</p>
<p>A simple way to pick good metrics is <b>Goal, Question, Metric (GQM)</b>, from Victor Basili:</p>
{flow('gqm')}
{table(['Kind of metric', 'Answers', 'Examples'],
       ['Progress', 'How far are we?', 'Test cases executed, passed, blocked, burndown'],
       ['Product quality', 'How good is the product?', 'Open defects by severity, defect density, failed requirements'],
       ['Process quality', 'How good is our testing?', 'Defect removal efficiency, leakage, rejection ratio'],
       ['Coverage', 'What have we checked?', 'Requirements covered, risks covered, code coverage'],
       ['Cost', 'What did it take?', 'Effort in person days, cost of fixing defects by phase'])}
{warn('A metric used to judge people stops measuring the work. If testers are rewarded per bug, the team gets many tiny duplicate bugs. If developers are punished per bug, bugs get argued away. This is Goodhart\'s law: when a measure becomes a target, it stops being a good measure.')}
''', say(
        'A number is useful only if it helps someone decide something. Goal, question, metric is a simple way to choose: start with a goal, ask the questions that show progress towards it, and only then pick the numbers. Testers track progress, product quality, process quality, coverage and cost. Never use metrics to judge individual people.',
        'कोई number तभी उपयोगी है जब वह किसी फ़ैसले में मदद करे। Goal, question, metric चुनने का आसान तरीका है: goal से शुरू करें, उसकी ओर progress दिखाने वाले सवाल पूछें, फिर numbers चुनें। Testers progress, product quality, process quality, coverage और cost track करते हैं। Metrics से कभी लोगों को judge न करें।',
        'Number ನಿರ್ಧಾರಕ್ಕೆ ಸಹಾಯವಾದರೆ ಮಾತ್ರ ಉಪಯೋಗ. Goal, question, metric: goal, ಪ್ರಶ್ನೆಗಳು, ನಂತರ numbers. Progress, product quality, process quality, coverage, cost. ಜನರನ್ನು metrics ಇಂದ judge ಮಾಡಬೇಡಿ.',
        'Number ନିଷ୍ପତ୍ତିରେ ସାହାଯ୍ୟ କଲେ ହିଁ ଉପଯୋଗୀ। Goal, question, metric: goal, ପ୍ରଶ୍ନ, ତାପରେ numbers। Progress, product quality, process quality, coverage, cost। ଲୋକଙ୍କୁ metrics ରେ judge କରନ୍ତୁ ନାହିଁ।',
        'الرقم مفيد فقط إذا ساعد أحدًا على اتخاذ قرار. طريقة الهدف والسؤال والمقياس بسيطة: ابدأ بهدف، ثم اسأل ما يوضح التقدم نحوه، ثم اختر الأرقام. يتابع المختبرون التقدم وجودة المنتج وجودة العملية والتغطية والتكلفة. لا تستخدم المقاييس للحكم على الأفراد أبدًا.',
        'Eine Zahl nützt nur, wenn sie eine Entscheidung unterstützt. Ziel, Frage, Metrik ist ein einfacher Weg: mit dem Ziel beginnen, Fragen zum Fortschritt stellen, erst dann Zahlen wählen. Tester verfolgen Fortschritt, Produktqualität, Prozessqualität, Abdeckung und Kosten. Bewerte nie einzelne Menschen mit Metriken.')),

    sec('estimation', '⏳', 'Estimating test effort', f'''
<p>An estimate is a careful guess with its reasons written down. No technique is perfect, so experienced leads use two and compare.</p>
{table(['Technique', 'How it works', 'Good for'],
       ['Work breakdown structure (WBS)', 'Split testing into small tasks (design, data, execution, retest, reporting) and estimate each one', 'Any project, makes forgotten work visible'],
       ['Ratio based', 'Use a known ratio, such as test effort is about 40% of development effort in past projects', 'Early rough numbers'],
       ['Test case based', 'Number of test cases × average time per case, plus time for retests', 'Projects with a stable test case count'],
       ['Expert judgement and Wideband Delphi', 'Several experts estimate alone, discuss the differences, then estimate again until the numbers meet', 'New or unusual work'],
       ['Planning poker', 'The Agile team shows estimate cards at the same moment (1, 2, 3, 5, 8, 13), then the highest and lowest explain', 'Story points in sprints'],
       ['Three point (PERT)', 'Best case O, most likely M and worst case P give E = (O + 4M + P) ÷ 6', 'Showing uncertainty as a range'])}
<p>The three point formula gives the expected value and the spread:</p>
{eq(f'E = {fr("O + 4M + P", "6")}   and   SD = {fr("P − O", "6")}')}
<p>For several tasks you add the E values. The spreads add as squares: SD<sub>total</sub> = √(SD₁² + SD₂² + …). Saying "E ± 2 SD" gives a range that is right most of the time.</p>
{viz('estimate')}
{tip('Always add time for things that are not test execution: environment problems, waiting for builds, retesting fixes and meetings. Forgetting these is the most common reason test estimates fail.')}
''', say(
        'An estimate is a careful guess with its reasons written down. Common techniques are work breakdown, ratio based, test case based, expert judgement and Wideband Delphi, planning poker and three point estimation. Three point uses the best, most likely and worst case: E equals O plus four M plus P, divided by six. Always add time for retests, waiting and environment problems.',
        'Estimate सावधानी से लगाया गया अनुमान है जिसके कारण लिखे हों। आम तरीके हैं work breakdown, ratio based, test case based, expert judgement और Wideband Delphi, planning poker और three point। Three point best, most likely और worst case लेता है: E बराबर O plus चार M plus P, भाग छह। Retests, इंतज़ार और environment problems का समय हमेशा जोड़ें।',
        'Estimate ಕಾರಣ ಬರೆದ ಎಚ್ಚರಿಕೆಯ ಅಂದಾಜು. WBS, ratio, test case based, Wideband Delphi, planning poker, three point. E = O + 4M + P ಭಾಗ 6. Retest, ಕಾಯುವಿಕೆ, environment ಸಮಯ ಸೇರಿಸಿ.',
        'Estimate କାରଣ ଲେଖାଥିବା ସତର୍କ ଅନୁମାନ। WBS, ratio, test case based, Wideband Delphi, planning poker, three point। E = O + 4M + P ଭାଗ 6। Retest, ଅପେକ୍ଷା, environment ସମୟ ଯୋଡ଼ନ୍ତୁ।',
        'التقدير تخمين مدروس مكتوبة أسبابه. من الطرق الشائعة: تفكيك العمل، والنسبة، وعدد الحالات، ورأي الخبراء ودلفي الموسعة، وبوكر التخطيط، والنقاط الثلاث. تستخدم النقاط الثلاث أفضل حالة والأرجح والأسوأ: E يساوي O زائد أربعة M زائد P مقسومًا على ستة. أضف دائمًا وقت إعادة الاختبار والانتظار ومشكلات البيئة.',
        'Eine Schätzung ist eine sorgfältige Vermutung mit aufgeschriebenen Gründen. Übliche Techniken sind Arbeitsaufteilung, Verhältnis, Testfallbasis, Expertenurteil und Wideband Delphi, Planning Poker und Dreipunktschätzung. E ist O plus vier M plus P, geteilt durch sechs. Plane immer Zeit für Nachtests, Warten und Umgebungsprobleme ein.')),

    sec('progress', '📈', 'Measuring test progress', f'''
<p>During execution, the lead checks progress every day. A few numbers tell most of the story:</p>
{table(['Metric', 'Formula', 'What it tells you'],
       ['Execution %', 'executed × 100 ÷ planned', 'How much of the plan has been run'],
       ['Pass %', 'passed × 100 ÷ executed', 'How much of what ran works'],
       ['Blocked count', 'cases that cannot run', 'Usually an environment or a blocker bug. Needs action today'],
       ['Daily run rate', 'cases executed per day', 'Whether the remaining cases fit the remaining days'],
       ['Open defects by severity', 'count per severity', 'Whether the exit criteria can be met'])}
<p>A <b>burndown chart</b> shows the remaining work going down day by day against an ideal line. If the real line stays above the ideal line, the team is behind and must cut scope, add people or move the date. It is far better to show this on day 4 than on the last day.</p>
{flow('burndown')}
{deep('reading a burndown like a lead', '<p>A flat line for two days usually means blocked work, not lazy people. Look at the blocked count. A sudden drop often means cases were removed from scope, which must be written down. A line that goes up means new work was added, such as new stories or a respin with new features. Ask which one happened before you report the trend.</p>')}
''', say(
        'During execution a lead watches a few numbers every day: execution percent, pass percent, blocked cases, the daily run rate and open defects by severity. A burndown chart shows the remaining work against an ideal line. If the real line stays above it, the team is behind, and it is far better to say so early.',
        'Execution के दौरान lead रोज़ कुछ numbers देखता है: execution percent, pass percent, blocked cases, daily run rate और severity के हिसाब से open defects। Burndown chart बचा हुआ काम ideal line के साथ दिखाता है। असली line ऊपर रहे तो team पीछे है, और यह जल्दी बताना बेहतर है।',
        'Execution ಸಮಯದಲ್ಲಿ execution percent, pass percent, blocked, run rate, open defects. Burndown chart ಉಳಿದ ಕೆಲಸ ideal line ಜೊತೆ. ಮೇಲಿದ್ದರೆ team ಹಿಂದೆ, ಬೇಗ ಹೇಳಿ.',
        'Execution ସମୟରେ execution percent, pass percent, blocked, run rate, open defects। Burndown chart ବାକି କାମ ideal line ସହ। ଉପରେ ରହିଲେ team ପଛରେ, ଶୀଘ୍ର କୁହନ୍ତୁ।',
        'أثناء التنفيذ يراقب القائد أرقامًا قليلة يوميًا: نسبة التنفيذ، ونسبة النجاح، والحالات المعطلة، ومعدل التنفيذ اليومي، والعيوب المفتوحة حسب الخطورة. ويظهر مخطط الإنجاز العمل المتبقي مقابل خط مثالي. إن بقي الخط الفعلي أعلى فالفريق متأخر، والأفضل قول ذلك مبكرًا.',
        'Während der Ausführung beobachtet die Leitung täglich wenige Zahlen: Ausführungsquote, Erfolgsquote, blockierte Fälle, Tagesrate und offene Fehler nach Schwere. Ein Burndown-Diagramm zeigt die Restarbeit gegen eine Ideallinie. Liegt die echte Linie darüber, ist das Team im Verzug, und das sagt man besser früh.')),

    sec('defect-metrics', '🐞', 'Defect metrics that show how good testing is', f'''
<p>These numbers measure the testing process itself. They are asked about in interviews and in every release review.</p>
{table(['Metric', 'Formula', 'Healthy sign'],
       ['Defect removal efficiency (DRE)', 'defects found before release × 100 ÷ (found before + found after release)', 'High, often above 90%'],
       ['Defect leakage', 'defects found by users × 100 ÷ (found before + found after release)', 'Low. It is 100% − DRE'],
       ['Defect density', 'defects ÷ size (KLOC, function points or modules)', 'Compare modules. The densest needs more attention'],
       ['Defect rejection ratio', 'rejected defects × 100 ÷ defects reported', 'Low. High values mean unclear requirements or weak reports'],
       ['Reopen rate', 'reopened defects × 100 ÷ fixed defects', 'Low. High values mean rushed fixes or weak retests'],
       ['Defect age', 'days from logged to closed', 'Short, especially for critical defects'],
       ['Mean time to detect and repair (MTTD, MTTR)', 'average hours to notice and to fix a production problem', 'Falling over time'])}
{viz('metrics')}
{exam('DRE is calculated with valid defects only. Rejected and duplicate bugs are not real defects, so remove them before you divide.')}
''', say(
        'Defect metrics measure the testing process. Defect removal efficiency is the share of all defects found before release. Leakage is the share users found after release. Defect density divides defects by the size of the code or module. Rejection ratio, reopen rate and defect age show the quality of reports and fixes. Use valid defects only.',
        'Defect metrics testing process को मापते हैं। Defect removal efficiency release से पहले मिले defects का हिस्सा है। Leakage वह हिस्सा है जो users ने release के बाद पाया। Defect density defects को code या module के size से भाग देती है। Rejection ratio, reopen rate और defect age reports और fixes की quality दिखाते हैं। सिर्फ़ valid defects लें।',
        'Defect metrics testing process ಅಳೆಯುತ್ತವೆ. DRE release ಮೊದಲು ಸಿಕ್ಕ ಪಾಲು, leakage users ಕಂಡ ಪಾಲು, density defects ಭಾಗ size. Rejection, reopen, age. Valid defects ಮಾತ್ರ.',
        'Defect metrics testing process ମାପେ। DRE release ପୂର୍ବରୁ ମିଳିଥିବା ଅଂଶ, leakage users ପାଇଥିବା ଅଂଶ, density defects ଭାଗ size। Rejection, reopen, age। କେବଳ valid defects।',
        'تقيس مقاييس العيوب عملية الاختبار. كفاءة إزالة العيوب هي نسبة العيوب المكتشفة قبل الإطلاق. والتسرب هو النسبة التي وجدها المستخدمون بعده. وكثافة العيوب تقسم العيوب على حجم الشيفرة أو الوحدة. ونسبة الرفض وإعادة الفتح وعمر العيب تظهر جودة التقارير والإصلاحات. استخدم العيوب الصحيحة فقط.',
        'Fehlermetriken messen den Testprozess. Die Fehlerentfernungseffizienz ist der Anteil der vor dem Release gefundenen Fehler. Leckage ist der Anteil, den Nutzer danach fanden. Fehlerdichte teilt Fehler durch die Größe von Code oder Modul. Ablehnungsquote, Wiedereröffnungsrate und Fehleralter zeigen die Qualität von Berichten und Korrekturen. Nur gültige Fehler zählen.')),

    sec('coverage', '🧩', 'Coverage: what have we really checked', f'''
<p>"How much have we tested?" has several honest answers, and each one sees something different.</p>
{table(['Coverage type', 'Measured as', 'Blind spot'],
       ['Requirement coverage', 'requirements with at least one passed test ÷ all requirements, from the RTM', 'One weak test per requirement still counts as covered'],
       ['Risk coverage', 'high risks with tests run ÷ all high risks', 'Depends on how well the risks were found'],
       ['Code coverage', 'lines or branches run by tests ÷ all lines or branches (white box)', 'Running a line is not the same as checking its result'],
       ['Platform coverage', 'browser, device and OS combinations tested ÷ supported combinations', 'Real users may use combinations nobody listed'],
       ['Data coverage', 'equivalence classes and boundaries tested ÷ identified', 'Classes nobody identified'])}
{tip('Say coverage with its type. "We have 100% requirement coverage, 85% of high risks executed and Safari 17 not yet tested" lets a manager decide. "We have good coverage" does not.')}
''', say(
        'Coverage has several types: requirements, risks, code, platforms and data. Each has a blind spot. A requirement with one weak test still counts as covered, and running a line of code is not the same as checking its result. Always state the type of coverage and what is still not tested.',
        'Coverage के कई प्रकार हैं: requirements, risks, code, platforms और data। हर एक का एक blind spot है। एक कमज़ोर test वाली requirement भी covered गिनी जाती है, और code की line चलाना उसका result जाँचना नहीं है। हमेशा coverage का प्रकार और जो test नहीं हुआ वह बताएँ।',
        'Coverage ಪ್ರಕಾರಗಳು: requirements, risks, code, platforms, data. ಪ್ರತಿಯೊಂದಕ್ಕೂ blind spot. ಪ್ರಕಾರ ಮತ್ತು test ಆಗದದ್ದನ್ನು ಹೇಳಿ.',
        'Coverage ପ୍ରକାର: requirements, risks, code, platforms, data। ପ୍ରତ୍ୟେକର blind spot। ପ୍ରକାର ଓ test ହୋଇନଥିବା କୁହନ୍ତୁ।',
        'للتغطية أنواع: المتطلبات والمخاطر والشيفرة والمنصات والبيانات، ولكل منها نقطة عمياء. المتطلب الذي له اختبار ضعيف واحد يعد مغطى، وتشغيل سطر من الشيفرة لا يعني التحقق من نتيجته. اذكر دائمًا نوع التغطية وما لم يختبر بعد.',
        'Abdeckung gibt es für Anforderungen, Risiken, Code, Plattformen und Daten, und jede hat einen blinden Fleck. Eine Anforderung mit einem schwachen Test gilt als abgedeckt, und eine ausgeführte Codezeile ist noch kein geprüftes Ergebnis. Nenne immer die Art der Abdeckung und was noch fehlt.')),

    sec('reporting', '📰', 'Test status and completion reports', f'''
<p>The ISO/IEC/IEEE 29119 standard names two main reports. A <b>test status report</b> (also called a progress report) goes out regularly, often daily or weekly. A <b>test completion report</b> (often called the test summary report) closes a level or a release.</p>
{table(['Section of a good report', 'What to write'],
       ['Summary in three lines', 'Where we are, the biggest risk, and the recommendation'],
       ['Progress', 'Planned, executed, passed, failed, blocked, with a trend'],
       ['Quality', 'Open defects by severity and module, top three open issues with owners'],
       ['Coverage', 'Requirements and risks covered, and what is not tested and why'],
       ['Risks and blockers', 'What could stop the release and what is being done about it'],
       ['Deviations', 'Changes from the test plan: scope cuts, extra cycles, new environments'],
       ['Recommendation', 'Go, go with conditions, or no go, with reasons'])}
{flow('audience')}
{rule('A good report is honest about bad news. "Payments is not ready, 2 critical bugs are open, we recommend moving the release by 3 days" protects users and the company. Hiding it only moves the problem to production.')}
''', say(
        'A test status report goes out regularly to show progress, quality, coverage and risks. A test completion report closes a level or release and gives a recommendation: go, go with conditions, or no go. Start every report with a three line summary and match the detail to the reader. Be honest about bad news.',
        'Test status report नियमित रूप से progress, quality, coverage और risks दिखाने के लिए भेजी जाती है। Test completion report किसी level या release को बंद करती है और सिफ़ारिश देती है: go, शर्तों के साथ go, या no go। हर report तीन line के summary से शुरू करें और detail पढ़ने वाले के हिसाब से रखें। बुरी ख़बर पर ईमानदार रहें।',
        'Status report ನಿಯಮಿತವಾಗಿ progress, quality, coverage, risks. Completion report release ಮುಚ್ಚಿ go, conditions ಜೊತೆ go, ಅಥವಾ no go. ಮೂರು line summary, ಓದುಗರಿಗೆ ತಕ್ಕ detail, ಪ್ರಾಮಾಣಿಕತೆ.',
        'Status report ନିୟମିତ progress, quality, coverage, risks। Completion report release ବନ୍ଦ କରି go, conditions ସହ go, କିମ୍ବା no go। ତିନି line summary, ପାଠକ ଅନୁଯାୟୀ detail, ସଚ୍ଚୋଟତା।',
        'يرسل تقرير حالة الاختبار بانتظام ليبين التقدم والجودة والتغطية والمخاطر. ويغلق تقرير إكمال الاختبار مستوى أو إصدارًا ويقدم توصية: إطلاق، أو إطلاق بشروط، أو عدم إطلاق. ابدأ كل تقرير بملخص من ثلاثة أسطر وناسب التفاصيل مع القارئ. وكن صادقًا في الأخبار السيئة.',
        'Ein Teststatusbericht zeigt regelmäßig Fortschritt, Qualität, Abdeckung und Risiken. Ein Testabschlussbericht schließt eine Stufe oder ein Release ab und empfiehlt: Go, Go mit Bedingungen oder No-Go. Beginne jeden Bericht mit drei Zeilen Zusammenfassung und passe die Details an den Leser an. Sei ehrlich bei schlechten Nachrichten.')),

    sec('closure', '📦', 'Test closure: finishing properly', f'''
<p>When a release ships, testing is not simply dropped. <b>Test completion</b> (closure) activities make the next release easier:</p>
{grid(box('✅ Check the exit criteria', 'Confirm every criterion is met, or record the agreed exceptions and who approved them.'),
      box('🐞 Settle open defects', 'Every open defect is deferred with a reason, moved to the backlog, or accepted as a known issue in the release notes.'),
      box('🗄️ Archive the testware', 'Test cases, data, scripts, environment details and reports are stored and versioned for reuse.'),
      box('🤝 Hand over', 'Give the support team the known issues and workarounds, and the maintenance team the regression suite.'),
      box('🔁 Lessons learned', 'A short retrospective: what went well, what hurt, what we change next time.'),
      box('📊 Final metrics', 'DRE after the first month in production, effort against estimate, defect trends per module.'))}
{tip('Measure DRE again a few weeks after release, once real users have found what they will find. A DRE written on release day is always too optimistic.')}
''', say(
        'Test closure finishes testing properly. The team checks the exit criteria, settles every open defect, archives test cases, data and reports, hands known issues to support, holds a lessons learned meeting and records final metrics. Measure defect removal efficiency again a few weeks after release, because the release day number is always too optimistic.',
        'Test closure testing को ठीक से समाप्त करता है। Team exit criteria जाँचती है, हर open defect का फ़ैसला करती है, test cases, data और reports archive करती है, known issues support को देती है, lessons learned meeting करती है और final metrics लिखती है। Release के कुछ हफ़्ते बाद DRE फिर मापें, क्योंकि release वाले दिन का number हमेशा ज़्यादा अच्छा दिखता है।',
        'Test closure: exit criteria, open defects ನಿರ್ಧಾರ, testware archive, support ಗೆ handover, lessons learned, final metrics. ಕೆಲವು ವಾರಗಳ ನಂತರ DRE ಮತ್ತೆ ಅಳೆಯಿರಿ.',
        'Test closure: exit criteria, open defects ନିଷ୍ପତ୍ତି, testware archive, support କୁ handover, lessons learned, final metrics। କିଛି ସପ୍ତାହ ପରେ DRE ପୁଣି ମାପନ୍ତୁ।',
        'إغلاق الاختبار ينهيه بشكل صحيح: يتحقق الفريق من معايير الخروج، ويحسم كل عيب مفتوح، ويؤرشف الحالات والبيانات والتقارير، ويسلم المشكلات المعروفة للدعم، ويعقد اجتماع الدروس المستفادة، ويسجل المقاييس النهائية. أعد قياس كفاءة إزالة العيوب بعد أسابيع من الإطلاق.',
        'Der Testabschluss beendet das Testen sauber: Endekriterien prüfen, jeden offenen Fehler entscheiden, Testmittel archivieren, bekannte Probleme an den Support übergeben, Lessons Learned durchführen und Abschlussmetriken festhalten. Miss die Fehlerentfernungseffizienz einige Wochen nach dem Release erneut.')),
]

INFO = {"title": "Numbers that help people decide", "panels": [
    {"s": [["e", "⏳"], ["t", "(O + 4M + P) ÷ 6", {"b": 1}]], "h": "Before testing", "t": "Estimate as a range, not a promise.", "more": "Add time for retests and waiting."},
    {"s": [["e", "📈"], ["t", "executed · passed · blocked", {"b": 1, "size": 12}]], "h": "During testing", "t": "Watch progress every day.", "more": "Say early when the line is behind."},
    {"s": [["e", "🐞"], ["t", "DRE 90%", {"b": 1}]], "h": "How good was testing", "t": "Count what escaped to users.", "more": "Use valid defects only."},
    {"s": [["e", "📰"], ["t", "go · conditions · no go", {"b": 1, "size": 12}]], "h": "The report", "t": "Three lines first, then the detail.", "more": "Honest about bad news."}],
    "remember": "Measure to help decisions, never to judge people. Estimate with ranges, report with honesty, and always say what is not tested."}

REAL = [
    ["🚕", "A taxi app's arrival time", "\"Arriving in 6 to 9 minutes\" is a three point estimate. A range is more honest than one exact number, and people trust it more."],
    ["🩺", "A health check report", "A doctor's report gives a few key numbers, marks the ones outside the normal range and ends with advice. A good test report does the same."],
    ["🏏", "A cricket scorecard", "Runs, overs and the required run rate tell everyone at a glance whether the team is on track. A burndown chart is the scorecard of a test cycle."]]

QUIZ = [
    Qz('e', 'What does DRE stand for?', ['Defect reporting effort', 'Defect removal efficiency', 'Development release estimate', 'Daily run execution'], 1, 'How well testing removes defects.', 'Defect removal efficiency is the share of defects found before release.'),
    Qz('e', 'Execution progress is calculated as...', ['passed × 100 ÷ executed', 'executed × 100 ÷ planned', 'defects ÷ KLOC', 'planned ÷ executed'], 1, 'How much of the plan ran.', 'Executed cases × 100 ÷ planned cases.'),
    Qz('e', 'In planning poker, why do people show their cards at the same moment?', ['To save time', 'So nobody is influenced by the first number said', 'Because it is a game', 'So the manager can choose'], 1, 'Think about anchoring.', 'Showing together avoids anchoring on the first or the loudest estimate.'),
    Qz('m', 'Best case 4 days, most likely 6, worst case 14. What is the three point estimate E?', ['6', '7', '8', '8.5'], 1, '(O + 4M + P) ÷ 6.', '(4 + 24 + 14) ÷ 6 = 42 ÷ 6 = 7 days.'),
    Qz('m', 'Testing found 90 valid defects and users found 10 after release. What is the DRE?', ['10%', '80%', '90%', '100%'], 2, 'Found before ÷ all.', '90 × 100 ÷ (90 + 10) = 90%.'),
    Qz('m', 'Why must rejected and duplicate bugs be removed before calculating DRE?', ['They are too small', 'They are not real defects in the product', 'Managers ask for it', 'They are counted twice in leakage'], 1, 'DRE is about real defects.', 'Only valid defects show how well testing removed real problems.'),
    Qz('m', 'A burndown line stays flat for two days. What should a lead check first?', ['Whether testers are lazy', 'The blocked count, for environment or blocker issues', 'The colour of the chart', 'The number of meetings'], 1, 'Flat usually means stuck.', 'A flat line usually means work cannot progress, for example a blocker bug or a broken environment.'),
    Qz('h', 'Which report closes a test level or a release and gives a go or no go recommendation?', ['Test status report', 'Test completion (summary) report', 'Bug report', 'RTM'], 1, 'Completion closes.', 'The completion report summarises results, deviations, risks and the recommendation.'),
    Qz('h', 'Testers are rewarded for every bug they log. What is the most likely result?', ['Better quality', 'Many small duplicate bugs and arguments', 'Fewer bugs', 'Faster releases'], 1, 'Goodhart\'s law.', 'When a measure becomes a target, people optimise the number instead of the goal.'),
    Qz('h', 'Which statement about 100% code coverage is true?', ['The product has no bugs', 'Every line ran during tests, but results may not have been checked', 'Every requirement passed', 'No more testing is needed'], 1, 'Running is not checking.', 'Coverage shows what ran, not whether the right result was verified or whether requirements are missing.'),
    Qz('x', 'Three tasks have SD values 1, 2 and 2 days. What is the total SD?', ['5', '3', '2.24', '9'], 1, 'Add the squares, then take the root.', '√(1 + 4 + 4) = √9 = 3 days.'),
    Qz('x', 'Module A has 30 defects in 15 KLOC and module B has 24 defects in 6 KLOC. Where should the next cycle focus?', ['Module A, more defects', 'Module B, higher density', 'Both equally', 'Neither'], 1, 'Divide by size.', 'A has 2 per KLOC, B has 4 per KLOC. B is twice as dense, so it is the riskier module.'),
]

CALC = [
    Calc('e', '400 test cases are planned and 320 are executed. What is the execution percentage?', '80', '320 * 100 / 400', 'Executed × 100 ÷ planned.', [eq(f'{fr("320 × 100", "400")} = 80%')], unit='%'),
    Calc('e', 'Of 320 executed cases, 288 passed. What is the pass percentage?', '90', '288 * 100 / 320', 'Passed × 100 ÷ executed.', [eq(f'{fr("288 × 100", "320")} = 90%')], unit='%'),
    Calc('m', 'Best case 3 days, most likely 5 days, worst case 13 days. What is E?', '6', '(3 + 4 * 5 + 13) / 6', '(O + 4M + P) ÷ 6.', [eq(f'{fr("3 + 20 + 13", "6")} = {fr("36", "6")} = 6') + ' days']),
    Calc('m', 'Testing found 140 valid defects. Users found 10 after release. What is the DRE? Round to one decimal.', '93.3', '140 * 100 / 150', 'Before × 100 ÷ (before + after).', [eq(f'{fr("140 × 100", "140 + 10")} = {fr("14,000", "150")} ≈ 93.3%')], unit='%'),
    Calc('m', '60 bugs were reported and 9 were rejected. What is the rejection ratio?', '15', '9 * 100 / 60', 'Rejected × 100 ÷ reported.', [eq(f'{fr("9 × 100", "60")} = 15%')], unit='%'),
    Calc('h', '180 cases remain, 6 working days are left, and the team runs 25 cases a day. How many cases will be left undone on the last day?', '30', '180 - 6 * 25', 'Remaining − days × rate.', [eq('6 × 25 = 150') + ' cases possible', eq('180 − 150 = 30') + ' cases left. Report this now, not on day 6.']),
    Calc('x', 'Two tasks: O, M, P = 2, 4, 8 and 3, 6, 15. What is the upper end of the range E + 2 SD for the total? Round to one decimal.', '15.8', '(2 + 16 + 8) / 6 + (3 + 24 + 15) / 6 + 2 * ((1) ** 2 + (2) ** 2) ** 0.5', 'Add the E values. SD total = √(SD₁² + SD₂²).', [eq('E₁ = 26 ÷ 6 ≈ 4.33, E₂ = 42 ÷ 6 = 7, total ≈ 11.33'), eq('SD₁ = 6 ÷ 6 = 1, SD₂ = 12 ÷ 6 = 2, SD = √5 ≈ 2.24'), eq('11.33 + 2 × 2.24 ≈ 15.8')]),
]

DG = {
    "gqm": {"t": "Goal, question, metric", "w": 820, "h": 250,
        "n": [["goal", 10, 90, 200, 70, "Goal", {"c": 0, "ic": "🎯", "sub": "safe payments release"}],
              ["q1", 290, 20, 230, 56, "Are high risk flows tested?", {"c": 3}],
              ["q2", 290, 100, 230, 56, "Are serious bugs still open?", {"c": 3}],
              ["q3", 290, 180, 230, 56, "Do bugs escape to users?", {"c": 3}],
              ["m1", 600, 20, 210, 56, "High risk cases passed", {"c": 2, "sub": "36 of 38"}],
              ["m2", 600, 100, 210, 56, "Open critical and major", {"c": 2, "sub": "0 and 2"}],
              ["m3", 600, 180, 210, 56, "Leakage last release", {"c": 2, "sub": "6%"}]],
        "e": [["goal", "q1", {}], ["goal", "q2", {}], ["goal", "q3", {}], ["q1", "m1", {}], ["q2", "m2", {}], ["q3", "m3", {}]],
        "st": [[["goal"], "Start with a goal that matters to the business: release the new payments feature safely."],
               [["q1", "q2", "q3", "goal>q1", "goal>q2", "goal>q3"], "Ask the questions that would show whether the goal is being met."],
               [["m1", "m2", "m3", "q1>m1", "q2>m2", "q3>m3"], "Only now choose metrics, one or two per question. Every number on the report now has a reason to be there."]]},
    "burndown": {"t": "A ten day test cycle burndown", "w": 760, "h": 300,
        "g": [[56, 20, 680, 240, "", 2]],
        "n": [["z", 700, 236, 14, 14, "", {"c": 1, "sh": "circle"}],
              ["d0", 64, 30, 14, 14, "", {"c": 2, "sh": "circle"}], ["d3", 260, 92, 14, 14, "", {"c": 2, "sh": "circle"}],
              ["d5", 390, 110, 14, 14, "", {"c": 6, "sh": "circle"}], ["d6", 455, 110, 14, 14, "", {"c": 6, "sh": "circle"}],
              ["d10", 700, 200, 14, 14, "", {"c": 6, "sh": "circle"}],
              ["note", 470, 30, 250, 56, "Behind plan: about 50 cases\nwill be left on day 10", {"sh": "note"}],
              ["blk", 300, 160, 190, 46, "Days 5 to 6: blocker bug", {"c": 6, "sh": "pill"}]],
        "e": [["d0", "d3", {"c": 2}], ["d3", "d5", {"c": 2}], ["d5", "d6", {"c": 6}], ["d6", "d10", {"c": 6, "d": 1, "id": "proj", "t": "projected"}],
              ["d0", "z", {"id": "ideal", "d": 1, "c": 1, "t": "ideal line", "tx": 200, "ty": 150}]],
        "tx": [[30, 30, "400", {"s": 11}], [30, 243, "0", {"s": 11}], [390, 285, "days 0 to 10", {"s": 11}], [16, 140, "cases\nleft", {"s": 11}]],
        "st": [[["ideal", "z"], "The ideal line goes from 400 cases on day 0 to zero on day 10: 40 cases a day."],
               [["d0", "d3", "d0>d3"], "Days 1 to 3 go almost to plan. The real line runs just above the ideal line."],
               [["d5", "d3>d5"], "Days 4 and 5 slow down as harder cases are reached."],
               [["d6", "blk", "d5>d6"], "Days 5 to 6 are flat. A blocker bug stops the transfer module, so nothing can move. The blocked count explains the flat line."],
               [["d10", "proj", "note"], "At this rate about 50 cases will be left on day 10. The lead reports it now, with options: add a tester, cut low risk cases, or move the date."]]},
    "audience": {"t": "One report, three readers", "w": 820, "h": 230,
        "n": [["rep", 10, 80, 170, 76, "Test report", {"c": 5, "sh": "doc", "sub": "same facts"}],
              ["exec", 290, 10, 220, 60, "Sponsor or director", {"c": 0, "ic": "👔"}],
              ["pm", 290, 88, 220, 60, "Project manager", {"c": 3, "ic": "🗓️"}],
              ["team", 290, 166, 220, 60, "Developers and testers", {"c": 2, "ic": "🛠️"}],
              ["e1", 570, 10, 240, 60, "Go or no go, top risk,\nin three lines", {"sh": "note"}],
              ["e2", 570, 88, 240, 60, "Trend, dates, blockers,\nwhat needs a decision", {"sh": "note"}],
              ["e3", 570, 166, 240, 60, "Bug ids, modules, steps,\nenvironment issues", {"sh": "note"}]],
        "e": [["rep", "exec", {}], ["rep", "pm", {}], ["rep", "team", {}], ["exec", "e1", {}], ["pm", "e2", {}], ["team", "e3", {}]],
        "st": [[["rep"], "The facts are the same for everyone. What changes is how much detail each reader needs."],
               [["exec", "e1", "rep>exec", "exec>e1"], "A director has two minutes. Give the recommendation and the biggest risk first."],
               [["pm", "e2", "rep>pm", "pm>e2"], "The project manager needs the trend, the dates and anything that needs a decision."],
               [["team", "e3", "rep>team", "team>e3"], "The team needs the details: which bugs, which modules, which environment problems."]]},
}

X = {}
