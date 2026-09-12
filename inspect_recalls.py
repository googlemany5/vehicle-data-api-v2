import zipfile
import os

ZIP_FILE = "recalls.zip"

print("Opening recall database...")

with zipfile.ZipFile(ZIP_FILE, "r") as zip_file:

    files = zip_file.namelist()

    print()
    print("FILES INSIDE ZIP:")
    print()

    for file in files:
        print(file)

print()
print("Inspection complete!")