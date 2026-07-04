import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path

LAST_FILE = "last_notice.json"

URLS = {
    "shed": "https://shed.gov.bd",
    "tmed": "https://tmed.gov.bd"
}

def load_data():
    if not Path(LAST_FILE).exists():
        return {"shed": "", "tmed": ""}
    with open(LAST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_title(url):
    r = requests.get(url, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    return soup.title.text.strip() if soup.title else "No Title"

data = load_data()

for key, url in URLS.items():
    title = get_title(url)

    if data[key] != title:
        print(f"New notice detected on {key}: {title}")
        data[key] = title

save_data(data)

print("Finished.")
