from kit import *

FILE = 'specialised-testing.html'
SLUG, TOPIC, PREFIX = 'mt-specialised', 'specialised', 'mtx'
TITLE = 'Security, Accessibility, Localization and Mobile Testing'
CRUMB = 'Security, accessibility, localization and mobile'
MODULE = '🚀 Regression and non functional testing'
EMOJI = '🛡️'
DESCRIPTION = 'The specialised checks every manual tester is now expected to know: security basics and the OWASP Top 10 2025, accessibility with WCAG 2.2 and the European Accessibility Act, globalization and localization, mobile app testing, and privacy testing.'
LEAD = 'A login page can work perfectly and still let a stranger read your bank statement. A shop can sell well and still lock out a blind customer. This page covers the checks that protect people: security, accessibility, other languages and countries, mobile phones, and privacy.'
PREV = ('non-functional-testing.html', 'non-functional', '⚡ Non-functional Testing')
NEXT = ('test-plan.html', 'test-plan', '🗓️ The Test Plan')

TOP_SAY = say(
    'Welcome. This chapter covers the checks that protect people: security, accessibility, other languages and countries, mobile phones and privacy. Each one has a hands on lab, so try them as you read.',
    'स्वागत है। यह chapter उन checks के बारे में है जो लोगों की रक्षा करते हैं: security, accessibility, दूसरी भाषाएँ और देश, mobile phones और privacy। हर एक का hands on lab है, पढ़ते हुए आज़माइए।',
    'ಸ್ವಾಗತ. ಈ chapter ಜನರನ್ನು ರಕ್ಷಿಸುವ checks ಬಗ್ಗೆ: security, accessibility, ಬೇರೆ ಭಾಷೆ ಮತ್ತು ದೇಶಗಳು, mobile ಮತ್ತು privacy. ಪ್ರತಿಯೊಂದಕ್ಕೂ lab ಇದೆ.',
    'ସ୍ୱାଗତ। ଏହି chapter ଲୋକଙ୍କୁ ସୁରକ୍ଷା ଦେଉଥିବା checks ବିଷୟରେ: security, accessibility, ଅନ୍ୟ ଭାଷା ଓ ଦେଶ, mobile ଓ privacy। ପ୍ରତ୍ୟେକର lab ଅଛି।',
    'مرحبًا. يغطي هذا الفصل الفحوص التي تحمي الناس: الأمان وإمكانية الوصول واللغات والبلدان الأخرى والهواتف والخصوصية. لكل منها مختبر تفاعلي، فجربه أثناء القراءة.',
    'Willkommen. Dieses Kapitel behandelt Prüfungen, die Menschen schützen: Sicherheit, Barrierefreiheit, andere Sprachen und Länder, Mobilgeräte und Datenschutz. Zu jedem gibt es ein Labor zum Ausprobieren.')

