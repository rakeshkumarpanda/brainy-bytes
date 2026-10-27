from kit import *

FILE = 'non-functional-testing.html'

SECTIONS = [
    sec('iso25010', '🏅', 'The quality model: ISO/IEC 25010:2023', f'''
<p>"Non functional" is a big bag. The international standard <b>ISO/IEC 25010</b> sorts product quality into named characteristics, and its 2023 edition updated the list. Teams use it as a checklist so that no kind of quality is forgotten in the test plan.</p>
{flow('iso')}
{table(['Characteristic', 'Question it asks', 'Example test'],
       ['Functional suitability', 'Does it do the right things, correctly and completely?', 'All functional testing'],
       ['Performance efficiency', 'Is it fast enough with the expected load and resources?', 'Load, stress and soak tests'],
       ['Compatibility', 'Does it work with other systems and on other platforms?', 'Browser and device testing, integrations'],
       ['Interaction capability (was usability)', 'Can people learn and use it, including people with disabilities?', 'Usability sessions, accessibility testing'],
       ['Reliability', 'Does it keep working, and recover from faults?', 'Soak, failover and recovery tests'],
       ['Security', 'Is data protected from people who should not access it?', 'Access control, injection, session tests'],
       ['Maintainability', 'Can it be changed easily and safely?', 'Code reviews, static analysis'],
       ['Flexibility (was portability)', 'Can it be moved, installed and scaled to new environments?', 'Installation, upgrade and scalability tests'],
       ['Safety (new in 2023)', 'Does it avoid putting people or property in danger?', 'Hazard analysis, fail safe tests in medical or car software'])}
{tip('Security, accessibility and localization are covered in depth in the chapter "Security, Accessibility, Localization and Mobile Testing".')}
''', say(
        'The ISO 25010 standard sorts product quality into named characteristics. The 2023 edition lists functional suitability, performance efficiency, compatibility, interaction capability which replaced usability, reliability, security, maintainability, flexibility which replaced portability, and the new characteristic safety. Teams use it as a checklist for the test plan.',
        'ISO 25010 standard product quality को नामित characteristics में बाँटता है। 2023 edition में functional suitability, performance efficiency, compatibility, interaction capability जो usability की जगह आई, reliability, security, maintainability, flexibility जो portability की जगह आई, और नई characteristic safety है। Teams इसे test plan की checklist की तरह इस्तेमाल करती हैं।',
        'ISO 25010 product quality ವಿಂಗಡಣೆ. 2023: functional suitability, performance, compatibility, interaction capability, reliability, security, maintainability, flexibility, ಹೊಸ safety. Test plan checklist.',
        'ISO 25010 product quality ବିଭାଜନ। 2023: functional suitability, performance, compatibility, interaction capability, reliability, security, maintainability, flexibility, ନୂଆ safety। Test plan checklist।',
        'يصنف معيار ISO 25010 جودة المنتج في خصائص مسماة. تضم طبعة 2023 الملاءمة الوظيفية، وكفاءة الأداء، والتوافق، وقدرة التفاعل التي حلت محل قابلية الاستخدام، والموثوقية، والأمان، وقابلية الصيانة، والمرونة التي حلت محل قابلية النقل، والخاصية الجديدة السلامة.',
        'Die Norm ISO 25010 ordnet Produktqualität in benannte Merkmale. Die Ausgabe 2023 nennt funktionale Eignung, Leistungseffizienz, Kompatibilität, Interaktionsfähigkeit statt Benutzbarkeit, Zuverlässigkeit, Sicherheit, Wartbarkeit, Flexibilität statt Übertragbarkeit und neu Sicherheit im Sinne von Safety. Teams nutzen sie als Checkliste für den Testplan.')),

    sec('reliability', '🛟', 'Reliability, recovery and installation testing', f'''
<p>Users forgive a slow day. They do not forgive lost money or lost data. These tests check that the product keeps working, and comes back safely when something breaks.</p>
{table(['Test', 'What it checks', 'Example'],
       ['Reliability', 'The system works without failure for a long time under normal use', 'Run normal traffic for 72 hours and count failures'],
       ['Recovery', 'After a crash, power cut or network loss, the system comes back with correct data', 'Pull the network cable during a transfer, then check both balances'],
       ['Failover', 'When one server dies, another takes over without users noticing', 'Switch off the main database node during a load test'],
       ['Backup and restore', 'Backups can really be restored, within the promised time', 'Restore last night\'s backup to a test server and compare records'],
       ['Installation', 'Fresh install, upgrade, repair and uninstall all work', 'Upgrade from version 3.2 to 4.0 and check that settings and data survive'],
       ['Disaster recovery', 'The service can move to another data centre or region', 'A planned drill moving all traffic to the backup region'])}
<p>Availability is often promised as "nines". Each extra nine cuts the allowed downtime by ten:</p>
{table(['Availability', 'Allowed downtime per year', 'Per month (30 days)'],
       ['99%', 'about 3.65 days', 'about 7.2 hours'],
       ['99.9%', 'about 8.76 hours', 'about 43 minutes'],
       ['99.99%', 'about 53 minutes', 'about 4.3 minutes'],
       ['99.999%', 'about 5.3 minutes', 'about 26 seconds'])}
<p>Two more numbers describe reliability. <b>MTBF</b>, the mean time between failures, should be long. <b>MTTR</b>, the mean time to repair or recover, should be short. Availability is close to:</p>
{eq(f'availability = {fr("MTBF", "MTBF + MTTR")}')}
''', say(
        'Reliability testing checks long failure free running. Recovery testing checks that the system comes back with correct data after a crash or network loss. Failover, backup and restore, installation and disaster recovery tests check the rest. Availability is promised in nines: 99.9 percent allows about 8.76 hours of downtime a year. Availability equals MTBF divided by MTBF plus MTTR.',
        'Reliability testing लंबे समय तक बिना failure चलना जाँचती है। Recovery testing देखती है कि crash या network जाने के बाद system सही data के साथ लौटे। Failover, backup और restore, installation और disaster recovery tests बाकी जाँचते हैं। Availability nines में वादा होती है: 99.9 percent में साल में लगभग 8.76 घंटे downtime। Availability बराबर MTBF भाग MTBF plus MTTR।',
        'Reliability ದೀರ್ಘ ಸಮಯ failure ಇಲ್ಲದೆ. Recovery crash ನಂತರ ಸರಿಯಾದ data. Failover, backup, installation, disaster recovery. 99.9 percent ವರ್ಷಕ್ಕೆ ಸುಮಾರು 8.76 ಗಂಟೆ. Availability = MTBF ÷ (MTBF + MTTR).',
        'Reliability ଲମ୍ବା ସମୟ failure ବିନା। Recovery crash ପରେ ଠିକ୍ data। Failover, backup, installation, disaster recovery। 99.9 percent ବର୍ଷକୁ ପ୍ରାୟ 8.76 ଘଣ୍ଟା। Availability = MTBF ÷ (MTBF + MTTR)।',
        'اختبار الموثوقية يفحص العمل الطويل دون إخفاق. واختبار الاسترداد يتحقق من عودة النظام ببيانات صحيحة بعد انهيار أو انقطاع الشبكة. وتكمل اختبارات تجاوز الفشل والنسخ الاحتياطي والاستعادة والتثبيت والتعافي من الكوارث الصورة. يوعد بالتوافر بالتسعات: 99.9 بالمئة تسمح بنحو 8.76 ساعة توقف سنويًا. والتوافر يساوي MTBF مقسومًا على MTBF زائد MTTR.',
        'Zuverlässigkeitstests prüfen langen fehlerfreien Betrieb. Wiederherstellungstests prüfen, ob das System nach Absturz oder Netzverlust mit korrekten Daten zurückkommt. Failover, Sicherung und Wiederherstellung, Installation und Notfallwiederherstellung ergänzen das. Verfügbarkeit wird in Neunen versprochen: 99,9 Prozent erlauben etwa 8,76 Stunden Ausfall im Jahr. Verfügbarkeit ist MTBF geteilt durch MTBF plus MTTR.')),
]

