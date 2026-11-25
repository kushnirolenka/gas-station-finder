# Рисунок 1.3: двоетапний пошук у межах радіуса (приклад на випадкових точках навколо користувача).
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

R = 5.0                                           # радіус пошуку, км
rng = np.random.default_rng(3)
x, y = rng.uniform(-9, 9, 45), rng.uniform(-9, 9, 45)   # східна та північна відстані від користувача, км
in_rect = (abs(x) <= R) & (abs(y) <= R)
in_circ = x**2 + y**2 <= R**2

fig, ax = plt.subplots(figsize=(6.4, 6.4))
ax.add_patch(Circle((0, 0), R, color="#2a9d8f", alpha=0.12))
ax.add_patch(Circle((0, 0), R, fill=False, ec="#2a9d8f", lw=1, ls=":"))
ax.add_patch(Rectangle((-R, -R), 2 * R, 2 * R, fill=False, ec="#e76f51", ls="--", lw=1.5))
ax.scatter(x[~in_rect], y[~in_rect], c="#999999", s=22, label="відсіяно на кроці 1 (поза прямокутником)")
ax.scatter(x[in_rect & ~in_circ], y[in_rect & ~in_circ], c="#f4a261", s=30, label="відсіяно на кроці 2 (у прямокутнику, поза колом)")
ax.scatter(x[in_circ], y[in_circ], c="#2a9d8f", s=30, label="результат (у межах радіуса)")
ax.plot(0, 0, marker="*", color="#d1495b", ms=16, ls="", label="користувач")
ax.set_xlim(-9.5, 9.5); ax.set_ylim(-9.5, 9.5); ax.set_aspect("equal")
ax.set_xlabel("схід-захід, км"); ax.set_ylabel("північ-південь, км")
ax.grid(alpha=0.25)
ax.xaxis.set_major_formatter(lambda v, _: f"{v:g}".replace(".", ","))
ax.yaxis.set_major_formatter(lambda v, _: f"{v:g}".replace(".", ","))
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), fontsize=9, frameon=False)
plt.tight_layout()
plt.savefig("rysunok_1_3.png", dpi=200, bbox_inches="tight")
print("Збережено rysunok_1_3.png")
