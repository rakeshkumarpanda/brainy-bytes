from kit import *

FILE = 'testing-levels.html'

SECTIONS = [
    sec('pos-neg', '➕', 'Positive, negative and end to end testing', f'''
<p>Every level of testing mixes two attitudes:</p>
{grid(box('✅ Positive testing', 'Valid input, normal steps: does the feature do what it should? Transfer ₹5,000 to a valid account with enough balance and see it succeed.'),
      box('❌ Negative testing', 'Invalid input or wrong steps: does the feature refuse safely, with a clear message? Transfer ₹0, a negative amount, letters, more than the balance, or to your own account.'))}
<p>A rough rule many teams use: for every positive test there are several negative ones, because there are many more ways to be wrong than to be right. Negative tests find the bugs that real users hit when they make mistakes.</p>
<h3>End to end testing</h3>
<p><b>End to end (E2E) testing</b> follows one complete user journey through every connected part of the system, including outside services, the way a real customer would:</p>
{flow('e2e')}
{table(['Kind', 'What it checks', 'Example'],
       ['Monkey testing', 'Random input with no plan, to see if the app crashes', 'Tapping randomly on every screen of a phone app'],
       ['Gorilla testing', 'One module tested again and again very hard', 'Hitting the login page with every kind of input for a whole day'],
       ['Sanity testing', 'A quick, narrow check of one fixed area in a new build', 'After a fix to the OTP, check OTP and login only'],
       ['End to end testing', 'A full real journey across all systems', 'Sign up, add money, pay a bill, see the SMS and the statement'])}
''', say(
        'Positive testing uses valid input to check the feature works. Negative testing uses invalid input or wrong steps to check the feature refuses safely with a clear message. There are usually many more negative cases than positive ones. End to end testing follows one complete user journey through every connected system, including outside services such as payment and SMS.',
        'Positive testing valid input से देखती है कि feature काम करता है। Negative testing invalid input या गलत steps से देखती है कि feature साफ़ message के साथ सुरक्षित रूप से मना करता है। आमतौर पर negative cases positive से कहीं ज़्यादा होते हैं। End to end testing एक पूरी user journey को हर जुड़े system से होकर ले जाती है, payment और SMS जैसी बाहरी services सहित।',
        'Positive testing valid input, negative testing invalid input ಮತ್ತು ಸ್ಪಷ್ಟ message. Negative cases ಹೆಚ್ಚು. End to end testing ಸಂಪೂರ್ಣ user journey, payment ಮತ್ತು SMS ಸೇರಿ.',
        'Positive testing valid input, negative testing invalid input ଓ ସ୍ପଷ୍ଟ message। Negative cases ଅଧିକ। End to end testing ସମ୍ପୂର୍ଣ୍ଣ user journey, payment ଓ SMS ସହ।',
        'الاختبار الإيجابي يستخدم مدخلات صحيحة للتحقق من عمل الميزة. والاختبار السلبي يستخدم مدخلات خاطئة أو خطوات خاطئة للتحقق من أن الميزة ترفض بأمان مع رسالة واضحة. عادة تكون الحالات السلبية أكثر بكثير. واختبار النهاية إلى النهاية يتبع رحلة مستخدم كاملة عبر كل الأنظمة المتصلة، ومنها خدمات الدفع والرسائل.',
        'Positives Testen prüft mit gültigen Eingaben, ob die Funktion arbeitet. Negatives Testen prüft mit ungültigen Eingaben, ob sie sicher und mit klarer Meldung ablehnt. Meist gibt es weit mehr negative als positive Fälle. End-to-End-Testen folgt einer vollständigen Nutzerreise durch alle verbundenen Systeme, auch externe Dienste wie Zahlung und SMS.')),

    sec('api-level', '🔌', 'Testing below the screen: APIs and system integration', f'''
<p>Modern applications are built from many services that talk through <b>APIs</b> (application programming interfaces). The screen is only the last step. A manual tester who can check the API layer finds bugs earlier and pinpoints them faster.</p>
{table(['Level', 'What is connected', 'A typical defect'],
       ['Component integration', 'Modules inside one application, such as the transfer module and the balance module', 'Balance not reduced after a transfer'],
       ['System integration', 'Our system and outside systems: payment gateway, SMS provider, credit bureau, another bank', 'Payment succeeds at the gateway but our order still shows "pending"'],
       ['API testing', 'One service checked directly, without the screen', 'The API accepts a negative amount that the screen would block'])}
{grid(box('🧰 Tools a manual tester uses', 'Postman, Insomnia or Bruno to send requests by hand, the browser developer tools Network tab to watch the requests a page makes, and Swagger or OpenAPI pages that list every endpoint.'),
      box('🧪 What to check', 'Status codes (200, 400, 401, 403, 404, 500), the response fields and values, error messages, required and optional fields, and that the API enforces the same rules as the screen.'))}
{tip('The Network tab is the easiest start. Open it, do something on the page, and look at the request and response. You will often see that a field the screen hides is still sent, or that an error is swallowed silently. The Manual API Testing subject covers this in depth.')}
''', say(
        'Modern applications are built from services that talk through APIs. Component integration connects modules inside one application. System integration connects our system with outside systems such as a payment gateway. API testing checks one service directly, without the screen, using tools such as Postman or the browser Network tab, and verifies that the API enforces the same rules as the screen.',
        'आधुनिक applications services से बने हैं जो APIs से बात करती हैं। Component integration एक application के modules जोड़ता है। System integration हमारे system को payment gateway जैसे बाहरी systems से जोड़ता है। API testing एक service को screen के बिना, Postman या browser के Network tab से, सीधे जाँचती है और देखती है कि API वही rules लागू करे जो screen करती है।',
        'Applications services ಮತ್ತು APIs ಇಂದ. Component integration ಒಳಗಿನ modules, system integration ಹೊರಗಿನ systems. API testing Postman ಅಥವಾ Network tab ಇಂದ ನೇರವಾಗಿ, screen rules ಅದೇ ಆಗಿರಬೇಕು.',
        'Applications services ଓ APIs ରୁ। Component integration ଭିତର modules, system integration ବାହାର systems। API testing Postman କିମ୍ବା Network tab ରୁ ସିଧା, screen rules ସମାନ ହେବା ଉଚିତ।',
        'تبنى التطبيقات الحديثة من خدمات تتحدث عبر واجهات برمجية. التكامل بين المكونات يربط الوحدات داخل تطبيق واحد. وتكامل الأنظمة يربط نظامنا بأنظمة خارجية مثل بوابة الدفع. واختبار الواجهات البرمجية يفحص خدمة مباشرة دون الشاشة، بأدوات مثل Postman أو تبويب الشبكة في المتصفح، ويتحقق من أنها تطبق قواعد الشاشة نفسها.',
        'Moderne Anwendungen bestehen aus Diensten, die über APIs sprechen. Komponentenintegration verbindet Module innerhalb einer Anwendung, Systemintegration verbindet unser System mit externen Systemen wie einem Zahlungsdienst. API-Tests prüfen einen Dienst direkt ohne Oberfläche, etwa mit Postman oder dem Netzwerk-Tab, und ob die API dieselben Regeln durchsetzt wie die Oberfläche.')),
]

