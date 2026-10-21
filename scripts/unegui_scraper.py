"""unegui.mn-ээс сонгосон загваруудын зарыг татаж, option-оор үнийн харьцуулалт гаргана.

Энэ скриптийг unegui.mn нээгддэг компьютер дээр ажиллуулна (Claude-ийн cloud орчинд
тухайн домэйн хаалттай байсан тул сайт дээр шалгагдаагүй — HTML бүтэц өөрчлөгдсөн бол
SELECTORS-ыг засна).

Суулгах:   pip install requests beautifulsoup4
Ажиллуулах:
    python3 scripts/unegui_scraper.py --pages 5 --out data/unegui_raw.csv
    python3 scripts/unegui_scraper.py --analyze data/unegui_raw.csv --import-year 2026
"""
import argparse
import csv
import re
import statistics
import sys
import time
from collections import defaultdict

BASE = "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/toyota/"
CATEGORIES = {
    "Prius 40": "prius-40/",
    "Prius 41": "prius-41/",
    "Prius 50": "50/",
    "Prius 55": "Prius55/",
    "Prius 60": "prius-60/",
    "Camry": "camry/",
    "Crown": "crown/",
    "Harrier": "harrier/",
}
SELECTORS = {
    "item_link": "a.advert__content-title",
    "char_row": "ul.chars-column li",
    "char_key": ".key-chars",
    "char_value": ".value-chars",
    "description": ".js-description",
    "price": ".announcement-price__cost",
}
# Тайлбар/гарчигт байвал тухайн option-той гэж үзэх түлхүүр үгс (жижиг үсгээр).
OPTIONS = {
    "4WD / E-Four": ["4wd", "e-four", "efour", "бүх дугуй", "4х4", "4x4"],
    "Арьсан суудал": ["leather", "арьсан", "кожа"],
    "Люк / панорам": ["sunroof", "люк", "panoram", "панорам"],
    "Touring": ["touring", "туринг"],
    "A Premium / Z / G-Executive": ["a premium", "aプレミアム", " z ", "z leather", "g-executive", "g executive", "progress"],
    "JBL / премиум аудио": ["jbl", "premium sound"],
    "Радар круиз / Safety Sense": ["radar", "радар", "safety sense", "tss", "adaptive cruise"],
    "360 камер": ["360", "panoramic view", "бүх талын камер"],
    "Монголд яваагүй": ["монголд яваагүй", "яваагүй", "0 км", "гаалиас"],
}
TITLE_RE = re.compile(r",\s*(\d{4})\s*/\s*(\d{4})")
NUM_RE = re.compile(r"[\d.,]+")
HEADERS = {"User-Agent": "Mozilla/5.0 (market research; contact: owner)"}


def parse_price(text):
    """'32 сая ₮' -> 32.0, '32,500,000 ₮' -> 32.5 (сая ₮-өөр)."""
    m = NUM_RE.search(text or "")
    if not m:
        return None
    val = float(m.group().replace(",", "").rstrip("."))
    return val if "сая" in text else val / 1_000_000


def scrape(pages, delay):
    import requests
    from bs4 import BeautifulSoup

    session = requests.Session()
    session.headers.update(HEADERS)
    seen = set()
    for model, slug in CATEGORIES.items():
        for page in range(1, pages + 1):
            resp = session.get(BASE + slug, params={"page": page}, timeout=30)
            if resp.status_code != 200:
                print(f"[{model}] хуудас {page}: HTTP {resp.status_code}", file=sys.stderr)
                break
            links = BeautifulSoup(resp.text, "html.parser").select(SELECTORS["item_link"])
            if not links:
                break
            for a in links:
                url = requests.compat.urljoin(BASE, a.get("href", ""))
                if url in seen:
                    continue
                seen.add(url)
                time.sleep(delay)
                detail = session.get(url, timeout=30)
                if detail.status_code != 200:
                    continue
                yield parse_detail(model, url, a.get_text(" ", strip=True), detail.text)
            time.sleep(delay)


