from __future__ import annotations
import textwrap
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from health_report.common.paths import FIGURES
from health_report.common.config import REPORT_END_DATE
from health_report.visualization.style import DAILY_COLOR, TREND_COLOR, GRID_COLOR, ZERO_COLOR, style_time_axis, save_compact


def plot_weight(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11.2, 4.8))
    ax.plot(df["Date"], df["Weight kg"], color=DAILY_COLOR, alpha=0.72, linewidth=1.55, label="Daily")
    ax.plot(df["Date"], df["Weight_7d_calc"], color=TREND_COLOR, linewidth=2.65, label="7-day mean")
    ax.set_title("Weight trajectory", pad=8, fontsize=12)
    ax.set_ylabel("kg")
    style_time_axis(ax)
    ax.legend(frameon=False, fontsize=8.8)
    out = FIGURES / "fig_4_1_weight_trajectory.png"
    save_compact(fig, out)
    plt.close(fig)
    return out


def plot_fat(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11.2, 4.8))
    ax.plot(df["Date"], df["Fat mass kg"], color=DAILY_COLOR, alpha=0.72, linewidth=1.55, label="Daily")
    ax.plot(df["Date"], df["Fat_7d"], color=TREND_COLOR, linewidth=2.65, label="7-day mean")
    ax.set_title("Fat Mass trajectory", pad=8, fontsize=12)
    ax.set_ylabel("kg")
    style_time_axis(ax)
    ax.legend(frameon=False, fontsize=8.8)
    out = FIGURES / "fig_4_2_fat_trajectory.png"
    save_compact(fig, out)
    plt.close(fig)
    return out


def plot_lean(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11.2, 4.8))
    ax.plot(df["Date"], df["Lean mass kg"], color=DAILY_COLOR, alpha=0.72, linewidth=1.55, label="Daily")
    ax.plot(df["Date"], df["Lean_7d"], color=TREND_COLOR, linewidth=2.65, label="7-day mean")
    ax.set_title("Lean Mass trajectory", pad=8, fontsize=12)
    ax.set_ylabel("kg")
    style_time_axis(ax)
    ax.legend(frameon=False, fontsize=8.8)
    out = FIGURES / "fig_4_3_lean_trajectory.png"
    save_compact(fig, out)
    plt.close(fig)
    return out


def plot_delta(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11.2, 4.8))
    ax.plot(df["Date"], df["Delta_Weight_from_start"], color=DAILY_COLOR, linewidth=2.35, label="Weight Δ from Aug baseline")
    ax.plot(df["Date"], df["Delta_Fat_from_start"], color=TREND_COLOR, linewidth=2.35, label="Fat Mass Δ from Aug baseline")
    ax.axhline(0, color=ZERO_COLOR, linewidth=1.25, alpha=0.95)
    ax.set_title("Weight and Fat Mass change from baseline", pad=8, fontsize=12)
    ax.set_ylabel("kg change")
    style_time_axis(ax)
    ax.legend(frameon=False, fontsize=8.8)
    out = FIGURES / "fig_4_4_delta_weight_fat.png"
    save_compact(fig, out)
    plt.close(fig)
    return out


