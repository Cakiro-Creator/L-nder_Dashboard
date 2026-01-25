# app.py
# Einfaches Streamlit-Dashboard fuer die World Bank Daten
from pathlib import Path
import pandas as pd
import altair as alt
import streamlit as st
import colorsys
from src.run_pipeline import main as run_pipeline


st.set_page_config(page_title="World-Bank-Dashboard", layout="wide")

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "processed" / "worldbank_clean.csv"

st.title("World-Bank-Dashboard")
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
indicators = indicators[indicators["indicator_code"] != "SP.DYN.LE00.IN"]
indicator_de = {
    "SP.POP.TOTL": "Bevoelkerung",
    "NY.GDP.MKTP.CD": "BIP (aktuelle US$)",
    "GDP.PER.CAP.CALC": "BIP pro Kopf (berechnet)",
    "SL.UEM.TOTL.ZS": "Arbeitslosenquote (%)",
}
indicators["indicator_name_de"] = indicators["indicator_code"].map(indicator_de).fillna(indicators["indicator_name"])
indicator_names = indicators["indicator_name_de"].tolist()
default_indicator = "Bevoelkerung" if "Bevoelkerung" in indicator_names else indicator_names[0]
indicator_choice = st.sidebar.selectbox("Indikator", indicator_names, index=indicator_names.index(default_indicator))

ind_code = indicators[indicators["indicator_name_de"] == indicator_choice]["indicator_code"].iloc[0]

# Filter: Jahre
min_year = int(df["year"].min())
max_year = int(df["year"].max())
year_range = st.sidebar.slider("Zeitraum", min_year, max_year, (min_year, max_year))

# Filter: Region / Einkommen
region_de = {
    "East Asia & Pacific": "Ostasien & Pazifik",
    "Europe & Central Asia": "Europa & Zentralasien",
    "Latin America & Caribbean": "Lateinamerika & Karibik",
    "Middle East, North Africa, Afghanistan & Pakistan": "Nahost, Nordafrika, Afghanistan & Pakistan",
    "North America": "Nordamerika",
    "South Asia": "Suedasien",
    "Sub-Saharan Africa": "Subsahara-Afrika",
}
income_de = {
    "High income": "Hohes Einkommen",
    "Upper middle income": "Oberes mittleres Einkommen",
    "Lower middle income": "Unteres mittleres Einkommen",
    "Low income": "Niedriges Einkommen",
    "Not classified": "Nicht klassifiziert",
}
df["region_de"] = df["region"].map(region_de).fillna(df["region"])
df["income_level_de"] = df["income_level"].map(income_de).fillna(df["income_level"])
regions = sorted(df["region_de"].dropna().unique().tolist())
incomes = sorted(df["income_level_de"].dropna().unique().tolist())
region_choice = st.sidebar.multiselect("Region", regions, default=regions)
income_choice = st.sidebar.multiselect("Einkommensgruppe", incomes, default=incomes)

# Filter: Laender
last_year = int(df["year"].max())
latest_all = df[(df["indicator_code"] == ind_code) & (df["year"] == last_year)]
top10_countries = (
    latest_all.sort_values("value", ascending=False)
    .head(10)["country_code"]
    .tolist()
)
country_labels = (
    df[["country_code", "country_name_de"]]
    .drop_duplicates()
    .set_index("country_code")["country_name_de"]
)
country_options = country_labels.index.tolist()
country_choice = st.sidebar.multiselect(
    "Laender (Auswahl)",
    country_options,
    default=[],
    format_func=lambda c: country_labels.get(c, c),
)

# Anwenden der Filter
filtered = df[
    (df["indicator_code"] == ind_code)
    & (df["year"].between(year_range[0], year_range[1]))
    & (df["region_de"].isin(region_choice))
    & (df["income_level_de"].isin(income_choice))
]

if country_choice:
    filtered = filtered[filtered["country_code"].isin(country_choice)]

# Standard-Ansicht (ohne Laender-Filter) fuer saubere Top/Unterste-Listen
base_filtered = df[
    (df["indicator_code"] == ind_code)
    & (df["year"].between(year_range[0], year_range[1]))
    & (df["region_de"].isin(region_choice))
    & (df["income_level_de"].isin(income_choice))
]

