# fetch_api.py
# Laedt Daten live von der World Bank API
import time
import requests
import pandas as pd
from src.config import BASE_URL, START_YEAR, END_YEAR, INDICATORS, SLEEP_SEC
def _get_json(url, params=None):
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()
def _fetch_paged(endpoint, params=None):
    params = params or {}
    params["format"] = "json"
    params["per_page"] = 20000
    url = f"{BASE_URL}{endpoint}"
    data = _get_json(url, params=params)
    if not isinstance(data, list) or len(data) < 2:
        return []
    meta, records = data[0], data[1]
    pages = int(meta.get("pages", 1))
    all_records = records or []
    for page in range(2, pages + 1):
        params["page"] = page
        data = _get_json(url, params=params)
        records = data[1] if isinstance(data, list) and len(data) > 1 else []
        all_records.extend(records or [])
        time.sleep(SLEEP_SEC)
    return all_records
def get_countries():
    # Holt Laenderliste und filtert Aggregates heraus
    records = _fetch_paged("/country")
    countries = {}
    for c in records:
        region = c.get("region", {}).get("value", "")
        if region == "Aggregates":
            continue
        iso2 = c.get("iso2Code")
        if not iso2:
            continue
        countries[iso2] = {
            "iso2": iso2,
            "iso3": c.get("id"),
            "name": c.get("name"),
            "region": region,
            "income_level": c.get("incomeLevel", {}).get("value", ""),
        }
    return countries
def _normalize_record(r, countries):
    country = r.get("country", {})
    iso2 = country.get("id")
    if iso2 not in countries:
        return None
    return {
        "country_code": iso2,
        "country_name": country.get("value"),
        "region": countries[iso2]["region"],
        "income_level": countries[iso2]["income_level"],
        "indicator_code": r.get("indicator", {}).get("id"),
        "indicator_name": r.get("indicator", {}).get("value"),
        "year": r.get("date"),
        "value": r.get("value"),
    }
def fetch_indicator_data_all(countries):
    # Holt Daten fuer alle Laender und alle Indikatoren
    rows = []
    for ind_code in INDICATORS.keys():
        endpoint = f"/country/all/indicator/{ind_code}"
        params = {"date": f"{START_YEAR}:{END_YEAR}"}
        records = _fetch_paged(endpoint, params=params)
        for r in records:
            rec = _normalize_record(r, countries)
            if rec:
                rows.append(rec)
        time.sleep(SLEEP_SEC)
    return pd.DataFrame(rows)
