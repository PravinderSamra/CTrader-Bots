# -*- coding: utf-8 -*-
"""Shared schematic-chart helpers for the Carmine Rosato syllabus diagrams.

Used by make_diagrams.py (module 1) and make_module2_diagrams.py. Every diagram
built on these illustrates a rule stated in a transcript - nothing invented.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "03-diagrams")
os.makedirs(OUT, exist_ok=True)

UP, DN = "#2e8b57", "#c0392b"
DEMAND, SUPPLY = "#2e8b57", "#c0392b"
INK, MUTE = "#1b1b1b", "#8a8a8a"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})


def candle(ax, x, o, c, h, l, w=0.34):
    up = c >= o
    col = UP if up else DN
    ax.plot([x, x], [l, h], color=col, lw=1.1, solid_capstyle="round", zorder=3)
    ax.add_patch(Rectangle((x - w / 2, min(o, c)), w, max(abs(c - o), 0.035),
                           facecolor=col, edgecolor=col, lw=0.8, zorder=4))


def finish(ax, title, sub=None):
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    pad = 27 if sub else 10
    ax.set_title(title, fontsize=11, fontweight="bold", color=INK, pad=pad, loc="left")
    if sub:
        ax.text(0, 1.012, sub, transform=ax.transAxes, fontsize=8.5,
                color=MUTE, va="bottom")


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=190, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print("  wrote", name)
