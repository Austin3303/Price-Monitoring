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
        "name": "GW Gentle Pace Cap",
        "url": "https://www.gentlewomanonline.com/product/1103913",
        "selector": ".product-price"
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
        el = soup.select_one(item["selector"])
        print(f"{item['name']} raw: {el}")
        price_text = el.text.strip()
        price = float(price_text.replace("฿", "").replace(",", "").replace("THB", "").strip())
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