if filtered.empty:
    st.warning("Keine Daten fuer die aktuelle Filterauswahl. Bitte Filter anpassen.")
    st.stop()

# Ranking-Quelle: immer aus den uebrigen Regionen/Einkommensgruppen, ohne Laender-Filter
rank_base = base_filtered

st.sidebar.header("Darstellung")
scale_choice = st.sidebar.selectbox("Skalierung", ["Linear", "Logarithmisch"])

unit_label = "Wert"
scale_factor = 1.0
if ind_code == "SP.POP.TOTL":
    unit_label = "Millionen"
    scale_factor = 1e6
elif ind_code == "NY.GDP.MKTP.CD":
    unit_label = "Milliarden US$"
    scale_factor = 1e9
elif ind_code == "GDP.PER.CAP.CALC":
    unit_label = "Tsd. US$"
    scale_factor = 1e3
elif ind_code == "SL.UEM.TOTL.ZS":
    unit_label = "%"
    scale_factor = 1.0

latest_filtered = filtered[filtered["year"] == last_year].copy()
latest_all_for_rank = rank_base[rank_base["year"] == last_year].copy()
latest_filtered["value_scaled"] = (latest_filtered["value"] / scale_factor).round(2)
latest_all_for_rank["value_scaled"] = (latest_all_for_rank["value"] / scale_factor).round(2)
use_log = scale_choice == "Logarithmisch"
if use_log and (filtered["value"] <= 0).any():
    st.warning("Logarithmische Skalierung ist nicht moeglich, weil Werte <= 0 vorhanden sind.")
    use_log = False

st.subheader("Uebersicht")
col1, col2, col3 = st.columns(3)
label = "Laender und Territorien"
country_count_base = df[
    (df["region_de"].isin(region_choice))
    & (df["income_level_de"].isin(income_choice))
]["country_code"].nunique()
if country_choice:
    country_count_base = filtered["country_code"].nunique()
col1.metric(label, country_count_base)
col2.metric("Indikatoren", df["indicator_code"].nunique())
col3.metric("Jahre", df["year"].nunique())

# Farbskala fuer Laender (global)
country_domain = df["country_name_de"].dropna().unique().tolist()
color_range = []
if country_domain:
    # Eindeutige Farben pro Land (Hash + Golden-Angle)
    for name in country_domain:
        h = (hash(name) % 360) / 360.0
        h = (h + 0.61803398875) % 1.0
        s = 0.65 if (hash(name) % 2 == 0) else 0.8
        v = 0.55 if (hash(name) % 3 == 0) else 0.7
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        color_range.append(f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}")
color_scale = alt.Scale(domain=country_domain, range=color_range) if country_domain else alt.Scale()



# Chart 2: Top 10 im letzten Jahr
top_count = min(10, len(latest_all_for_rank))
st.subheader(f"Top {top_count} im letzten Jahr")
top10 = latest_all_for_rank.sort_values("value", ascending=False).head(top_count)
bar = (
    alt.Chart(top10)
    .mark_bar()
    .encode(
        x=alt.X("value_scaled:Q", title=f"{indicator_choice} ({unit_label})", scale=alt.Scale(type="log" if use_log else "linear")),
        y=alt.Y("country_name_de:N", sort="-x", title="Land"),
        color=alt.Color("country_name_de:N", legend=None, scale=color_scale),
        tooltip=[alt.Tooltip("country_name_de:N", title="Land"), alt.Tooltip("value_scaled:Q", title="Wert")],
    )
    .properties(height=380)
)
st.altair_chart(bar, use_container_width=True)

