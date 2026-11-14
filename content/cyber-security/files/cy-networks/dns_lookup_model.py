# 2.2 Networks for security: layers, addresses, subnets, TCP and DNS
# Example "dns_lookup_model" from the lesson.
# From the Brainy Bytes Cybersecurity subject. Run it with: python3 <this file>
# Every attack here runs on made up data on your own computer. Never point it at a system you do not own.

# A model of how a resolver finds www.example.com, asking from the top of the tree down
root = {"com": "TLD server for .com"}
tld = {"example.com": "authoritative server for example.com"}
authoritative = {"www.example.com": ("A", "93.184.215.14"), "example.com": ("MX", "mail.example.com")}
cache = {}

def resolve(name):
    if name in cache:
        print("  answer from cache")
        return cache[name]
    label = name.split(".")[-1]
    print("  ask a root server -> go to the", root[label])
    zone = ".".join(name.split(".")[-2:])
    print("  ask the .com server -> go to the", tld[zone])
    answer = authoritative[name]
    print("  ask the authoritative server ->", answer)
    cache[name] = answer
    return answer

print("first lookup:")
resolve("www.example.com")
print("second lookup:")
resolve("www.example.com")
