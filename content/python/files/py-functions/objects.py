# 4.1 Functions: def, return and every kind of argument
# Example "objects" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

def shout(text):
    return text.upper() + "!"

def whisper(text):
    return text.lower() + "..."

speak = shout                 # a function is an object: give it another name
print(speak("hi"), speak is shout)

def apply_twice(func, value): # and pass it to another function
    return func(func(value))

print(apply_twice(whisper, "HELLO"))
print(apply_twice(lambda n: n * 3, 2))

tools = {"loud": shout, "soft": whisper}   # or store it in a dict
print(tools["soft"]("Good Night"))
print(type(shout), shout.__name__)