# Chart 2b: Top/Unterste 10 fuer den gewaehlten Indikator
st.subheader(f"Top/Unterste {top_count} (aktuelles Jahr)")
top_current = latest_all_for_rank.sort_values("value", ascending=False).head(top_count)
bottom_current = latest_all_for_rank.sort_values("value", ascending=True).head(top_count)
cc1, cc2 = st.columns(2)
with cc1:
    st.caption("Top 10")
    tbar = (
        alt.Chart(top_current)
        .mark_bar()
        .encode(
            x=alt.X("value_scaled:Q", title=f"{indicator_choice} ({unit_label})", scale=alt.Scale(type="log" if use_log else "linear")),
            y=alt.Y("country_name_de:N", sort="-x", title="Land"),
            color=alt.Color("country_name_de:N", legend=None, scale=color_scale),
            tooltip=[alt.Tooltip("country_name_de:N", title="Land"), alt.Tooltip("value_scaled:Q", title="Wert")],
        )
        .properties(height=300)
    )
    st.altair_chart(tbar, use_container_width=True)
with cc2:
    st.caption("Unterste 10")
    bbar = (
        alt.Chart(bottom_current)
        .mark_bar()
        .encode(
            x=alt.X("value_scaled:Q", title=f"{indicator_choice} ({unit_label})", scale=alt.Scale(type="log" if use_log else "linear")),
            y=alt.Y("country_name_de:N", sort="x", title="Land"),
            color=alt.Color("country_name_de:N", legend=None, scale=color_scale),
            tooltip=[alt.Tooltip("country_name_de:N", title="Land"), alt.Tooltip("value_scaled:Q", title="Wert")],
        )
        .properties(height=300)
    )
    st.altair_chart(bbar, use_container_width=True)

# Chart 2c: Jahres-Delta Heatmap (Land x Jahr)
st.subheader("Jahresveraenderung (Heatmap)")
heat_base = base_filtered.copy()
if country_choice:
    heat_base = filtered.copy()

if heat_base.empty:
    st.info("Keine Daten fuer die Heatmap vorhanden.")
else:
    heat_base = heat_base.sort_values(["country_code", "year"])
    heat_base["prev_value"] = heat_base.groupby("country_code")["value"].shift(1)
    heat_base["delta_pct"] = ((heat_base["value"] - heat_base["prev_value"]) / heat_base["prev_value"]) * 100
    heat_base = heat_base.dropna(subset=["delta_pct"])
    # Top 10 Laender nach letzter Veraenderung
    last_y = int(heat_base["year"].max())
    last_slice = heat_base[heat_base["year"] == last_y].copy()
    top_codes = (
        last_slice.sort_values("delta_pct", ascending=False)
        .head(10)["country_code"]
        .tolist()
    )
    heat_top = heat_base[heat_base["country_code"].isin(top_codes)].copy()

    if heat_top.empty:
        st.info("Keine Daten fuer die Heatmap vorhanden.")
    else:
        heat_chart = (
            alt.Chart(heat_top)
            .mark_rect()
            .encode(
                x=alt.X("year:O", title="Jahr"),
                y=alt.Y("country_name_de:N", title="Land"),
                color=alt.Color(
                    "delta_pct:Q",
                    title="Veraenderung zum Vorjahr (%)",
                    scale=alt.Scale(scheme="redblue"),
                ),
                tooltip=[
                    alt.Tooltip("country_name_de:N", title="Land"),
                    alt.Tooltip("year:O", title="Jahr"),
                    alt.Tooltip("delta_pct:Q", title="Veraenderung (%)", format=".2f"),
                ],
            )
            .properties(height=320)
        )
        st.altair_chart(heat_chart, use_container_width=True)

# Chart 2d: Start vs Ende (Dumbbell)
st.subheader("Start vs Ende im Zeitraum (Dumbbell)")
dumb_base = base_filtered.copy()
if country_choice:
    dumb_base = filtered.copy()

if dumb_base.empty:
    st.info("Keine Daten fuer den Vergleich vorhanden.")
