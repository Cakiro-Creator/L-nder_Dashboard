-- schema.sql
-- Normalisierte Tabellen fuer World Bank Daten
CREATE TABLE IF NOT EXISTS countries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  iso2 TEXT UNIQUE,
  iso3 TEXT,
  name TEXT,
  region TEXT,
  income_level TEXT
);
CREATE TABLE IF NOT EXISTS indicators (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT UNIQUE,
  name TEXT
);
CREATE TABLE IF NOT EXISTS facts (
  country_id INTEGER,
  indicator_id INTEGER,
  year INTEGER,
  value REAL,
  PRIMARY KEY (country_id, indicator_id, year),
  FOREIGN KEY (country_id) REFERENCES countries(id),
  FOREIGN KEY (indicator_id) REFERENCES indicators(id)
);