SECTIONS = [
    sec('security', '🔐', 'Security testing: what it protects', f'''
<p><b>Security testing checks that the application protects its data and its users from people who want to misuse it.</b> A functional tester asks "does it work for the right user?" A security tester also asks "what happens when the wrong user tries?"</p>
<p>Security rests on three ideas, often called the <b>CIA triad</b>:</p>
{grid(box('🤫 Confidentiality', 'Only the right people can see the data. Asha must never see Ravi\'s bank statement.'),
      box('🧱 Integrity', 'Data cannot be changed by someone who should not change it. Nobody can edit the amount after a transfer is approved.'),
      box('🟢 Availability', 'The service is there when users need it. A flood of fake requests must not take the site down on salary day.'),
      box('🪪 Authentication and authorisation', 'Authentication asks "who are you?" (login, OTP, fingerprint). Authorisation asks "what are you allowed to do?" (only your own accounts, only admins can delete).'))}
{flow('authflow')}
{warn('Only test security on systems you have written permission to test, and only on test environments. Trying these checks on a real website you do not own can be a crime, even with good intentions.')}
''', say(
        'Security testing checks that the application protects its data and users from people who want to misuse it. It rests on confidentiality, integrity and availability. Authentication asks who you are. Authorisation asks what you are allowed to do. Only ever test security with written permission and on test environments.',
        'Security testing जाँचती है कि application अपने data और users को गलत इस्तेमाल करने वालों से बचाता है। इसकी नींव confidentiality, integrity और availability है। Authentication पूछता है आप कौन हैं। Authorisation पूछता है आपको क्या करने की अनुमति है। Security testing हमेशा लिखित अनुमति से और test environment पर ही करें।',
        'Security testing application data ಮತ್ತು users ಅನ್ನು ದುರುಪಯೋಗದಿಂದ ರಕ್ಷಿಸುತ್ತದೆಯೇ ಎಂದು ನೋಡುತ್ತದೆ. ಆಧಾರ confidentiality, integrity, availability. Authentication ನೀವು ಯಾರು, authorisation ನಿಮಗೆ ಏನು ಅನುಮತಿ. ಲಿಖಿತ ಅನುಮತಿ ಮತ್ತು test environment ನಲ್ಲಿ ಮಾತ್ರ.',
        'Security testing ଦେଖେ application data ଓ users କୁ ଅପବ୍ୟବହାରରୁ ରକ୍ଷା କରେ କି। ମୂଳ confidentiality, integrity, availability। Authentication ଆପଣ କିଏ, authorisation ଆପଣଙ୍କୁ କଣ ଅନୁମତି। ଲିଖିତ ଅନୁମତି ଓ test environment ରେ ହିଁ।',
        'يتحقق اختبار الأمان من أن التطبيق يحمي بياناته ومستخدميه ممن يريد إساءة استخدامه. ويقوم على السرية والسلامة والتوافر. المصادقة تسأل من أنت، والتفويض يسأل ماذا يسمح لك أن تفعل. لا تختبر الأمان إلا بإذن مكتوب وفي بيئات الاختبار.',
        'Sicherheitstests prüfen, ob die Anwendung Daten und Nutzer vor Missbrauch schützt. Grundlage sind Vertraulichkeit, Integrität und Verfügbarkeit. Authentifizierung fragt, wer du bist, Autorisierung, was du darfst. Teste Sicherheit nur mit schriftlicher Erlaubnis und nur auf Testumgebungen.')),

    sec('owasp', '🔟', 'The OWASP Top 10 (2025) for testers', f'''
<p>OWASP, the Open Worldwide Application Security Project, publishes a list of the ten most serious risks for web applications, based on data from thousands of real applications. The newest edition is the <b>OWASP Top 10:2025</b>. Every tester should know it, because each item suggests checks you can do by hand.</p>
{table(['Rank', 'Risk', 'What a manual tester can try'],
       ['A01', 'Broken Access Control', 'Change an id in the address or request and see if another user\'s data appears. Open an admin page as a normal user.'],
       ['A02', 'Security Misconfiguration', 'Look for default passwords, detailed error pages with stack traces, open directory listings, test pages left in production.'],
       ['A03', 'Software Supply Chain Failures (new)', 'Ask whether third party libraries are scanned and kept up to date. Check that the app loads scripts only from trusted places.'],
       ['A04', 'Cryptographic Failures', 'Confirm HTTPS everywhere, and that passwords and card numbers never appear in URLs, logs, emails or screenshots.'],
       ['A05', 'Injection', 'Type special characters such as a single quote, &lt;script&gt; or ../ into fields and check the app treats them as plain text.'],
       ['A06', 'Insecure Design', 'Look for missing limits in the business flow: unlimited OTP attempts, a coupon that can be reused forever.'],
       ['A07', 'Authentication Failures', 'Check lockout after wrong passwords, session timeout, logout really ending the session, and strong password rules.'],
       ['A08', 'Software or Data Integrity Failures', 'Check that a price or role sent from the browser cannot be changed to buy for ₹1 or become admin.'],
       ['A09', 'Security Logging and Alerting Failures', 'Confirm that failed logins and suspicious actions are logged and that someone is alerted.'],
       ['A10', 'Mishandling of Exceptional Conditions (new)', 'Cut the network mid payment, send empty or huge values, and check the app fails safely without leaking details.'])}
{viz('idor')}
{tip('Broken access control has been number one since 2021. The test is simple: log in as user A, copy a link that belongs to user B, and open it. A tester who does this on every page with an id finds real, critical bugs.')}
''', say(
        'OWASP publishes the ten most serious risks for web applications. The 2025 list starts with broken access control, then security misconfiguration and the new software supply chain failures. Many items suggest simple manual checks, such as changing an id in the address bar to see if another user\'s data appears. Try it in the lab.',
        'OWASP web applications के दस सबसे गंभीर risks प्रकाशित करता है। 2025 की list broken access control से शुरू होती है, फिर security misconfiguration और नया software supply chain failures। कई items से आसान manual checks बनते हैं, जैसे address bar में id बदलकर देखना कि दूसरे user का data दिखता है या नहीं। Lab में आज़माइए।',
        'OWASP web applications ನ ಹತ್ತು ಗಂಭೀರ risks ಪ್ರಕಟಿಸುತ್ತದೆ. 2025 list broken access control ನಿಂದ ಆರಂಭ, ನಂತರ security misconfiguration ಮತ್ತು ಹೊಸ supply chain failures. Address bar ನಲ್ಲಿ id ಬದಲಿಸಿ ಬೇರೆ user data ಕಾಣುತ್ತದೆಯೇ ನೋಡಿ.',
        'OWASP web applications ର ଦଶଟି ଗମ୍ଭୀର risks ପ୍ରକାଶ କରେ। 2025 list broken access control ରୁ ଆରମ୍ଭ, ତାପରେ security misconfiguration ଓ ନୂଆ supply chain failures। Address bar ରେ id ବଦଳାଇ ଅନ୍ୟ user data ଦେଖାଯାଏ କି ଦେଖନ୍ତୁ।',
        'تنشر OWASP أخطر عشرة مخاطر لتطبيقات الويب. تبدأ قائمة 2025 بضعف التحكم في الوصول، ثم سوء التهيئة الأمنية، ثم الجديد إخفاقات سلسلة توريد البرمجيات. كثير من البنود يقترح فحوصًا يدوية بسيطة، مثل تغيير الرقم في شريط العنوان لمعرفة هل تظهر بيانات مستخدم آخر.',
        'OWASP veröffentlicht die zehn gravierendsten Risiken für Webanwendungen. Die Liste 2025 beginnt mit fehlerhafter Zugriffskontrolle, dann Sicherheitsfehlkonfiguration und neu Fehler in der Software-Lieferkette. Viele Punkte ergeben einfache manuelle Prüfungen, etwa eine ID in der Adresszeile zu ändern. Probiere es im Labor.')),

    sec('a11y', '♿', 'Accessibility: software for everyone', f'''
<p><b>Accessibility testing checks that people with disabilities can use the product.</b> That includes people who are blind or have low vision, are deaf, cannot use a mouse, have tremors, dyslexia or memory problems. The World Health Organization estimates that about 1.3 billion people, around one in six, live with a significant disability.</p>
<p>Accessibility also helps everyone in some moment: a broken arm (temporary), bright sunlight on a phone or a noisy train (situational), or simply growing older.</p>
{table(['WCAG principle', 'Meaning', 'Example check'],
       ['Perceivable', 'Users can see or hear the content in some way', 'Images have alt text, videos have captions, text has enough contrast'],
       ['Operable', 'Users can use every control', 'Everything works with the keyboard alone, nothing flashes more than three times a second'],
       ['Understandable', 'Users can understand the content and how it behaves', 'Form errors say what is wrong and how to fix it, labels are clear'],
       ['Robust', 'It works with assistive technology', 'Buttons are real buttons, so screen readers announce them correctly'])}
<p>The rules come from <b>WCAG</b>, the Web Content Accessibility Guidelines from the W3C. Version <b>2.2</b> was published in October 2023 and added checks such as focus not being hidden, a minimum size for touch targets and not forcing people to solve puzzles to log in. Each rule has a level: <b>A</b> (minimum), <b>AA</b> (the usual legal target) and <b>AAA</b> (the highest).</p>
{grid(box('🇪🇺 European Accessibility Act', 'Applies since 28 June 2025 to many products and services sold in the EU, such as online shops, banking, e-books and transport tickets.'),
      box('🇺🇸 ADA and Section 508', 'US laws used in many court cases about inaccessible websites and apps.'),
      box('🇮🇳 RPwD Act 2016 and GIGW', 'India\'s Rights of Persons with Disabilities Act and the government website guidelines require accessible public services.'),
      box('🏢 Company policy', 'Many companies now set WCAG 2.2 level AA as an exit criterion before release.'))}
{viz('srsim')}
''', say(
        'Accessibility testing checks that people with disabilities can use the product, such as people who are blind, deaf, or cannot use a mouse. About one in six people live with a significant disability. The rules come from WCAG, whose four principles are perceivable, operable, understandable and robust. Version 2.2 is current, level AA is the usual target, and laws like the European Accessibility Act now require it.',
        'Accessibility testing जाँचती है कि disability वाले लोग product इस्तेमाल कर सकें, जैसे जो देख नहीं सकते, सुन नहीं सकते या mouse नहीं चला सकते। लगभग छह में से एक व्यक्ति के साथ ऐसी disability है। Rules WCAG से आते हैं: perceivable, operable, understandable और robust। Version 2.2 मौजूदा है, level AA आम लक्ष्य है, और European Accessibility Act जैसे कानून इसे ज़रूरी बनाते हैं।',
        'Accessibility testing disability ಇರುವವರು product ಬಳಸಬಲ್ಲರೇ ಎಂದು ನೋಡುತ್ತದೆ. ಸುಮಾರು ಆರರಲ್ಲಿ ಒಬ್ಬರು. Rules WCAG ಇಂದ: perceivable, operable, understandable, robust. Version 2.2, level AA ಸಾಮಾನ್ಯ ಗುರಿ, European Accessibility Act ನಂತಹ ಕಾನೂನುಗಳು ಕಡ್ಡಾಯ ಮಾಡುತ್ತವೆ.',
        'Accessibility testing disability ଥିବା ଲୋକେ product ବ୍ୟବହାର କରିପାରନ୍ତି କି ଦେଖେ। ପ୍ରାୟ ଛଅରେ ଜଣେ। Rules WCAG ରୁ: perceivable, operable, understandable, robust। Version 2.2, level AA ସାଧାରଣ ଲକ୍ଷ୍ୟ, European Accessibility Act ଭଳି ଆଇନ ବାଧ୍ୟତାମୂଳକ କରେ।',
        'يتحقق اختبار إمكانية الوصول من أن ذوي الإعاقة يستطيعون استخدام المنتج، مثل المكفوفين والصم ومن لا يستطيع استخدام الفأرة. نحو شخص من كل ستة يعيش بإعاقة كبيرة. القواعد من إرشادات WCAG ومبادئها الأربعة: قابل للإدراك، قابل للتشغيل، مفهوم، ومتين. الإصدار الحالي 2.2، والمستوى AA هو الهدف المعتاد، وقوانين مثل قانون الإتاحة الأوروبي تفرضه.',
        'Barrierefreiheitstests prüfen, ob Menschen mit Behinderung das Produkt nutzen können, etwa blinde oder gehörlose Menschen oder solche ohne Maus. Etwa jeder Sechste lebt mit einer erheblichen Behinderung. Die Regeln stammen aus den WCAG mit den Prinzipien wahrnehmbar, bedienbar, verständlich und robust. Aktuell ist Version 2.2, Ziel meist Stufe AA, und Gesetze wie der European Accessibility Act verlangen es.')),

    sec('a11y-how', '⌨️', 'How to test accessibility by hand', f'''
<p>Automated tools such as axe, Lighthouse and WAVE are a good first step, but they catch only part of the problems. They can see that an image has no alt text. They cannot tell that the alt text "image123" is useless. A manual pass is always needed.</p>
{table(['Check', 'How to do it', 'What a failure looks like'],
       ['Keyboard only', 'Put the mouse away. Use Tab, Shift+Tab, Enter, Space and the arrow keys', 'A control you cannot reach, a menu you cannot close, focus that jumps around'],
       ['Visible focus', 'Watch the focus outline as you Tab', 'You cannot see where you are on the page'],
       ['Screen reader', 'NVDA or JAWS on Windows, VoiceOver on Mac and iPhone, TalkBack on Android', 'Unlabelled buttons, images read as file names, errors never announced'],
       ['Zoom and reflow', 'Zoom the browser to 200% and 400%, or use a 320 pixel wide window', 'Text cut off, overlapping boxes, sideways scrolling'],
       ['Colour and contrast', 'Use a contrast checker, and check that colour is never the only signal', 'Light grey text, errors shown only in red'],
       ['Media', 'Play videos and audio', 'No captions or transcript, video that plays sound automatically'],
       ['Forms and errors', 'Submit with mistakes', 'Error not tied to the field, or only a red border with no text'],
       ['Touch targets', 'Tap small icons on a phone', 'Targets so small that you hit the wrong one (WCAG 2.2 asks for at least 24 by 24 CSS pixels)'])}
<p>Contrast has an exact formula. Each colour gets a relative luminance L between 0 (black) and 1 (white), and the ratio is worked out like this:</p>
{eq(f'contrast ratio = {fr("L<sub>light</sub> + 0.05", "L<sub>dark</sub> + 0.05")}')}
<p>Normal text needs at least <b>4.5 : 1</b> for level AA, and large text needs <b>3 : 1</b>.</p>
{viz('contrast')}
{deep('the easiest high value accessibility test', '<p>Spend five minutes on any form with the keyboard only. Can you reach every field in a sensible order? Can you see the focus? Can you submit with Enter? Can you read every error? This single test finds blockers in a surprising number of real products, and it needs no tool at all.</p>')}
''', say(
        'Automatic tools find only part of the accessibility problems, so manual checks are needed. Use the keyboard only, watch the focus, listen with a screen reader such as NVDA, VoiceOver or TalkBack, zoom to 200 and 400 percent, check colour contrast, captions, form errors and touch target size. Normal text needs a contrast ratio of at least 4.5 to 1.',
        'Automatic tools accessibility की केवल कुछ समस्याएँ पकड़ते हैं, इसलिए manual checks ज़रूरी हैं। सिर्फ़ keyboard इस्तेमाल करें, focus देखें, NVDA, VoiceOver या TalkBack जैसे screen reader से सुनें, 200 और 400 percent zoom करें, colour contrast, captions, form errors और touch target size जाँचें। Normal text को कम से कम 4.5 से 1 contrast चाहिए।',
        'Tools ಕೆಲವು ಸಮಸ್ಯೆಗಳನ್ನು ಮಾತ್ರ ಹಿಡಿಯುತ್ತವೆ, manual checks ಬೇಕು. Keyboard ಮಾತ್ರ, focus ನೋಡಿ, NVDA, VoiceOver ಅಥವಾ TalkBack ಕೇಳಿ, 200 ಮತ್ತು 400 percent zoom, contrast, captions, form errors, touch targets. Normal text ಗೆ 4.5 to 1 contrast.',
        'Tools କିଛି ସମସ୍ୟା ହିଁ ଧରନ୍ତି, manual checks ଦରକାର। କେବଳ keyboard, focus ଦେଖନ୍ତୁ, NVDA, VoiceOver କିମ୍ବା TalkBack ଶୁଣନ୍ତୁ, 200 ଓ 400 percent zoom, contrast, captions, form errors, touch targets। Normal text ପାଇଁ 4.5 to 1 contrast।',
        'تكتشف الأدوات الآلية جزءًا فقط من مشكلات الإتاحة، لذا يلزم الفحص اليدوي. استخدم لوحة المفاتيح وحدها، وراقب التركيز، واستمع بقارئ شاشة مثل NVDA أو VoiceOver أو TalkBack، وكبر إلى 200 و400 بالمئة، وافحص التباين والترجمة النصية وأخطاء النماذج وحجم أهداف اللمس. النص العادي يحتاج تباينًا لا يقل عن 4.5 إلى 1.',
        'Automatische Werkzeuge finden nur einen Teil der Barrieren, deshalb braucht es manuelle Prüfungen. Nur Tastatur benutzen, den Fokus beobachten, mit einem Screenreader wie NVDA, VoiceOver oder TalkBack hören, auf 200 und 400 Prozent zoomen, Kontrast, Untertitel, Formularfehler und Zielgrößen prüfen. Normaler Text braucht mindestens 4,5 zu 1 Kontrast.')),

    sec('l10n', '🌍', 'Globalization: one product, many countries', f'''
<p>When a product is sold in many countries, two jobs appear:</p>
{grid(box('🧰 Internationalization (i18n)', 'Building the product so it <b>can</b> support any language and region: no text hard coded in the program, Unicode everywhere, layouts that can grow and flip. Tested once, by the core team.'),
      box('🗺️ Localization (l10n)', 'Adapting the product <b>for one</b> place: translated text, local date, number and currency formats, local laws, images and colours that suit the culture. Tested for every new language.'))}
<p>(The numbers in i18n and l10n count the letters between the first and the last letter.) Globalization testing is the whole effort. These are the checks that find real bugs:</p>
{table(['Area', 'What changes between countries', 'A typical bug'],
       ['Dates', '04/03/2026 is 4 March in India and the UK, 3 April in the US', 'A delivery date that is a month wrong'],
       ['Numbers', '1,234,567.5 in the US, 12,34,567.5 in India, 1.234.567,5 in Germany', 'Price parsed as 1.2 instead of 1,200'],
       ['Currency', 'Symbol, position and decimals. The yen has no decimals', '¥1,500.00 shown for Japan'],
       ['Text length', 'German and Finnish text is often 30% or more longer than English', 'A cut off button, labels wrapping over each other'],
       ['Direction', 'Arabic and Hebrew read right to left', 'Arrows pointing the wrong way, mixed numbers in the wrong order'],
       ['Characters', 'Accents, Devanagari, Chinese, emoji', 'Names saved as ??? or boxes, search not finding "José"'],
       ['Sorting', 'Alphabet order differs per language', 'Ä sorted after Z in a German list'],
       ['Time zones', 'IST is UTC + 5:30, many countries change clocks for summer', 'An offer that ends at the wrong hour, a meeting on the wrong day'],
       ['Culture and law', 'Colours, icons, address formats, tax and privacy rules', 'A PIN code field that rejects a UK postcode'])}
{viz('locale')}
{tip('Pseudo localization is a clever early test. Before real translators start, every text is replaced by a longer accented version such as [Ƥȧȧẏ ƞǿǿẇ !!!]. Hard coded text stays plain English and stands out at once, and too small boxes cut the extra length.')}
''', say(
        'Internationalization builds a product so it can support any language and region. Localization adapts it for one place: translated text, local dates, numbers and currency, laws and culture. Testers check date and number formats, currency, text that grows by thirty percent or more, right to left languages, special characters, sorting and time zones. Pseudo localization finds hard coded text early.',
        'Internationalization product को ऐसा बनाता है कि वह कोई भी भाषा और region support कर सके। Localization उसे एक जगह के लिए ढालता है: translated text, local dates, numbers, currency, कानून और संस्कृति। Testers date और number formats, currency, तीस percent या अधिक बढ़ता text, right to left भाषाएँ, special characters, sorting और time zones जाँचते हैं। Pseudo localization hard coded text जल्दी पकड़ता है।',
        'Internationalization ಯಾವುದೇ ಭಾಷೆ ಮತ್ತು region support ಮಾಡುವಂತೆ ಕಟ್ಟುವುದು. Localization ಒಂದು ಜಾಗಕ್ಕೆ ಹೊಂದಿಸುವುದು. Date, number, currency formats, ಮೂವತ್ತು percent ಬೆಳೆಯುವ text, right to left, characters, sorting, time zones ಪರೀಕ್ಷಿಸಿ.',
        'Internationalization ଯେକୌଣସି ଭାଷା ଓ region support କରିବା ପାଇଁ ତିଆରି। Localization ଗୋଟିଏ ସ୍ଥାନ ପାଇଁ ଖାପ ଖୁଆଇବା। Date, number, currency formats, ତିରିଶ percent ବଢ଼ୁଥିବା text, right to left, characters, sorting, time zones ଯାଞ୍ଚ କରନ୍ତୁ।',
        'التدويل يبني المنتج ليدعم أي لغة ومنطقة. والتوطين يكيفه لمكان واحد: نص مترجم وتواريخ وأرقام وعملة محلية وقوانين وثقافة. يفحص المختبرون صيغ التاريخ والأرقام والعملة والنص الذي يطول بثلاثين بالمئة أو أكثر واللغات من اليمين إلى اليسار والحروف الخاصة والترتيب والمناطق الزمنية.',
        'Internationalisierung baut ein Produkt so, dass es jede Sprache und Region unterstützen kann. Lokalisierung passt es an einen Ort an: übersetzter Text, lokale Datums-, Zahlen- und Währungsformate, Gesetze und Kultur. Tester prüfen Formate, Texte, die um dreißig Prozent oder mehr wachsen, Rechts-nach-links-Sprachen, Sonderzeichen, Sortierung und Zeitzonen.')),

    sec('mobile', '📱', 'Mobile app testing', f'''
<p>A phone is not a small computer. It moves between networks, runs on a battery, gets calls in the middle of a task, and comes in thousands of models. Mobile testing adds these questions to normal functional testing.</p>
{table(['App type', 'What it is', 'Example', 'Testing focus'],
       ['Native', 'Built for one platform with its own language and tools (Swift or Kotlin)', 'Camera, banking apps', 'Device features, OS versions, app store rules'],
       ['Mobile web', 'A website opened in the phone browser', 'm.site.com', 'Browsers, screen sizes, touch, network'],
       ['Hybrid and cross platform', 'One code base wrapped for both platforms (Flutter, React Native)', 'Many shopping apps', 'Both platforms, plugins, behaviour differences'])}
{grid(box('📲 Devices', 'Thousands of Android models and several iPhone generations. Pick devices from user analytics, then use cloud device farms such as BrowserStack, Sauce Labs or Firebase Test Lab for wider coverage.'),
      box('🧪 Emulators and real devices', 'Emulators (Android) and simulators (iOS) are fast and free for early checks. Real devices are needed for camera, battery, touch feel, sensors and real network behaviour.'),
      box('👆 Gestures and orientation', 'Tap, double tap, long press, swipe, pinch, rotate. Data must survive a rotation.'),
      box('📶 Network', 'Wi-Fi to 4G to 5G, weak signal, airplane mode, switching networks in the middle of an upload.'),
      box('🔑 Permissions', 'Camera, location, contacts, notifications. Test "allow", "deny", "allow once" and changing your mind later in settings.'),
      box('🔋 Resources', 'Battery drain, memory, storage full, app size, low end phones with little RAM.'),
      box('🏪 Install and update', 'Fresh install, update from the old version with data kept, uninstall, reinstall, app store review rules.'),
      box('🔔 Interruptions', 'Calls, messages, alarms, low battery, notifications, the app sent to the background.'))}
{viz('mobileint')}
''', say(
        'Mobile testing adds new questions to functional testing. Apps can be native, mobile web or hybrid. Testers choose devices from user data and use emulators early and real devices for camera, battery, touch and network behaviour. They test gestures, rotation, weak and switching networks, permissions, battery and memory, installs and updates, and interruptions like calls and notifications.',
        'Mobile testing functional testing में नए सवाल जोड़ती है। Apps native, mobile web या hybrid हो सकते हैं। Testers user data से devices चुनते हैं, शुरुआत में emulators और camera, battery, touch और network के लिए real devices इस्तेमाल करते हैं। वे gestures, rotation, कमज़ोर और बदलते network, permissions, battery, memory, install और update, और calls व notifications जैसे interruptions test करते हैं।',
        'Mobile testing ಹೊಸ ಪ್ರಶ್ನೆಗಳನ್ನು ಸೇರಿಸುತ್ತದೆ. Native, mobile web, hybrid apps. User data ಇಂದ devices, ಮೊದಲು emulators, camera, battery, network ಗೆ real devices. Gestures, rotation, network, permissions, battery, install, update, calls ಮತ್ತು notifications interruptions.',
        'Mobile testing ନୂଆ ପ୍ରଶ୍ନ ଯୋଡ଼େ। Native, mobile web, hybrid apps। User data ରୁ devices, ପ୍ରଥମେ emulators, camera, battery, network ପାଇଁ real devices। Gestures, rotation, network, permissions, battery, install, update, calls ଓ notifications interruptions।',
        'يضيف اختبار تطبيقات الهاتف أسئلة جديدة. التطبيقات قد تكون أصلية أو ويب للجوال أو هجينة. يختار المختبرون الأجهزة من بيانات المستخدمين، ويستعملون المحاكيات مبكرًا والأجهزة الحقيقية للكاميرا والبطارية واللمس والشبكة. ويختبرون الإيماءات والتدوير والشبكات الضعيفة والأذونات والبطارية والتثبيت والتحديث والمقاطعات مثل المكالمات.',
        'Mobiles Testen ergänzt neue Fragen. Apps sind nativ, mobiles Web oder hybrid. Tester wählen Geräte nach Nutzerdaten, nutzen früh Emulatoren und echte Geräte für Kamera, Akku, Touch und Netz. Sie testen Gesten, Drehung, schwache und wechselnde Netze, Berechtigungen, Akku und Speicher, Installation und Update sowie Unterbrechungen wie Anrufe.')),

    sec('privacy', '🔏', 'Privacy and data protection testing', f'''
<p>Laws now give people rights over their personal data, and products must prove they respect them. Testers check these rights like any other requirement.</p>
{table(['Law', 'Where', 'Since'],
       ['GDPR (General Data Protection Regulation)', 'European Union', '2018'],
       ['DPDP Act (Digital Personal Data Protection Act)', 'India', 'Passed 2023, rules notified November 2025 and phased in over 12 to 18 months'],
       ['CCPA and CPRA', 'California, USA', '2020 and 2023'],
       ['HIPAA', 'US health data', '1996, updated since'])}
{table(['Privacy requirement', 'How a tester checks it'],
       ['Consent', 'Optional cookies and marketing are off until the user agrees. "Reject all" is as easy as "Accept all".'],
       ['Purpose and minimum data', 'The form asks only for what the feature needs. A newsletter does not need a date of birth.'],
       ['Right to access', 'A user can download a copy of their data, and it is complete.'],
       ['Right to erasure', 'After "Delete my account", the data is gone from the screens, search, exports and emails, as the policy says.'],
       ['No leaks', 'Personal data never appears in URLs, logs, analytics, error messages or screenshots attached to bug reports.'],
       ['Test data', 'Testers never use real customer data without masking. See the test data part of the environments chapter.'])}
{rule('Treat personal data in your own bug reports with the same care. Blur names, phone numbers and card numbers in every screenshot you attach.')}
''', say(
        'Privacy laws such as GDPR in Europe and the DPDP Act in India give people rights over their data. Testers check consent, collecting only the data that is needed, the right to download and delete data, and that personal data never leaks into URLs, logs or screenshots. Blur personal data in your own bug reports too.',
        'Europe का GDPR और India का DPDP Act जैसे privacy कानून लोगों को अपने data पर अधिकार देते हैं। Testers consent, सिर्फ़ ज़रूरी data लेना, data download और delete करने का अधिकार, और यह जाँचते हैं कि personal data URLs, logs या screenshots में न जाए। अपनी bug reports में भी personal data धुँधला करें।',
        'GDPR ಮತ್ತು India ದ DPDP Act ಜನರಿಗೆ data ಮೇಲೆ ಹಕ್ಕು ಕೊಡುತ್ತವೆ. Consent, ಅಗತ್ಯ data ಮಾತ್ರ, download ಮತ್ತು delete ಹಕ್ಕು, URLs, logs, screenshots ನಲ್ಲಿ leak ಇಲ್ಲ ಎಂದು ಪರೀಕ್ಷಿಸಿ.',
        'GDPR ଓ India ର DPDP Act ଲୋକଙ୍କୁ data ଉପରେ ଅଧିକାର ଦିଏ। Consent, ଦରକାରୀ data ହିଁ, download ଓ delete ଅଧିକାର, URLs, logs, screenshots ରେ leak ନାହିଁ ଯାଞ୍ଚ କରନ୍ତୁ।',
        'تمنح قوانين الخصوصية مثل GDPR في أوروبا وقانون DPDP في الهند الناس حقوقًا على بياناتهم. يفحص المختبرون الموافقة، وجمع البيانات الضرورية فقط، وحق تنزيل البيانات وحذفها، وعدم تسرب البيانات الشخصية إلى العناوين أو السجلات أو لقطات الشاشة. وموه البيانات الشخصية في تقارير الأخطاء أيضًا.',
        'Datenschutzgesetze wie die DSGVO in Europa und der DPDP Act in Indien geben Menschen Rechte an ihren Daten. Tester prüfen Einwilligung, Datensparsamkeit, das Recht auf Auskunft und Löschung und dass persönliche Daten nie in URLs, Logs oder Screenshots gelangen. Mach persönliche Daten auch in deinen eigenen Fehlerberichten unkenntlich.')),
]

