from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
import time
import os
from dotenv import load_dotenv

from database import (
    get_connection,
    save_vehicle,
    validate_api_key,
    increment_usage
)


# Load environment variables
load_dotenv()


app = FastAPI(
    title="Vehicle Data API",
    description="Vehicle specifications, VIN decoding, recalls, safety ratings, search, and comparison.",
    version="1.0.0"
)


# -----------------------------
# API KEY SECURITY
# -----------------------------

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


# -----------------------------
# RATE LIMITING
# -----------------------------

RATE_LIMIT = int(os.getenv("RATE_LIMIT", "60"))
RATE_WINDOW = int(os.getenv("RATE_WINDOW", "60"))

request_log = {}


def authenticate_and_limit(
    api_key: str = Depends(api_key_header)
):

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key"
        )

    key = validate_api_key(api_key)

    if key is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    current_time = time.time()

    if api_key not in request_log:
        request_log[api_key] = []

    request_log[api_key] = [
        timestamp
        for timestamp in request_log[api_key]
        if current_time - timestamp < RATE_WINDOW
    ]

    if len(request_log[api_key]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )

    request_log[api_key].append(current_time)

    increment_usage(api_key)

    return key


def authenticate_only(
    api_key: str = Depends(api_key_header)
):

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key"
        )

    key = validate_api_key(api_key)

    if key is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return key


# -----------------------------
# HOME
# -----------------------------

@app.get("/")
def home():

    return {
        "message": "Vehicle Data API is working!",
        "version": "1.0.0"
    }


# -----------------------------
# HEALTH CHECK
# -----------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# -----------------------------
# GET ALL VEHICLES
# -----------------------------

@app.get("/vehicles")
def get_vehicles(
    api_key=Depends(authenticate_and_limit)
):

    connection = get_connection()

    rows = connection.execute(
        "SELECT * FROM vehicles"
    ).fetchall()

    connection.close()

    return {
        "count": len(rows),
        "vehicles": [dict(row) for row in rows]
    }


# -----------------------------
# GET ONE VEHICLE
# -----------------------------

@app.get("/vehicle")
def get_vehicle(
    make: str,
    model: str,
    year: int,
    api_key=Depends(authenticate_and_limit)
):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM vehicles
        WHERE LOWER(make) = LOWER(?)
        AND LOWER(model) = LOWER(?)
        AND year = ?
        """,
        (make, model, year)
    ).fetchone()

    connection.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    return dict(row)


# -----------------------------
# SEARCH VEHICLES
# -----------------------------

@app.get("/search")
def search_vehicles(
    make: str = "",
    model: str = "",
    year: int = 0,
    min_horsepower: int = 0,
    max_horsepower: int = 0,
    min_mpg: int = 0,
    max_mpg: int = 0,
    drivetrain: str = "",
    vehicle_type: str = "",
    fuel_type: str = "",
    api_key=Depends(authenticate_and_limit)
):

    connection = get_connection()

    query = "SELECT * FROM vehicles WHERE 1=1"
    parameters = []

    if make:
        query += " AND LOWER(make) = LOWER(?)"
        parameters.append(make)

    if model:
        query += " AND LOWER(model) = LOWER(?)"
        parameters.append(model)

    if year:
        query += " AND year = ?"
        parameters.append(year)

    if min_horsepower:
        query += " AND horsepower >= ?"
        parameters.append(min_horsepower)

    if max_horsepower:
        query += " AND horsepower <= ?"
        parameters.append(max_horsepower)

    if min_mpg:
        query += " AND mpg_city >= ?"
        parameters.append(min_mpg)

    if max_mpg:
        query += " AND mpg_city <= ?"
        parameters.append(max_mpg)

    if drivetrain:
        query += " AND LOWER(drivetrain) = LOWER(?)"
        parameters.append(drivetrain)

    if vehicle_type:
        query += " AND LOWER(vehicle_type) = LOWER(?)"
        parameters.append(vehicle_type)

    if fuel_type:
        query += " AND LOWER(fuel_type) = LOWER(?)"
        parameters.append(fuel_type)

    rows = connection.execute(
        query,
        parameters
    ).fetchall()

    connection.close()

    return {
        "count": len(rows),
        "vehicles": [dict(row) for row in rows]
    }


# -----------------------------
# GET MAKES
# -----------------------------

@app.get("/makes")
def get_makes(
    api_key=Depends(authenticate_and_limit)
):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT DISTINCT make
        FROM vehicles
        ORDER BY make
        """
    ).fetchall()

    connection.close()

    return {
        "makes": [row["make"] for row in rows]
    }


# -----------------------------
# GET MODELS
# -----------------------------

@app.get("/models")
def get_models(
    make: str,
    api_key=Depends(authenticate_and_limit)
):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT DISTINCT model
        FROM vehicles
        WHERE LOWER(make) = LOWER(?)
        ORDER BY model
        """,
        (make,)
    ).fetchall()

    connection.close()

    return {
        "make": make,
        "models": [row["model"] for row in rows]
    }


# -----------------------------
# GET YEARS
# -----------------------------

@app.get("/years")
def get_years(
    make: str,
    model: str,
    api_key=Depends(authenticate_and_limit)
):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT DISTINCT year
        FROM vehicles
        WHERE LOWER(make) = LOWER(?)
        AND LOWER(model) = LOWER(?)
        ORDER BY year DESC
        """,
        (make, model)
    ).fetchall()

    connection.close()

    return {
        "make": make,
        "model": model,
        "years": [row["year"] for row in rows]
    }


# -----------------------------
# NHTSA VIN DECODER
# -----------------------------

