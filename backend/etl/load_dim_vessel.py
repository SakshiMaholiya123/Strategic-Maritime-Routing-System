import pandas as pd
from sqlalchemy import text
from backend.config import Config
from backend.database.create_database import engine

vessels = pd.read_csv(
    Config.DATASET_PATH / "vessels.csv"
)


required_columns = [

    "Vessel_ID",
    "Vessel_Name",
    "IMO_Number",
    "Vessel_Type",
    "Capacity_Tons",
    "Fuel_Consumption_TPD",
    "Max_Speed_Knots",
    "Current_Status",
    "Home_Port_ID",
    "Year_Built",
    "Crew_Size"

]

missing_columns = set(required_columns) - set(vessels.columns)

if missing_columns:

    raise ValueError(
        f"Missing Columns : {missing_columns}"
    )


vessels = vessels[required_columns]

vessels = vessels.drop_duplicates(
    subset=["Vessel_ID"]
)

vessels = vessels.where(
    pd.notnull(vessels),
    None
)

query = text("""

INSERT INTO maritime.Dim_Vessel(

    Vessel_ID,
    Vessel_Name,
    IMO_Number,
    Vessel_Type,
    Capacity_Tons,
    Fuel_Consumption_TPD,
    Max_Speed_Knots,
    Current_Status,
    Home_Port_ID,
    Year_Built,
    Crew_Size

)

VALUES(

    :Vessel_ID,
    :Vessel_Name,
    :IMO_Number,
    :Vessel_Type,
    :Capacity_Tons,
    :Fuel_Consumption_TPD,
    :Max_Speed_Knots,
    :Current_Status,
    :Home_Port_ID,
    :Year_Built,
    :Crew_Size

)

ON CONFLICT (Vessel_ID)

DO UPDATE SET

    Vessel_Name = EXCLUDED.Vessel_Name,
    IMO_Number = EXCLUDED.IMO_Number,
    Vessel_Type = EXCLUDED.Vessel_Type,
    Capacity_Tons = EXCLUDED.Capacity_Tons,
    Fuel_Consumption_TPD = EXCLUDED.Fuel_Consumption_TPD,
    Max_Speed_Knots = EXCLUDED.Max_Speed_Knots,
    Current_Status = EXCLUDED.Current_Status,
    Home_Port_ID = EXCLUDED.Home_Port_ID,
    Year_Built = EXCLUDED.Year_Built,
    Crew_Size = EXCLUDED.Crew_Size;

""")

with engine.begin() as connection:

    connection.execute(

        query,

        vessels.to_dict(orient="records")

    )

print("=" * 60)
print("Dim_Vessel Loaded Successfully")
print("=" * 60)
print(f"Rows Loaded : {len(vessels)}")
print(f"Columns     : {len(vessels.columns)}")
print("=" * 60)