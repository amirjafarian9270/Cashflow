import json, re, os, datetime, urllib.request

HEAD = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.tsetmc.com/", "Accept": "application/json, text/plain, */*"}

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HEAD), timeout=20).read().decode("utf-8", "ignore")

def fa(s):
    return (s or "").replace("ي", "ی").replace("ك", "ک").strip()

def tgju(key):
    h = get("https://www.tgju.org/profile/" + key)
    m = re.search(r'data-col="info\.last_trade\.PDrCotVal"[^>]*>\s*([\d,\.]+)', h)
    return float(m.group(1).replace(",", "")) / 10

CATALOG = {
    "geram18": "طلای ۱۸ عیار", "geram24": "طلای ۲۴ عیار", "gold_mini_size": "طلای دست دوم",
    "sekee": "سکه امامی", "sekeb": "سکه بهار آزادی", "nim": "نیم‌سکه", "rob": "ربع‌سکه",
    "silver_999": "نقره ۹۹۹", "price_dollar_rl": "دلار", "price_eur": "یورو", "price_aed": "درهم امارات",
}

out = {"prices": {}, "catalog": {}}
if os.path.exists("prices.json"):
    try:
        old = json.load(open("prices.json", encoding="utf-8"))
        out["prices"], out["catalog"] = old.get("prices", {}), old.get("catalog", {})
    except Exception:
        pass
out["updated"] = datetime.datetime.utcnow().isoformat() + "Z"

# بورس: سهام و صندوق‌ها، قیمت پایانی، یک درخواست برای همه نمادها
try:
    q = "market=0&industrialGroup=&paperTypes%5B0%5D=1&paperTypes%5B1%5D=8&showTraded=false&withBestLimits=false"
    rows = json.loads(get("https://cdn.tsetmc.com/api/ClosingPrice/GetMarketWatch?" + q))["marketwatch"]
    n = 0
    for r in rows:
        p = r.get("pcl") or r.get("pdv")
        if not p:
            continue
        k = "tsetmc:" + str(r["insCode"])
        out["prices"][k] = p / 10
        out["catalog"][k] = fa(r.get("lva")) + " — " + fa(r.get("lvc")) + (" (صندوق)" if str(r.get("insID", "")).startswith("IRT") else "")
        n += 1
    print("OK bourse", n)
except Exception as e:
    print("FAIL bourse", e)

# طلا، سکه، نقره، ارز و کلیدهای اضافه‌ی فایل watchlist.json
extra = [w["key"] for w in json.load(open("watchlist.json", encoding="utf-8")) if w.get("src") == "tgju"]
for key in list(CATALOG) + [k for k in extra if k not in CATALOG]:
    try:
        out["prices"]["tgju:" + key] = tgju(key)
        if key in CATALOG:
            out["catalog"]["tgju:" + key] = CATALOG[key]
        print("OK tgju", key, out["prices"]["tgju:" + key])
    except Exception as e:
        print("FAIL tgju", key, e)

json.dump(out, open("prices.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
