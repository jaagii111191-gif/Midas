"""unegui.mn зарын түүврээс загвар бүрийн үнийн харьцуулалтыг гаргана.

Ажиллуулах:  python3 scripts/analyze_listings.py [data/unegui_listings_2026-10.csv]
Гаралт: Markdown хүснэгтүүд (stdout).
"""
import csv
import statistics
import sys
from collections import defaultdict

PATH = sys.argv[1] if len(sys.argv) > 1 else "data/unegui_listings_2026-10.csv"
YEAR = 2026


def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if "гажуу" in r["note"] or "ангиллын" in r["note"]:
                continue  # гажуу утга, ангиллын min/max-ийг дунджаас хасна
            r["price"] = float(r["price_mnt_m"])
            r["mfg"] = int(r["mfg_year"]) if r["mfg_year"] else None
            r["imp"] = int(r["import_year"])
            r["km"] = int(r["mileage_km"]) if r["mileage_km"] else None
            rows.append(r)
    return rows


def summary(prices):
    return (len(prices), min(prices), statistics.median(prices), max(prices))


def table(title, groups):
    print(f"\n### {title}\n")
    print("| Бүлэг | n | Мин | Медиан | Макс |")
    print("|---|---|---|---|---|")
    for k, prices in groups:
        n, lo, med, hi = summary(prices)
        print(f"| {k} | {n} | {lo:.1f} | {med:.1f} | {hi:.1f} |")


def slope(xs, ys):
    """Энгийн шугаман регрессийн налуу (OLS)."""
    mx, my = statistics.mean(xs), statistics.mean(ys)
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else float("nan")


rows = load(PATH)
fresh = [r for r in rows if r["imp"] == YEAR]

by_model = defaultdict(list)
for r in fresh:
    by_model[r["model"]].append(r["price"])
order = sorted(by_model, key=lambda m: statistics.median(by_model[m]))
table(f"{YEAR} онд орж ирсэн машинууд — загвараар (сая ₮)", [(m, by_model[m]) for m in order])

by_code = defaultdict(list)
for r in fresh:
    by_code[(r["model"], r["code"])].append(r["price"])
table(
    f"{YEAR} онд орж ирсэн — үеэр (generation) (сая ₮)",
    [(f"{m} · {c}", p) for (m, c), p in sorted(by_code.items(), key=lambda kv: statistics.median(kv[1]))],
)

ub_ok = defaultdict(lambda: {"≤2015 (УБ дугаар авахгүй)": [], "2016+ (УБ дугаар авна)": []})
for r in fresh:
    if r["mfg"] is None:
        continue
    key = "2016+ (УБ дугаар авна)" if r["mfg"] >= YEAR - 10 else "≤2015 (УБ дугаар авахгүй)"
    ub_ok[r["model"]][key].append(r["price"])
print("\n### 10 жилийн насжилтын босго — үйлдвэрлэсэн оноор (сая ₮, медиан)\n")
print("| Загвар | ≤2015 | 2016+ |")
print("|---|---|---|")
for m, d in ub_ok.items():
    cells = [f"{statistics.median(v):.1f} (n={len(v)})" if v else "—" for v in d.values()]
    print(f"| {m} | {cells[0]} | {cells[1]} |")

print("\n### Он, гүйлтийн нөлөө (2026 онд орж ирсэн)\n")
print("| Загвар | n | +1 жил шинэ = сая ₮ | +10,000 км = сая ₮ |")
print("|---|---|---|---|")
for group, models in [
    ("Prius 40/41", {"Prius 40", "Prius 41 (7 суудал)"}),
    ("Camry", {"Camry"}),
    ("Crown", {"Crown"}),
    ("Harrier", {"Harrier"}),
]:
    g = [r for r in fresh if r["model"] in models and r["mfg"]]
    s_year = slope([r["mfg"] for r in g], [r["price"] for r in g])
    gk = [r for r in g if r["km"]]
    s_km = slope([r["km"] / 10000 for r in gk], [r["price"] for r in gk]) if len(gk) > 2 else float("nan")
    print(f"| {group} | {len(g)} | {s_year:+.1f} | {s_km:+.2f} (n={len(gk)}) |")

print("\n### 2025 ба 2026 онд орж ирсэн — ижил үйлдвэрлэсэн оны харьцуулалт (сая ₮, медиан)\n")
print("| Загвар · он | 2025 онд орсон | 2026 онд орсон |")
print("|---|---|---|")
pairs = defaultdict(lambda: defaultdict(list))
for r in rows:
    if r["mfg"]:
        pairs[(r["model"], r["mfg"])][r["imp"]].append(r["price"])
for (m, y), d in sorted(pairs.items()):
    if 2025 in d and 2026 in d:
        print(f"| {m} · {y} | {statistics.median(d[2025]):.1f} | {statistics.median(d[2026]):.1f} |")
