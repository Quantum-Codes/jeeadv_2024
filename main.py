from PyPDF2 import PdfReader
import mysql.connector, dotenv, os, json, csv

# every scraping module has its own section in the code, enclosed by """ and #""" (this was built like jyupiter notebook; running cells one by one)
# also note that some of the variable names might be misleading (they were made for a purpose but now have a different purpose in different modules)
# the data for nits, iiits and gftis are generated from a webscraper in webscraper.py.
"""
Table def:
CREATE TABLE data (
    roll INT PRIMARY KEY, 
    CRL INT,
    marks INT, 
    category VARCHAR(20), 
    cat_rank INT, 
    institute VARCHAR(50), 
    programme VARCHAR(120),
    AAT_qualified BOOL,
    program_duration TINYINT,
    state VARCHAR(40),
    city VARCHAR(30)
);

CREATE TABLE branches (
    institute VARCHAR(50),
    programme VARCHAR(120),
    duration TINYINT,
    chosen INT,
    PRIMARY KEY (institute, programme, duration)
);

CREATE TABLE ORCR ( # ORCR = Opening Rank Closing Rank
    institute VARCHAR(50),
    branch VARCHAR(300),
    category VARCHAR(10),
    pool VARCHAR(10),
    opening_rank INT,
    closing_rank INT
);

CREATE TABLE centre_codes (
    code CHAR(4) PRIMARY KEY,
    city VARCHAR(30),
    state VARCHAR(40)
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


#"""
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
#"""



#"""
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

categories = []
for line in page_content:
    if 'Score' in line:
        categories.append(line[:line.index(" ")].replace("-", "").strip()) # remove - to make CRL-PwD match CRLPwD
        db.commit() # SAVE EACH CATEGORIES SCORE
        continue
    
    line = line.split(" ")
    if categories[-1] == "CRL":
        sql.execute("UPDATE data SET marks = %s WHERE %s >= CRL AND CRL > %s - 100;", (line[1], line[0],line[0]))
        
        # this floor expression gives the lower marks to each guy in the 100 people bracket
        continue
    sql.execute("UPDATE data SET marks = %s WHERE %s >= cat_rank AND cat_rank > %s - 100 AND category = %s AND CRL IS NULL;", (line[1], line[0],line[0], categories[-1]))
    # CRL is null to give preference to CRL marks as they have more wide categories so should be more specific to each category
    # candidate where clause that sadly failed (cuz last rank not set properly) CEIL(cat_rank / 100) * 100 + 1 = %s
    print(categories)

# Turns out that the document is wrong at page 20 JIC report 2024. There is no column for EWS rank 5401. so we use the following query to fix:
# UPDATE data SET marks = 98 WHERE 5333 >= cat_rank AND cat_rank >= 5302 AND category = "EWS" AND marks IS NULL AND CRL IS NULL;

db.commit()
#"""




#"""
# the following data in json files were not scraped. just the table was copy pasted into chatgpt as text and converted to json
with open("institutes.json", "r") as f:
    institutes = json.load(f)
with open("4year_branches.json", "r") as f:
    year4_branches = json.load(f)
with open("5year_branches.json", "r") as f:
    year5_branches = json.load(f)

# CRL vs Marks
page_nos = range(256, 451)
page_content = []
headers = [] # to make all table headers appear only once


# Theres malformation in this too.
# PwD of form (pure pwd, not prep pwd) (regular malformed lines):
# SC-PwD
# RankRollNo Inst.Code Br.CodeSC-PwD
# RankRollNo Inst.Code Br.Code

# So we remove next 2 lines.

# PREP form: (this is irregular unlike pure pwd, so need to detect)
# PREP-SC-
# PwD RankRollNo Inst.Code Br.CodePREP-SC-
# PwD RankRollNo Inst.Code Br.Code

# OR

# PREP-
# CRL-PwD
# RankRollNo Inst.Code Br.CodePREP-
# CRL-PwD


