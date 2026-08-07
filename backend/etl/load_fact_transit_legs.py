import pandas as pd
from sqlalchemy import text
from backend.config import Config
from backend.database.create_database import engine

shipments = pd.read_csv(Config.DATASET_PATH / "shipments.csv")


# Resolve surrogate keys from dimension tables
with engine.begin() as connection:

    dim_vessel = pd.read_sql(
        'SELECT "vesselkey" AS "VesselKey", "vessel_id" AS "Vessel_ID" FROM maritime.dim_vessel',
        connection
    )

    dim_route = pd.read_sql(
        'SELECT "routekey" AS "RouteKey", "route_id" AS "Route_ID" FROM maritime.dim_route',
        connection
    )

    dim_port = pd.read_sql(
        'SELECT "portkey" AS "PortKey", "port_id" AS "Port_ID" FROM maritime.dim_port',
        connection
    )
    
shipments = shipments.merge(
    dim_vessel, left_on="Vessel_ID", right_on="Vessel_ID", how="left"
)

shipments = shipments.merge(
    dim_route, left_on="Route_ID", right_on="Route_ID", how="left"
)

shipments = shipments.merge(
    dim_port.rename(columns={"PortKey": "OriginPortKey", "Port_ID": "Origin_Port_ID"}),
    on="Origin_Port_ID", how="left"
)

shipments = shipments.merge(
    dim_port.rename(columns={"PortKey": "DestinationPortKey", "Port_ID": "Destination_Port_ID"}),
    on="Destination_Port_ID", how="left"
)


# Convert Shipment_Date -> ShipmentDateKey (YYYYMMDD)

shipments["ShipmentDateKey"] = (
    pd.to_datetime(shipments["Shipment_Date"], errors="coerce")
    .dt.strftime("%Y%m%d")
    .astype("Int64")
)

# Drop rows where any required FK failed to resolve

before = len(shipments)

shipments = shipments.dropna(
    subset=["VesselKey", "RouteKey", "OriginPortKey", "DestinationPortKey", "ShipmentDateKey"]
)

after = len(shipments)

if before != after:
    print(f"Warning: {before - after} rows dropped due to unresolved FK / date")

shipments = shipments.drop_duplicates(subset=["Shipment_ID"])

shipments = shipments.where(pd.notnull(shipments), None)

# Insert Query

query = text("""

INSERT INTO maritime.Fact_TransitLegs (

    Shipment_ID,
    VesselKey,
    RouteKey,
    OriginPortKey,
    DestinationPortKey,
    ShipmentDateKey,
    Supplier_ID,
    Country,
    Product_Type,
    Monthly_Demand_Tons,
    Shipment_Volume_Tons,
    Route_Risk_Score,
    Historical_Delay_Days,
    Fuel_Price_USD,
    Political_Risk_Index,
    Port_Congestion_Index,
    Inventory_Days,
    Supplier_Reliability,
    Alternative_Supplier_Count,
    Transit_Time_Days,
    Delay_Probability,
    Current_Delay_Days,
    Freight_Cost_USD,
    Revenue_Impact_USD,
    Disruption_Event,
    Cargo_Value_USD,
    Shipment_Status

)

VALUES (

    :Shipment_ID,
    :VesselKey,
    :RouteKey,
    :OriginPortKey,
    :DestinationPortKey,
    :ShipmentDateKey,
    :Supplier_ID,
    :Country,
    :Product_Type,
    :Monthly_Demand_Tons,
    :Shipment_Volume_Tons,
    :Route_Risk_Score,
    :Historical_Delay_Days,
    :Fuel_Price_USD,
    :Political_Risk_Index,
    :Port_Congestion_Index,
    :Inventory_Days,
    :Supplier_Reliability,
    :Alternative_Supplier_Count,
    :Transit_Time_Days,
    :Delay_Probability,
    :Current_Delay_Days,
    :Freight_Cost_USD,
    :Revenue_Impact_USD,
    :Disruption_Event,
    :Cargo_Value_USD,
    :Shipment_Status

)

ON CONFLICT (Shipment_ID) DO NOTHING;

""")

insert_columns = [
    "Shipment_ID", "VesselKey", "RouteKey", "OriginPortKey", "DestinationPortKey",
    "ShipmentDateKey", "Supplier_ID", "Country", "Product_Type", "Monthly_Demand_Tons",
    "Shipment_Volume_Tons", "Route_Risk_Score", "Historical_Delay_Days", "Fuel_Price_USD",
    "Political_Risk_Index", "Port_Congestion_Index", "Inventory_Days", "Supplier_Reliability",
    "Alternative_Supplier_Count", "Transit_Time_Days", "Delay_Probability", "Current_Delay_Days",
    "Freight_Cost_USD", "Revenue_Impact_USD", "Disruption_Event", "Cargo_Value_USD", "Shipment_Status"
]

records = shipments[insert_columns].to_dict(orient="records") 

with engine.begin() as connection:
    connection.execute(query, records)

print("=" * 60)
print("Fact_TransitLegs Loaded Successfully")
print("=" * 60)
print(f"Rows Loaded : {len(records)}")
print("=" * 60)