QUIZ = [
    Qz('e', 'In ISO/IEC 25010:2023, which characteristic replaced "usability"?', ['Flexibility', 'Interaction capability', 'Safety', 'Compatibility'], 1, 'How people interact with it.', 'Usability was renamed interaction capability, and portability became flexibility. Safety is new.'),
    Qz('m', 'Pulling the network cable during a transfer and checking both balances afterwards is...', ['Load testing', 'Recovery testing', 'Usability testing', 'Smoke testing'], 1, 'Coming back after a break.', 'Recovery testing checks that the system returns to a correct state after a failure.'),
    Qz('h', 'About how much downtime per year does 99.9% availability allow?', ['53 minutes', '8.76 hours', '3.65 days', '5 minutes'], 1, '0.1% of 8,760 hours.', '8,760 hours × 0.001 = 8.76 hours.'),
    Qz('x', 'Why is a backup that has never been restored a risk?', ['It is too big', 'Nobody knows if it can really be restored in time', 'It slows the server', 'It breaks the law'], 1, 'Untested promise.', 'Only a real restore test proves the backup is complete and the restore time meets the promise.'),
]

CALC = [
    Calc('m', 'A service promises 99.9% availability over a 30 day month. How many minutes of downtime are allowed? Round to the nearest minute.', '43', '30 * 24 * 60 * 0.001', 'Minutes in the month × 0.1%.', [eq('30 × 24 × 60 = 43,200') + ' minutes', eq('43,200 × 0.001 ≈ 43') + ' minutes']),
    Calc('h', 'MTBF is 990 hours and MTTR is 10 hours. What is the availability in percent?', '99', '990 * 100 / (990 + 10)', 'MTBF ÷ (MTBF + MTTR).', [eq(f'{fr("990", "990 + 10")} = 0.99 = 99%')], unit='%'),
]

