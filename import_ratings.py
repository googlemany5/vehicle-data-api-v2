import pandas as pd
import sqlite3

DATABASE = "vehicles.db"
CSV_FILE = "Safercar_data.csv"

print("Loading NHTSA safety data...")

df = pd.read_csv(
    CSV_FILE,
    encoding="latin-1",
    low_memory=False
)

print(f"Loaded {len(df)} vehicles.")
print("Importing into database...")

connection = sqlite3.connect(DATABASE)

df.to_sql(
    "safety_ratings",
    connection,
    if_exists="replace",
    index=False
)

connection.close()

print("================================")
print("NHTSA DATA IMPORTED!")
print("================================")
print(f"Records imported: {len(df)}")
print("Table: safety_ratings")