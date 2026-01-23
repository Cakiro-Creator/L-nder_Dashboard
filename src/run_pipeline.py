# run_pipeline.py
# Orchestriert den gesamten Ablauf
from src.config import RAW_CSV, CLEAN_CSV, PLOT_PATH, PLOT_POP_CHANGE_TOP, PLOT_POP_CHANGE_BOTTOM, PLOT_GDP_LIFE, PLOT_GDP_PC
from src.fetch_api import get_countries, fetch_indicator_data_all
from src.transform import clean_data, add_features
from src.quality_checks import validate
from src.load_sqlite import load_to_sqlite
from src.viz import (
    plot_top_population,
    plot_population_change_top10,
    plot_population_change_bottom10,
    plot_gdp_vs_life_expectancy,
    plot_top_gdp_per_capita,
)
def main():
    # 1) Laender laden
    countries = get_countries()
    # 2) Daten fuer alle Laender holen
    raw_df = fetch_indicator_data_all(countries)
    # 4) Raw speichern
    RAW_CSV.parent.mkdir(parents=True, exist_ok=True)
    raw_df.to_csv(RAW_CSV, index=False)
    # 5) Cleaning + Features
    clean_df = clean_data(raw_df)
    clean_df = add_features(clean_df)
    # 6) Checks
    checks = validate(clean_df)
    print("Checks:")
    for k, v in checks.items():
        print(f"- {k}: {v}")
    # 7) Processed speichern
    CLEAN_CSV.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(CLEAN_CSV, index=False)
    # 8) SQLite laden
    load_to_sqlite(clean_df)
    # 9) Plot speichern
    PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plot_top_population(clean_df, PLOT_PATH)
    plot_population_change_top10(clean_df, PLOT_POP_CHANGE_TOP)
    plot_population_change_bottom10(clean_df, PLOT_POP_CHANGE_BOTTOM)
    plot_gdp_vs_life_expectancy(clean_df, PLOT_GDP_LIFE)
    plot_top_gdp_per_capita(clean_df, PLOT_GDP_PC)
    print(f"Saved: {RAW_CSV}")
    print(f"Saved: {CLEAN_CSV}")
    print(f"Saved: {PLOT_PATH}")
    print(f"Saved: {PLOT_POP_CHANGE_TOP}")
    print(f"Saved: {PLOT_POP_CHANGE_BOTTOM}")
    print(f"Saved: {PLOT_GDP_LIFE}")
    print(f"Saved: {PLOT_GDP_PC}")
if __name__ == "__main__":
    main()
