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
page_nos = range(53, 212) # until and including AAT text
page_content = []
aat_page_content = []
headers = [] # to make all table headers appear only once. 
aat = 0 # aat switch, if currently viewing aat then its 1
prep = 0 # prep switch, if currently viewing prep then its 1. cuz prepcourse ranks are joined with roll numbers

# noise appear only for PREP courses as:
# (All these inconsistent entries start with line "Roll NoPREP-" and continue till the first numeric entry)
# Roll NoPREP-
# OBC-
# PwDRoll NoPREP-
# OBC-
# PwDRoll NoPREP-
# OBC-
# PwDRoll NoPREP-
# OBC-
# PwDRoll NoPREP-
# OBC-
# PwDRoll NoPREP-
# OBC-
# PwD

# or

# Roll NoPREP-
# SC-PwDRoll NoPREP-
# SC-PwDRoll NoPREP-
# SC-PwDRoll NoPREP-
# SC-PwDRoll NoPREP-
# SC-PwDRoll NoPREP-
# SC-PwD

for i in page_nos:
    content = reader.pages[i].extract_text()
    content = content.split("\n")
    if i == 53:
        del content[0:3]
    else:
        content.pop(0)
    
    content.pop(-1)
    
    for line_no, line in enumerate(content): 
        if line == "deleted":
            continue
        if "Rank" in line:
            content[line_no] = "deleted"
            continue
        
        # handle AAT roll numbers
        if "AAT" in line: #header no = AAT candidate
            aat = 1
            prep = 0
            content[line_no] = "deleted"
            continue
        

        if "Roll" in line:
            if "NoPREP-" in line: # malformed line group
                prep = 1
                tmp_line_no = line_no + 1
                next_line = content[tmp_line_no]
                malformed_lines = line # contains all malformed lines joined together in a single string
                while not next_line[0].isnumeric(): # loop till a numeric entry is found
                    malformed_lines += next_line.strip() # remove newline
                    content[tmp_line_no] = "deleted"
                    tmp_line_no += 1
                    next_line = content[tmp_line_no]
                # we have now deleted all malformed lines and put them in malformed_lines
                # now we need to detect the category 
                malformed_lines = malformed_lines.split(" ")
                category = malformed_lines[1][2:-4] # category is the second word in the malformed line
                # to remove the 'No' infront of category and 'Roll' at end of it, we put [2:]
                headers.append(category)
                print(f"Header found: {category}")
                # now we need to replace the malformed lines with the category
                content[line_no] = category
                continue
                
                    
                
            line = line.split(" ")
            if line[0] == "Adv": # for Prep courses, its written as just "roll no", so need to delete "Adv" for other categories
                line.pop(0)
            
            category = line[2]
            
            if category in headers:
                content[line_no] = "deleted"
                print(f"Duplicate header found: {category}")
                continue
            headers.append(category)
            print(f"Header found: {category}")
            content[line_no] = category
        
        # handle ranks and roll numbers + fix entries for prep courses(rank joined with roll)
        # roll number = 9 digit
        # rank = upto 5 digit
        if prep:
            line = line.split(" ")
            for j, item in enumerate(line):
                if len(item) > 9: # joined rank and roll
                    roll = item[-9:]
                    rank = item[:-9]
                    line[j] = rank
                    line.insert(j + 1, roll)
                    continue
            content[line_no] = " ".join(line)
                     
        
                
    for i in range(content.count("deleted")):
        content.remove("deleted")
    page_content.extend(content)

print("\n".join(page_content))
categories = []
for line in page_content:
    if line[0].isalpha() and not line == "No":
        categories.append(line)
        continue
    
    if line == "No":
        categories.append("AAT")
        db.commit()
        continue
    
    line = line.split(" ")
    if categories[-1] != "AAT":
        grouped = zip(line[0::2], line[1::2])
        for item in grouped:
            if categories[-1] == "CRL":
                sql.execute("INSERT INTO data (CRL, roll, cat_rank, category) VALUES (%s, %s, %s, \"gen\");", (item[1], item[0], item[1]))
                continue
            else: 
                # on duplicate is for some guys who already had a CRL and was misclassified as a gen
                sql.execute("INSERT INTO data (roll, cat_rank, category) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE cat_rank = %s, category = %s;", (item[0], item[1], categories[-1], item[1], categories[-1]))
                continue
            
    else:
        for item in line:
            sql.execute("INSERT INTO data (roll, AAT_qualified) VALUES (%s, 1) ON DUPLICATE KEY UPDATE AAT_qualified = 1;", (item,))
db.commit()

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