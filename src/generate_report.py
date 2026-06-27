from __future__ import annotations
from health_report.preprocessing.merge_daily import build_master_dataframe, save_master_dataframe
from health_report.analysis.body_composition import first_last_metrics, monthly_summary, phase_summary
from health_report.visualization.chapter4 import plot_weight, plot_fat, plot_lean, plot_delta, plot_timeline, plot_growth_rate
from health_report.report.pdf_chapter4 import build_pdf, REPORT_VERSION
from health_report.common.paths import OUTPUT


def main():
    df = build_master_dataframe()
    save_master_dataframe(df)
    metrics = first_last_metrics(df)
    monthly = monthly_summary(df)
    phases = phase_summary(df)
    metrics.to_csv(OUTPUT / "body_composition_metrics.csv", index=False)
    monthly.to_csv(OUTPUT / "monthly_body_composition.csv")
    phases.to_csv(OUTPUT / "phase_summary.csv", index=False)
    figs = [
        ("Weight trajectory, daily values and 7-day rolling mean.", plot_weight(df)),
        ("Fat Mass trajectory, daily values and 7-day rolling mean.", plot_fat(df)),
        ("Lean Mass trajectory, daily values and 7-day rolling mean.", plot_lean(df)),
        ("Weight and Fat Mass change relative to August baseline.", plot_delta(df)),
        ("Fat Mass with major events and intervention periods. Intervention bands show long-running medication intervals and travel periods; vertical markers show discrete events.", plot_timeline(df)),
        ("Rolling 28-day Fat Mass growth rate, expressed as g/week.", plot_growth_rate(df)),
    ]
    pdf = build_pdf(df, metrics, monthly, phases, figs)
    print(f"Generated {REPORT_VERSION}: {pdf}")


if __name__ == "__main__":
    main()
