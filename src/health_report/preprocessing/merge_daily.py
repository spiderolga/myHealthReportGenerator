from __future__ import annotations
import pandas as pd
from health_report.common.paths import DATA, PROCESSED
from health_report.common.config import REPORT_START_DATE, REPORT_END_DATE
from health_report.loaders.withings_loader import load_withings
from health_report.loaders.garmin_loader import load_garmin_daily, load_activities, load_steps, load_garmin_calories_csv
from health_report.loaders.mfp_loader import load_mfp_daily
from health_report.loaders.events_loader import load_events, add_event_flags

def build_master_dataframe(start_date: str = REPORT_START_DATE, end_date: str = REPORT_END_DATE) -> pd.DataFrame:
    main = DATA / "Health_Analytics_Database_DailySummary.xlsx"
    withings_csv = DATA / "withings" / "weight.csv"
    mfp = DATA / "MyFitnessPal_parsed_data.xlsx"
    events_path = DATA / "events.csv"
    activities_csv = DATA / "garmin" / "Activities.csv"
    steps_csv = DATA / "garmin" / "Steps.csv"
    calories_csv = DATA / "garmin" / "Calories.csv"
    dates = pd.DataFrame({"Date": pd.date_range(start_date, end_date, freq="D")})
    frames = [
        load_withings(str(withings_csv if withings_csv.exists() else main), start_date, end_date),
        load_garmin_calories_csv(str(calories_csv), start_date, end_date) if calories_csv.exists() else load_garmin_daily(str(main), start_date, end_date),
        load_steps(str(steps_csv), start_date, end_date),
        load_activities(str(activities_csv if activities_csv.exists() else main), start_date, end_date),
        load_mfp_daily(str(mfp), start_date, end_date),
    ]
    master = dates.copy()
    for frame in frames:
        master = master.merge(frame, on="Date", how="left")
    ev = load_events(str(events_path), start_date, end_date)
    master = add_event_flags(master, ev)
    for c in ["Garmin Active Calories", "Garmin Resting Calories", "Garmin Total Calories", "Activity Count", "Activity Duration min", "Activity Calories", "Activity Steps", "Badminton Count", "Badminton Duration min", "Badminton Calories", "Strength Count", "Strength Duration min", "Strength Calories", "Walking Count", "Walking Duration min", "Walking Calories", "Steps"]:
        if c in master.columns:
            master[c] = master[c].fillna(0)
    master["Energy Balance"] = master["Garmin Total Calories"] - master["Calories In"]
    master["Fat_7d"] = master["Fat mass kg"].rolling(7, min_periods=3).mean()
    master["Lean_7d"] = master["Lean mass kg"].rolling(7, min_periods=3).mean()
    master["Weight_7d_calc"] = master["Weight kg"].rolling(7, min_periods=3).mean()
    first_fat = master["Fat_7d"].dropna().iloc[0]
    first_weight = master["Weight_7d_calc"].dropna().iloc[0]
    master["Delta_Fat_from_start"] = master["Fat_7d"] - first_fat
    master["Delta_Weight_from_start"] = master["Weight_7d_calc"] - first_weight
    master["Fat_28d_change"] = master["Fat_7d"] - master["Fat_7d"].shift(28)
    master["Fat_g_per_week_28d"] = master["Fat_28d_change"] / 4.0 * 1000
    return master


def save_master_dataframe(master: pd.DataFrame) -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    master.to_csv(PROCESSED / "master_dataframe.csv", index=False)
    try:
        master.to_parquet(PROCESSED / "master_dataframe.parquet", index=False)
    except Exception:
        # Parquet requires an optional engine such as pyarrow. CSV remains canonical if unavailable.
        pass
