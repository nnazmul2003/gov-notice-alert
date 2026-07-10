import requests
from bs4 import BeautifulSoup
import os
import urllib3

# SSL সার্টিফিকেট ভেরিফিকেশন এরর এড়াতে ওয়ার্নিং মেসেজ বন্ধ করা হয়েছে
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- কনফিগারেশন ---
URL = "https://mofa.gov.bd/site/view/notices"
TELEGRAM_TOKEN = "8535636772:AAHvIK1Lgu90_K5PkCHxQjnCwzKmIVfkYjo"  # ⚙️ আপনার দেওয়া নতুন বটের টোকেন সেট করা হয়েছে
CHAT_ID = "6382850126"                             
TRACK_FILE = "mofa_notices.txt"                    

# ফাইল চেক এবং রিড
if os.path.exists(TRACK_FILE):
    with open(TRACK_FILE, "r", encoding="utf-8") as f:
        sent_notices = set(f.read().splitlines())
else:
    sent_notices = set()

def send_telegram_message(text):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(telegram_url, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ টেলিগ্রাম এরর: {e}")

def check_recent_notice():
    global sent_notices
    print("🔄 MOFA ওয়েবসাইটের নোটিশ চেক করা হচ্ছে...")
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
            
            # পুরানো থেকে নতুনের দিকে (নিচ থেকে উপরে) লুপ চলবে
            for row in reversed(rows):
                columns = row.find_all('td')
                
                # টেবিলে কমপক্ষে ৩টি কলাম থাকতে হবে (ক্রমিক, শিরোনাম, তারিখ)
                if len(columns) < 3:
                    continue
                
                link_element = row.find('a', href=True)
                if link_element:
                    link = link_element['href']
                    
                    # ২য় কলামে থাকে নোটিশের শিরোনাম এবং ৩য় কলামে প্রকাশের তারিখ
                    title = columns[1].text.strip()
                    published_date = columns[2].text.strip()
                    
                    # সাইটের ডোমেইন লিংক ঠিক করা
                    if link.startswith('/'):
                        link = f"https://mofa.gov.bd{link}"
                    elif not link.startswith('http'):
                        link = f"https://mofa.gov.bd/site/view/notices/{link}"
                        
                    # সার্কুলার ফিল্টার
                    if "circular" in title.lower() or "সার্কুলার" in title:
                        continue
                        
                    if link in sent_notices:
                        continue
                    
                    # 🔔 টেলিগ্রাম মেসেজ ফরম্যাট
                    message = (
                        f"🌍 *MOFA (পররাষ্ট্র মন্ত্রণালয়) নতুন নোটিশ!*\n\n"
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

if __name__ == "__main__":
    check_recent_notice()
