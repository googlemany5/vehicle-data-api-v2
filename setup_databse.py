import sqlite3
from database import create_database, DATABASE

create_database()

vehicles = [
    ("Ford", "F-150", 2025, "3.5L V6", 430, 20, 26, "4WD", 5),
    ("Toyota", "Camry", 2025, "2.5L 4-Cylinder", 225, 53, 50, "FWD", 5),
    ("Chevrolet", "Corvette", 2025, "6.2L V8", 495, 16, 24, "RWD", 2),
    ("Honda", "Civic", 2025, "2.0L 4-Cylinder", 150, 30, 38, "FWD", 5)
]

connection = sqlite3.connect(DATABASE)

connection.executemany("""
    INSERT INTO vehicles
    (make, model, year, engine, horsepower, mpg_city,
     mpg_highway, drivetrain, seating)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", vehicles)

connection.commit()
connection.close()

print("Vehicles added to database!")