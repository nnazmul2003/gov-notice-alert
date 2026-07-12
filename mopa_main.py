import os
import time
import requests
from bs4 import BeautifulSoup
import urllib3
from flask import Flask
from threading import Thread

# SSL certificate error avoid korar jnno warning off kora holo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Flask Server setup Render-er active thakar jnno ---
app = Flask('')

@app.route('/')
def home():
    return "MOPA Notice Bot is Running!"

def run_flask():
    # Render default portfolio port use korbe, na thakle 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- Bot Config & Scraper Logic ---
URL = "https://mopa.gov.bd/views/latest-news"

# Env variables theke data nibe, na thakle hardcoded backup
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8535636772:AAHvIK1Lgu90_K5PkCHxQjnCwzKmIVfkYjo")
CHAT_ID = os.getenv("CHAT_ID", "6382850126")                             
TRACK_FILE = "mopa_notices.txt"                    

# Track file check and read
if os.path.exists(TRACK_FILE):
    with open(TRACK_FILE, "r", encoding="utf-8") as f:
        sent_notices = set(f.read().splitlines())
else:
    sent_notices = set()

def send_telegram_message(text):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(telegram_url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"❌ Telegram Error Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

def check_recent_notice():
    global sent_notices
    print("🔄 MOPA (জনপ্রশাসন মন্ত্রণালয়) ওয়েবসাইটের নোটিশ চেক করা হচ্ছে...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(URL, headers=headers, timeout=15, verify=False)
        
        if response.status_code != 200:
            print(f"❌ ওয়েবসাইটে প্রবেশ করা যাচ্ছে না। স্ট্যাটাস কোড: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        
        if table:
            rows = table.find_all('tr')
            new_count = 0
            
            for row in reversed(rows):
                columns = row.find_all('td')
                if len(columns) < 3:
                    continue
                
                link_element = row.find('a', href=True)
                if link_element:
                    link = link_element['href']
                    title = columns[1].text.strip()
                    published_date = columns[2].text.strip()
                    
                    if link.startswith('/'):
                        link = f"https://mopa.gov.bd{link}"
                    elif not link.startswith('http'):
                        link = f"https://mopa.gov.bd/views/latest-news/{link}"
                        
                    if "circular" in title.lower() or "সার্কুলার" in title:
                        continue
                        
                    if link in sent_notices:
                        continue
                    
                    message = (
                        f"🏛️ *MOPA (জনপ্রশাসন মন্ত্রণালয়) সর্বশেষ খবর!*\n\n"
                        f"📌 *শিরোনাম:* {title}\n\n"
                        f"📅 *প্রকাশের তারিখ:* {published_date}\n"
                        f"🔗 *লিংক:* {link}"
                    )
                    
                    send_telegram_message(message)
                    print(f"✅ নতুন বটে পাঠানো হয়েছে: {title}")
                    
                    with open(TRACK_FILE, "a", encoding="utf-8") as f:
                        f.write(link + "\n")
                    sent_notices.add(link)
                    new_count += 1
            
            if new_count == 0:
                print("ℹ️ নতুন কোনো নোটিশ পাওয়া যায়নি।")
        else:
            print("❌ নোটিশ টেবিলটি খুঁজে পাওয়া যায়নি।")
            
    except Exception as e:
        print(f"❌ ত্রুটি: {e}")

def bot_loop():
    while True:
        check_recent_notice()
        print("😴 5 minutes-er jnno script ghumacche...")
        time.sleep(300) # 5 mins wait

if __name__ == "__main__":
    # Background thread-e flask server start kora hobe jate render active thake
    server_thread = Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()
    
    # Main thread-e scraper cholbe
    bot_loop()
