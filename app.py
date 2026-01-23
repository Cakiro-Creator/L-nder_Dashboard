# app.py
# Einfaches Streamlit-Dashboard fuer die World Bank Daten
from pathlib import Path
import pandas as pd
import altair as alt
import streamlit as st
from src.run_pipeline import main as run_pipeline


st.set_page_config(page_title="World Bank Dashboard", layout="wide")

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "processed" / "worldbank_clean.csv"

st.title("World Bank Dashboard")
st.caption("Datenquelle: World Bank API (letzte 5 Jahre)")


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

st.sidebar.header("Aktionen")
if st.sidebar.button("Daten aktualisieren"):
    with st.spinner("Daten werden geladen..."):
        run_pipeline()
    load_data.clear()
    st.success("Aktualisierung abgeschlossen.")

if not DATA_PATH.exists():
    st.error("Es fehlen Daten. Bitte zuerst `python run_all.py` ausfuehren.")
    st.stop()

df = load_data()

# Grund-Checks
df = df.dropna(subset=["country_code", "indicator_code", "year", "value"])
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
df["value"] = pd.to_numeric(df["value"], errors="coerce")

st.sidebar.header("Filter")

# Filter: Indikator
indicators = (
    df[["indicator_code", "indicator_name"]]
    .drop_duplicates()
    .sort_values("indicator_name")
)
indicator_names = indicators["indicator_name"].tolist()
default_indicator = "Population" if "Population" in indicator_names else indicator_names[0]
indicator_choice = st.sidebar.selectbox("Indikator", indicator_names, index=indicator_names.index(default_indicator))

ind_code = indicators[indicators["indicator_name"] == indicator_choice]["indicator_code"].iloc[0]

# Filter: Jahre
min_year = int(df["year"].min())
max_year = int(df["year"].max())
year_range = st.sidebar.slider("Zeitraum", min_year, max_year, (min_year, max_year))

# Filter: Region / Einkommen
regions = sorted(df["region"].dropna().unique().tolist())
incomes = sorted(df["income_level"].dropna().unique().tolist())
region_choice = st.sidebar.multiselect("Region", regions, default=regions)
income_choice = st.sidebar.multiselect("Einkommensgruppe", incomes, default=incomes)

# Filter: Laender
last_year = int(df["year"].max())
latest = df[(df["indicator_code"] == ind_code) & (df["year"] == last_year)]
top10_countries = (
    latest.sort_values("value", ascending=False)
    .head(10)["country_code"]
    .tolist()
)
country_labels = (
    df[["country_code", "country_name_de"]]
    .drop_duplicates()
    .set_index("country_code")["country_name_de"]
)
country_options = country_labels.index.tolist()
default_countries = [c for c in top10_countries if c in country_options]
country_choice = st.sidebar.multiselect(
    "Laender (Auswahl)",
    country_options,
    default=default_countries,
    format_func=lambda c: country_labels.get(c, c),
)

# Anwenden der Filter
filtered = df[
    (df["indicator_code"] == ind_code)
    & (df["year"].between(year_range[0], year_range[1]))
    & (df["region"].isin(region_choice))
    & (df["income_level"].isin(income_choice))
]

if country_choice:
    filtered = filtered[filtered["country_code"].isin(country_choice)]

st.subheader("Uebersicht")
col1, col2, col3 = st.columns(3)
col1.metric("Laender", df["country_code"].nunique())
col2.metric("Indikatoren", df["indicator_code"].nunique())
col3.metric("Jahre", df["year"].nunique())

# Chart 1: Zeitreihe
st.subheader("Zeitreihe")
line = (
    alt.Chart(filtered)
    .mark_line(point=True)
    .encode(
        x=alt.X("year:O", title="Jahr"),
        y=alt.Y("value:Q", title=indicator_choice),
        color=alt.Color("country_name_de:N", title="Land"),
        tooltip=["country_name_de", "year", "value"],
    )
    .properties(height=380)
)
st.altair_chart(line, use_container_width=True)

# Chart 2: Top 10 im letzten Jahr
st.subheader("Top 10 im letzten Jahr")
top10 = (
    latest.sort_values("value", ascending=False)
    .head(10)
)
bar = (
    alt.Chart(top10)
    .mark_bar()
    .encode(
        x=alt.X("value:Q", title=indicator_choice),
        y=alt.Y("country_name_de:N", sort="-x", title="Land"),
        tooltip=["country_name_de", "value"],
    )
    .properties(height=380)
)
st.altair_chart(bar, use_container_width=True)