for i in page_nos:
    content = reader.pages[i].extract_text()
    content = content.split("\n")
    content.pop(0)
    content.pop(-1)
    
    if i == 256:
        del content[0:2]
    
    for line_no, line in enumerate(content):
        if line == "deleted":
            continue
        
        if "Seat" in line:
            content[line_no] = "deleted"
            continue
            
        if line[0].isalpha():
            line = line.split(" ")
            
            if "PREP" in line[0]: # malformed line group for prep courses
                line = " ".join(line)
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
                if "Rank" in malformed_lines[0]:
                    category = malformed_lines[0][:malformed_lines[0].find("Rank")] # category is first item. sometimes the Rank word from "PREP-CRL-PwDRank" combines like this. need to remove that
                else:
                    category = malformed_lines[0]
                    
                if category in headers:
                    content[line_no] = "deleted"
                    print(f"Duplicate header found: {category}")
                    continue
                
                print(f"Header found: {category}")
                headers.append(category)
                continue
            
            if "PwD" in line[0]: # malformed line group for pure PwD
                content[line_no + 1] = "deleted"
                content[line_no + 2] = "deleted"
                
            if line[0] in headers:
                content[line_no] = "deleted"
                continue
            headers.append(line[0])
            content[line_no] = line[0]
            print(f"Header found: {line[0]}")
            continue
        
            
    for i in range(content.count("deleted")):
        content.remove("deleted")
    page_content.extend(content)
print(headers)

categories = []
# combine year4 and year5 branches in a single dict to make it easier to update
branches = year4_branches
branches.update(year5_branches)
for line in page_content:
    if line[0].isalpha():
        if "PREP" not in line:
            line = line.replace("-", "") # remove - to make CRL-PwD match CRLPwD but not remove dash from PREP courses
        categories.append(line.strip()) 
        db.commit() # SAVE EACH CATEGORIES SCORE
        continue
    
    line = line.split(" ")
    stud1 = line[:4]
    stud2 = line[4:]
    # here roll number is unique for every student so category rank or category is not required. so we can get away with the mistake we made when extracting category name since it wasnst needed anyway 
    # first char of branch code is the year duration of the course.
    sql.execute("UPDATE data SET institute = %s, programme = %s, program_duration = %s WHERE roll = %s ;", (institutes[stud1[2]],branches[stud1[3]],stud1[3][0],stud1[1]))
    if len(stud2)>1: #no 2nd column
        sql.execute("UPDATE data SET institute = %s, programme = %s, program_duration = %s WHERE roll = %s ;", (institutes[stud2[2]],branches[stud2[3]],stud2[3][0],stud2[1]))
    print(categories)
    
db.commit()
#"""




#"""
# choice count

# take data of code - name
with open("institutes.json", "r") as f:
    institutes = json.load(f)
with open("4year_branches.json", "r") as f:
    year4_branches = json.load(f)
with open("5year_branches.json", "r") as f:
    year5_branches = json.load(f)
    
# branches consists of all branches
branches = year4_branches
branches.update(year5_branches)
  
page_nos = range(451, 454)
page_content = []
for i in page_nos:
    content = reader.pages[i].extract_text()
    content = content.split("\n")
    content.pop(0)
    content.pop(-1)
    
    if i==451:
        content.pop(0)
    
    for line_no,line in enumerate(content):
        if line[0].isalpha():
            content[line_no] = "deleted"
        elif "Inst" in line:
            content[line_no] = line[0:line.find("I")].split(" ") # remove the text at the end of any entry (Inst. Code...)
        else:
            content[line_no] = line.split()
            
            
            
    for i in range(content.count("deleted")):
        content.remove("deleted")
    page_content.extend(content)

        
  
for line in page_content:
    print(line)
    sql.execute("INSERT INTO branches (institute, programme, chosen, duration) VALUES (%s,%s,%s,%s);", (institutes[line[0]],branches[line[1]],int(line[2]),int(line[1][0])))
db.commit()
#"""




#"""
# getting Opening and Closing ranks
page_nos = range(455, 595) #last page 455,595 (2nd argument)
page_content = []
headers = [] # to make all table headers appear only once
fixed_line = "" 
with open("institutes.json", "r") as f:
    institutes = json.load(f)