DG = {
    "iso": {"t": "ISO/IEC 25010:2023 product quality", "w": 860, "h": 290,
        "n": [["q", 330, 115, 200, 60, "Product quality", {"c": 5, "sh": "pill"}],
              ["f", 10, 10, 190, 50, "Functional suitability", {"c": 1}], ["p", 230, 10, 190, 50, "Performance efficiency", {"c": 1}],
              ["c", 450, 10, 190, 50, "Compatibility", {"c": 1}], ["i", 670, 10, 180, 50, "Interaction capability", {"c": 0, "sub": "was usability"}],
              ["r", 10, 230, 190, 50, "Reliability", {"c": 2}], ["s", 230, 230, 190, 50, "Security", {"c": 2}],
              ["m", 450, 230, 190, 50, "Maintainability", {"c": 2}], ["x", 670, 230, 180, 50, "Flexibility", {"c": 0, "sub": "was portability"}],
              ["sf", 670, 120, 180, 50, "Safety", {"c": 6, "sub": "new in 2023"}]],
        "e": [["q", "f", {"d": 1}], ["q", "p", {"d": 1}], ["q", "c", {"d": 1}], ["q", "i", {"d": 1}], ["q", "r", {"d": 1}], ["q", "s", {"d": 1}], ["q", "m", {"d": 1}], ["q", "x", {"d": 1}], ["q", "sf", {"d": 1}]],
        "st": [[["q"], "Product quality is split into nine characteristics."],
               [["f", "p", "c", "q>f", "q>p", "q>c"], "Does it do the right things, fast enough, and work with other systems?"],
               [["i", "q>i"], "Can people use it? The 2023 edition renamed usability to interaction capability and added inclusivity."],
               [["r", "s", "m", "q>r", "q>s", "q>m"], "Does it keep working, protect data and stay easy to change?"],
               [["x", "sf", "q>x", "q>sf"], "Portability became flexibility, which now includes scalability, and safety is a new characteristic."]]},
}
