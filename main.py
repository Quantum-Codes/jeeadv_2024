from PyPDF2 import PdfReader

reader = PdfReader("JIC 2024.pdf")
number_of_pages = len(reader.pages)

# CRL vs Marks
page_nos = range(18, 21)
page_content = []
headers = [] # to make all table headers appear only once
for i in page_nos:
    content = reader.pages[i].extract_text()
    content = content.split("\n")
    content.pop(0)
    content.pop(-1)
    
    for line_no, line in enumerate(content):
        if "Aggregate" in line:
            content[line_no] = "deleted"
            continue
        
        for id, char in enumerate(line):
            if char.isalpha():
                if id == 0:
                    if line in headers:
                        content[line_no] = "deleted"
                        break
                    headers.append(line)
                    break # normal table header line like 'CRL Score'
                new_items = ( line[:id], line[id:] )
                content[line_no] = new_items[0]
                content.insert(line_no + 1, new_items[1])
                break
                
    for i in range(content.count("deleted")):
        content.remove("deleted")
    page_content.extend(content)

print(page_content)
