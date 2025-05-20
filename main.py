from PyPDF2 import PdfReader
import mysql.connector, dotenv, os

"""
Table def:
CREATE TABLE data (
    roll INT PRIMARY KEY, 
    CRL INT, marks INT, 
    category VARCHAR(20), 
    cat_rank INT, 
    institute VARCHAR(50), 
    programme VARCHAR(120),
    AAT_qualified BOOL
);
"""

dotenv.load_dotenv()
db = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user=os.environ["db_user"],
    password=os.environ["db_pass"],
    database = "jeeadv_2024"
)
sql = db.cursor()


reader = PdfReader("JIC 2024.pdf")
number_of_pages = len(reader.pages)



# Roll vs CRL
page_nos = range(53, 212) # until AAT text
page_content = []
headers = [] # to make all table headers appear only once
for i in page_nos:
    content = reader.pages[i].extract_text()
    content = content.split("\n")
    content.pop(0)
    content.pop(-1)
    print("\n".join(content))
    
    # for line_no, line in enumerate(content):
    #     if "Aggregate" in line:
    #         content[line_no] = "deleted"
    #         continue
        
    #     for id, char in enumerate(line):
    #         if char.isalpha():
    #             if id == 0:
    #                 if line in headers:
    #                     content[line_no] = "deleted"
    #                     break
    #                 headers.append(line)
    #                 break # normal table header line like 'CRL Score'
    #             new_items = ( line[:id], line[id:] )
    #             content[line_no] = new_items[0]
    #             content.insert(line_no + 1, new_items[1])
    #             break
                
    # for i in range(content.count("deleted")):
    #     content.remove("deleted")
    # page_content.extend(content)




# CRL vs Marks
# page_nos = range(18, 21)
# page_content = []
# headers = [] # to make all table headers appear only once
# for i in page_nos:
#     content = reader.pages[i].extract_text()
#     content = content.split("\n")
#     content.pop(0)
#     content.pop(-1)
    
#     for line_no, line in enumerate(content):
#         if "Aggregate" in line:
#             content[line_no] = "deleted"
#             continue
        
#         for id, char in enumerate(line):
#             if char.isalpha():
#                 if id == 0:
#                     if line in headers:
#                         content[line_no] = "deleted"
#                         break
#                     headers.append(line)
#                     break # normal table header line like 'CRL Score'
#                 new_items = ( line[:id], line[id:] )
#                 content[line_no] = new_items[0]
#                 content.insert(line_no + 1, new_items[1])
#                 break
                
#     for i in range(content.count("deleted")):
#         content.remove("deleted")
#     page_content.extend(content)

# categories = []
# for line in page_content:
#     if 'Score' in line:
#         categories.append(line[:line.index(" ")])
#         continue
    
#     line = line.split(" ")
#     if categories[-1] == "CRL":
#         sql.execute("INSERT INTO data (CRL, marks, cat_rank) VALUES (%s, %s, %s);", (line[0], line[1], line[0]))
#         continue
#     sql.execute("INSERT INTO data (cat_rank, marks) VALUES (%s, %s);", (line[0], line[1]))

# db.commit()