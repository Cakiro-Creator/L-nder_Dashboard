# load_sqlite.py
# Schreibt normalisierte Tabellen in SQLite
import sqlite3
import pandas as pd
from src.config import SQLITE_DB, SCHEMA_PATH
def load_to_sqlite(df: pd.DataFrame):
    # Alte DB loeschen, damit der Lauf reproduzierbar ist
    if SQLITE_DB.exists():
        SQLITE_DB.unlink()
    conn = sqlite3.connect(SQLITE_DB)
    cur = conn.cursor()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        cur.executescript(f.read())
    countries = (
        df[["country_code", "country_name_de", "region", "income_level"]]
        .drop_duplicates()
        .rename(columns={
            "country_code": "iso2",
            "country_name_de": "name",
        })
    )
    indicators = (
        df[["indicator_code", "indicator_name"]]
        .drop_duplicates()
        .rename(columns={
            "indicator_code": "code",
            "indicator_name": "name",
        })
    )
    countries.to_sql("countries", conn, if_exists="append", index=False)
    indicators.to_sql("indicators", conn, if_exists="append", index=False)
    country_ids = pd.read_sql_query("SELECT id, iso2 FROM countries", conn)
    indicator_ids = pd.read_sql_query("SELECT id, code FROM indicators", conn)
    facts = df.merge(country_ids, left_on="country_code", right_on="iso2")
    facts = facts.merge(indicator_ids, left_on="indicator_code", right_on="code")
    facts = facts[["id_x", "id_y", "year", "value"]]
    facts.columns = ["country_id", "indicator_id", "year", "value"]
    facts.to_sql("facts", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()
