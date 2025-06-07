import requests, os, time
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd

# this file is used to scrape the opening and closing ranks of JOSAA 2024 website to also get NIT, IIIT, GFTI's opening and closing ranks

# to get started to understand this, first go to https://josaa.admissions.nic.in/applicant/seatmatrix/openingclosingrankarchieve.aspx
# and open the developer tools (ctrl+shift+i) and go to the network tab. Then reload the page and see the first request that is made.
# the current one is a GET request to the same URL.
# Stop and start recording network activity to clear it.
# Now try to fill one one of the fields, say you fill 2024 as the year and the site automatically reloads
# the page with the new data. Now you can see that a POST request is made to the same URL with some data.
# This data is sent as form data and contains the values of the fields that were filled. If you navigate to the payload tab then you see all the POST params
# that were sent. You can see that there are some weird stuff too in addition to your 2024 selection. These are .NET variables like __VIEWSTATE, __EVENTVALIDATION, etc.
# if you navigate to the source tab then you can see that these are actually present in the HTML as hidden input fields.
# So the first step is to get these hidden input fields after every single request, save them for next request and then fill the fields that you want to fill.
# there is also a "__EVENTTARGET" field that is used to specify which field is being updated. So we can fill that ourselves.
# now go learn some python, some html, requests package, BeautifulSoup4 package in this order and then come back to this file to understand it better. (or maybe ask gemini to explain it to you)
# this is a relatively harder webscraping cuz of these .NET variables.. its better to try out some simpler webscraping tasks first


# using request sessions to save the session cookie and use headers issued by the site
session = requests.Session()
res = session.get("https://josaa.admissions.nic.in/applicant/seatmatrix/openingclosingrankarchieve.aspx")

soup = BeautifulSoup(res.text, 'html.parser')
hidden_params = {item["name"]: item.get("value", "") for item in soup.find_all("input", {"type": "hidden"})}

field_data = ( # like immutable dict so order is preserved. These are found in the networks tab of browser when a request is made
    ("ctl00$ContentPlaceHolder1$ddlYear", "2024"),
    ("ctl00$ContentPlaceHolder1$ddlroundno", "5"),
    ("ctl00$ContentPlaceHolder1$ddlInstype", "explore"), # explore means that the current field will have a list of items to explore
    ("ctl00$ContentPlaceHolder1$ddlInstitute", "explore"),
    ("ctl00$ContentPlaceHolder1$ddlBranch", "ALL"),
    ("ctl00$ContentPlaceHolder1$ddlSeatType", "ALL"),
    ("ctl00$ContentPlaceHolder1$btnSubmit", "Submit")
)

# the following code was converted to a recursive function. kept it here to come back to try to rewrite to use loops
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


# as it turns out, this is a dfs algorithm lmao (really gotta start DSA soon, i couldve made this a lot faster if i knew it and didnt rediscover the wheel)
def explore_field(index, post_data):
    field, data = field_data[index]
    print(f"Exploring field: {field}, data: {data}, index: {index}")
    post_data = post_data.copy()  # make a copy of post_data to avoid modifying the original
    # request current field to get the next field data. field:data is supposed to be filled by the caller function
    post_data["__EVENTTARGET"] = field
    time.sleep(0.1) # to avoid overwhelming the server with requests (i wont cause a DoS with this but better safe than sorry)
    res = session.post("https://josaa.admissions.nic.in/applicant/seatmatrix/openingclosingrankarchieve.aspx", data=post_data)
    soup = BeautifulSoup(res.text, 'html.parser')
    hidden_params = {item["name"]: item.get("value", "") for item in soup.find_all("input", {"type": "hidden"})}
    post_data.update(hidden_params) # update .NET variables like __VIEWSTATE, __EVENTVALIDATION, etc.
    
    if index == len(field_data) - 1:  # if we have reached the last field, return
        table = soup.find("table")
        table = pd.read_html(StringIO(str(table)))[0]
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
post_data = hidden_params.copy() # we copy everywhere to not modify the original copy
post_data.update({field_data[0][0]: field_data[0][1]}) # set the first field data. 
explore_field(0, post_data)
