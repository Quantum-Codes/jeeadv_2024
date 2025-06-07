# ☢️ JEE 2024 JOSAA dataset

Welcome to the JEE 2024 JoSAA dataset! This project aims to make the publicly available JoSAA and JEE Advanced data more accessible and understandable for students participating in future counseling sessions (JoSAA 2025 onwards).

While all this data was already available publicly through official JIC reports on the JEE Advanced website and the JoSAA website, we've transformed it into easy-to-use Excel sheets and CSVs. This allows you to analyze the data more efficiently and make informed decisions during your counseling process.

## 🔬 What's Inside This Dataset?
1. **Opening and Closing Ranks**: Detailed rank data for all participating institutes (IITs, NITs, IIITs, GFTIs).
2. **Seat Matrix**: A clear breakdown of available seats across all institutes and categories.
3. **IIT Allotment Data**: Insights into the academic programs and ranks of students allotted seats in IITs.
4. **JoSAA choice count**: A count on how many people put a branch of an IIT in their priority order.
5. **Derived Statistics**: Various statistics generated from the raw data to provide deeper insights into performance and trends.

## 📊 How Was This Data Processed?
For those interested in the technical details, the entire codebase (specifically `main.py`, `webscraper.py`, and `seat_matrix.py`) is heavily commented in a beginner friendly manner. You can explore these files to understand the data processing, web scraping techniques, and the decisions made during data transformation.<br>
The data for NITs, IIITs and GFTIs are webscraped from the JOSAA website using `requests` and `BeautifulSoup` libraries, while the IIT data is taken from the JIC report available on the jeeadv website. Webscraping script is at `webscraper.py` and `seat_matrix.py`.<br>



## 📂 Accessing the Data

The Excel sheets and CSV files can be accessed from the `exported_data`  directory in this repository. Simply navigate to the folder and download the required files.
> ⚠️ It's recommended to download the `combined.xlsx` file present in `exported_data/excel` directory.

## 📋 About the files

### combined.xlsx  (The only file most need!)
This file contains all the data from the other files in a single file and also contains some manual fixes to the data (ORCR) which is not present in the other files.<br>
It is highly recommended to use this file over the others.<br>
Also available as a [google sheet](https://docs.google.com/spreadsheets/d/1ez1bSFRGYce8Dr5TDo__EJHnm9NkGhE0/edit?usp=sharing&ouid=107837900740285460736&rtpof=true&sd=true)
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

### seat_matrix.xlsx

It consists of the number of seats offered by an institute for every category for a given academic programme as well as the total seats available in that institute.














