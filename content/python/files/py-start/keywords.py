# 1.1 What a program is and your first Python program
# Example "keywords" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import keyword

print("Python has", len(keyword.kwlist), "keywords:")
print(keyword.kwlist)
print("Soft keywords:", keyword.softkwlist)
print("Is 'class' a keyword?", keyword.iskeyword("class"))
print("Is 'print' a keyword?", keyword.iskeyword("print"))
