# Рисунок 2.4: середня відносна похибка формул відстані за інтервалами відстаней (дані таблиці 2.3).
import numpy as np
import matplotlib.pyplot as plt

intervals = ["до 1", "1-5", "5-20", "20-100", "понад 100"]
euclid = [33.06, 31.05, 34.09, 45.23, 44.14]       # Евклід у градусах, %
equid = [0.19, 0.18, 0.20, 0.26, 0.22]             # еквідистантна, %
haversine = [0.19, 0.18, 0.20, 0.26, 0.25]         # гаверсинус, %

x = np.arange(len(intervals))
w = 0.27
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.bar(x - w, euclid, w, label="Евклід у градусах", color="#d1495b")
ax.bar(x, equid, w, label="Еквідистантна", color="#2a6f97")
ax.bar(x + w, haversine, w, label="Гаверсинус", color="#e9a23b")
ax.set_yscale("log")
ax.set_xticks(x)
ax.set_xticklabels(intervals)
ax.set_xlabel("Інтервал відстаней, км")
ax.set_ylabel("Середня відносна похибка, % (логарифмічна шкала)")
ax.set_ylim(0.1, 300)
ax.legend(loc="upper center", ncol=3)
ax.grid(axis="y", which="both", alpha=0.3)
plt.tight_layout()
plt.savefig("rysunok_2_4.png", dpi=200)
print("Збережено rysunok_2_4.png")
