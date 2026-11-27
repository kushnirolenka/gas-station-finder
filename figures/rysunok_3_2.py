# Рисунок 3.2: історія версій застосунку в репозиторії (основна гілка main, гілки ітерацій, теги).
import matplotlib.pyplot as plt

versions = ["v1.0", "v1.1", "v1.2", "v1.3", "v2.0"]
branches = [                       # (назва гілки, кількість комітів, дефекти)
    ("iter/v1.1-correctness", 4, "Д1, Д2, Д6"),
    ("iter/v1.2-geocoding", 3, "Д3"),
    ("iter/v1.3-maintainability", 3, "Д4, Д5, Д7"),
    ("iter/v2.0-performance", 2, "Д9, Д11"),
]
word = {2: "коміти", 3: "коміти", 4: "коміти"}
step = 4.0
fig, ax = plt.subplots(figsize=(11, 4.2))

xs = [i * step for i in range(len(versions))]
ax.plot([-0.9, xs[-1] + 0.9], [0, 0], color="#2a6f97", lw=4, zorder=1)
for x, v in zip(xs, versions):
    ax.plot(x, 0, "o", ms=16, color="#2a6f97", zorder=3)
    ax.text(x, -0.35, "тег " + v, ha="center", va="top", fontsize=13, fontweight="bold")
ax.text(-0.9, 0.28, "main", color="#2a6f97", fontsize=14, fontweight="bold")

for i, (name, n, defects) in enumerate(branches):
    x0, x1 = xs[i], xs[i + 1]
    inner = [x0 + (x1 - x0) * (k + 1) / (n + 1) for k in range(n)]
    ax.plot([x0] + inner + [x1], [0] + [1.2] * n + [0], color="#e9a23b", lw=2.5, zorder=1)
    ax.plot(inner, [1.2] * n, "o", ms=11, color="#e9a23b", zorder=3)
    ax.text((x0 + x1) / 2, 1.85, name, ha="center", fontsize=12, color="#8a5a0a", fontweight="bold")
    ax.text((x0 + x1) / 2, 1.5, f"{n} {word[n]}, {defects}", ha="center", fontsize=11, color="#444444")

ax.set_xlim(-1.2, xs[-1] + 1.0)
ax.set_ylim(-1.0, 2.25)
ax.axis("off")
plt.tight_layout()
plt.savefig("rysunok_3_2.png", dpi=200, bbox_inches="tight")
print("Збережено rysunok_3_2.png")
