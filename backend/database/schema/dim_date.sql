CREATE TABLE Dim_Date (
    DateKey INTEGER PRIMARY KEY,
    Full_Date DATE UNIQUE,
    Day_Number INTEGER,
    Day_Name VARCHAR(20),
    Week_Number INTEGER,
    Month_Number INTEGER,
    Month_Name VARCHAR(20),
    Quarter INTEGER,
    Year INTEGER,
    Is_Weekend BOOLEAN
);