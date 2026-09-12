import requests

URL = "https://static.nhtsa.gov/odi/ffdd/rcl/FLAT_RCL_POST_2010.zip"
OUTPUT_FILE = "recalls.zip"

print("Downloading NHTSA recall data...")

response = requests.get(URL, timeout=120)

if response.status_code != 200:
    print("Download failed.")
    print("Status code:", response.status_code)
    exit()

with open(OUTPUT_FILE, "wb") as file:
    file.write(response.content)

print("Download complete!")
print("Saved as:", OUTPUT_FILE)