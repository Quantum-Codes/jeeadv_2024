from PyPDF2 import PdfReader

reader = PdfReader("JIC 2024.pdf")
number_of_pages = len(reader.pages)
page = reader.pages[13]
text = page.extract_text()
print(number_of_pages)
print(text)