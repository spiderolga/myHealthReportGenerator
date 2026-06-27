from __future__ import annotations
import matplotlib.dates as mdates

DAILY_COLOR = "#202020"
TREND_COLOR = "#1D4ED8"
ALT_COLOR = "#0F766E"
GRID_COLOR = "#D1D5DB"
ZERO_COLOR = "#4B5563"


def style_time_axis(ax):
    ax.grid(True, color=GRID_COLOR, alpha=0.28, linewidth=0.55)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.tick_params(axis="x", rotation=35, labelsize=8.8)
    ax.tick_params(axis="y", labelsize=8.8)


def save_compact(fig, out):
    fig.subplots_adjust(left=0.075, right=0.985, top=0.90, bottom=0.18)
    fig.savefig(out, dpi=220)
    return out
