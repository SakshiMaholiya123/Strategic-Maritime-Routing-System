import random
import pandas as pd
from faker import Faker
from pathlib import Path

fake = Faker()

random.seed(42)
Faker.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent

ports = pd.read_csv(BASE_DIR / "processed" / "ports.csv")

port_ids = ports["Port_ID"].tolist()

vessel_types = [
    "Container",
    "Bulk Carrier",
    "Oil Tanker",
    "LNG Carrier",
    "Ro-Ro"
]

status = [
    "Active",
    "Docked",
    "Maintenance",
    "In Transit"
]

prefix = [
    "MV",
    "MT"
]

rows = []

for i in range(1, 61):

    rows.append({

        "Vessel_ID": f"V{i:03}",

        "Vessel_Name": f"{random.choice(prefix)} {fake.word().title()} {fake.word().title()}",

        "IMO_Number": random.randint(9000000,9999999),

        "Vessel_Type": random.choice(vessel_types),

        "Capacity_Tons": random.randint(30000,220000),

        "Fuel_Consumption_TPD": random.randint(25,120),

        "Max_Speed_Knots": random.randint(14,28),

        "Current_Status": random.choice(status),

        "Home_Port_ID": random.choice(port_ids),

        "Year_Built": random.randint(2005,2024),

        "Crew_Size": random.randint(18,35)

    })

vessels = pd.DataFrame(rows)

vessels.to_csv(BASE_DIR/"processed"/"vessels.csv",index=False)

print(vessels.head())