# 1.1 Logging, monitoring and the SIEM
# Example "base_rate" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# The base rate fallacy: what share of alerts are real attacks? (Bayes' rule)
TOTAL = 1_000_000

def precision(attacks, detection_rate, false_alarm_rate):
    true_alerts = attacks * detection_rate
    false_alerts = (TOTAL - attacks) * false_alarm_rate
    return true_alerts, false_alerts, true_alerts / (true_alerts + false_alerts)

print("attacks  detect  false alarm   true   false   precision")
for attacks, det, fa in [(100, 0.99, 0.01), (100, 0.99, 0.001), (100, 0.99, 0.0001), (10000, 0.99, 0.01), (100, 0.50, 0.0001)]:
    tp, fp, p = precision(attacks, det, fa)
    print(f"{attacks:7}  {det:6.2f}  {fa:11.4f}  {tp:5.0f}  {fp:6.0f}   {p:9.4f}")

print("\nLesson: when attacks are rare, cutting false alarms helps far more than catching a few more attacks.")