def parse_detail(model, url, title, html):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    chars = {}
    for li in soup.select(SELECTORS["char_row"]):
        k, v = li.select_one(SELECTORS["char_key"]), li.select_one(SELECTORS["char_value"])
        if k and v:
            chars[k.get_text(strip=True).rstrip(":")] = v.get_text(" ", strip=True)
    desc_el = soup.select_one(SELECTORS["description"])
    price_el = soup.select_one(SELECTORS["price"])
    m = TITLE_RE.search(title)
    return {
        "model": model,
        "title": title,
        "mfg_year": chars.get("Үйлдвэрлэсэн он") or (m.group(1) if m else ""),
        "import_year": chars.get("Орж ирсэн он") or (m.group(2) if m else ""),
        "mileage": chars.get("Явсан", ""),
        "engine": chars.get("Мотор багтаамж", ""),
        "fuel": chars.get("Хөдөлгүүр", ""),
        "drive": chars.get("Хөтлөгч", ""),
        "price_mnt_m": parse_price(price_el.get_text(" ", strip=True) if price_el else title),
        "description": (desc_el.get_text(" ", strip=True) if desc_el else "")[:2000],
        "url": url,
        **{f"char:{k}": v for k, v in chars.items()},
    }


def write_csv(rows, path):
    rows = list(rows)
    fields = sorted({k for r in rows for k in r}, key=lambda k: (k.startswith("char:"), k))
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} зар → {path}")


def analyze(path, import_year):
    with open(path, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r.get("price_mnt_m")]
    if import_year:
        rows = [r for r in rows if str(r.get("import_year", "")).startswith(str(import_year))]
    by_model = defaultdict(list)
    for r in rows:
        r["price"] = float(r["price_mnt_m"])
        by_model[r["model"]].append(r)

    print(f"\n## Загвар бүрийн үнэ (орж ирсэн он = {import_year or 'бүгд'})\n")
    print("| Загвар | n | Медиан | P25 | P75 |")
    print("|---|---|---|---|---|")
    for model, items in sorted(by_model.items(), key=lambda kv: statistics.median(r["price"] for r in kv[1])):
        p = sorted(r["price"] for r in items)
        q = statistics.quantiles(p, n=4) if len(p) >= 4 else [p[0], 0, p[-1]]
        print(f"| {model} | {len(p)} | {statistics.median(p):.1f} | {q[0]:.1f} | {q[2]:.1f} |")

    print("\n## Option-ийн нэмэгдэл (ижил загвар, ижил үйлдвэрлэсэн оны дотор харьцуулсан медиан зөрүү, сая ₮)\n")
    print("| Загвар | Option | n (option-той) | Нэмэгдэл |")
    print("|---|---|---|---|")
    for model, items in by_model.items():
        for opt, keys in OPTIONS.items():
            diffs, n_with = [], 0
            by_year = defaultdict(lambda: ([], []))
            for r in items:
                text = f" {r['title']} {r.get('description', '')} {r.get('drive', '')} ".lower()
                has = any(k in text for k in keys)
                n_with += has
                by_year[r.get("mfg_year")][0 if has else 1].append(r["price"])
            for with_p, without_p in by_year.values():
                if with_p and without_p:
                    diffs.append(statistics.median(with_p) - statistics.median(without_p))
            if n_with >= 3 and diffs:
                print(f"| {model} | {opt} | {n_with} | {statistics.median(diffs):+.1f} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=3, help="ангилал бүрээс татах хуудасны тоо")
    ap.add_argument("--delay", type=float, default=1.0, help="хүсэлт хоорондын завсар (сек)")
    ap.add_argument("--out", default="data/unegui_raw.csv")
    ap.add_argument("--analyze", metavar="CSV", help="татсан CSV-г шинжлэх")
    ap.add_argument("--import-year", type=int, default=None)
    args = ap.parse_args()
    if args.analyze:
        analyze(args.analyze, args.import_year)
    else:
        write_csv(scrape(args.pages, args.delay), args.out)


if __name__ == "__main__":
    main()
