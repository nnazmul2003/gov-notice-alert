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

    rows = soup.select("table tr")

    for row in rows[1:]:
        cols = row.find_all("td")

        if len(cols) >= 2:
            title = cols[1].get_text(" ", strip=True)
            link_tag = cols[1].find("a")

            if link_tag:
                return {
                    "title": title,
                    "link": urljoin(url, link_tag["href"])
                }

    return None


def send_ntfy(title, message):
    if not NTFY_SERVER or not NTFY_TOPIC:
        print("NTFY config missing")
        return

    try:
        requests.post(
            f"{NTFY_SERVER}/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers={
                "Title": title,
                "Priority": "default"
            },
            timeout=20
        )
        print("ntfy notification sent")
    except Exception as e:
        print("ntfy error:", e)


def send_email(subject, body):
    if not BREVO_API_KEY:
        print("BREVO_API_KEY missing")
        return

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    payload = {
        "sender": {
            "name": "Gov Notice Alert",
            "email": SENDER
        },
        "to": [
            {
                "email": RECEIVER
            }
        ],
        "subject": subject,
        "textContent": body
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        print("Email Status:", r.status_code)
        print(r.text)
    except Exception as e:
        print("Email Error:", e)


def check_sites():
    print("===== TEST MODE =====")

    title = "GitHub Test Notification"
    body = """এটি একটি টেস্ট মেসেজ।

যদি এই মেইল বা ntfy নোটিফিকেশন পান,
তাহলে Brevo এবং ntfy ঠিকভাবে কাজ করছে।
"""

    print("Sending ntfy...")
    send_ntfy(title, body)

    print("Sending email...")
    send_email(title, body)

    print("Test notification sent successfully.")


check_sites()

print("Government Notice Checker Started")