for i in page_nos:
    content = reader.pages[i].extract_text()
    content = content.split("\n")
    content.pop(0)
    content.pop(-1)
    
    if i == 455:
        del content[0:2]
        
    if i == 594:
        content.append("001 LOSER CODE HEHEHAHA")
    
    
    for line_no, line in enumerate(content):
        if "Academic Program" in line:
            continue
        line = line.strip()
        if line[0].isdigit():
            if "PwD" not in fixed_line:
                # process line
                fixed_line = fixed_line.replace("(includingSupernumerary)", " ").replace("Female-only", " Female-only")
                fixed_line = fixed_line.replace("IIT", " IIT")
                fixed_line = fixed_line.replace("  ", " ") # remove double spaces
                fixed_line = fixed_line.replace("(ISM)", "(ISM) ")
                fixed_line = fixed_line.replace("(BHU)", "(BHU) ")
                for institute in institutes.values():
                    fixed_line = fixed_line.replace(institute, institute + " ")
                
                for category in ["OPEN", "EWS", "OBC-NCL", "SC", "ST"]:
                    fixed_line = fixed_line.replace(category, " " + category)
                
                # i want that each institute name is 2 part - IIT <place>.. so... ISM and BHU has to face this heartless treatment
                fixed_line = fixed_line.replace("(ISM) ", "(ISM)")
                fixed_line = fixed_line.replace("(BHU) ", "(BHU)")
                page_content.append(fixed_line)
                
                
    

            fixed_line = line # now process the new line that had the number infront

            
        else:
            fixed_line += line

# print("\n".join(page_content))
page_content.pop(0) # remove the first line which is empty

for line in page_content:
    line = line.split(" ")[1:] # remove the first item which is the serial number
    institute = " ".join(line[:2])
    del line[:2] # remove institute name
    OR = line.pop(-2)
    CR = line.pop(-1) # remove OR and CR
    gender_pool = line.pop(-1)
    category = line.pop(-1) # remove category
    # now remaining is the branch in list form
    branch = " ".join(line)
 
    print(institute, branch, category, gender_pool, OR, CR, sep=" | ")
    sql.execute("INSERT INTO ORCR (institute, branch, category, pool, opening_rank, closing_rank) VALUES (%s, %s, %s, %s, %s, %s)", (institute, branch, category, gender_pool, OR, CR))
db.commit()
db.close()
# close the database connection

# Also somehow, every occurance of Artificial had weird characters, so do this:
# UPDATE ORCR SET branch = REPLACE(branch, "Artiﬁcial Intelligence", "Artificial Intelligence") WHERE branch LIKE "%Art%";


# At this point, i just wrote the data to a csv file using the code below. the paragraph right below this line was added later when some inconsistency in data was observed.

# Now also there is a problem in the data. JIC report does not label prep ranks in ORCR properly so we gotta remove them to not confuse people
# OR rather than removing, we could check out the allotment table (data table) and see if the roll number is prep or not. If it is, then we can remove the ORCR entry.
# Also this is commentatory after me doing this stuff and it was too late for me to realise that there were easier ways to detect these entries. - 1. Check OR > CR 2. Check if female opening < male opening 3. Check for architecture programme manually (while querying i noticed that these cases are almost exclusively for female ST seats)
# if you are folliwing this code, then you can use the method i said above to remove the prep entries from ORCR table.

# THIS IS WRONG BELOW (corrected manually in excel) but i just decided to put these here as a learning

