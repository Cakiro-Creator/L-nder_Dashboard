# config.py
# Zentrale Einstellungen fuer API und Pfade
from pathlib import Path
from datetime import datetime
BASE_URL = "https://api.worldbank.org/v2"
END_YEAR = datetime.now().year - 1
START_YEAR = END_YEAR - 4
INDICATORS = {
    "SP.POP.TOTL": "Population",
    "NY.GDP.MKTP.CD": "GDP (current US$)",
    "SP.DYN.LE00.IN": "Life expectancy (years)",
}
SLEEP_SEC = 0.1
ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = ROOT / "data" / "raw" / "worldbank_raw.csv"
CLEAN_CSV = ROOT / "data" / "processed" / "worldbank_clean.csv"
SQLITE_DB = ROOT / "data" / "processed" / "worldbank.db"
PLOT_PATH = ROOT / "reports" / "figures" / "top_population.png"
PLOT_POP_CHANGE_TOP = ROOT / "reports" / "figures" / "population_change_top10.png"
PLOT_POP_CHANGE_BOTTOM = ROOT / "reports" / "figures" / "population_change_bottom10.png"
PLOT_GDP_LIFE = ROOT / "reports" / "figures" / "gdp_vs_life_expectancy.png"
PLOT_GDP_PC = ROOT / "reports" / "figures" / "top_gdp_per_capita.png"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"
