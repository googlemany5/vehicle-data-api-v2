import zipfile
import csv
import sqlite3

from database import DATABASE, create_database


ZIP_FILE = "recalls.zip"


create_database()

print("Opening NHTSA recall database...")


connection = sqlite3.connect(DATABASE)


# Delete the old incomplete table
connection.execute("DROP TABLE IF EXISTS recalls")


# Create the complete recall table
connection.execute("""
    CREATE TABLE recalls (
        record_id INTEGER PRIMARY KEY,
        campaign_number TEXT,
        make TEXT,
        model TEXT,
        model_year INTEGER,
        manufacturer_campaign_number TEXT,
        component TEXT,
        manufacturer TEXT,
        begin_manufacturing_date TEXT,
        end_manufacturing_date TEXT,
        recall_type TEXT,
        potential_units_affected INTEGER,
        owner_notification_date TEXT,
        recall_initiator TEXT,
        manufacturer_vehicle_product TEXT,
        report_received_date TEXT,
        record_creation_date TEXT,
        regulation_part_number TEXT,
        fmvss TEXT,
        defect_summary TEXT,
        consequence_summary TEXT,
        corrective_action TEXT,
        notes TEXT,
        component_id TEXT
    )
""")


print("Importing recall records...")


with zipfile.ZipFile(ZIP_FILE, "r") as zip_file:

    with zip_file.open("FLAT_RCL_POST_2010.txt") as file:

        reader = csv.reader(
            (line.decode("latin-1") for line in file),
            delimiter="\t"
        )

        batch = []
        count = 0

        for row in reader:

            if not row:
                continue

            # Make sure the row has all expected fields
            if len(row) < 24:
                continue

            def clean(value):
                return value.strip() if value else None

            def number(value):
                value = clean(value)

                if not value:
                    return None

                try:
                    return int(value)
                except ValueError:
                    return None

            record = (
                number(row[0]),
                clean(row[1]),
                clean(row[2]),
                clean(row[3]),
                number(row[4]),
                clean(row[5]),
                clean(row[6]),
                clean(row[7]),
                clean(row[8]),
                clean(row[9]),
                clean(row[10]),
                number(row[11]),
                clean(row[12]),
                clean(row[13]),
                clean(row[14]),
                clean(row[15]),
                clean(row[16]),
                clean(row[17]),
                clean(row[18]),
                clean(row[19]),
                clean(row[20]),
                clean(row[21]),
                clean(row[22]),
                clean(row[23])
            )

            batch.append(record)

            if len(batch) >= 5000:

                connection.executemany(
                    """
                    INSERT OR REPLACE INTO recalls (
                        record_id,
                        campaign_number,
                        make,
                        model,
                        model_year,
                        manufacturer_campaign_number,
                        component,
                        manufacturer,
                        begin_manufacturing_date,
                        end_manufacturing_date,
                        recall_type,
                        potential_units_affected,
                        owner_notification_date,
                        recall_initiator,
                        manufacturer_vehicle_product,
                        report_received_date,
                        record_creation_date,
                        regulation_part_number,
                        fmvss,
                        defect_summary,
                        consequence_summary,
                        corrective_action,
                        notes,
                        component_id
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?
                    )
                    """,
                    batch
                )

                connection.commit()

                count += len(batch)

                print(f"Imported {count:,} records...")

                batch = []


        # Import remaining records
        if batch:

            connection.executemany(
                """
                INSERT OR REPLACE INTO recalls (
                    record_id,
                    campaign_number,
                    make,
                    model,
                    model_year,
                    manufacturer_campaign_number,
                    component,
                    manufacturer,
                    begin_manufacturing_date,
                    end_manufacturing_date,
                    recall_type,
                    potential_units_affected,
                    owner_notification_date,
                    recall_initiator,
                    manufacturer_vehicle_product,
                    report_received_date,
                    record_creation_date,
                    regulation_part_number,
                    fmvss,
                    defect_summary,
                    consequence_summary,
                    corrective_action,
                    notes,
                    component_id
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?
                )
                """,
                batch
            )

            connection.commit()

            count += len(batch)


connection.close()


print()
print("================================")
print("RECALL DATA IMPORTED!")
print("================================")
print(f"Records imported: {count:,}")
print("Full recall information is now stored.")