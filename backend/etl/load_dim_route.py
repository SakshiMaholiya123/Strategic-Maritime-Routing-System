import pandas as pd
from sqlalchemy import text
from backend.config import Config
from backend.database.create_database import engine

routes = pd.read_csv(
    Config.DATASET_PATH / "routes.csv"
)

required_columns = [

    "Route_ID",
    "Origin_Port_ID",
    "Destination_Port_ID",
    "Route_Name",
    "Distance_NM",
    "Expected_Days",
    "Risk_Zone",
    "Canal_Used",
    "Weather_Risk"

]

missing_columns = set(required_columns) - set(routes.columns)

if missing_columns:

    raise ValueError(
        f"Missing Columns : {missing_columns}"
    )

routes = routes[required_columns]

routes = routes.drop_duplicates(
    subset=["Route_ID"]
)

routes = routes.where(
    pd.notnull(routes),
    None
)


query = text("""

INSERT INTO maritime.Dim_Route(

    Route_ID,
    Origin_Port_ID,
    Destination_Port_ID,
    Route_Name,
    Distance_NM,
    Expected_Days,
    Risk_Zone,
    Canal_Used,
    Weather_Risk

)

VALUES(

    :Route_ID,
    :Origin_Port_ID,
    :Destination_Port_ID,
    :Route_Name,
    :Distance_NM,
    :Expected_Days,
    :Risk_Zone,
    :Canal_Used,
    :Weather_Risk

)

ON CONFLICT (Route_ID)

DO UPDATE SET

    Origin_Port_ID = EXCLUDED.Origin_Port_ID,
    Destination_Port_ID = EXCLUDED.Destination_Port_ID,
    Route_Name = EXCLUDED.Route_Name,
    Distance_NM = EXCLUDED.Distance_NM,
    Expected_Days = EXCLUDED.Expected_Days,
    Risk_Zone = EXCLUDED.Risk_Zone,
    Canal_Used = EXCLUDED.Canal_Used,
    Weather_Risk = EXCLUDED.Weather_Risk;

""")

with engine.begin() as connection:

    connection.execute(

        query,

        routes.to_dict(orient="records")

    )

print("=" * 60)
print("Dim_Route Loaded Successfully")
print("=" * 60)
print(f"Rows Loaded : {len(routes)}")
print(f"Columns     : {len(routes.columns)}")
print("=" * 60)