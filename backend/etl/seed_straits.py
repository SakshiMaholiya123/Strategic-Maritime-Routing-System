from sqlalchemy import text
from backend.database.create_database import engine

straits_data = [
    {"Strait_Name": "Strait of Hormuz", "Region": "Persian Gulf", "Risk_Level": "High", "Typical_Daily_Transit": 18},
    {"Strait_Name": "Strait of Malacca", "Region": "Southeast Asia", "Risk_Level": "Medium", "Typical_Daily_Transit": 90},
    {"Strait_Name": "Bab-el-Mandeb", "Region": "Red Sea", "Risk_Level": "High", "Typical_Daily_Transit": 22},
    {"Strait_Name": "Suez Canal", "Region": "Egypt", "Risk_Level": "Medium", "Typical_Daily_Transit": 50},
]

insert_query = text("""

INSERT INTO maritime.Dim_Strait (
    Strait_Name,
    Region,
    Risk_Level,
    Typical_Daily_Transit
)

VALUES (
    :Strait_Name,
    :Region,
    :Risk_Level,
    :Typical_Daily_Transit
)

ON CONFLICT (Strait_Name) DO NOTHING;

""")

rows_inserted = 0

with engine.begin() as connection:

    for row in straits_data:

        connection.execute(insert_query, row)

        rows_inserted += 1

print("=" * 60)
print("Dim_Strait Seeded Successfully")
print("=" * 60)
print(f"Rows Inserted : {rows_inserted}")
print("=" * 60)