from kit import *

FILE = 'test-design.html'

SECTIONS = [
    sec('use-case', '🎭', 'Use case testing and checklist based testing', f'''
<p>A <b>use case</b> describes how an actor (a user or another system) reaches a goal, step by step. It has a <b>main flow</b> where everything goes well, <b>alternative flows</b> where the user takes another valid path, and <b>exception flows</b> where something goes wrong. Use case testing writes at least one test for each flow.</p>
{flow('usecase')}
{table(['Flow', 'Steps of "Withdraw cash at an ATM"', 'Test idea'],
       ['Main', 'Insert card, enter PIN, choose amount, take cash, take card', 'Withdraw ₹2,000 with enough balance'],
       ['Alternative', 'Choose "other amount" instead of a quick amount', 'Withdraw ₹1,500 using other amount'],
       ['Alternative', 'Ask for a receipt', 'Receipt shows the right amount and balance'],
       ['Exception', 'Wrong PIN three times', 'Card is blocked with a clear message'],
       ['Exception', 'Amount above the balance', '"Insufficient balance", no cash, no debit'],
       ['Exception', 'Cash not taken within 30 seconds', 'Cash is taken back and the account is not debited'])}
<h3>Checklist based testing</h3>
<p>Experienced testers keep <b>checklists</b>: short lists of things to verify, built from past bugs, standards and experience. A checklist does not give exact steps, so each tester applies it a little differently, which adds variety.</p>
{grid(box('📝 Form checklist', 'Required fields marked, tab order, max length, paste, leading spaces, error next to the field, data kept after an error, double submit.'),
      box('🔁 Every release checklist', 'Login and logout, password reset, main journeys, emails and SMS, mobile view, browser back button, session timeout.'))}
''', say(
        'A use case describes how an actor reaches a goal step by step, with a main flow, alternative flows and exception flows. Use case testing writes at least one test for each flow, for example an ATM withdrawal with a quick amount, another amount, a wrong PIN or too little balance. Checklist based testing uses short lists built from experience and past bugs.',
        'Use case बताता है कि actor step by step लक्ष्य तक कैसे पहुँचता है, main flow, alternative flows और exception flows के साथ। Use case testing हर flow के लिए कम से कम एक test लिखती है, जैसे ATM से quick amount, दूसरी amount, गलत PIN या कम balance। Checklist based testing अनुभव और पुराने bugs से बनी छोटी lists इस्तेमाल करती है।',
        'Use case actor ಗುರಿ ತಲುಪುವ ಹಂತಗಳು: main, alternative, exception flows. ಪ್ರತಿ flow ಗೆ test, ATM ಉದಾಹರಣೆ. Checklist based testing ಅನುಭವದ ಪಟ್ಟಿಗಳು.',
        'Use case actor ଲକ୍ଷ୍ୟରେ ପହଞ୍ଚିବା steps: main, alternative, exception flows। ପ୍ରତି flow ପାଇଁ test, ATM ଉଦାହରଣ। Checklist based testing ଅନୁଭବର lists।',
        'تصف حالة الاستخدام كيف يصل الفاعل إلى هدفه خطوة بخطوة، مع مسار رئيسي ومسارات بديلة ومسارات استثناء. ويكتب اختبار حالات الاستخدام اختبارًا واحدًا على الأقل لكل مسار، مثل السحب من الصراف بمبلغ سريع أو مبلغ آخر أو رقم سري خاطئ أو رصيد غير كاف. ويستخدم الاختبار بقوائم التحقق قوائم قصيرة مبنية على الخبرة والأخطاء السابقة.',
        'Ein Anwendungsfall beschreibt Schritt für Schritt, wie ein Akteur sein Ziel erreicht, mit Hauptablauf, alternativen Abläufen und Ausnahmeabläufen. Anwendungsfalltests schreiben mindestens einen Test je Ablauf, etwa eine Abhebung mit Schnellbetrag, anderem Betrag, falscher PIN oder zu wenig Guthaben. Checklistenbasiertes Testen nutzt kurze Listen aus Erfahrung und früheren Fehlern.')),

    sec('good-cases', '✨', 'Writing test cases that others can run', f'''
<p>A test case is written once and run many times, often by someone else. These habits make it useful for years.</p>
{table(['Mistake', 'Example', 'Better'],
       ['Vague step', 'Enter details and submit', 'Enter amount 5,000 and account 1234567890, then click Transfer'],
       ['Vague expected result', 'It should work', 'Message "Transfer successful" and balance reduced by 5,000'],
       ['Many checks in one case', 'Test login, transfer and logout', 'One goal per case, so a failure points to one thing'],
       ['Hidden dependency', 'Uses the account created in case 12', 'Preconditions list the data the case needs'],
       ['Only happy paths', 'Valid amounts only', 'Add boundaries, invalid classes and error recovery'],
       ['Copied UI text that changes', 'Click the blue button', 'Click Transfer (the button name, not its look)'])}
{grid(box('🎯 One clear goal', 'The title says what is checked: "Transfer is refused when the amount exceeds the daily limit".'),
      box('🧱 Independent', 'Each case can run alone, in any order.'),
      box('🔗 Traceable', 'Each case points to its requirement id, so the RTM stays honest.'),
      box('♻️ Maintainable', 'Common steps such as login live in one place, and cases refer to them.'))}
{tip('Read your own case as if you joined the team today. If you would need to ask a question to run it, the answer belongs in the case.')}
''', say(
        'A good test case can be run by someone else without asking questions. Use exact steps and data, a precise expected result, one goal per case, listed preconditions instead of hidden dependencies, negative and boundary cases, and a link to the requirement. Read your case as if you joined the team today.',
        'अच्छा test case कोई और बिना सवाल पूछे चला सके। सटीक steps और data, साफ़ expected result, हर case का एक लक्ष्य, छिपी निर्भरता की जगह लिखी preconditions, negative और boundary cases, और requirement से link रखें। अपना case ऐसे पढ़ें जैसे आज ही team में आए हों।',
        'ಒಳ್ಳೆಯ test case ಬೇರೆಯವರು ಪ್ರಶ್ನೆ ಇಲ್ಲದೆ ನಡೆಸಬಹುದು. ನಿಖರ steps, data, expected result, ಒಂದು ಗುರಿ, preconditions, negative cases, requirement link.',
        'ଭଲ test case ଅନ୍ୟ କେହି ପ୍ରଶ୍ନ ବିନା ଚଳାଇପାରିବେ। ସଠିକ୍ steps, data, expected result, ଗୋଟିଏ ଲକ୍ଷ୍ୟ, preconditions, negative cases, requirement link।',
        'حالة الاختبار الجيدة يستطيع غيرك تنفيذها دون أسئلة. استخدم خطوات وبيانات دقيقة، ونتيجة متوقعة محددة، وهدفًا واحدًا لكل حالة، وشروطًا مسبقة مكتوبة بدل الاعتماد الخفي، وحالات سلبية وحدية، وربطًا بالمتطلب. اقرأ حالتك كأنك انضممت للفريق اليوم.',
        'Ein guter Testfall lässt sich von anderen ohne Rückfragen ausführen. Nutze genaue Schritte und Daten, ein präzises erwartetes Ergebnis, ein Ziel je Fall, geschriebene Vorbedingungen statt versteckter Abhängigkeiten, negative und Grenzfälle und einen Link zur Anforderung. Lies deinen Fall, als wärst du heute neu im Team.')),
]

