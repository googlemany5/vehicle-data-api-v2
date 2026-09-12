import zipfile

ZIP_FILE = "recalls.zip"

with zipfile.ZipFile(ZIP_FILE, "r") as zip_file:
    with zip_file.open("FLAT_RCL_POST_2010.txt") as file:
        for i in range(10):
            line = file.readline().decode("latin-1").strip()
            print(line)