# Chart 2b: Top/Bottom 10 fuer den gewaehlten Indikator
st.subheader("Top/Bottom 10 (aktuelles Jahr)")
top_current = latest.sort_values("value", ascending=False).head(10)
bottom_current = latest.sort_values("value", ascending=True).head(10)
cc1, cc2 = st.columns(2)
with cc1:
    st.caption("Top 10")
    tbar = (
        alt.Chart(top_current)
        .mark_bar()
        .encode(
            x=alt.X("value:Q", title=indicator_choice),
            y=alt.Y("country_name_de:N", sort="-x", title="Land"),
        )
        .properties(height=300)
    )
    st.altair_chart(tbar, use_container_width=True)
with cc2:
    st.caption("Bottom 10")
    bbar = (
        alt.Chart(bottom_current)
        .mark_bar()
        .encode(
            x=alt.X("value:Q", title=indicator_choice),
            y=alt.Y("country_name_de:N", sort="x", title="Land"),
        )
        .properties(height=300)
    )
    st.altair_chart(bbar, use_container_width=True)

# Chart 3: Relative Bevoelkerungsaenderung (Top/Bottom 10)
st.subheader("Bevoelkerungsveraenderung (relativ, 5 Jahre)")
pop = df[df["indicator_code"] == "SP.POP.TOTL"].copy()
if not pop.empty:
    first_year = int(pop["year"].min())
    last_year = int(pop["year"].max())
    first = pop[pop["year"] == first_year][["country_code", "value"]].rename(columns={"value": "v_start"})
    last = pop[pop["year"] == last_year][["country_code", "value"]].rename(columns={"value": "v_end"})
    meta = pop.drop_duplicates("country_code")[["country_code", "country_name_de"]]
    change = meta.merge(first, on="country_code").merge(last, on="country_code")
    change["rel_change_pct"] = ((change["v_end"] - change["v_start"]) / change["v_start"]) * 100
    change["rel_change_pct"] = change["rel_change_pct"].round(2)

    top_change = change.sort_values("rel_change_pct", ascending=False).head(10)
    low_change = change.sort_values("rel_change_pct", ascending=True).head(10)

    c1, c2 = st.columns(2)
    with c1:
        st.caption("Top 10 Wachstum")
        chart_top = (
            alt.Chart(top_change)
            .mark_bar()
            .encode(
                x=alt.X("rel_change_pct:Q", title="Veraenderung in %"),
                y=alt.Y("country_name_de:N", sort="-x", title="Land"),
            )
            .properties(height=320)
        )
        st.altair_chart(chart_top, use_container_width=True)
    with c2:
        st.caption("Geringste Veraenderung")
        chart_low = (
            alt.Chart(low_change)
            .mark_bar()
            .encode(
                x=alt.X("rel_change_pct:Q", title="Veraenderung in %"),
                y=alt.Y("country_name_de:N", sort="x", title="Land"),
            )
            .properties(height=320)
        )
        st.altair_chart(chart_low, use_container_width=True)

# Chart 4: GDP vs Lebenserwartung
st.subheader("BIP vs Lebenserwartung (letztes Jahr)")
gdp = df[(df["indicator_code"] == "NY.GDP.MKTP.CD") & (df["year"] == last_year)][
    ["country_code", "country_name_de", "value"]
].rename(columns={"value": "gdp"})
life = df[(df["indicator_code"] == "SP.DYN.LE00.IN") & (df["year"] == last_year)][
    ["country_code", "value"]
].rename(columns={"value": "life"})
scatter = gdp.merge(life, on="country_code")
if not scatter.empty:
    sc = (
        alt.Chart(scatter)
        .mark_circle(size=60, opacity=0.6)
        .encode(
            x=alt.X("gdp:Q", scale=alt.Scale(type="log"), title="BIP (log, US$)"),
            y=alt.Y("life:Q", title="Lebenserwartung"),
            tooltip=["country_name_de", "gdp", "life"],
        )
        .properties(height=380)
    )
    st.altair_chart(sc, use_container_width=True)

st.subheader("Verteilung (aktuelles Jahr)")
hist = (
    alt.Chart(latest)
    .mark_bar()
    .encode(
        x=alt.X("value:Q", bin=alt.Bin(maxbins=30), title=indicator_choice),
        y=alt.Y("count()", title="Anzahl Laender"),
    )
    .properties(height=280)
)
st.altair_chart(hist, use_container_width=True)

st.subheader("Daten-Tabelle")
st.dataframe(
    filtered[["country_name_de", "indicator_name", "year", "value", "region", "income_level"]]
    .sort_values(["year", "country_name_de"])
    .reset_index(drop=True),
    use_container_width=True,
)

st.download_button(
    "Gefilterte Daten als CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="worldbank_filtered.csv",
    mime="text/csv",
)
