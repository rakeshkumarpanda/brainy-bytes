from kit import *

FILE = 'regression-automation.html'

SECTIONS = [
    sec('what-first', '🥇', 'Choosing what to automate first', f'''
<p>Nobody automates everything at once. A simple score helps a team pick the cases that pay back fastest:</p>
{table(['Factor', 'Score high when', 'Example'],
       ['Frequency', 'The case runs every build or every release', 'Login, smoke checks, main payment journey'],
       ['Business risk', 'A failure would hurt many users or cost money', 'Fund transfer, checkout, interest calculation'],
       ['Stability', 'The feature and its screens rarely change', 'An address form unchanged for two years'],
       ['Effort to run by hand', 'Many data sets or many browsers', 'The same rule checked for 40 tariff plans'],
       ['Effort to automate (subtract)', 'It is easy to automate and to maintain', 'An API check is easier than a drag and drop screen'])}
<p>Multiply or add the scores and start from the top of the list. Combine this with the <b>test pyramid</b>: a rule checked through an API is faster and steadier than the same rule checked through the browser.</p>
{grid(box('👀 Visual regression', 'Tools compare screenshots of each page with an approved baseline and highlight differences. They catch layout bugs that functional checks miss, such as a button pushed off the screen.'),
      box('📜 Contract testing', 'Checks that two services still agree on the shape of the data they exchange, so a change in one does not silently break the other.'))}
{deep('return on investment in one line', '<p>Automation pays back when <b>cost to build + cost to maintain</b> is less than <b>manual time saved</b> over the runs you expect. A case that runs 50 times a year and takes 20 minutes by hand saves 1,000 minutes a year. If it takes 300 minutes to automate and 100 minutes a year to maintain, it pays back in the first year, and keeps paying after that.</p>')}
''', say(
        'Teams automate first the cases that run often, carry high business risk, belong to stable features, take long by hand and are easy to automate. Combine this score with the test pyramid, because a rule checked through an API is faster and steadier than through the browser. Visual regression and contract testing catch problems that functional checks miss.',
        'Teams पहले वे cases automate करती हैं जो अक्सर चलते हैं, जिनका business risk ऊँचा है, जो stable features के हैं, हाथ से लंबे हैं और automate करने में आसान हैं। इस score को test pyramid के साथ जोड़ें, क्योंकि API से जाँचा गया rule browser से तेज़ और स्थिर है। Visual regression और contract testing वे समस्याएँ पकड़ते हैं जो functional checks से छूटती हैं।',
        'ಮೊದಲು automate: ಆಗಾಗ ನಡೆಯುವ, ಹೆಚ್ಚು risk, stable, ಕೈಯಿಂದ ದೀರ್ಘ, ಸುಲಭ cases. Test pyramid ಜೊತೆ. Visual regression ಮತ್ತು contract testing.',
        'ପ୍ରଥମେ automate: ବାରମ୍ବାର ଚାଲୁଥିବା, ଅଧିକ risk, stable, ହାତରେ ଲମ୍ବା, ସହଜ cases। Test pyramid ସହ। Visual regression ଓ contract testing।',
        'تؤتمت الفرق أولًا الحالات التي تعمل كثيرًا وذات مخاطر أعمال عالية ولميزات مستقرة وتستغرق وقتًا يدويًا وسهلة الأتمتة. ادمج هذا التقييم مع هرم الاختبار، لأن القاعدة المفحوصة عبر الواجهة البرمجية أسرع وأثبت من المتصفح. ويلتقط الانحدار البصري واختبار العقود مشكلات تفوت الفحوص الوظيفية.',
        'Teams automatisieren zuerst Fälle, die oft laufen, hohes Geschäftsrisiko tragen, stabile Funktionen betreffen, von Hand lange dauern und leicht zu automatisieren sind. Kombiniere das mit der Testpyramide, denn eine Regel über die API ist schneller und stabiler als über den Browser. Visuelle Regression und Vertragstests finden, was Funktionstests übersehen.')),

    sec('flaky', '🎲', 'Flaky tests and why they matter', f'''
<p>A <b>flaky test</b> passes and fails on the same code without any change. Run it ten times and you might see eight green and two red. Flaky tests are dangerous because people learn to ignore red results, and then a real failure is ignored too.</p>
{viz('flaky')}
{table(['Common cause', 'Example', 'Typical fix'],
       ['Timing', 'The test clicks before the page finished loading', 'Wait for a condition, never a fixed sleep'],
       ['Shared data', 'Two tests use the same account at the same time', 'Each test creates or owns its data'],
       ['Test order', 'A test only passes if another test ran first', 'Make tests independent'],
       ['Environment', 'A slow or overloaded test server, an outside service that times out', 'Stable environments, mocks for outside services'],
       ['Real product bug', 'A race condition in the app itself', 'Report it as a bug. Users will meet it too'])}
{tip('As a manual tester, if an automated check is flaky, try the same steps by hand quickly and repeatedly. If you can make it fail, the flakiness may be a real bug in the product, not in the test.')}
''', say(
        'A flaky test passes and fails on the same code without any change. It is dangerous because people learn to ignore red results. Common causes are timing, shared data, test order, unstable environments, and sometimes a real race condition in the product. Automatic retries hide flakiness instead of fixing it. Try the lab and turn retry on to see what it hides.',
        'Flaky test बिना किसी बदलाव के उसी code पर कभी pass कभी fail होता है। यह खतरनाक है क्योंकि लोग red results को अनदेखा करना सीख जाते हैं। आम कारण timing, shared data, test order, अस्थिर environments और कभी product में असली race condition हैं। Automatic retry flakiness ठीक नहीं करता, छिपाता है। Lab में retry चालू करके देखें।',
        'Flaky test ಅದೇ code ನಲ್ಲಿ ಒಮ್ಮೆ pass ಒಮ್ಮೆ fail. Red results ನಿರ್ಲಕ್ಷಿಸುವ ಅಭ್ಯಾಸ ಅಪಾಯ. Timing, shared data, order, environment, race condition. Retry ಮುಚ್ಚುತ್ತದೆ.',
        'Flaky test ସମାନ code ରେ କେବେ pass କେବେ fail। Red results ଅଣଦେଖା ଅଭ୍ୟାସ ବିପଦ। Timing, shared data, order, environment, race condition। Retry ଲୁଚାଏ।',
        'الاختبار المتقلب ينجح ويفشل على الشيفرة نفسها دون أي تغيير. وهو خطير لأن الناس يعتادون تجاهل النتائج الحمراء. أسبابه الشائعة التوقيت والبيانات المشتركة وترتيب الاختبارات والبيئات غير المستقرة، وأحيانًا حالة سباق حقيقية في المنتج. وإعادة المحاولة التلقائية تخفي التقلب ولا تصلحه.',
        'Ein flakiger Test besteht und scheitert am selben Code ohne Änderung. Gefährlich, weil Menschen lernen, rote Ergebnisse zu ignorieren. Häufige Ursachen sind Timing, geteilte Daten, Testreihenfolge, instabile Umgebungen und manchmal eine echte Race Condition im Produkt. Automatische Wiederholungen verbergen das Problem, statt es zu lösen.')),
]