else:
    start_y = int(dumb_base["year"].min())
    end_y = int(dumb_base["year"].max())
    start_vals = dumb_base[dumb_base["year"] == start_y][["country_code", "country_name_de", "value"]].rename(columns={"value": "v_start"})
    end_vals = dumb_base[dumb_base["year"] == end_y][["country_code", "country_name_de", "value"]].rename(columns={"value": "v_end"})
    dumb = start_vals.merge(end_vals, on=["country_code", "country_name_de"])
    dumb["delta"] = dumb["v_end"] - dumb["v_start"]
    dumb = dumb.sort_values("delta", ascending=False).head(10)
    dumb["v_start_scaled"] = (dumb["v_start"] / scale_factor).round(2)
    dumb["v_end_scaled"] = (dumb["v_end"] / scale_factor).round(2)

    if dumb.empty:
        st.info("Keine Daten fuer den Vergleich vorhanden.")
    else:
        base_chart = alt.Chart(dumb).encode(
            y=alt.Y("country_name_de:N", sort="-x", title="Land")
        )

        line = base_chart.mark_rule(color="#9CA3AF").encode(
            x=alt.X("v_start_scaled:Q", title=f"{indicator_choice} ({unit_label})"),
            x2="v_end_scaled:Q",
        )
        dots_start = base_chart.mark_point(filled=True, size=60).encode(
            x="v_start_scaled:Q",
            color=alt.value("#1f77b4"),
            tooltip=[
                alt.Tooltip("country_name_de:N", title="Land"),
                alt.Tooltip("v_start_scaled:Q", title=f"Start {start_y}", format=".2f"),
            ],
        )
        dots_end = base_chart.mark_point(filled=True, size=60).encode(
            x="v_end_scaled:Q",
            color=alt.value("#ef4444"),
            tooltip=[
                alt.Tooltip("country_name_de:N", title="Land"),
                alt.Tooltip("v_end_scaled:Q", title=f"Ende {end_y}", format=".2f"),
            ],
        )

        dumbbell = (line + dots_start + dots_end).properties(height=320)
        st.altair_chart(dumbbell, use_container_width=True)

# Chart 3: Relative Bevoelkerungsaenderung (Top/Unterste 10)
if ind_code == "SP.POP.TOTL":
    st.subheader("Bevoelkerungsveraenderung (relativ, 5 Jahre)")
    pop = df[df["indicator_code"] == "SP.POP.TOTL"].copy()
    first_year = int(pop["year"].min())
    last_year = int(pop["year"].max())
    first = pop[pop["year"] == first_year][["country_code", "value"]].rename(columns={"value": "v_start"})
    last = pop[pop["year"] == last_year][["country_code", "value"]].rename(columns={"value": "v_end"})
    meta = pop.drop_duplicates("country_code")[["country_code", "country_name_de"]]
    change = meta.merge(first, on="country_code").merge(last, on="country_code")
    change["rel_change_pct"] = ((change["v_end"] - change["v_start"]) / change["v_start"]) * 100
    change["rel_change_pct"] = pd.to_numeric(change["rel_change_pct"], errors="coerce").round(2)
    change = change.dropna(subset=["rel_change_pct"])

    top_change = change.sort_values("rel_change_pct", ascending=False).head(10)
    low_change = change.sort_values("rel_change_pct", ascending=True).head(10)

    c1, c2 = st.columns(2)
    with c1:
        st.caption("Top 10 Wachstum")
        chart_top = (
            alt.Chart(top_change)
            .mark_bar()
            .encode(
                x=alt.X("rel_change_pct:Q", title="Veraenderung in %", scale=alt.Scale(domain=[0, float(top_change["rel_change_pct"].max())])),
                y=alt.Y("country_name_de:N", sort="-x", title="Land"),
                color=alt.Color("country_name_de:N", legend=None, scale=color_scale),
                tooltip=[alt.Tooltip("country_name_de:N", title="Land"), alt.Tooltip("rel_change_pct:Q", title="Veraenderung in %")],
            )
            .properties(height=320)
        )
        st.altair_chart(chart_top, use_container_width=True)
    with c2:
        st.caption("Top 10 Abnahme")
        chart_low = (
            alt.Chart(low_change)
            .mark_bar()
            .encode(
                x=alt.X("rel_change_pct:Q", title="Veraenderung in %", scale=alt.Scale(domain=[float(low_change["rel_change_pct"].min()), 0])),
                y=alt.Y("country_name_de:N", sort="x", title="Land"),
                color=alt.Color("country_name_de:N", legend=None, scale=color_scale),
                tooltip=[alt.Tooltip("country_name_de:N", title="Land"), alt.Tooltip("rel_change_pct:Q", title="Veraenderung in %")],
            )
            .properties(height=320)
        )
        st.altair_chart(chart_low, use_container_width=True)


