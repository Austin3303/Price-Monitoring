import requests, json, os
from bs4 import BeautifulSoup
from datetime import datetime

ITEMS = [
    {
        "name": "NB 9060",
        "url": "https://www.newbalance.co.th/new-balance-9060-men-s-sneakers-rain-cloud-with-castlerock-11.html",
        "selector": ".special-price .price"
    },
    {
    "name": "EMIS Small Logo Cap",
    "url": "https://www.central.co.th/th/emis-unisex-ball-cap-small-logo-grcds2512150002?sku=CDS26607344",
    "selector": ".text-base.text-central-red"
    },
    
]

data = {}
if os.path.exists("data.json"):
    with open("data.json") as f:
        data = json.load(f)

for item in ITEMS:
    try:
        res = requests.get(item["url"], headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        price_text = soup.select_one(item["selector"]).text.strip()
        price = float(price_text.replace("฿", "").replace(",", ""))

        name = item["name"]
        if name not in data:
            data[name] = []

        data[name].append({
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            "price": price
        })
        data[name] = data[name][-720:]
        print(f"{name}: {price}")
    except Exception as e:
        print(f"Failed {item['name']}: {e}")

with open("data.json", "w") as f:
    json.dump(data, f)
