import requests, json, os
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.newbalance.co.th/new-balance-9060-men-s-sneakers-rain-cloud-with-castlerock-11.html"
SELECTOR = ".special-price .price"

res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(res.text, "html.parser")

price_text = soup.select_one(SELECTOR).text.strip()
price = float(price_text.replace("฿", "").replace(",", ""))

# Load existing data
data = []
if os.path.exists("data.json"):
    with open("data.json") as f:
        data = json.load(f)

# Append new entry
data.append({
    "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
    "price": price
})

# Keep last 720 entries (12 months × 2/day × 30 days)
data = data[-720:]

with open("data.json", "w") as f:
    json.dump(data, f)
