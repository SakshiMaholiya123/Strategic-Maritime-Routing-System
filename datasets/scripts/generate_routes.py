import random
import pandas as pd
from pathlib import Path

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent

ports = pd.read_csv(BASE_DIR / "processed" / "ports.csv")

risk = [
    "Low",
    "Medium",
    "High",
    "Critical"
]

canals = [
    "Strait of Hormuz",
    "Suez Canal",
    "Cape of Good Hope",
    "None"
]

weather = [
    "Low",
    "Medium",
    "High"
]

rows = []

for i in range(1,51):

    origin = ports.sample(1).iloc[0]

    destination = ports.sample(1).iloc[0]

    while destination["Port_ID"] == origin["Port_ID"]:

        destination = ports.sample(1).iloc[0]

    rows.append({

        "Route_ID": f"R{i:03}",

        "Origin_Port_ID": origin["Port_ID"],

        "Destination_Port_ID": destination["Port_ID"],

        "Route_Name": f'{origin["Port_Name"]} → {destination["Port_Name"]}',

        "Distance_NM": random.randint(500,12000),

        "Expected_Days": random.randint(3,35),

        "Risk_Zone": random.choice(risk),

        "Canal_Used": random.choice(canals),

        "Weather_Risk": random.choice(weather)

    })

routes = pd.DataFrame(rows)

routes.to_csv(BASE_DIR/"processed"/"routes.csv",index=False)

print(routes.head())