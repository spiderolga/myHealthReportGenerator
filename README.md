# Personal Weight Regulation Report Generator

This folder contains a reproducible report generator for the project:

**Body Composition Regulation After Successful Weight Loss - N-of-1 Case Study**

Current scope: Draft v0.6, Sprint 1 - Body Composition Analysis.

## Inputs

Place these files in `data/`:

- `Health_Analytics_Database_DailySummary.xlsx`
- `MyFitnessPal_parsed_data.xlsx` (reserved for Nutrition sprint)
- `events.csv`

## Run

```bash
python src/generate_report.py

# or, from IntelliJ IDEA / Gradle:
./gradlew generateReport   # if Gradle wrapper is added locally
gradle generateReport      # if Gradle is installed
```

## Outputs

- `output/Personal_Weight_Regulation_Model_v0.6.pdf`
- `output/body_composition_metrics.csv`
- `output/monthly_body_composition.csv`
- `output/phase_summary.csv`
- figures in `figures/`

## Notes

- Withings Fat Mass and Lean Mass are treated as trend-level metrics, not clinical-grade body composition measurement.
- DEXA is not reproduced in this Sprint.
- Garmin calories are not interpreted in Sprint 1.


## Gradle / IntelliJ IDEA

This project includes `settings.gradle` and `build.gradle` so it can be opened in IntelliJ IDEA as a Gradle project.

Available tasks:

- `installPythonDeps` - installs Python dependencies from `requirements.txt`.
- `generateReport` - generates the report PDF, figures, and CSV outputs.
- `cleanReport` - deletes generated `figures/` and `output/`.
- `build` - depends on `generateReport`.

If your Python executable is not named `python`, run:

```bash
gradle generateReport -PpythonExecutable=python3
```

## Changelog

### v0.6

- Redesigned Figure 4.5.
- Added compact right-side **Event reference** table.
- Restored full event/intervention names.
- Split the Event reference into Interventions, Clinical events, and Travel.
- Added distinct visual grammar: intervention bands, vertical event markers, and translucent travel areas.
- Added Gradle build files for IntelliJ IDEA workflow.
