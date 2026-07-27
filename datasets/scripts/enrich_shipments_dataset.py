import random
from pathlib import Path
from datetime import timedelta

import pandas as pd
from faker import Faker


fake = Faker()

random.seed(42)
Faker.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent


shipments = pd.read_csv(BASE_DIR / "raw" / "supply_chain_hormuz_crisis_700.csv")

ports = (
    pd.read_csv(BASE_DIR / "processed" / "ports.csv")
    .drop_duplicates(subset=["Port_ID"])
    .reset_index(drop=True)
)

vessels = pd.read_csv(BASE_DIR / "processed" / "vessels.csv")
routes = pd.read_csv(BASE_DIR / "processed" / "routes.csv")

port_ids = ports["Port_ID"].tolist()
vessel_ids = vessels["Vessel_ID"].tolist()
route_ids = routes["Route_ID"].tolist()

shipment_status = [
    "Pending",
    "In Transit",
    "Delayed",
    "Delivered"
]

cargo_types = {
    "Electronics": (500000, 3000000),
    "Oil": (1500000, 5000000),
    "Chemicals": (750000, 3500000),
    "Machinery": (600000, 2500000),
    "Food": (100000, 800000),
    "Automobile": (800000, 4000000)
}


vessel_column = []
origin_port_column = []
destination_port_column = []
route_column = []
cargo_value_column = []
shipment_date_column = []
shipment_status_column = []

for _, row in shipments.iterrows():

    # Vessel
    vessel = random.choice(vessel_ids)

    # Route
    route = routes.sample(1).iloc[0]

    origin = route["Origin_Port_ID"]
    destination = route["Destination_Port_ID"]

    # Cargo Value
    product = row["Product_Type"]

    if product in cargo_types:
        low, high = cargo_types[product]
    else:
        low, high = (200000, 2500000)

    cargo_value = random.randint(low, high)

    # Shipment Date (within last year)
    shipment_date = fake.date_between(
        start_date="-365d",
        end_date="today"
    )

    # Status
    status = random.choices(
        shipment_status,
        weights=[15, 40, 20, 25],
        k=1
    )[0]

    vessel_column.append(vessel)
    origin_port_column.append(origin)
    destination_port_column.append(destination)
    route_column.append(route["Route_ID"])
    cargo_value_column.append(cargo_value)
    shipment_date_column.append(shipment_date)
    shipment_status_column.append(status)



shipments["Vessel_ID"] = vessel_column
shipments["Origin_Port_ID"] = origin_port_column
shipments["Destination_Port_ID"] = destination_port_column
shipments["Route_ID"] = route_column
shipments["Cargo_Value_USD"] = cargo_value_column
shipments["Shipment_Date"] = shipment_date_column
shipments["Shipment_Status"] = shipment_status_column


OUTPUT_DIR = BASE_DIR / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "shipments.csv"

shipments.to_csv(OUTPUT_FILE, index=False)

print(shipments.head())