QUIZ = [
    Qz('e', 'What is a flaky test?', ['A test that always fails', 'A test that passes and fails on the same code without changes', 'A slow test', 'A manual test'], 1, 'Same code, different result.', 'Flaky tests give different results without any change, which destroys trust in the suite.'),
    Qz('m', 'Which case should usually be automated first?', ['A one time data migration check', 'The login and payment smoke checks that run every build', 'A screen that changes every sprint', 'A usability review'], 1, 'Frequent, risky, stable.', 'Frequent, high risk, stable checks pay back fastest.'),
    Qz('h', 'Why can automatic retry of failed tests be harmful?', ['It is slow', 'It hides flakiness and possibly real race conditions', 'It uses more memory', 'It changes the code'], 1, 'Green is not always healthy.', 'Retries turn red runs green and hide the real cause, which may also affect users.'),
]

CALC = [
    Calc('m', 'A case runs 50 times a year and takes 20 minutes by hand. Automating takes 300 minutes and maintenance 100 minutes a year. How many minutes are saved in year one?', '600', '50 * 20 - (300 + 100)', 'Manual time − (build + maintain).', [eq('50 × 20 = 1,000') + ' manual minutes', eq('1,000 − (300 + 100) = 600')]),
    Calc('h', 'A test fails randomly 10% of the time. What is the chance, in percent, that 20 runs are all green? Round to one decimal.', '12.2', '0.9 ** 20 * 100', '(1 − p) to the power 20.', [eq('0.9<sup>20</sup> ≈ 0.122 = 12.2%')], unit='%'),
]

DG = {}