INFO = {"title": "Four checks that protect people", "panels": [
    {"s": [["e", "🔐"], ["t", "/accounts/1043", {"b": 1}]], "h": "Security", "t": "Change one number and see what you can open.", "more": "Broken access control is number one on the OWASP Top 10."},
    {"s": [["e", "♿"], ["t", "Tab ⇥ Tab ⇥ Enter", {"b": 1}]], "h": "Accessibility", "t": "Use the page with the keyboard and a screen reader.", "more": "WCAG 2.2 level AA is the usual target."},
    {"s": [["e", "🌍"], ["t", "04/03 = 4 March or 3 April?", {"b": 1, "size": 12}]], "h": "Localization", "t": "Dates, money and text change per country.", "more": "German text is often 30% longer than English."},
    {"s": [["e", "📱"], ["t", "📞 call during payment", {"b": 1}]], "h": "Mobile", "t": "Phones get interrupted, rotate and lose signal.", "more": "Real devices for touch, battery and network."}],
    "remember": "A product is only done when it is safe, usable by everyone, correct in every country and steady on a real phone."}

REAL = [
    ["🏨", "A hotel key card", "Your card opens your room and not room 1043. A hotel that checks only \"is this a guest?\" and not \"which room?\" has broken access control."],
    ["🛗", "A ramp next to the stairs", "Built for wheelchair users, but used by parents with prams, delivery workers and travellers with suitcases. Accessible software helps far more people than expected."],
    ["🔌", "A travel adapter", "Your charger works at home but not in London without an adapter. Localization is the adapter that makes a product fit each country."]]

