import json, os
from datetime import datetime
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup

ITEMS = [
    {
        "name": "NB 9060",
        "url": "https://www.newbalance.co.th/new-balance-9060-men-s-sneakers-rain-cloud-with-castlerock-11.html",
        "selector": ".special-price .price",
        "js": False
    },
    {
        "name": "EMIS Small Logo Cap",
        "url": "https://www.central.co.th/th/emis-unisex-ball-cap-small-logo-grcds2512150002?sku=CDS26607344",
        "selector": "[class*='central-red']",
        "js": True
    },
]

data = {}
if os.path.exists("data.json"):
    with open("data.json") as f:
        data = json.load(f)

def scrape_static(url, selector):
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    el = soup.select_one(selector)
    if not el:
        raise Exception(f"Selector not found: {selector}")
    return el.text.strip()

def scrape_js(url, selector):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        # Print all text on page to find price
        print(page.content()[:5000])
        browser.close()
        return "0"

for item in ITEMS:
    try:
        if item["js"]:
            price_text = scrape_js(item["url"], item["selector"])
        else:
            price_text = scrape_static(item["url"], item["selector"])

        price = float(price_text.replace("฿", "").replace(",", "").strip())

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
