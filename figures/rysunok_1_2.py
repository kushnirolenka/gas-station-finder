# Рисунок 1.2: відносна похибка евклідової формули в градусах вздовж паралелі залежно від широти.
import numpy as np
import matplotlib.pyplot as plt

phi = np.linspace(0, 70, 400)
err = (1 / np.cos(np.radians(phi)) - 1) * 100      # формула (1.4), у відсотках

fig, ax = plt.subplots(figsize=(8, 4.8))
ax.plot(phi, err, color="#2a6f97", lw=2)
for name, f, dy, c in (("Львів", 49.84, -22, "#d1495b"), ("Київ", 50.45, -34, "#2a9d8f")):
    e = (1 / np.cos(np.radians(f)) - 1) * 100
    ax.plot(f, e, "o", color=c)
    ax.annotate(f"{name} ({f:.2f}°): ≈{e:.0f} %".replace(".", ","), (f, e),
                xytext=(f - 30, e + 22 + (0 if name == "Львів" else -16)), color=c, fontsize=10,
                arrowprops=dict(arrowstyle="-", color=c, lw=0.8))
ax.set_xlim(0, 70)
ax.set_ylim(0, 200)
ax.set_xlabel("Географічна широта φ, градуси")
ax.set_ylabel("Відносна похибка, %")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("rysunok_1_2.png", dpi=200)
print("Збережено rysunok_1_2.png")
