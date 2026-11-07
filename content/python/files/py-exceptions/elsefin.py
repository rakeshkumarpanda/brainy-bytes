# 5.1 Exceptions: try, except, else, finally and raise
# Example "elsefin" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def read_number(text):
    try:
        n = int(text)
    except ValueError:
        print("  except: bad input")
        return None
    else:
        print("  else: only when there was no exception")
        return n
    finally:
        print("  finally: always, even after return")

for t in ["12", "twelve"]:
    print("read_number(" + repr(t) + ")")
    print("  returned", read_number(t))