# CREATE TABLE broken_branches AS SELECT DISTINCT institute, programme FROM data WHERE institute IS NOT NULL AND category LIKE "PREP%" AND category NOT LIKE "%PwD%"; # getting prep ranks
# CREATE TABLE fixed_ORCR AS SELECT B.institute AS inst, B.programme AS prog, MIN(cat_rank) AS OpR, MAX(cat_rank) AS CR FROM data as A, broken_branches as B WHERE A.category = "ST" AND A.institute = B.institute AND A.programme = B.programme GROUP BY B.institute, B.programme;
# now i see one table has 2 entries less than the other which was weird. query to see the difference:
# SELECT A.institute, A.programme FROM broken_branches AS A LEFT JOIN fixed_ORCR AS B   ON A.institute = B.inst AND A.programme = B.prog WHERE B.inst IS NULL;
# there was probably a better way ig but now we see 2 architecture branches
# now you have all branches with prep rank somewhere in ORCR and you also have the corrected OR and CR. just edit those entries with a script or manually
# -- wrong over --
# after doing all this i realised that the fixed_ORCR had females and males mixed up cuz JIC did not have distinct data for M and F
# also i noticed that most prep ranks had both OR prep and CR prep except for IIT BHU Chemical who had only 1 ST girl who was not prep, so i edited CR as 1802 manually
# then for rest of records in broken_branches, i just made OR and CR both NULL (blank) in excel. there were like 51 branches like this ig.. i dont remember 

# DATA FIXING FINALLY OVER!!!!!!!!!! (i hope)
#"""




#"""
# Writing ORCR data to CSV file

# get data
sql.execute("SELECT * FROM ORCR;")
page_content = sql.fetchall()
# write to csv file
with open("exported_data/csv/ORCR.csv",'w') as file:
    writer = csv.writer(file)
    for i in page_content:
        writer.writerow(i)

# Writing allotment data to CSV file

# get data
sql.execute("SELECT * FROM data;")
page_content = sql.fetchall()
# write to csv file
with open("exported_data/csv/allotment.csv",'w') as file:
    writer = csv.writer(file)
    for i in page_content:
        writer.writerow(i)
        
# Writing branches data to CSV file

# get data
sql.execute("SELECT * FROM branches;")
page_content = sql.fetchall()
# write to csv file
with open("exported_data/csv/choices.csv",'w') as file:
    writer = csv.writer(file)
    for i in page_content:
        writer.writerow(i)

#"""




#"""
# Page numbers to process for extracting city data
page_nos = range(32, 53)  # 53 is the second argument (end of range)

# Load city data from JSON file
with open("cities.json", "r") as file: 
    city_data = json.load(file)  # Load JSON file containing city names
with open("institutes.json", "r") as file: 
    institutes = json.load(file)
    # IIT Bbs always appears as IITBhubaneswar, so we update it
    institutes["101"] = "IITBhubaneswar"
cities = city_data.keys() # Extract the list of cities

# Initialize a list to store processed page content
page_content = []

# Loop through the specified page numbers
for i in page_nos:
    page = reader.pages[i].extract_text()  # Extract text from the current page
    content = page.split("\n")  # Split the page content into lines
    content.pop(0)  # Remove the first line (header)
    content.pop(0)  # Remove the second line (table headers)
    if i == 32:  # first page
        content.pop(0)  # title

    fixed_line = ""
    for line in content:
        if line[0].isnumeric():  # Check if the line starts with a number (indicating a new entry)
            # Process the accumulated line
            page_content.append(fixed_line)  # Add the processed line to the list
            fixed_line = line  # Start a new line for processing
        else:
            fixed_line += line  # Append the current line to the accumulated line

# btw the following code is not a good way of detecting cities. if you are making your own version then DO NOT use this method. there are a lot of problems like:
# "patna" in "vishakhapatnam" is true so if program tests for "patna" before "vishakhapatnam" then it returns wrong output. so in cities.json, vishakhapatnam is placed above patna. 
# also dicts are supposed to be unordered even after reading from files but after testing i see order is preserved :/ this script relies on that ordering (which is bad)
city_dir = {} 
for line in page_content:
    if line.strip() == "":  # Skip empty lines
        continue
        
    center_code = line.split()[0]  # Extract the center code (first word in the line)
    for insti in institutes.values(): # remove institute name because it also contains city names
        if insti in line:
            line = line.replace(insti,"")
    print(line)
    for city in cities:  # Check if any city name is present in the line
        if city.lower().replace("-","") in line.lower().replace("-",""): # Case-insensitive match, ignoring hyphens
            
            city_dir[center_code] = (city, city_data[city])  # Map the center code to the city name and state
            break
    print("DETECTED AS:", city_dir[center_code]) # this errors if city not in city.json

