# 1.3 The maths for security: bits, XOR, mod, counting, probability and entropy
# Example "bayes_alert" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# An intrusion detector catches 99% of attacks and wrongly flags 1% of normal events.
# Only 10 in 10,000 events are attacks. If it raises an alarm, how likely is a real attack?
events = 10000
attacks = 10
normal = events - attacks

detection_rate = 0.99
false_alarm_rate = 0.01

true_alarms = attacks * detection_rate
false_alarms = normal * false_alarm_rate
print("true alarms:", true_alarms)
print("false alarms:", false_alarms)
print("P(attack | alarm) =", round(true_alarms / (true_alarms + false_alarms), 4))

# The same with Bayes rule written with probabilities
p_attack = attacks / events
p_alarm = detection_rate * p_attack + false_alarm_rate * (1 - p_attack)
print("Bayes rule gives  ", round(detection_rate * p_attack / p_alarm, 4))
