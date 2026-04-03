import requests, json, os
from bs4 import BeautifulSoup
from datetime import datetime
from playwright.sync_api import sync_playwright

ITEMS = [
    {
        "name": "NB 9060",
        "url": "https://www.newbalance.co.th/new-balance-9060-men-s-sneakers-rain-cloud-with-castlerock-11.html",
        "selector": ".special-price .price",
        "js": False
    },
    {
        "name": "GW Gentle Pace Cap",
        "url": "https://www.gentlewomanonline.com/product/1103913",
        "selector": ".w-fit.pr-3.text-center.font-medium span",
        "js": True
    }
]

data = {}
if os.path.exists("data.json"):
    with open("data.json") as f:
        data = json.load(f)

def scrape_static(url, selector):
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    el = soup.select_one(selector)
    if not el: raise Exception("Selector not found")
    return el.text.strip()

def scrape_js(url, selector):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_selector(selector, timeout=15000)
        text = page.locator(selector).first.inner_text()
        browser.close()
        return text

for item in ITEMS:
    try:
        if item["js"]:
            price_text = scrape_js(item["url"], item["selector"])
        else:
            price_text = scrape_static(item["url"], item["selector"])
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
