import glob

for file in glob.glob("*.html"):
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "Funds successfully landed" in line:
                print(f"{file}:{i+1}: {line.strip()}")
