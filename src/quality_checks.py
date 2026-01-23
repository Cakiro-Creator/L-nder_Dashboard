# quality_checks.py
# Einfache Plausibilitaetschecks
from src.config import START_YEAR, END_YEAR
def validate(df):
    checks = {
        "no_missing_country": df["country_code"].notna().all(),
        "year_in_range": df["year"].between(START_YEAR, END_YEAR).all(),
        "values_non_negative": (df["value"] >= 0).all(),
        "no_duplicates": df.duplicated(["country_code", "indicator_code", "year"]).sum() == 0,
    }
    return checks