QUIZ = [
    Qz('e', 'Transferring a negative amount to check that it is refused is an example of...', ['Positive testing', 'Negative testing', 'Load testing', 'Smoke testing'], 1, 'Invalid input on purpose.', 'Negative testing checks that invalid input is refused safely with a clear message.'),
    Qz('m', 'Which test follows sign up, adding money, paying a bill and receiving the SMS?', ['Unit testing', 'Gorilla testing', 'End to end testing', 'Sanity testing'], 2, 'One complete journey.', 'End to end testing covers a full user journey across all connected systems.'),
    Qz('h', 'The screen blocks negative amounts, but the API accepts -500. What is true?', ['No bug, the screen blocks it', 'A real defect, because anyone can call the API directly', 'Only a UI issue', 'A performance problem'], 1, 'Rules must live on the server.', 'Validation only in the screen is easy to bypass. The API must enforce the same rules.'),
    Qz('x', 'Payment succeeds at the gateway but our order still shows "pending" forever. Which level most likely finds it?', ['Unit testing', 'Component integration testing', 'System integration testing', 'Usability testing'], 2, 'Our system and an outside system.', 'The defect is in the hand off between our system and the external payment gateway.'),
]

CALC = [
    Calc('e', 'A field has 1 valid class and 5 invalid classes. One test per class: how many negative tests is that?', '5', '5', 'Each invalid class needs a negative test.', [eq('5') + ' negative tests, plus 1 positive test']),
]

DG = {
    "e2e": {"t": "One end to end journey crosses many systems", "w": 880, "h": 250,
        "n": [["u", 10, 70, 100, 120, "Customer", {"c": 3, "sh": "actor"}],
              ["app", 150, 90, 130, 70, "Mobile app", {"c": 2, "sh": "screen"}],
              ["api", 330, 90, 130, 70, "Bank API", {"c": 0, "ic": "🔌"}],
              ["db", 510, 20, 120, 70, "Database", {"c": 5, "sh": "db"}],
              ["pg", 510, 160, 120, 70, "Biller system", {"c": 7, "ic": "🧾", "sub": "outside"}],
              ["sms", 720, 90, 150, 70, "SMS provider", {"c": 4, "ic": "📩", "sub": "outside"}]],
        "e": [["u", "app", {}], ["app", "api", {"t": "pay bill"}], ["api", "db", {"t": "debit"}], ["api", "pg", {"t": "pay"}], ["api", "sms", {"t": "notify", "tx": 600, "ty": 125}]],
        "st": [[["u", "app", "u>app"], "The customer pays an electricity bill in the mobile app."],
               [["api", "app>api"], "The app calls the bank's API. A component or API test would stop here."],
               [["db", "api>db"], "The API debits the account in the database."],
               [["pg", "api>pg"], "It pays the outside biller system. This is system integration."],
               [["sms", "api>sms"], "Finally an SMS goes out. An end to end test checks the whole chain: the balance, the biller receipt and the SMS text."]]},
}
