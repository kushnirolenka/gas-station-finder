# Рисунок 2.3: розподіл станцій за торговими марками та за рейтингом.
# Запуск: python rysunok_2_3.py gas_stations.csv   (файл береться з папки застосунку)
import sys
import pandas as pd
import matplotlib.pyplot as plt

path = sys.argv[1] if len(sys.argv) > 1 else "gas_stations.csv"
df = pd.read_csv(path)

brands = df["name"].value_counts().sort_values()          # кількість станцій за маркою
ratings = df["rating"].value_counts().sort_index()        # кількість станцій за рейтингом

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.5), gridspec_kw={"width_ratios": [1.5, 1]})

ax1.barh(brands.index, brands.values, color="#2a6f97")
ax1.set_xlabel("Кількість станцій")
ax1.set_title("За торговими марками")
for y, v in enumerate(brands.values):
    ax1.text(v + 0.2, y, str(v), va="center", fontsize=9)

ax2.bar(ratings.index.astype(str), ratings.values, color="#e07a1f")
ax2.set_xlabel("Рейтинг")
ax2.set_ylabel("Кількість станцій")
ax2.set_title("За рейтингом")
for x, v in enumerate(ratings.values):
    ax2.text(x, v + 0.4, str(v), ha="center", fontsize=9)

plt.tight_layout()
plt.savefig("rysunok_2_3.png", dpi=200)
print("Збережено rysunok_2_3.png; станцій:", len(df), ", марок:", len(brands))
