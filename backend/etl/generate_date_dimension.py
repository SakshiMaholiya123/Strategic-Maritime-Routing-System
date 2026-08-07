from datetime import datetime
import pandas as pd
from sqlalchemy import text
from backend.database.create_database import engine


START_DATE = "2024-01-01"
END_DATE = "2030-12-31"

CHUNK_SIZE = 200


dates = pd.date_range(
    start=START_DATE,
    end=END_DATE,
    freq="D"
)

date_df = pd.DataFrame({

    "DateKey": dates.strftime("%Y%m%d").astype(int),

    "Full_Date": dates.date,

    "Day_Number": dates.day,

    "Day_Name": dates.day_name(),

    "Week_Number": dates.isocalendar().week.astype(int),

    "Month_Number": dates.month,

    "Month_Name": dates.month_name(),

    "Quarter": dates.quarter,

    "Year": dates.year,

    "Is_Weekend": dates.dayofweek >= 5

})

insert_query = text("""

INSERT INTO maritime.Dim_Date (

    DateKey,
    Full_Date,
    Day_Number,
    Day_Name,
    Week_Number,
    Month_Number,
    Month_Name,
    Quarter,
    Year,
    Is_Weekend

)

VALUES (

    :DateKey,
    :Full_Date,
    :Day_Number,
    :Day_Name,
    :Week_Number,
    :Month_Number,
    :Month_Name,
    :Quarter,
    :Year,
    :Is_Weekend

)

ON CONFLICT (DateKey) DO NOTHING;

""")

rows = date_df.to_dict(orient="records")

rows_inserted = 0

for i in range(0, len(rows), CHUNK_SIZE):

    chunk = rows[i:i + CHUNK_SIZE]

    with engine.begin() as connection:
        connection.execute(insert_query, chunk)

    rows_inserted += len(chunk)

    print(f"Inserted {rows_inserted}/{len(rows)} rows...")

print("=" * 60)
print("Date Dimension Loaded Successfully")
print("=" * 60)

print(f"Start Date : {START_DATE}")
print(f"End Date   : {END_DATE}")
print(f"Rows       : {rows_inserted}")

print("=" * 60)