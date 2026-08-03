import pandas as pd
from sqlalchemy import text
from backend.config import Config 
from backend.database.create_database import engine


ports = pd.read_csv(Config.DATASET_PATH / "ports.csv")


required_columns = [

    "Port_ID",
    "Port_Name",
    "Country",
    "Port_Type",
    "Port_Capacity_Tons",
    "Avg_Vessel_Wait_Time_Hours",
    "Port_Utilization_Percent",
    "Active_Vessels",
    "Weather_Disruption_Score",
    "Labor_Availability_Percent",
    "Monthly_Port_Revenue_USD",
    "Operational_Status",
    "Port_Manager",
    "Last_Inspection_Date",
    "Latitude",
    "Longitude"

]

missing_columns = set(required_columns) - set(ports.columns)

if missing_columns:

    raise ValueError(
        f"Missing columns: {missing_columns}"
    )

# Data Cleaning

ports = ports[required_columns]

ports = ports.drop_duplicates(
    subset=["Port_ID"]
)

ports["Last_Inspection_Date"] = pd.to_datetime(
    ports["Last_Inspection_Date"],
    errors="coerce"
).dt.date

ports = ports.where(
    pd.notnull(ports),
    None
)

# Insert Query
query = text("""

INSERT INTO maritime.Dim_Port(

    Port_ID,
    Port_Name,
    Country,
    Port_Type,
    Port_Capacity_Tons,
    Avg_Vessel_Wait_Time_Hours,
    Port_Utilization_Percent,
    Active_Vessels,
    Weather_Disruption_Score,
    Labor_Availability_Percent,
    Monthly_Port_Revenue_USD,
    Operational_Status,
    Port_Manager,
    Last_Inspection_Date,
    Latitude,
    Longitude

)

VALUES(

    :Port_ID,
    :Port_Name,
    :Country,
    :Port_Type,
    :Port_Capacity_Tons,
    :Avg_Vessel_Wait_Time_Hours,
    :Port_Utilization_Percent,
    :Active_Vessels,
    :Weather_Disruption_Score,
    :Labor_Availability_Percent,
    :Monthly_Port_Revenue_USD,
    :Operational_Status,
    :Port_Manager,
    :Last_Inspection_Date,
    :Latitude,
    :Longitude

)

ON CONFLICT (Port_ID)

DO UPDATE SET

    Port_Name = EXCLUDED.Port_Name,
    Country = EXCLUDED.Country,
    Port_Type = EXCLUDED.Port_Type,
    Port_Capacity_Tons = EXCLUDED.Port_Capacity_Tons,
    Avg_Vessel_Wait_Time_Hours = EXCLUDED.Avg_Vessel_Wait_Time_Hours,
    Port_Utilization_Percent = EXCLUDED.Port_Utilization_Percent,
    Active_Vessels = EXCLUDED.Active_Vessels,
    Weather_Disruption_Score = EXCLUDED.Weather_Disruption_Score,
    Labor_Availability_Percent = EXCLUDED.Labor_Availability_Percent,
    Monthly_Port_Revenue_USD = EXCLUDED.Monthly_Port_Revenue_USD,
    Operational_Status = EXCLUDED.Operational_Status,
    Port_Manager = EXCLUDED.Port_Manager,
    Last_Inspection_Date = EXCLUDED.Last_Inspection_Date,
    Latitude = EXCLUDED.Latitude,
    Longitude = EXCLUDED.Longitude;

""")

# Load Data

with engine.begin() as connection:

    connection.execute(

        query,

        ports.to_dict(orient="records")

    )
# Summary


print("=" * 60)
print("Dim_Port Loaded Successfully")
print("=" * 60)
print(f"Rows Loaded : {len(ports)}")
print(f"Columns     : {len(ports.columns)}")
print("=" * 60)