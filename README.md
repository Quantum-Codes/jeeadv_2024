# JEE 2024 JOSAA dataset

All this data was already available publicly through the published JIC reports available on the jeeadv website and also the JoSAA website. This is just a more readable form (excel sheets or CSVs).

The goal of the project is to provide all data of the JIC report and JoSAA opening closing ranks in a more accessible way to all students in form of an excel spreadsheet which they can utilize make better decisions for the JOSAA councelling 2025+ and to also put them in a readable format for those curious about performance statistics.

Also for anyone curious, the whole `main.py` and `webscraper.py` has a lot of comments explaining the code and how it works and which decisions were made, so you can also check that out to understand how the data was processed.<br>
The data for NITs, IIITs and GFTIs are webscraped from the JOSAA website using `requests` and `BeautifulSoup` libraries, while the IIT data is taken from the JIC report available on the jeeadv website. Webscraping script is at `webscraper.py` and can be modified a bit to even scrape Seat matrix too!<br>



## Accessing the Data

The Excel sheets and CSV files can be accessed from the `exported_data`  directory in this repository. Simply navigate to the folder and download the required files.
It's recommended to download the `combined.xlsx` file present in `exported_data/excel` directory.

## About the files

### combined.xlsx
This file contains all the data from the other files in a single file and also contains some manual fixes to the data (ORCR) which is not present in the other files.<br>
It is highly recommended to use this file over the others.

### ORCR.xlsx
 
ORCR is an acronym for "Opening Ranks and Closing Ranks". It consists of the opening and closing ranks for each course offered by every IIT.<br>
It contains all the data present in the JOSAA website but in form of an excel sheet. This enables the user to compare multiple colleges offering the same branch, check all possible seats available for them at their rank and even more using excel's filters/formulae which would have been very tedious if done manually searching each item individually in the website.

### josaa24.xlsx

Contains ALL the institutes (IIT, NIT, IIIT, GFTI) opening and closing ranks for all categories including preparatory ranks marked as P (238P = preparatory rank 238).<br>
The `combined.xlsx` file has this data as well, just divided into IIT and mains colleges to remove any confusion.

### choices.xlsx

An “academic program” refers to the combination of academic program and institute.<br>
Every academic program that a student adds in thier prioirity list (in JOSAA) is called as a "choice".
This file contains the number of choices put for every academic program available in JOSAA 2024.<br>
This is independent of the priority order (ie the fact that IITB CS is placed above IITT Civil is ignored)

###  allotment.xlsx

It consists of the data including the academic program, rank, approximate marks for each student who got alloted in an IIT through JOSAA 2024.<br>
To avoid any confusions; CRL stands for "Common Rank Lists" and displays your stance among all students writing the exam regardless of category, AAT stands for "Architecture Aptitude Test" which is conducted every year for the candidates who wish to take admitted to the BArch programme offered by the IIT Kharagpur, IIT Varanasi and IIT Roorkee. 


Note that the marks are "approx" as JIC report does have the marks but are not individually mapped to each roll number, instead the marks are mapped to groups of 100 ranks making it slightly inaccurate. The marks would be slightly off for few candidates but correct for most.