QUIZ = [
    Qz('e', 'In a use case, "wrong PIN three times" is which kind of flow?', ['Main flow', 'Alternative flow', 'Exception flow', 'Data flow'], 2, 'Something goes wrong.', 'Exception flows describe what happens when the goal cannot be reached normally.'),
    Qz('m', 'Which expected result is best?', ['It should work', 'Transfer done', 'Message "Transfer successful" and balance reduced by exactly 5,000', 'No error'], 2, 'Can anyone check it the same way?', 'A precise, observable result lets any tester decide pass or fail identically.'),
    Qz('h', 'Why should each test case be independent of the others?', ['To save paper', 'So it can run alone and in any order, and a failure points to one cause', 'Because tools require it', 'To increase the count'], 1, 'Think of reruns and failures.', 'Dependent cases fail in chains and hide the real cause.'),
]

CALC = [
    Calc('m', 'A use case has 1 main flow, 3 alternative flows and 4 exception flows. At least how many tests does use case testing need?', '8', '1 + 3 + 4', 'One per flow.', [eq('1 + 3 + 4 = 8')]),
]

DG = {
    "usecase": {"t": "Use case: withdraw cash at an ATM", "w": 860, "h": 260,
        "n": [["card", 10, 100, 120, 60, "Insert card", {"c": 2}], ["pin", 160, 100, 120, 60, "Enter PIN", {"c": 2}],
              ["amt", 310, 100, 130, 60, "Choose amount", {"c": 2}], ["cash", 470, 100, 120, 60, "Take cash", {"c": 1}],
              ["done", 620, 100, 120, 60, "Take card", {"c": 1, "sh": "pill"}],
              ["alt", 310, 10, 130, 50, "Other amount", {"c": 0, "sub": "alternative"}],
              ["e1", 160, 200, 130, 50, "3 wrong PINs", {"c": 6, "sub": "card blocked"}],
              ["e2", 310, 200, 130, 50, "Low balance", {"c": 6, "sub": "no cash"}],
              ["e3", 470, 200, 140, 50, "Cash not taken", {"c": 6, "sub": "taken back"}]],
        "e": [["card", "pin", {}], ["pin", "amt", {}], ["amt", "cash", {}], ["cash", "done", {}], ["alt", "amt", {"d": 1}],
              ["pin", "e1", {"d": 1, "c": 6}], ["amt", "e2", {"d": 1, "c": 6}], ["cash", "e3", {"d": 1, "c": 6}]],
        "st": [[["card", "pin", "amt", "cash", "done", "card>pin", "pin>amt", "amt>cash", "cash>done"], "The main flow: everything goes well and the customer gets cash and the card."],
               [["alt", "alt>amt"], "An alternative flow: the customer types another amount. Still a success, through a different path."],
               [["e1", "pin>e1"], "Exception: three wrong PINs block the card."],
               [["e2", "amt>e2"], "Exception: the balance is too low. No cash, no debit."],
               [["e3", "cash>e3"], "Exception: the cash is not taken in time. The machine takes it back and the account is not debited. Each flow gets at least one test."]]},
}
