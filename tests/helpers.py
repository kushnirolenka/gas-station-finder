"""Допоміжні функції для тестів: генерація навчального набору станцій.

Набір повторює структуру навчальної бази: 85 записів, 20 торгових марок,
два кластери (Львівський регіон і Київ), рейтинг однаковий у межах марки.
"""
import random

BRANDS = ["OKKO", "Укрнафта", "WOG", "Socar", "БРСМ", "Shell", "Glusco", "Amic",
          "KLO", "Chipo", "Parallel", "Motto", "Lukoil", "Neftek", "Avias",
          "Marshal", "UPG", "Ukrpetrol", "Brend", "Aziya"]


def make_stations(n=85, seed=2026):
    """Повертає список рядків (id, name, latitude, longitude, rating)."""
    rnd = random.Random(seed)
    rating = {b: rnd.randint(5, 9) for b in BRANDS}
    rows = []
    for i in range(1, n + 1):
        if i <= round(n * 55 / 85):
            lat, lon = rnd.uniform(48.90, 49.91), rnd.uniform(23.89, 24.87)
        else:
            lat, lon = rnd.uniform(50.40, 50.53), rnd.uniform(30.39, 30.63)
        name = BRANDS[min(int(rnd.expovariate(0.35)), len(BRANDS) - 1)]
        rows.append((i, name, lat, lon, rating[name]))
    return rows


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        f.write("id,name,latitude,longitude,rating\n")
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")


def random_queries(count=100, seed=7):
    """Випадкові запити: (широта, довгота, залишок F, тип пального, об'єм k)."""
    rnd = random.Random(seed)
    return [(rnd.uniform(49.3, 49.9), rnd.uniform(23.9, 24.8),
             rnd.uniform(0.2, 10.0), rnd.choice(["бензин", "дизель"]),
             rnd.uniform(0.5, 2.5)) for _ in range(count)]