QUIZ = [
    Qz('e', 'Which item is number one on the OWASP Top 10:2025?', ['Injection', 'Broken Access Control', 'Cryptographic Failures', 'Security Misconfiguration'], 1, 'The same as in 2021.', 'Broken Access Control is A01 in both 2021 and 2025.'),
    Qz('e', 'Authentication answers which question?', ['What are you allowed to do?', 'Who are you?', 'Is the server up?', 'Is the data encrypted?'], 1, 'Login, OTP, fingerprint.', 'Authentication proves identity. Authorisation decides what that identity may do.'),
    Qz('e', 'What does WCAG stand for?', ['Web Content Accessibility Guidelines', 'World Computer Access Group', 'Web Code Analysis Guide', 'Wide Colour Accessibility Grade'], 0, 'It is from the W3C.', 'WCAG are the Web Content Accessibility Guidelines, currently version 2.2.'),
    Qz('e', 'Which minimum contrast ratio does normal text need for WCAG level AA?', ['2 : 1', '3 : 1', '4.5 : 1', '10 : 1'], 2, 'Large text needs less.', 'Normal text needs 4.5 : 1. Large text and interface parts need 3 : 1.'),
    Qz('m', 'Logged in as customer 1042, you change the address to /accounts/1043 and see another customer\'s statement. What is it?', ['A usability issue', 'Broken access control, a critical security bug', 'A localization bug', 'Expected behaviour'], 1, 'The server forgot to check whose account it is.', 'The server must check that the requested account belongs to the logged in user.'),
    Qz('m', 'What is the difference between internationalization and localization?', ['They are the same', 'i18n makes the product ready for any locale, l10n adapts it for one locale', 'l10n is done first', 'i18n is only translation'], 1, 'Ready for all, then fitted for one.', 'Internationalization prepares the code. Localization adds the translation and local formats for each market.'),
    Qz('m', 'Why can an automated accessibility scan not replace manual testing?', ['Tools are too slow', 'Tools can see that alt text exists but not whether it is meaningful', 'Tools need the source code', 'Tools work only on mobile'], 1, 'Think of alt="image123".', 'Tools check rules. People judge meaning, focus order and real usability with assistive technology.'),
    Qz('m', 'Which check belongs to mobile interruption testing?', ['Testing an incoming call during payment', 'Checking a date format', 'Checking contrast', 'Testing with 1,000 users'], 0, 'Interruptions come from outside the app.', 'Calls, notifications, low battery and network loss during a task are interruption tests.'),
    Qz('h', 'A German button reads "Jetzt bezahlen" and is cut to "Jetzt bez…". Which kind of bug is this?', ['Security', 'Localization (text expansion)', 'Performance', 'Access control'], 1, 'German text is often longer than English.', 'The layout was sized for English. Localization testing checks that every label fits in the longest language.'),
    Qz('h', 'Which practice best respects privacy when you attach a screenshot to a bug report?', ['Attach it as it is', 'Blur names, phone numbers and card numbers first', 'Send it by personal email', 'Store it on your desktop'], 1, 'Bug trackers are read by many people.', 'Personal data must be protected in test artefacts as well as in the product.'),
    Qz('x', 'Since when does the European Accessibility Act apply to many products and services in the EU?', ['1 January 2020', '28 June 2025', '5 October 2023', 'It is only a proposal'], 1, 'Mid 2025.', 'The European Accessibility Act applies from 28 June 2025.'),
    Qz('x', 'A tester sends a price of 1 instead of 49,999 from the browser and the order is accepted. Which OWASP 2025 category fits best?', ['A08 Software or Data Integrity Failures', 'A03 Software Supply Chain Failures', 'A09 Security Logging and Alerting Failures', 'A02 Security Misconfiguration'], 0, 'The server trusted data it should have checked.', 'The server must never trust a price sent by the client. That is a data integrity failure, and also a design flaw.'),
]

