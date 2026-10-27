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

watch = json.load(open("watchlist.json", encoding="utf-8"))
out = {"updated": datetime.datetime.utcnow().isoformat() + "Z", "prices": {}}
for w in watch:
    src, key = w.get("src"), w.get("key")
    try:
        out["prices"][f"{src}:{key}"] = {"tgju": tgju, "rahavard": rahavard}[src](key)
        print("OK", src, key, out["prices"][f"{src}:{key}"])
    except Exception as e:
        print("FAIL", src, key, e)
json.dump(out, open("prices.json", "w", encoding="utf-8"), ensure_ascii=False)