def plot_timeline(df: pd.DataFrame):
    fig = plt.figure(figsize=(13.2, 5.55))
    # Keep the reference column narrow, but remove unused right margin so text gets the full available width.
    gs = gridspec.GridSpec(1, 2, width_ratios=[5.45, 1.23], wspace=0.035)
    ax = fig.add_subplot(gs[0, 0])
    ax_ref = fig.add_subplot(gs[0, 1])
    ax_ref.axis("off")

    ax.plot(df["Date"], df["Fat_7d"], linewidth=2.75, color=DAILY_COLOR, zorder=6)

    intervention_bands = [
        ("Ozempic (0.5 mg -> taper -> stop)", "Sep-Dec 2025", pd.Timestamp("2025-09-01"), pd.Timestamp("2025-12-08"), "#4F46E5"),
        ("HRT 0.5 mg", "from 06 Jan 2026", pd.Timestamp("2026-01-06"), pd.Timestamp("2026-04-20"), "#86EFAC"),
        ("HRT 1.0 mg", "from 21 Apr 2026", pd.Timestamp("2026-04-21"), pd.Timestamp(REPORT_END_DATE), "#047857"),
    ]
    event_markers = [
        ("Perimenopausal signs", "from Sep 2025", pd.Timestamp("2025-09-20"), "#7C3AED", ":"),
        ("Strength training", "from Nov 2025", pd.Timestamp("2025-11-16"), "#7C3AED", "--"),
        ("RA flare", "Mar-Apr 2026", pd.Timestamp("2026-03-16"), "#DC2626", "-"),
        ("Medrol course", "30 Mar-03 Apr 2026", pd.Timestamp("2026-03-30"), "#B91C1C", "--"),
    ]
    travel_periods = [
        ("Italy trip 3", "", pd.Timestamp("2025-09-17"), pd.Timestamp("2025-09-27"), "#F59E0B"),
        ("Winter Trip", "", pd.Timestamp("2026-02-06"), pd.Timestamp("2026-02-23"), "#F59E0B"),
        ("Italy Trip 4", "", pd.Timestamp("2026-04-19"), pd.Timestamp("2026-05-02"), "#F59E0B"),
        ("Italy Trip 5", "", pd.Timestamp("2026-05-12"), pd.Timestamp("2026-05-30"), "#F59E0B"),
    ]
    for _, _, start, end, color in intervention_bands:
        ax.axvspan(start, end, color=color, alpha=0.20 if color == "#047857" else 0.16, linewidth=0, zorder=1)
    for _, _, start, end, color in travel_periods:
        ax.axvspan(start, end, color=color, alpha=0.19, linewidth=0, zorder=2)
    for _, _, date, color, linestyle in event_markers:
        ax.axvline(date, color=color, linewidth=1.75, linestyle=linestyle, alpha=0.90, zorder=4)

    ax.set_title("Fat Mass trajectory with intervention and event timeline", pad=8, fontsize=12)
    ax.set_ylabel("Fat Mass, kg")
    style_time_axis(ax)

    ax_ref.text(0.00, 0.985, "Event reference", transform=ax_ref.transAxes, fontsize=10.1, fontweight="bold", va="top", color="#111827")

    def ref_header(y, text):
        ax_ref.text(0.00, y, text, transform=ax_ref.transAxes, fontsize=8.4, fontweight="bold", va="top", color="#374151")
        return y - 0.046

    def label_text(label, note):
        return label if not note else f"{label}\n{note}"

    def ref_band(y, color, label, note="", alpha=0.25):
        ax_ref.add_patch(plt.Rectangle((0.00, y - 0.030), 0.065, 0.028, transform=ax_ref.transAxes, facecolor=color, alpha=alpha, edgecolor=color, linewidth=0.7))
        wrapped = "\n".join(textwrap.wrap(label_text(label, note), width=29, break_long_words=False))
        ax_ref.text(0.082, y - 0.016, wrapped, transform=ax_ref.transAxes, fontsize=7.25, va="center", color="#111827", linespacing=1.13)
        return y - (0.043 + 0.022 * max(0, wrapped.count("\n")))

    def ref_line(y, color, label, note="", linestyle="-"):
        ax_ref.plot([0.00, 0.065], [y - 0.016, y - 0.016], transform=ax_ref.transAxes, color=color, linewidth=1.75, linestyle=linestyle, solid_capstyle="butt")
        wrapped = "\n".join(textwrap.wrap(label_text(label, note), width=29, break_long_words=False))
        ax_ref.text(0.082, y - 0.016, wrapped, transform=ax_ref.transAxes, fontsize=7.25, va="center", color="#111827", linespacing=1.13)
        return y - (0.043 + 0.022 * max(0, wrapped.count("\n")))

    y = 0.92
    y = ref_header(y, "Interventions")
    for label, note, _, _, color in intervention_bands:
        y = ref_band(y, color, label, note, alpha=0.30 if "HRT 1.0" in label else 0.25)
    label, note, _, color, linestyle = event_markers[0]
    y = ref_line(y, color, label, note, linestyle=linestyle)

    y -= 0.016
    y = ref_header(y, "Clinical events")
    for label, note, _, color, linestyle in event_markers[1:]:
        y = ref_line(y, color, label, note, linestyle=linestyle)

    y -= 0.016
    y = ref_header(y, "Travel")
    for label, note, _, _, color in travel_periods:
        y = ref_band(y, color, label, alpha=0.30)

    out = FIGURES / "fig_4_5_fat_timeline_events.png"
    fig.subplots_adjust(left=0.060, right=0.998, top=0.91, bottom=0.17)
    fig.savefig(out, dpi=250)
    plt.close(fig)
    return out


def plot_growth_rate(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11.2, 4.8))
    ax.plot(df["Date"], df["Fat_g_per_week_28d"], color=DAILY_COLOR, linewidth=2.35)
    ax.axhline(0, color=ZERO_COLOR, linewidth=1.25, alpha=0.95)
    ax.set_title("Fat Mass growth rate estimated over rolling 28-day windows", pad=8, fontsize=12)
    ax.set_ylabel("g/week")
    style_time_axis(ax)
    out = FIGURES / "fig_4_6_fat_growth_rate.png"
    save_compact(fig, out)
    plt.close(fig)
    return out
