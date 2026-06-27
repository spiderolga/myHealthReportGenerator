from __future__ import annotations
from health_report.preprocessing.merge_daily import build_master_dataframe, save_master_dataframe
from health_report.analysis.body_composition import first_last_metrics, monthly_summary, phase_summary
from health_report.visualization.chapter4 import plot_weight, plot_fat, plot_lean, plot_delta, plot_timeline, plot_growth_rate
from health_report.analysis.nutrition import food_diary_coverage, detect_nutrition_phases, nutrition_phase_summary
from health_report.visualization.chapter5 import plot_food_diary_coverage
from health_report.report.pdf_chapter4 import build_pdf, REPORT_VERSION
from health_report.common.paths import OUTPUT


def main():
    df = build_master_dataframe()
    save_master_dataframe(df)
    metrics = first_last_metrics(df)
    monthly = monthly_summary(df)
    phases = phase_summary(df)
    nutrition_coverage = food_diary_coverage(df)
    nutrition_phases = detect_nutrition_phases(df)
    nutrition_summary = nutrition_phase_summary(df, nutrition_phases)
    metrics.to_csv(OUTPUT / "body_composition_metrics.csv", index=False)
    monthly.to_csv(OUTPUT / "monthly_body_composition.csv")
    phases.to_csv(OUTPUT / "phase_summary.csv", index=False)
    nutrition_coverage.to_csv(OUTPUT / "nutrition_coverage.csv", index=False)
    nutrition_phases.to_csv(OUTPUT / "nutrition_phases.csv", index=False)
    nutrition_summary.to_csv(OUTPUT / "nutrition_phase_summary.csv", index=False)
    figs = [
        ("Weight trajectory, daily values and 7-day rolling mean.", plot_weight(df)),
        ("Fat Mass trajectory, daily values and 7-day rolling mean.", plot_fat(df)),
        ("Lean Mass trajectory, daily values and 7-day rolling mean.", plot_lean(df)),
        ("Weight and Fat Mass change relative to August baseline.", plot_delta(df)),
        ("Fat Mass with major events and intervention periods. Intervention bands show long-running medication intervals and travel periods; vertical markers show discrete events.", plot_timeline(df)),
        ("Rolling 28-day Fat Mass growth rate, expressed as g/week.", plot_growth_rate(df)),
    ]
    nutrition_figs = [("Food diary coverage by month. Labels above bars show logged days.", plot_food_diary_coverage(nutrition_coverage))]
    pdf = build_pdf(df, metrics, monthly, phases, figs, nutrition_coverage, nutrition_phases, nutrition_summary, nutrition_figs)
    print(f"Generated {REPORT_VERSION}: {pdf}")


if __name__ == "__main__":
    main()
