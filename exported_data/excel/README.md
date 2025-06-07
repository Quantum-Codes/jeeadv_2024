# Note

The most updated version is the `combined.xlsx` file, which contains all the data from the other files in a single file and also contains some manual fixes to the data which is not present in the other files.

In `allotment.xlsx`, the marks column is actually the predicted marks since the JIC contained them in groups of roll numbers to marks, so there is some info lost about marks. there is no individual mapping of each roll to marks.
So top 10 people's marks are added manually since they were readily available and others are predicted.

Due to the nature of this grouping (uniform groups) and the normal distribution of marks, people close to the median have accurate marks and people scoring very high or very low have marks that are slightly inaccurate. 

`seat_matrix_25.xlsx` is a combination of `../csv/seat_matrix_25.csv` and `../csv/total_seats.xlsx`.