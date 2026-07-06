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

def load_last():
    if os.path.exists(LAST_FILE):
        with open(LAST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "shed": "",
        "tmed": ""
    }


def save_last(data):
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_latest_notice(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.select("table tr")

    for row in rows[1:]:
        cols = row.find_all("td")

        if len(cols) >= 2:
            title = cols[1].get_text(" ", strip=True)
            link = cols[1].find("a")

            if link:
                return {
                    "title": title,
                    "link": urljoin(url, link["href"])
                }

    return None

def send_ntfy(title, message):
    if not NTFY_SERVER or not NTFY_TOPIC:
        print("NTFY_SERVER বা NTFY_TOPIC পাওয়া যায়নি")
        return

    try:
        response = requests.post(
            f"{NTFY_SERVER}/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers={
                "Title": title,
                "Priority": "default"
            },
            timeout=20
        )

        print("ntfy status:", response.status_code)

        if response.status_code == 200:
            print("ntfy notification sent")
        else:
            print("ntfy error:", response.text)

    except Exception as e:
        print("ntfy exception:", e)

        def check_sites():
    print("===== Government Notice Checker =====")

    last = load_last()
    updated = False

    for name, url in SITES.items():
        print(f"Checking {name}...")

        try:
            notice = get_latest_notice(url)

            if not notice:
                print(f"No notice found for {name}")
                continue

            if notice["link"] != last.get(name, ""):
                title = f"📢 New Notice ({name.upper()})"
                body = f"{notice['title']}\n\n{notice['link']}"

                send_ntfy(title, body)

                last[name] = notice["link"]
                updated = True

                print("Notification sent.")

            else:
                print("No new notice.")

        except Exception as e:
            print(f"Error ({name}): {e}")

    if updated:
        save_last(last)


check_sites()

print("Government Notice Checker Finished")                             
