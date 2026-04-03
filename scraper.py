import json, os, re
from datetime import datetime
from curl_cffi import requests as cf_requests
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup

ITEMS = [
    {
        "name": "NB 9060",
        "url": "https://www.newbalance.co.th/new-balance-9060-men-s-sneakers-rain-cloud-with-castlerock-11.html",
        "selector": ".special-price .price",
        "mode": "static"
    },
    {
        "name": "GW Gentle Pace Cap",
        "url": "https://www.gentlewomanonline.com/product/1103913",
        "selector": ".w-fit.pr-3.text-center.font-medium span",
        "mode": "js"
    },

    {
    "name": "Uniqlo E471809",
    "url": "https://www.uniqlo.com/th/api/commerce/v5/th/products/E471809-000/price-groups/00/l2s?withPrices=true",
    "selector": None,
    "mode": "api"
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
    if not el: raise Exception("Selector not found")
    return el.text.strip()

def scrape_js(url, selector):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            locale="th-TH",
            geolocation={"latitude": 13.7563, "longitude": 100.5018},
            permissions=["geolocation"]
        )
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_selector(selector, timeout=15000)
        text = page.locator(selector).first.inner_text()
        browser.close()
        return text

def scrape_api(url):
    res = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0",
        "x-fr-clientid": "uqsp-th"
    })
    print(res.text[:300])
    data = res.json()
    price = data["result"]["l2s"][0]["prices"]["base"]["value"]["amount"]
    return str(price)

for item in ITEMS:
    try:
        if item["mode"] == "js":
            price_text = scrape_js(item["url"], item["selector"])
        elif item["mode"] == "api":
            price_text = scrape_api(item["url"])
        else:
            price_text = scrape_static(item["url"], item["selector"])
            price_text = scrape_static(item["url"], item["selector"])
        price = float(re.sub(r'[^\d.]', '', price_text).strip())
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
