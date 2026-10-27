import json, re, datetime, urllib.request

UA = {"User-Agent": "Mozilla/5.0"}

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "ignore")

def num(t):
    return float(t.replace(",", "").strip())

def tgju(key):
    h = get("https://www.tgju.org/profile/" + key)
    m = re.search(r'data-col="info\.last_trade\.PDrCotVal"[^>]*>\s*([\d,\.]+)', h)
    return num(m.group(1)) / 10

def rahavard(key):
    url = key if key.startswith("http") else "https://rahavard365.com/asset/" + key
    h = get(url)
    for p in (r'"last_price"\s*:\s*([\d\.]+)', r'"close_price"\s*:\s*([\d\.]+)', r'"final_price"\s*:\s*([\d\.]+)'):
        m = re.search(p, h)
        if m:
            return num(m.group(1)) / 10
    raise ValueError("price pattern not found")

CATALOG = {
    "geram18": "طلای ۱۸ عیار", "geram24": "طلای ۲۴ عیار", "gold_mini_size": "طلای دست دوم",
    "sekee": "سکه امامی", "sekeb": "سکه بهار آزادی", "nim": "نیم‌سکه", "rob": "ربع‌سکه",
    "silver_999": "نقره ۹۹۹", "price_dollar_rl": "دلار", "price_eur": "یورو", "price_aed": "درهم امارات",
}
watch = json.load(open("watchlist.json", encoding="utf-8"))
watch = [{"src": "tgju", "key": k} for k in CATALOG] + watch
out = {"updated": datetime.datetime.utcnow().isoformat() + "Z", "prices": {}, "catalog": {}}
for w in watch:
    src, key = w.get("src"), w.get("key")
    try:
        out["prices"][f"{src}:{key}"] = {"tgju": tgju, "rahavard": rahavard}[src](key)
        if src == "tgju" and key in CATALOG:
            out["catalog"][f"tgju:{key}"] = CATALOG[key]
        print("OK", src, key, out["prices"][f"{src}:{key}"])
    except Exception as e:
        print("FAIL", src, key, e)
json.dump(out, open("prices.json", "w", encoding="utf-8"), ensure_ascii=False)
