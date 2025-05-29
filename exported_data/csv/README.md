# Notice

Use these files if you want to do something with the data manually in code, 
else its a better choice to just use the excel files that is also present in this repo.

The excel files are formatted as a table so you can do simple sorting and filtering using excel for most use cases.

In `allotment.csv`, the marks column is actually the predicted marks since the JIC contained them in groups of roll numbers to marks, so there is some info lost about marks. there is no individual mapping of each roll to marks.

Due to the nature of this grouping (uniform groups) and the normal distribution of marks, people close to the median have accurate marks and people scoring very high or very low have marks that are slightly inaccurate.

Also in `ORCR.csv`, the info of preparatory and PwD candidates is removed since it is not labelled properly in the JIC data and it is not possible to determine which rank is for which category unless we also cross reference with the allotment data which I didn't do because of lack of gender divided data. The data changed manually (in `combined.xlsx`, not here) is of Architechture branches of IIT (BHU) Varanasi and IIT Roorkee, and of some other branches of ST female only with opening and closing ranks of preparatory candidates removed. BHU's chemical closing rank was modified after cross referencing with allotment data to remove the preparatory closing rank which wasnt labelled correctly in the JIC data.