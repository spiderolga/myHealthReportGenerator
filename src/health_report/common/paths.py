from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
FIGURES = ROOT / "figures"
OUTPUT = ROOT / "output"
REPORT = ROOT / "report"

for path in [PROCESSED, FIGURES, OUTPUT, REPORT / "chapters"]:
    path.mkdir(parents=True, exist_ok=True)
