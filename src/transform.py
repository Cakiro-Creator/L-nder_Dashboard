# transform.py
# Saeubert Daten und erstellt einfache Features
import pandas as pd
from babel import Locale
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    # Nur valide Zeilen behalten
    df = df.dropna(subset=["country_code", "indicator_code", "year", "value"])
    # Duplikate entfernen
    df = df.drop_duplicates(subset=["country_code", "indicator_code", "year"])
    # Deutsche Laendernamen aus ISO2
    locale = Locale("de")
    def to_de_name(code, fallback):
        return locale.territories.get(code, fallback)

    df["country_name_de"] = df.apply(
        lambda r: to_de_name(str(r["country_code"]), r["country_name"]),
        axis=1,
    )

    return df
def add_features(df: pd.DataFrame) -> pd.DataFrame:
    # Beispiel: berechnet GDP pro Kopf, wenn GDP und Population da sind
    df = df.copy()
    wide = df.pivot_table(
        index=["country_code", "year"],
        columns="indicator_code",
        values="value",
        aggfunc="first",
    )
    if "NY.GDP.MKTP.CD" in wide.columns and "SP.POP.TOTL" in wide.columns:
        wide["GDP_per_capita_calc"] = wide["NY.GDP.MKTP.CD"] / wide["SP.POP.TOTL"]
        gpc = wide[["GDP_per_capita_calc"]].reset_index()
        gpc["indicator_code"] = "GDP.PER.CAP.CALC"
        gpc["indicator_name"] = "GDP per capita (calc)"
        gpc["value"] = gpc["GDP_per_capita_calc"]
        gpc = gpc[["country_code", "year", "indicator_code", "indicator_name", "value"]]
        # Basis-Spalten aus Original behalten
        base = df[[
            "country_code",
            "country_name",
            "country_name_de",
            "region",
            "income_level",
            "indicator_code",
            "indicator_name",
            "year",
            "value",
        ]]
        # Namen/Region/Income fuer die neuen Zeilen aus dem Original ziehen
        meta = df.drop_duplicates("country_code")[
            ["country_code", "country_name", "country_name_de", "region", "income_level"]
        ]
        gpc = gpc.merge(meta, on="country_code", how="left")
        gpc = gpc[[
            "country_code",
            "country_name",
            "country_name_de",
            "region",
            "income_level",
            "indicator_code",
            "indicator_name",
            "year",
            "value",
        ]]
        df = pd.concat([base, gpc], ignore_index=True)
    return df