# Print the mapping of center codes to city names and save
for key, value in city_dir.items():
    #print(key, value)
    sql.execute("INSERT INTO centre_codes (code, city, state) VALUES (%s, %s, %s);", (key, value[0], value[1]))  # Insert the center code, city name, and state into the database

db.commit()
# now find that in roll number and map all cities - we can do this purely with sql queries
# UPDATE data AS D JOIN centre_codes AS B ON B.code = SUBSTRING(D.roll, 3, 4) SET D.city = B.city, D.state = B.state;
#"""

#"""
# Stats for reddit

# College preference stat (CS Stat in combined.xlsx)
sql.execute("SELECT institute, programme, duration, chosen FROM branches WHERE programme LIKE \"Computer%\" ORDER BY chosen DESC;")
data = sql.fetchall()
with open("exported_data/stats/stat.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["Institute", "programme", "duration", "Choices"])
    writer.writerows(data)

# State wise count of students
sql.execute("SELECT state, COUNT(*) FROM data GROUP BY state ORDER BY COUNT(*) DESC;")
data = sql.fetchall()
with open("exported_data/stats/state_wise_count.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["State", "Count"])
    writer.writerows(data)

#  Institute wise count of students in specific state
sql.execute("SELECT DISTINCT state FROM centre_codes;")
states = sql.fetchall()

for state in states:
    sql.execute("SELECT IFNULL(institute, 'Unalloted'), COUNT(*) FROM data WHERE state = %s GROUP BY institute ORDER BY COUNT(*) DESC;", (state[0],))
    data = sql.fetchall()
    with open(f"exported_data/stats/state_wise_institute_count.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow(["Institute", f"{state[0]} students"])
        writer.writerows(data)
        writer.writerows(([],[]))

# Institute wise count of students in specific state
with open("institutes.json", "r") as f:
    institutes = json.load(f)

for institute in institutes.values():
    sql.execute("SELECT state, COUNT(*) FROM data WHERE institute = %s GROUP BY state ORDER BY COUNT(*) DESC;", (institute,))
    data = sql.fetchall()
    with open(f"exported_data/stats/institute_wise_state_count.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow([institute, "students"])
        writer.writerows(data)
        writer.writerows(([],[]))

# allotment percentage by state
sql.execute("SELECT state, COUNT(*) FROM data WHERE institute IS NOT NULL GROUP BY state ORDER BY state DESC;")
data1 = sql.fetchall()
sql.execute("SELECT state, COUNT(*) FROM data GROUP BY state ORDER BY state DESC;")
data2 = sql.fetchall()
with open("exported_data/stats/state_wise_allotment_percentage.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["State", "Alloted Students"])
    for i in range(len(data2)):
        if i>=len(data1):
            item = [(data2[i][0]),0.0] #If nobody in that state was alloted in iit then data1 won't have its entry and len(data1)<len(data2)
        else:
            item = [(data1[i][0]),int((data1[i][1]*100/data2[i][1])*100)/100]  #int(item*100)/100 produces 2 decimal places instead of >2
        print(item)
        writer.writerow(item)

#  Institute choice of foreign students (UAE and nepal)
sql.execute("SELECT IFNULL(institute, 'Unalloted'), COUNT(*) FROM data WHERE state IN ('UAE', 'Nepal') GROUP BY institute ORDER BY COUNT(*) DESC;")
data = sql.fetchall()
with open(f"exported_data/stats/foreign_students_choice.csv", "a") as f:
    writer = csv.writer(f)
    writer.writerow(["Institute", f"Foreign Students"])
    writer.writerows(data)
    writer.writerows(([],[]))


# close the database connection
db.close()
#"""
"""
Rejected stats queries:
1. SELECT institute, SUM(chosen) AS chosen FROM branches GROUP BY institute ORDER BY SUM(chosen) DESC; -> this is highly sensitive to number of branches, so there is no use of this statistic
2. SELECT programme, COUNT(*) AS popularity FROM branches  GROUP BY programme  ORDER BY popularity DESC  LIMIT 10; -> there are a lot of branches with occurance close to 1.. some branches are the same but named differently.. so this is a useless query
"""