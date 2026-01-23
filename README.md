# Projekt Bank API (World Bank)

Kurz und simpel:
- Live API Abruf (World Bank)
- Cleaning + Checks + kleine Features
- Normalisierte SQL Tabellen (SQLite)
- Mehrere Plots als Report
- Dashboard (Streamlit)

## Bewerbungs-Text (kurz)
Dieses Projekt zeigt einen durchgaengigen Datenprozess: API-Abruf, Datenbereinigung,
Plausibilitaetschecks, Feature-Bildung, SQL-Normalisierung und Visualisierung.
Das Dashboard ermoeglicht interaktive Filter, Vergleich von Laendern und
eine schnelle Explorations-Analyse.

## Schnellstart
1) Pakete installieren
   - `pip install -r requirements.txt`
2) Alles in einem Schritt
   - `python run_all.py`
3) Dashboard lokal starten
   - `streamlit run app.py`

## Datenfluss
- API -> `data/raw/worldbank_raw.csv`
- Cleaning -> `data/processed/worldbank_clean.csv`
- SQLite -> `data/processed/worldbank.db`
- Plots -> `reports/figures/`
- Dashboard -> `app.py`

## Online Deployment (Streamlit Cloud)
1) Projekt nach GitHub pushen
2) Auf https://streamlit.io/cloud einloggen
3) "New app" -> Repo waehlen -> `app.py` auswaehlen
4) Deploy klicken und den Link teilen

## Struktur
- `src/`        Pipeline Code
- `sql/`        SQL Schema
- `data/`       raw, processed, sample
- `reports/`    Plots
