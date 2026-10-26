#!/usr/bin/env python3
"""Plot the three Lab 4 MCA spectra (Ortec .Chn files in ../data/mca).
Counts are rebinned by BIN channels for readability. Dashed line = centroid channel used in the report
(pulse_height_consistency.csv); voltage from V = -36.0 mV + 1.31 mV * n."""
import os, struct
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
MCA = os.path.join(HERE, "..", "data", "mca")
BIN = 16
SOURCES = [  # file stem, label, centroid channel, colour
    ("Co60", "Co-60", 2906, "#2878d6"),
    ("C14", "C-14", 3374, "#ec6a35"),
    ("Cl36", "Cl-36", 1939, "#00a070"),
]


def load_chn(path):
    b = open(path, "rb").read()
    n = struct.unpack("<h", b[30:32])[0]
    live = struct.unpack("<i", b[12:16])[0] * 0.02
    return np.frombuffer(b[32:32 + 4 * n], dtype="<i4").astype(float), live


plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.25})
fig, axes = plt.subplots(3, 1, figsize=(6.5, 6.0), sharex=True)
for ax, (stem, label, cen, col) in zip(axes, SOURCES):
    d, live = load_chn(os.path.join(MCA, f"lab4_sec3_{stem}.Chn"))
    nb = len(d) // BIN
    y = d[:nb * BIN].reshape(nb, BIN).sum(axis=1)
    x = np.arange(nb) * BIN
    ax.fill_between(x, y, step="post", color=col, alpha=0.35, lw=0)
    ax.step(x, y, where="post", color=col, lw=1.0)
    ax.axvline(cen, color="#444444", ls="--", lw=1)
    v = (-36.0 + 1.31 * cen) / 1000
    ax.text(0.02, 0.92, f"{label}: {int(d.sum())} counts\ncentroid channel {cen} ({v:.2f} V)",
            transform=ax.transAxes, ha="left", va="top")
    ax.set_ylabel(f"counts / {BIN} ch")
    ax.set_ylim(0, y.max() * 1.15)
axes[-1].set_xlim(0, 4000)
axes[-1].set_xlabel("MCA channel")
fig.tight_layout()
out = os.path.join(HERE, "figures", "mca_spectra.png")
fig.savefig(out, dpi=200)
print("wrote", out)
