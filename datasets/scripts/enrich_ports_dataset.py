import pandas as pd

INPUT_FILE = "datasets/raw/port_operations_master.csv"
OUTPUT_FILE = "datasets/processed/ports.csv"

df = pd.read_csv(INPUT_FILE)

# ---------------------------------------------------
# Real Port Coordinates
# ---------------------------------------------------

PORT_COORDINATES = {
    "Singapore Port": (1.2644, 103.8400),
    "Hamad Port": (25.6839, 51.5450),
    "Nhava Sheva": (18.9490, 72.9500),
    "Khor Fakkan": (25.3313, 56.3419),
    "Rotterdam Hub": (51.9550, 4.1400),
    "Dammam Port": (26.4282, 50.1033),
    "Jebel Ali": (25.0106, 55.0617),
    "Tianjin Port": (38.9790, 117.7640),
    "Ruwais Port": (24.1100, 52.7300),
    "Shanghai Port": (31.2304, 121.4737),
    "Hamburg Port": (53.5461, 9.9661),
    "Qingdao Port": (36.0671, 120.3826),
    "Mundra Port": (22.8390, 69.7210),
    "Ras Laffan": (25.9231, 51.5333),
    "Shuaiba Port": (29.0422, 48.1528),
    "Salalah Port": (16.9539, 54.0046),
    "Fujairah Port": (25.1288, 56.3265),
    "Busan Port": (35.1028, 129.0403),
    "Sohar Port": (24.4970, 56.6360),
    "Basra Oil Terminal": (29.7810, 48.8100)
}

# ---------------------------------------
# Add Coordinates
# ---------------------------------------

df["Latitude"] = df["Port_Name"].map(lambda x: PORT_COORDINATES[x][0])
df["Longitude"] = df["Port_Name"].map(lambda x: PORT_COORDINATES[x][1])

# ---------------------------------------
# Save
# ---------------------------------------

df.to_csv(OUTPUT_FILE, index=False)

print(df.head())
print("\nDataset saved successfully.")