st.subheader("Regionen-Anteil am Weltwert (aktuelles Jahr)")
region_sum = (
    latest_filtered.groupby("region_de", as_index=False)["value_scaled"].sum()
)
region_all = pd.DataFrame({"region_de": region_choice})
region_sum = region_all.merge(region_sum, on="region_de", how="left")
total = float(region_sum["value_scaled"].sum(skipna=True))
if total > 0:
    region_sum["anteil_pct"] = (region_sum["value_scaled"] / total) * 100
    region_sum["anzeige"] = region_sum["anteil_pct"].map(
        lambda v: f"{v:.2f}%" if pd.notna(v) else "Keine Daten verfuegbar"
    )
    region_sum["wert_bar"] = region_sum["anteil_pct"].fillna(0)
    region_sum["hat_daten"] = region_sum["anteil_pct"].notna()

    # Regionenfarbe = Land mit hoechster Bevoelkerung (letztes Jahr)
    pop_latest = df[(df["indicator_code"] == "SP.POP.TOTL") & (df["year"] == last_year)].copy()
    pop_latest = pop_latest.dropna(subset=["region_de", "country_name_de", "value"])
    idx = pop_latest.groupby("region_de")["value"].idxmax()
    pop_top = pop_latest.loc[idx, ["region_de", "country_name_de"]]
    pop_top = pop_top.set_index("region_de")["country_name_de"].to_dict()

    def get_color(name):
        if name in country_domain:
            i = country_domain.index(name)
            return color_range[i] if i < len(color_range) else "#666666"
        return "#666666"

    region_sum["color_hex"] = region_sum["region_de"].map(pop_top).map(get_color)
    region_sum["color_hex"] = region_sum["color_hex"].fillna("#c7c7c7")

    region_sum = region_sum.sort_values("wert_bar", ascending=False)
    color_domain_region = region_sum["color_hex"].dropna().unique().tolist()
    color_scale_region = alt.Scale(domain=color_domain_region, range=color_domain_region)

    reg_bar = (
        alt.Chart(region_sum)
        .mark_bar()
        .encode(
            x=alt.X("wert_bar:Q", title="Anteil am Weltwert (%)"),
            y=alt.Y("region_de:N", sort="-x", title="Region"),
            color=alt.Color("color_hex:N", legend=None, scale=color_scale_region),
            tooltip=["region_de", alt.Tooltip("anzeige:N", title="Anteil")],
        )
        .properties(height=320)
    )
    st.altair_chart(reg_bar, use_container_width=True)
else:
    st.info("Keine Daten fuer den Regionen-Vergleich vorhanden.")

st.subheader("Daten-Tabelle")
table_df = filtered.assign(
    indicator_name_de=filtered["indicator_code"].map(indicator_de).fillna(filtered["indicator_name"]),
    wert=(filtered["value"] / scale_factor).round(2),
    einheit=unit_label,
)
table_df = table_df.rename(columns={"indicator_name_de": "Indikator"})
table_df = table_df[["country_name_de", "Indikator", "year", "wert", "einheit", "region_de", "income_level_de"]]
table_df = table_df.rename(columns={
    "country_name_de": "Land",
    "year": "Jahr",
    "wert": "Wert",
    "einheit": "Einheit",
    "region_de": "Region",
    "income_level_de": "Einkommensgruppe",
})
table_df = table_df.sort_values(["Jahr", "Land"]).reset_index(drop=True)
table_df.index = table_df.index + 1
table_df.index.name = "Nr"
st.dataframe(table_df, use_container_width=True)

st.caption(f"Wert = {indicator_choice} in {unit_label}.")

st.download_button(
    "Gefilterte Daten als CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="worldbank_filtered.csv",
    mime="text/csv",
)

st.caption("Quelle: World Bank API (https://api.worldbank.org/v2)")