@app.get("/nhtsa/{vin}")
def get_nhtsa_vehicle(
    vin: str,
    api_key=Depends(authenticate_and_limit)
):

    import requests

    vin = vin.strip().upper()

    if len(vin) != 17:
        raise HTTPException(
            status_code=400,
            detail="VIN must be exactly 17 characters"
        )

    url = (
        "https://vpic.nhtsa.dot.gov/api/vehicles/"
        f"DecodeVinValues/{vin}?format=json"
    )

    try:
        response = requests.get(
            url,
            timeout=10
        )

    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to NHTSA"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="NHTSA request failed"
        )

    data = response.json()

    results = data.get("Results", [])

    if not results:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    vehicle = results[0]

    vehicle_data = {
        "make": vehicle.get("Make"),
        "model": vehicle.get("Model"),
        "year": vehicle.get("ModelYear"),
        "engine": vehicle.get("EngineModel"),
        "drive_type": vehicle.get("DriveType"),
        "vehicle_type": vehicle.get("VehicleType"),
        "body_class": vehicle.get("BodyClass"),
        "cylinders": vehicle.get("EngineCylinders"),
        "fuel": vehicle.get("FuelTypePrimary"),
        "transmission": vehicle.get("TransmissionStyle"),
        "manufacturer": vehicle.get("Manufacturer")
    }

    save_vehicle(vehicle_data)

    return {
        "vin": vin,
        "make": vehicle_data["make"],
        "model": vehicle_data["model"],
        "year": vehicle_data["year"],
        "vehicle_type": vehicle_data["vehicle_type"],
        "body_class": vehicle_data["body_class"],
        "engine": vehicle_data["engine"],
        "cylinders": vehicle_data["cylinders"],
        "fuel": vehicle_data["fuel"],
        "transmission": vehicle_data["transmission"],
        "drive_type": vehicle_data["drive_type"],
        "manufacturer": vehicle_data["manufacturer"]
    }


# -----------------------------
# VEHICLE RECALLS
# -----------------------------

@app.get("/recalls")
def get_recalls(
    make: str,
    model: str,
    year: int,
    api_key=Depends(authenticate_and_limit)
):
    import requests

    url = "https://api.nhtsa.gov/recalls/recallsByVehicle"

    response = requests.get(
        url,
        params={
            "make": make,
            "model": model,
            "modelYear": year
        },
        timeout=15
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="NHTSA recall service is unavailable"
        )

    data = response.json()
    recalls = data.get("results", [])

    return {
        "make": make,
        "model": model,
        "year": year,
        "recall_count": len(recalls),
        "recalls": recalls
    }


# -----------------------------
# NHTSA SAFETY RATINGS
# -----------------------------

@app.get("/safety")
def get_safety(
    make: str,
    model: str,
    year: int,
    api_key=Depends(authenticate_and_limit)
):
    import requests

    url = f"https://api.nhtsa.gov/SafetyRatings/modelyear/{year}/make/{make}/model/{model}"

    response = requests.get(url, timeout=15)

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="NHTSA safety ratings service is unavailable"
        )

    data = response.json()

    return {
        "make": make,
        "model": model,
        "year": year,
        "results": data.get("Results", [])
    }


# -----------------------------
# COMPARE VEHICLES
# -----------------------------

@app.get("/compare")
def compare_vehicles(
    make1: str,
    model1: str,
    year1: int,
    make2: str,
    model2: str,
    year2: int,
    api_key=Depends(authenticate_and_limit)
):

    connection = get_connection()

    vehicle1 = connection.execute(
        """
        SELECT *
        FROM vehicles
        WHERE LOWER(make) = LOWER(?)
        AND LOWER(model) = LOWER(?)
        AND year = ?
        """,
        (make1, model1, year1)
    ).fetchone()

    vehicle2 = connection.execute(
        """
        SELECT *
        FROM vehicles
        WHERE LOWER(make) = LOWER(?)
        AND LOWER(model) = LOWER(?)
        AND year = ?
        """,
        (make2, model2, year2)
    ).fetchone()

    connection.close()

    if vehicle1 is None or vehicle2 is None:
        raise HTTPException(
            status_code=404,
            detail="One or both vehicles were not found"
        )

    vehicle1 = dict(vehicle1)
    vehicle2 = dict(vehicle2)

    comparison = {}

    if (
        vehicle1["horsepower"] is not None
        and vehicle2["horsepower"] is not None
    ):
        comparison["horsepower_difference"] = (
            vehicle1["horsepower"] - vehicle2["horsepower"]
        )

    if (
        vehicle1["mpg_city"] is not None
        and vehicle2["mpg_city"] is not None
    ):
        comparison["city_mpg_difference"] = (
            vehicle1["mpg_city"] - vehicle2["mpg_city"]
        )

    if (
        vehicle1["mpg_highway"] is not None
        and vehicle2["mpg_highway"] is not None
    ):
        comparison["highway_mpg_difference"] = (
            vehicle1["mpg_highway"] - vehicle2["mpg_highway"]
        )

    if (
        vehicle1["seating"] is not None
        and vehicle2["seating"] is not None
    ):
        comparison["seating_difference"] = (
            vehicle1["seating"] - vehicle2["seating"]
        )

    return {
        "vehicle_1": vehicle1,
        "vehicle_2": vehicle2,
        "comparison": comparison
    }


# -----------------------------
# API USAGE
# -----------------------------

@app.get("/usage")
def get_usage(
    api_key=Depends(authenticate_only)
):

    return {
        "api_key_name": api_key["name"],
        "requests_count": api_key["requests_count"]
    }
    

