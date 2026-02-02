# Projekt Bank API (World Bank)

Dieses Projekt zeigt eine durchgaengige Datenpipeline mit der World-Bank-API:
API-Abruf, Cleaning, Plausibilitaetschecks, Feature-Bildung, SQL-Normalisierung
und Visualisierung inklusive Streamlit-Dashboard.

## Features
- Live API Abruf (World Bank)
- Cleaning + Checks + einfache Features
- Normalisierte SQL Tabellen (SQLite)
- Mehrere Plots als Report (Bevoelkerung, BIP, BIP pro Kopf)
- Dashboard (Streamlit)

## Bewerbungs-Text (kurz)
Dieses Projekt zeigt einen durchgaengigen Datenprozess: API-Abruf, Datenbereinigung,
Plausibilitaetschecks, Feature-Bildung, SQL-Normalisierung und Visualisierung.
Das Dashboard ermoeglicht interaktive Filter, Vergleich von Laendern und
eine schnelle Explorations-Analyse.

## Schnellstart
```bash
pip install -r requirements.txt
python run_all.py
streamlit run app.py
```

## Datenfluss
- API -> `data/raw/worldbank_raw.csv`
- Cleaning -> `data/processed/worldbank_clean.csv`
- SQLite -> `data/processed/worldbank.db`
- Plots -> `reports/figures/`
- Dashboard -> `app.py`

## Zeitraum
- Standardmaessig `START_YEAR = 2000` bis `END_YEAR = aktuelles Jahr - 1`

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

## Hinweise
- Rohdaten und abgeleitete Daten sind reproduzierbar und werden per `.gitignore` ausgeschlossen.
- Keine sensiblen Daten enthalten (nur oeffentliche API).

## Lizenz
Siehe `LICENSE`.
