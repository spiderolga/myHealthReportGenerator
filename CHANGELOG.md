
## v0.7.2

### Added
- Added Garmin `data/garmin/Calories.csv` as source for daily Garmin calories.
- Added Garmin `data/garmin/Steps.csv` loader into master dataframe build.

### Changed
- `master_dataframe.csv` now includes `Steps`, `Garmin Active Calories`, `Garmin Resting Calories`, `Garmin Total Calories`, and `Energy Balance`.
- Step Goal and Distance are intentionally excluded from the master dataframe.

# Changelog

## v0.7.3

### Added
- Added centralized report configuration in `src/health_report/common/config.py`.

### Changed
- Feature #19: report end date is now `2026-06-27`.
- Master dataframe now uses the updated Withings CSV export from `data/withings/weight.csv` when present.
- Phase III and HRT timeline overlays now use the shared report end date instead of local hardcoded values.
- README documents the single source of truth for report start/end dates.

### Verified
- `data/processed/master_dataframe.csv` runs from `2025-08-01` through `2026-06-27`.
- No `2026-06-25` hardcoded value remains in source code.

## v0.7

### Changed
- Introduced Version 2 architecture with modular loaders, preprocessing, analysis, visualization, and report layers.
- Added `data/processed/master_dataframe.csv` as the central daily dataset.
- Chapter 4 figures and tables now build from the master dataframe rather than reading Excel sheets directly.
- Observation period starts from 2025-08-01 to include the pre-drift baseline.

### Added
- `src/health_report/loaders/` for Withings, Garmin, MyFitnessPal, and events.
- `src/health_report/preprocessing/merge_daily.py` for the daily master dataframe.
- `src/health_report/analysis/body_composition.py`.
- `src/health_report/visualization/chapter4.py`.
- `src/health_report/report/pdf_chapter4.py`.

## v0.6

### Changed
- Figure 4.5 Event reference column reduced to approximately 18% of figure width.
- Removed redundant micro-notes from the Event reference block.
- HRT 0.5 mg and HRT 1.0 mg are now visually distinct and include start-date notes.
- Increased effective plot area across longitudinal figures by reducing margins.

### Added
- Event reference grouping retained: Interventions, Clinical events, Travel.

## v0.5

### Changed
- Redesigned Figure 4.5 with Event reference.
- Added Gradle build task for report generation.

## v0.6.1

### Changed
- Issue #18: made daily/main lines darker and more visible across Chapter 4 plots.
- Issue #19: aligned figure captions with the plot area rather than the page margin.
- Strengthened zero reference line in growth-rate and delta plots.
- Replaced Gradle project setup with Python packaging via `pyproject.toml`.

## v0.7.1

### Added
- Added Garmin activity CSV input at `data/garmin/Activities.csv`.
- Added Garmin step CSV input at `data/garmin/Steps.csv`.
- Added Garmin activity aggregation into the master dataframe.
- Added daily Badminton, Strength, and Walking counts, duration, calories, and activity steps.

### Changed
- Master dataframe now prefers Garmin CSV activity export when present and falls back to the legacy Excel Activities sheet otherwise.
- Garmin activity category detection now uses both `Activity Type` and `Title`, so Garmin Cardio sessions titled `Badminton` are classified correctly.
