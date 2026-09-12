import csv
import sqlite3
from database import DATABASE, create_database

create_database()

CSV_FILE = "vehicle_data.csv"

connection = sqlite3.connect(DATABASE)

with open(CSV_FILE, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        connection.execute(
            """
            INSERT OR IGNORE INTO vehicles
            (
                make,
                model,
                year,
                engine,
                horsepower,
                mpg_city,
                mpg_highway,
                drivetrain,
                seating
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["make"],
                row["model"],
                int(row["year"]),
                row["engine"],
                int(row["horsepower"]),
                int(row["mpg_city"]),
                int(row["mpg_highway"]),
                row["drivetrain"],
                int(row["seating"])
            )
        )

connection.commit()
connection.close()

print("Vehicle data imported successfully!")