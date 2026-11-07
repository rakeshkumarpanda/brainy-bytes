# 6.2 CSV, JSON, XML and settings files
# Example "xml_data" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import xml.etree.ElementTree as ET

text = """<library>
  <book id="1" lang="en"><title>Python Basics</title><price>20.5</price></book>
  <book id="2" lang="de"><title>Datenbanken</title><price>31</price></book>
</library>"""

root = ET.fromstring(text)
print(root.tag, len(root))
for book in root.findall("book"):
    print(book.get("id"), book.find("title").text, float(book.findtext("price")))
print([t.text for t in root.iter("title")])
print(root.find(".//book[@lang='de']/title").text)    # a small part of XPath

new = ET.SubElement(root, "book", id="3", lang="en")
ET.SubElement(new, "title").text = "Regex & More"
ET.SubElement(new, "price").text = "15"
root.find("book").set("lang", "fr")
print(ET.tostring(new, encoding="unicode"))           # & is written as &amp; for us
ET.indent(root)
print(ET.tostring(root, encoding="unicode").splitlines()[1])
