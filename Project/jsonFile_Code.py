import requests
import json
import os

URL = "http://192.168.1.254:8000/positions.json"       # Remote JSON file
CACHE_FILE = "backup_data.json"              # Local copy


def load_json():
    try:
        print("Trying to fetch from server...")
        response = requests.get(URL, timeout=5)
        response.raise_for_status()

        data = response.json()

        # Save a fresh local backup
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f, indent=2)

        print("Loaded from server and cached.")
        return data

    except Exception as e:
        print(f"Server not available ({e}).")
        print("Trying to load from local cache...")

        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
            print("Loaded from local cache.")
            return data
        else:
            print("No local cache available.")
            return None


data = load_json()
print(data)