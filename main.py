import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

LAST_FILE = "last_notice.json"

SITES = {
    "shed": "https://shed.gov.bd/pages/notification-circulars",
    "tmed": "https://tmed.gov.bd/pages/notices/"
}

NTFY_SERVER = os.getenv("NTFY_SERVER")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
SENDER = "2023nazmul1234@gmail.com"
RECEIVER = "smnazmul415@gmail.com"


def load_last():
    if os.path.exists(LAST_FILE):
        with open(LAST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"shed": "", "tmed": ""}


def save_last(data):
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_latest_notice(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)

        if len(text) > 8:
            return {
                "title": text,
                "link": urljoin(url, a["href"])
            }

    return None


print("Government Notice Checker Started")
