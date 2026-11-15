# 2.3 Differential privacy
# Example "budget_tracker" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A privacy budget: sequential composition adds epsilons, parallel composition on disjoint groups does not
class Budget:
    def __init__(self, total):
        self.total, self.spent = total, 0.0

    def spend(self, eps, what):
        if self.spent + eps > self.total + 1e-12:
            print(f"  REFUSED  {what:38} needs {eps}, only {self.total - self.spent:.2f} left")
            return False
        self.spent += eps
        print(f"  ok       {what:38} eps {eps:<4}  spent {self.spent:.2f} of {self.total}")
        return True

b = Budget(1.0)
print("sequential queries on the same people:")
b.spend(0.3, "count of diabetics")
b.spend(0.3, "average age of diabetics")
b.spend(0.3, "count of smokers")
b.spend(0.3, "count of diabetic smokers")          # 1.2 would exceed the budget

print("\nparallel queries: one count per city, and each person lives in exactly one city")
cities = ["Delhi", "Mumbai", "Chennai", "Kolkata"]
per_city = 0.5
print(f"  four counts at eps {per_city} each cost only max = {per_city}, not {per_city * len(cities)}")

print("\npost processing is free: rounding or clipping a noisy answer to 0 or more uses no extra budget.")
print("group privacy: protecting a family of 4 with eps 0.5 each person means eps 2.0 for the family.")
