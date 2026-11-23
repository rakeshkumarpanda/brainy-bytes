# 4.3 IoT and industrial control security: Mirai, Modbus, Purdue and Stuxnet
# Example "sensor_anomaly" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# Watching the process itself: flag readings that do not fit what the physics says should happen
import statistics

level = [40, 41, 40, 42, 41, 40, 41, 42, 41, 40, 47, 55, 63, 71, 79]   # tank level %, one reading a minute
valve_cmd = [0] * 15                                                  # the HMI says the inlet valve is shut

window = level[:10]
mean, sd = statistics.mean(window), statistics.pstdev(window)
print(f"normal level {mean:.1f} +/- {sd:.2f}")
for t in range(10, len(level)):
    z = (level[t] - mean) / sd
    rise = level[t] - level[t - 1]
    flags = []
    if abs(z) > 3:
        flags.append(f"z score {z:.1f}")
    if rise > 3 and valve_cmd[t] == 0:
        flags.append("level rising while the valve is commanded shut")
    print(f"minute {t:2d}: level {level[t]:3d}%  {'; '.join(flags) if flags else 'normal'}")

print("\nA change in the physical process that no operator ordered is the strongest sign of tampering,")
print("even when the network traffic looks normal.")
