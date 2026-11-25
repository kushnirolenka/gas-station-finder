# Рисунок 2.5: час одного запиту залежно від кількості станцій (дані таблиці 2.4, мс).
import matplotlib.pyplot as plt

n = [85, 1000, 10_000, 100_000, 1_000_000]
loop = [0.12, 1.24, 14.0, 183, 2595]
numpy_ = [0.026, 0.047, 0.34, 4.3, 63.7]
balltree = [0.061, 0.064, 0.068, 0.079, 0.101]
kd = [0.029, 0.024, 0.024, 0.025, 0.025]

fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(n, loop, "o-", label="Цикл Python", color="#d1495b")
ax.plot(n, numpy_, "s-", label="NumPy", color="#2a6f97")
ax.plot(n, balltree, "^-", label="BallTree", color="#e9a23b")
ax.plot(n, kd, "d-", label="k-d дерево", color="#3a7d44")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Кількість станцій n")
ax.set_ylabel("Час одного запиту, мс")
ax.legend()
ax.grid(which="both", alpha=0.3)
plt.tight_layout()
plt.savefig("rysunok_2_5.png", dpi=200)
print("Збережено rysunok_2_5.png")