CALC = [
    Calc('e', 'A 4 digit PIN uses the digits 0 to 9. How many different PINs exist?', '10000', '10 ** 4', '10 choices for each of 4 places.', [eq('10<sup>4</sup> = 10,000')]),
    Calc('m', 'The account locks after 3 wrong PIN attempts. What percentage of all 4 digit PINs can an attacker try before the lock?', '0.03', '3 * 100 / 10000', 'Tries × 100 ÷ all PINs.', [eq(f'{fr("3 × 100", "10,000")} = 0.03%')], unit='%'),
    Calc('e', 'An English label has 20 characters. German text is about 30% longer. How many characters must the label fit?', '26', '20 * 1.3', 'Add 30%.', [eq('20 × 1.3 = 26')]),
    Calc('m', 'You test 3 Android versions, 4 screen sizes and 2 orientations. How many combinations is that?', '24', '3 * 4 * 2', 'Multiply the choices.', [eq('3 × 4 × 2 = 24')]),
    Calc('h', 'White has luminance 1.0 and a grey has luminance 0.18. What is the contrast ratio? Round to two decimals.', '4.57', '(1 + 0.05) / (0.18 + 0.05)', '(L1 + 0.05) ÷ (L2 + 0.05).', [eq(f'{fr("1 + 0.05", "0.18 + 0.05")} = {fr("1.05", "0.23")} ≈ 4.57'), 'That passes 4.5 : 1 for normal text, just barely.']),
    Calc('x', 'An offer ends at 23:30 IST. IST is UTC + 5:30. At what hour (UTC, 24 hour clock) does it end? Give the hour only.', '18', '(23 * 60 + 30 - 330) // 60', 'Subtract 5 hours 30 minutes.', [eq('23:30 − 5:30 = 18:00'), 'It ends at 18:00 UTC.']),
]

