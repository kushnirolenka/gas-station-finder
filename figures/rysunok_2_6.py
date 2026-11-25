# Рисунок 2.6: складові часу обробки одного запиту в базовій версії (n = 85), мс.
import matplotlib.pyplot as plt

parts = ["Геокодування", "Формування HTML карти", "Побудова об'єктів карти", "Читання CSV", "Пошук станцій"]
ms = [200, 6.2, 4.2, 0.9, 0.12]                  # геокодування: медіана 0,20 с = 200 мс

fig, ax = plt.subplots(figsize=(9, 4.8))
y = range(len(parts))
ax.barh(list(y), ms, color=["#d1495b", "#2a6f97", "#2a6f97", "#2a6f97", "#2a6f97"])
ax.set_yticks(list(y))
ax.set_yticklabels(parts)
ax.invert_yaxis()
ax.set_xscale("log")
ax.set_xlabel("Час, мс (логарифмічна шкала)")
for i, v in enumerate(ms):
    ax.text(v * 1.15, i, f"{v:g}".replace(".", ","), va="center", fontsize=10)
ax.set_xlim(0.05, 800)
ax.grid(axis="x", which="both", alpha=0.3)
plt.tight_layout()
plt.savefig("rysunok_2_6.png", dpi=200)
print("Збережено rysunok_2_6.png")
