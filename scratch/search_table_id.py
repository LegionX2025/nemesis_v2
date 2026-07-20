import os

with open("nemesis_id.html", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "id=\"interacted-table\"" in line or "id=\"rt-tx-body\"" in line:
            print(f"Line {i}: {line.strip()}")
