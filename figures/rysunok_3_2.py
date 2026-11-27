# Рисунок 3.2: історія версій застосунку в репозиторії (основна гілка main, гілки ітерацій, теги).
import matplotlib.pyplot as plt

versions = ["v1.0", "v1.1", "v1.2", "v1.3", "v2.0"]
branches = [                       # (назва гілки, кількість комітів, дефекти)
    ("iter/v1.1-correctness", 4, "Д1, Д2, Д6"),
    ("iter/v1.2-geocoding", 3, "Д3"),
    ("iter/v1.3-maintainability", 3, "Д4, Д5, Д7"),
    ("iter/v2.0-performance", 2, "Д9, Д11"),
]
step = 4.0
fig, ax = plt.subplots(figsize=(11, 5))

# основна гілка main
xs = [i * step for i in range(len(versions))]
ax.plot([-0.8, xs[-1] + 0.8], [0, 0], color="#2a6f97", lw=3, zorder=1)
ax.text(-1.1, 0.3, "main", color="#2a6f97", fontsize=12, fontweight="bold")
for x, v in zip(xs, versions):
    ax.plot(x, 0, "o", ms=13, color="#2a6f97", zorder=3)
    ax.text(x, -0.55, "тег " + v, ha="center", va="top", fontsize=11, fontweight="bold")

# гілки ітерацій: відходять від попередньої версії, зливаються у наступну
for i, (name, n, defects) in enumerate(branches):
    x0, x1 = xs[i], xs[i + 1]
    inner = [x0 + (x1 - x0) * (k + 1) / (n + 1) for k in range(n)]
    ax.plot([x0] + inner + [x1], [0] + [1.4] * n + [0], color="#e9a23b", lw=2, zorder=1)
    ax.plot(inner, [1.4] * n, "o", ms=9, color="#e9a23b", zorder=3)
    ax.text((x0 + x1) / 2, 1.95, name, ha="center", fontsize=10, color="#9a6a12")
    ax.text((x0 + x1) / 2, 1.65, f"{n} к., {defects}".replace("к.", "комітів" if n > 4 else "коміти" if n > 1 else "коміт"),
            ha="center", fontsize=9, color="#555555")

ax.set_xlim(-1.2, xs[-1] + 1.2)
ax.set_ylim(-1.4, 2.6)
ax.axis("off")
plt.tight_layout()
plt.savefig("rysunok_3_2.png", dpi=200)
print("Збережено rysunok_3_2.png")
