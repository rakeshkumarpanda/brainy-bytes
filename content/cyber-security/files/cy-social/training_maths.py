# 4.1 Social engineering and phishing: tricks, email authentication and defences
# Example "training_maths" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Phishing numbers: click rates, report rates and why technical controls still matter
staff = 2000
emails_per_person_per_year = 12          # real phishing that slips past the filter
for label, click, report in [("before training", 0.20, 0.07), ("after a year of practice", 0.05, 0.60)]:
    clicks = staff * emails_per_person_per_year * click
    print(f"{label:25s} click rate {click:4.0%}  report rate {report:4.0%}  -> about {clicks:,.0f} clicks a year")

# chance that at least one person clicks one campaign sent to n people
for n, p in [(10, 0.05), (50, 0.05), (200, 0.05)]:
    print(f"campaign to {n:3d} people, each clicks with {p:.0%}: P(at least one click) = {1 - (1 - p) ** n:.3f}")

# the first reporter matters: with 500 recipients and a 60% report rate, the first report comes fast
recipients, report_rate, minutes_to_open = 500, 0.6, 30
print(f"expected reporters in a campaign of {recipients}: {recipients * report_rate:.0f}")
print("so the defence is people who report quickly plus controls (passkeys, filters) for the few who click")
