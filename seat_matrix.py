import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import csv

# better to read webscraper.py before this

session = requests.Session()
res = session.get("https://josaa.admissions.nic.in/applicant/seatmatrix/seatmatrixinfo.aspx")
soup = BeautifulSoup(res.text,'html.parser')
data = {item["name"]:item.get("value","") for item in soup.find_all("input",{"type":"hidden"})}

# contains non hidden input fields to be filled. kept in a list for easier access
fields=[
"ctl00$ContentPlaceHolder1$ddlInstType",
"ctl00$ContentPlaceHolder1$ddlInstitute",
"ctl00$ContentPlaceHolder1$ddlBranch",
"ctl00$ContentPlaceHolder1$btnSubmit"]

#As this only contains just 3 select inputs, looping is sufficient 
inst_type = [item["value"] for item in soup.find("select",{"name":"ctl00$ContentPlaceHolder1$ddlInstType"}).find_all("option")][1:]
for type in inst_type:
    #find list of institutes
    data = {item["name"]:item.get("value","") for item in soup.find_all("input",{"type":"hidden"})}
    data[fields[0]] = type
    data["__EVENTTARGET"] = fields[0]
    res = session.post("https://josaa.admissions.nic.in/applicant/seatmatrix/seatmatrixinfo.aspx",data = data)
    soup = BeautifulSoup(res.text,'html.parser')
    institutes = [item["value"] for item in soup.find("select",{"name":"ctl00$ContentPlaceHolder1$ddlInstitute"}).find_all("option")][1:]

    for institute in institutes:
        #find list of branches
        data.update({item["name"]:item.get("value","") for item in soup.find_all("input",{"type":"hidden"})}) #updating to not lose the branch type
        data[fields[1]] = institute
        data["__EVENTTARGET"] = fields[1]
        res = session.post("https://josaa.admissions.nic.in/applicant/seatmatrix/seatmatrixinfo.aspx",data = data)
        soup = BeautifulSoup(res.text,'html.parser')
        branches = [item["value"] for item in soup.find("select",{"name":"ctl00$ContentPlaceHolder1$ddlBranch"}).find_all("option")][1:]

        #put branch
        data.update({item["name"]:item.get("value","") for item in soup.find_all("input",{"type":"hidden"})})
        data[fields[2]] = "0"
        data["__EVENTTARGET"] = fields[2]
        res = session.post("https://josaa.admissions.nic.in/applicant/seatmatrix/seatmatrixinfo.aspx",data = data)
        soup = BeautifulSoup(res.text,'html.parser')
            #soup is html consisting of only 1 table

        #submit
        data.update({item["name"]:item.get("value","") for item in soup.find_all("input",{"type":"hidden"})})
        data[fields[3]] = "Submit"
        data["__EVENTTARGET"] = fields[3]
        res = session.post("https://josaa.admissions.nic.in/applicant/seatmatrix/seatmatrixinfo.aspx",data = data)
        soup = BeautifulSoup(res.text,'html.parser')
            
        #put all table data in csv file
        table = soup.find("table")
        table = pd.read_html(StringIO(str(table)))[0]
        # delete last row from the table if it is empty
        table.dropna(inplace=True, how='all')
        with open('seat_matrix_25.csv', 'a', encoding='utf-8') as f:
            table.to_csv(f, index=False, header=False, mode='a')

#put a separate file for total seats and programme specific seats to make it easy to navigate and make tables(excel)
with open("seat_matrix_25.csv","r") as file_1, open("total_seats.csv","w") as file_2, open("programme.csv","w") as file_3:
    csv_reader = csv.reader(file_1) #this consists of both programme specific and total seats which has to be separated
    csv_writer1 = csv.writer(file_2)
    csv_writer2 = csv.writer(file_3)
    prev_row = []
    for row in csv_reader:
        if row[0] == "": #total seat lines stores nothing in their first item
            new_row = [prev_row[0]] #add institute in the first item by taking it from previous row
            new_row.extend(row[3:])
            csv_writer1.writerow(new_row)
        else:
            csv_writer2.writerow(row) #this writes the programme specific branches
        prev_row = row
        





            


