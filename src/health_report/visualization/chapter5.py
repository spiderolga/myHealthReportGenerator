from __future__ import annotations
import pandas as pd
import matplotlib.pyplot as plt
from health_report.common.paths import FIGURES
from health_report.visualization.style import DAILY_COLOR, TREND_COLOR, GRID_COLOR, save_compact


def plot_food_diary_coverage(coverage: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11.2, 4.8))
    x = range(len(coverage))
    bars = ax.bar(x, coverage["Coverage %"], color=TREND_COLOR, alpha=0.82)
    ax.set_title("Food diary coverage by month", pad=8, fontsize=12)
    ax.set_ylabel("Coverage, %")
    ax.set_ylim(0, max(100, float(coverage["Coverage %"].max()) + 8))
    ax.set_xticks(list(x))
    ax.set_xticklabels(coverage["Month"], rotation=35, ha="right", fontsize=8.8)
    ax.tick_params(axis="y", labelsize=8.8)
    ax.grid(True, axis="y", color=GRID_COLOR, alpha=0.28, linewidth=0.55)
    for rect, logged in zip(bars, coverage["Logged days"]):
        h = rect.get_height()
        if logged > 0:
            ax.text(rect.get_x() + rect.get_width()/2, h + 1.4, str(int(logged)), ha="center", va="bottom", fontsize=7.8, color=DAILY_COLOR)
    out = FIGURES / "fig_5_1_food_diary_coverage.png"
    save_compact(fig, out)
    plt.close(fig)
    return out
