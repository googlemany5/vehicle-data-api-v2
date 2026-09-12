import requests

URL = "https://static.nhtsa.gov/nhtsa/downloads/Safercar/Safercar_data.csv"
OUTPUT_FILE = "Safercar_data.csv"

print("Downloading NHTSA data...")

response = requests.get(URL, timeout=120)

if response.status_code != 200:
    print("Download failed.")
    print("Status code:", response.status_code)
    print(response.text[:500])
    exit()

with open(OUTPUT_FILE, "wb") as file:
    file.write(response.content)

print("Download complete!")
print("Saved as:", OUTPUT_FILE)