DG = {
    "authflow": {"t": "Where the security checks sit in a login", "w": 860, "h": 270,
        "n": [["user", 10, 90, 110, 120, "User", {"c": 3, "sh": "actor"}],
              ["form", 160, 100, 140, 70, "Login form", {"c": 2, "sh": "screen"}],
              ["srv", 350, 100, 140, 70, "Server", {"c": 0, "ic": "🖥️", "sub": "checks password"}],
              ["sess", 540, 100, 140, 70, "Session", {"c": 5, "ic": "🍪", "sub": "secure cookie"}],
              ["page", 720, 100, 130, 70, "My account", {"c": 1, "sh": "screen"}],
              ["n1", 160, 200, 140, 56, "Masked password,\nHTTPS only", {"sh": "note"}],
              ["n2", 350, 200, 140, 56, "Lockout after\nwrong attempts", {"sh": "note"}],
              ["n3", 540, 200, 140, 56, "Timeout, logout\nends it", {"sh": "note"}],
              ["n4", 720, 200, 130, 56, "Only my own\ndata (authz)", {"sh": "note"}],
              ["n0", 160, 14, 520, 50, "Every step must also fail safely, with no stack traces or hints", {"c": 6, "sh": "pill"}]],
        "e": [["user", "form", {}], ["form", "srv", {"t": "credentials", "tx": 325, "ty": 84}], ["srv", "sess", {"t": "who you are", "tx": 515, "ty": 84}], ["sess", "page", {"t": "what you may see", "tx": 700, "ty": 84}]],
        "st": [[["user", "form", "user>form", "n1"], "The user types a password. It must be masked on screen and sent only over HTTPS."],
               [["srv", "form>srv", "n2"], "The server checks the password. After a few wrong tries it locks the account or adds a delay, so nobody can guess forever."],
               [["sess", "srv>sess", "n3"], "Authentication succeeded, so a session starts. It must expire after inactivity, and logout must really end it."],
               [["page", "sess>page", "n4"], "Authorisation decides what this user may see. Only their own accounts, never someone else's."],
               [["n0"], "At every step, errors must be calm and vague, such as \"Invalid username or password\", never \"user exists, wrong password\"."]]},
}

X = {}
