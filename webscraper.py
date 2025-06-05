import requests, os
from bs4 import BeautifulSoup
import pandas as pd


# get params
session = requests.Session()
res = session.get("https://josaa.admissions.nic.in/applicant/seatmatrix/openingclosingrankarchieve.aspx")

soup = BeautifulSoup(res.text, 'html.parser')
hidden_params = {item["name"]: item.get("value", "") for item in soup.find_all("input", {"type": "hidden"})}

field_data = ( # like immutable dict so order is preserved
    ("ctl00$ContentPlaceHolder1$ddlYear", "2024"),
    ("ctl00$ContentPlaceHolder1$ddlroundno", "5"),
    ("ctl00$ContentPlaceHolder1$ddlInstype", "explore"),
    ("ctl00$ContentPlaceHolder1$ddlInstitute", "explore"),
    ("ctl00$ContentPlaceHolder1$ddlBranch", "ALL"),
    ("ctl00$ContentPlaceHolder1$ddlSeatType", "ALL"),
    ("ctl00$ContentPlaceHolder1$btnSubmit", "Submit")
)

# the following code was converted to a recursive function
# post_data = hidden_params.copy()
# for i in range(len(field_data)):
#     field, data = field_data[i]
#     if data == "explore":
#         print("Exploring field:", field_data[i][0], soup.find("select", {"name": field_data[i][0]}))
#         # print(post_data)
#         itemlist = [item["value"] for item in soup.find("select", {"name": field_data[i][0]}).find_all("option")][2:] # remove "0" and "ALL"
#         print(itemlist)
#         data = itemlist[0] 
        
        
        
#     post_data.update({field: data})
#     post_data["__EVENTTARGET"] = field
#     res = session.post("https://josaa.admissions.nic.in/applicant/seatmatrix/openingclosingrankarchieve.aspx", data=post_data)
#     soup = BeautifulSoup(res.text, 'html.parser')
#     hidden_params = {item["name"]: item.get("value", "") for item in soup.find_all("input", {"type": "hidden"})}
#     post_data.update(hidden_params)

def explore_field(index, post_data):
    field, data = field_data[index]
    print(f"Exploring field: {field}, data: {data}, index: {index}")
    post_data = post_data.copy()  # make a copy of post_data to avoid modifying the original
    # request current field to get the next field data. field:data is supposed to be filled by the caller function
    post_data["__EVENTTARGET"] = field
    res = session.post("https://josaa.admissions.nic.in/applicant/seatmatrix/openingclosingrankarchieve.aspx", data=post_data)
    soup = BeautifulSoup(res.text, 'html.parser')
    hidden_params = {item["name"]: item.get("value", "") for item in soup.find_all("input", {"type": "hidden"})}
    post_data.update(hidden_params)
    
    if index == len(field_data) - 1:  # if we have reached the last field, return
        table = soup.find("table")
        table = pd.read_html(str(table))[0]
        # delete last row from the table if it is empty
        table.dropna(inplace=True, how='all')
        with open('exported_data/csv/josaa24.csv', 'a', encoding='utf-8') as f:
            table.to_csv(f, index=False, header=False, mode='a')
        return
    
    if field_data[index + 1][1] == "explore": # if the next field's data has a list of items to explore
        itemlist = [item["value"] for item in soup.find("select", {"name": field_data[index+1][0]}).find_all("option")][2:]
        print(itemlist)
        # if not itemlist:
        #     print(soup.prettify())
        for item in itemlist:
            post_data.update({field_data[index + 1][0]: item}) # fill data for next call
            explore_field(index + 1, post_data)
            print(f"Explored {field_data[index+1][0]} with value {item}")
    else:
        post_data.update({field_data[index+1][0]: field_data[index+1][1]})
        explore_field(index+1, post_data) # if definite data, just go to the next field


with open('exported_data/csv/josaa24.csv', 'w', encoding='utf-8') as f:
    f.write("Institute,Academic Program Name,Quota,Seat Type,Gender,Opening Rank,Closing Rank\n")  # write header
# start exploring from the first field
post_data = hidden_params.copy()
post_data.update({field_data[0][0]: field_data[0][1]}) # set the first field data. 
explore_field(0, post_data)

    #print(res.text)

# post_data = {
#     "ctl00$ContentPlaceHolder1$ddlYear": "2024",
#     "ctl00$ContentPlaceHolder1$ddlroundno": "5",
#     "__EVENTTARGET": field
#     }
# post_data = {
#     "ctl00$ContentPlaceHolder1$ddlYear": "2024",
#     "ctl00$ContentPlaceHolder1$ddlroundno": "5",
#     "ctl00$ContentPlaceHolder1$ddlInstype": "IIT",
#     "ctl00$ContentPlaceHolder1$ddlInstitute": "102",
#     "ctl00$ContentPlaceHolder1$ddlBranch": "ALL",
#     "ctl00$ContentPlaceHolder1$ddlSeatType": "ALL",
#     "ctl00$ContentPlaceHolder1$btnSubmit": "Submit"
# }