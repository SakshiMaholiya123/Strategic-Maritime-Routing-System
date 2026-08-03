CREATE TABLE Dim_Strait (
    StraitKey SERIAL PRIMARY KEY,
    Strait_Name VARCHAR(100) UNIQUE NOT NULL,
    Region VARCHAR(100),
    Risk_Level VARCHAR(30),
    Typical_Daily_Transit INTEGER
);