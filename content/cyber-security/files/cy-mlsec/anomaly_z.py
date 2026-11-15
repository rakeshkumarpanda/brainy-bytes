# 1.1 Machine learning for security
# Example "anomaly_z" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Anomaly detection for user behaviour: megabytes uploaded per day by one employee
import statistics as st

uploads = [120, 135, 110, 128, 140, 118, 125, 132, 900, 122, 130, 2400, 127, 119]

mean, sd = st.mean(uploads), st.pstdev(uploads)
med = st.median(uploads)
mad = st.median([abs(x - med) for x in uploads])     # median absolute deviation

print(f"mean {mean:.1f}  sd {sd:.1f}   median {med}  MAD {mad}")
print("day  MB     z     robust z")
for day, x in enumerate(uploads, 1):
    z = (x - mean) / sd
    rz = 0.6745 * (x - med) / mad                     # Iglewicz and Hoaglin modified z score
    flag = "ALERT" if abs(rz) > 3.5 else ""
    print(f"{day:3} {x:5} {z:6.2f} {rz:9.2f}  {flag}")
print("\nThe plain z score passes 3 only on day 12: the two big days inflate the mean and sd and hide day 9.")
print("The median and MAD barely move, so the robust z score catches both.")
