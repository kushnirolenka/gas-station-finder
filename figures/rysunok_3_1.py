# Рисунок 3.1: час одного запиту для циклу v1.0, NumPy і k-d дерева (дані таблиці 3.6, мс).
import matplotlib.pyplot as plt

n = [85, 1000, 10_000, 100_000, 1_000_000]
loop = [0.029, 0.353, 3.58, 38.1, 362.6]
numpy_ = [0.009, 0.023, 0.131, 1.32, 16.4]
kd = [0.014, 0.020, 0.022, 0.021, 0.023]

fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(n, loop, "o-", label="Цикл v1.0", color="#d1495b")
ax.plot(n, numpy_, "s-", label="NumPy", color="#2a6f97")
ax.plot(n, kd, "d-", label="k-d дерево", color="#3a7d44")
ax.axhline(20, color="#777777", ls="--", lw=1)
ax.text(90, 24, "критерій успіху: 20 мс", color="#555555", fontsize=10)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Кількість станцій n")
ax.set_ylabel("Час одного запиту, мс")
ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.88))
ax.grid(which="both", alpha=0.3)
plt.tight_layout()
plt.savefig("rysunok_3_1.png", dpi=200)
print("Збережено rysunok_3_1.png")
