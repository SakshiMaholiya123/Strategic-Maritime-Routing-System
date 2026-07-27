import random
from pathlib import Path

import pandas as pd
from faker import Faker


fake = Faker()

random.seed(42)
Faker.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent

routes = pd.read_csv(BASE_DIR / "processed" / "routes.csv")


providers = [
    "Allianz Marine",
    "Lloyd's",
    "AXA XL",
    "Zurich Marine",
    "Chubb Marine",
    "AIG Marine",
    "Tokio Marine",
    "Travelers Marine"
]

coverage_types = [
    "Standard",
    "Comprehensive",
    "Marine Cargo",
    "War Risk"
]

risk_to_premium = {
    "Low": (0.5, 1.2),
    "Medium": (1.3, 2.0),
    "High": (2.1, 3.5),
    "Critical": (3.6, 5.0)
}

rows = []


for index, route in routes.iterrows():

    risk = route["Risk_Zone"]

    min_premium, max_premium = risk_to_premium[risk]

    premium = round(
        random.uniform(min_premium, max_premium),
        2
    )

    effective_date = fake.date_between(
        start_date="-2y",
        end_date="-30d"
    )

    expiry_date = fake.date_between(
        start_date="+30d",
        end_date="+2y"
    )

    rows.append({

        "Insurance_ID": f"INS{index + 1:03}",

        "Route_ID": route["Route_ID"],

        "Insurance_Provider": random.choice(providers),

        "Risk_Level": risk,

        "Premium_Percentage": premium,

        "Coverage_Type": random.choice(coverage_types),

        "Coverage_Limit_USD": random.randint(
            1_000_000,
            10_000_000
        ),

        "Effective_Date": effective_date,

        "Expiry_Date": expiry_date,

        "Claim_Approval_Rate": round(
            random.uniform(75, 99),
            2
        )

    })

insurance = pd.DataFrame(rows)

OUTPUT_DIR = BASE_DIR / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "insurance.csv"

insurance.to_csv(
    OUTPUT_FILE,
    index=False
)

print(insurance.head())