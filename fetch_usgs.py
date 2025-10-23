# fetch_usgs.py
import requests
import json
import os

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
DATA_DIR = "data"
CACHE_FILE = os.path.join(DATA_DIR, "earthquakes.json")

def fetch_usgs(cache=True):
    os.makedirs(DATA_DIR, exist_ok=True)
    if cache and os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            print(f"Loading cached data: {CACHE_FILE}")
            return json.load(f)
    print("Fetching data from USGS...")
    r = requests.get(USGS_URL, timeout=30)
    r.raise_for_status()
    data = r.json()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data

if __name__ == "__main__":
    fetch_usgs(cache=False)

