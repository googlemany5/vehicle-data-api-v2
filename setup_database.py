import sqlite3
from database import create_database, DATABASE


create_database()


vehicles = [
    ("Ford", "F-150", 2025, "3.5L V6", 430, 20, 26, "4WD", 5),
    ("Toyota", "Camry", 2025, "2.5L 4-Cylinder", 225, 53, 50, "FWD", 5),
    ("Chevrolet", "Corvette", 2025, "6.2L V8", 495, 16, 24, "RWD", 2),
    ("Honda", "Civic", 2025, "2.0L 4-Cylinder", 150, 30, 38, "FWD", 5),

    ("Ford", "F-250", 2025, "6.7L V8", 500, 15, 20, "4WD", 5),
    ("Toyota", "GR Supra", 2025, "3.0L I6", 382, 23, 31, "RWD", 2),
    ("Chevrolet", "Tahoe", 2025, "5.3L V8", 355, 15, 20, "4WD", 7),
    ("BMW", "M3", 2025, "3.0L I6", 473, 16, 23, "RWD", 5),
    ("Tesla", "Model 3", 2025, "Electric", 510, 138, 126, "AWD", 5)
]


connection = sqlite3.connect(DATABASE)


connection.executemany(
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
    vehicles
)


connection.commit()
connection.close()


print("Vehicle database created successfully!")
print(f"{len(vehicles)} test vehicles loaded.")