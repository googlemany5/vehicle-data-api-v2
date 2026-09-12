import sqlite3
import secrets
from datetime import datetime


DATABASE = "vehicles.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,

            engine TEXT,
            horsepower INTEGER,
            mpg_city INTEGER,
            mpg_highway INTEGER,

            drivetrain TEXT,
            seating INTEGER,

            vehicle_type TEXT,
            body_class TEXT,
            cylinders INTEGER,
            fuel_type TEXT,
            transmission TEXT,
            manufacturer TEXT,

            UNIQUE(make, model, year)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            requests_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_vehicle(vehicle):
    connection = get_connection()

    connection.execute(
        """
        INSERT OR IGNORE INTO vehicles
        (
            make,
            model,
            year,
            engine,
            drivetrain,
            vehicle_type,
            body_class,
            cylinders,
            fuel_type,
            transmission,
            manufacturer
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            vehicle.get("make"),
            vehicle.get("model"),
            vehicle.get("year"),
            vehicle.get("engine"),
            vehicle.get("drive_type"),
            vehicle.get("vehicle_type"),
            vehicle.get("body_class"),
            vehicle.get("cylinders"),
            vehicle.get("fuel"),
            vehicle.get("transmission"),
            vehicle.get("manufacturer")
        )
    )

    connection.commit()
    connection.close()


def create_api_key(name):
    api_key = secrets.token_urlsafe(32)

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO api_keys
        (
            api_key,
            name,
            requests_count,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            api_key,
            name,
            0,
            datetime.utcnow().isoformat()
        )
    )

    connection.commit()
    connection.close()

    return api_key


def validate_api_key(api_key):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM api_keys
        WHERE api_key = ?
        """,
        (api_key,)
    ).fetchone()

    connection.close()

    return row


def increment_usage(api_key):
    connection = get_connection()

    connection.execute(
        """
        UPDATE api_keys
        SET requests_count = requests_count + 1
        WHERE api_key = ?
        """,
        (api_key,)
    )

    connection.commit()
    connection.close()