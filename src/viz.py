# viz.py
# Erstellt einfache Plots fuer den Report
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def plot_top_population(df, out_path):
    # Letztes Jahr in den Daten
    last_year = int(df["year"].max())
    pop = df[
        (df["indicator_code"] == "SP.POP.TOTL") & (df["year"] == last_year)
    ]
    if pop.empty:
        return False
    top = (
        pop.sort_values("value", ascending=False)
           .head(10)
           .sort_values("value")
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = top["country_name_de"] if "country_name_de" in top else top["country_name"]
    ax.barh(labels, top["value"])
    ax.set_title(f"Top 10 Bevoelkerung ({last_year})")
    ax.set_xlabel("Bevoelkerung in Milliarden")
    ax.set_ylabel("Land")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x/1e9:.1f} Milliarden"))
    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    return True


def _population_change_table(df):
    # Prozentuale Veraenderung ueber den Zeitraum je Land
    pop = df[df["indicator_code"] == "SP.POP.TOTL"].copy()
    if pop.empty:
        return None
    first_year = int(pop["year"].min())
    last_year = int(pop["year"].max())
    first = pop[pop["year"] == first_year][["country_code", "value"]].rename(columns={"value": "v_start"})
    last = pop[pop["year"] == last_year][["country_code", "value"]].rename(columns={"value": "v_end"})
    meta = pop.drop_duplicates("country_code")[["country_code", "country_name", "country_name_de"]]
    merged = meta.merge(first, on="country_code").merge(last, on="country_code")
    merged["rel_change_pct"] = ((merged["v_end"] - merged["v_start"]) / merged["v_start"]) * 100
    merged["rel_change_pct"] = merged["rel_change_pct"].round(2)
    return merged


def plot_population_change_top10(df, out_path):
    # Top 10 Laender mit hoechster relativer Bevoelkerungsveraenderung
    merged = _population_change_table(df)
    if merged is None or merged.empty:
        return False
    top = merged.sort_values("rel_change_pct", ascending=False).head(10).sort_values("rel_change_pct")
    labels = top["country_name_de"] if "country_name_de" in top else top["country_name"]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(labels, top["rel_change_pct"])
    ax.set_title("Top 10: Relativer Bevoelkerungswandel (5 Jahre)")
    ax.set_xlabel("Veraenderung in %")
    ax.set_ylabel("Land")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    return True


def plot_population_change_bottom10(df, out_path):
    # Laender mit der geringsten relativen Bevoelkerungsveraenderung
    merged = _population_change_table(df)
    if merged is None or merged.empty:
        return False
    bottom = merged.sort_values("rel_change_pct", ascending=True).head(10)
    labels = bottom["country_name_de"] if "country_name_de" in bottom else bottom["country_name"]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(labels, bottom["rel_change_pct"])
    ax.set_title("Top 10: Geringster Bevoelkerungswandel (5 Jahre)")
    ax.set_xlabel("Veraenderung in %")
    ax.set_ylabel("Land")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    return True


def plot_top_gdp_per_capita(df, out_path):
    # Top 10 GDP pro Kopf (berechnet) im letzten Jahr
    last_year = int(df["year"].max())
    gpc = df[
        (df["indicator_code"] == "GDP.PER.CAP.CALC") & (df["year"] == last_year)
    ]
    if gpc.empty:
        return False
    top = (
        gpc.sort_values("value", ascending=False)
           .head(10)
           .sort_values("value")
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = top["country_name_de"] if "country_name_de" in top else top["country_name"]
    ax.barh(labels, top["value"])
    ax.set_title(f"Top 10 BIP pro Kopf ({last_year})")
    ax.set_xlabel("BIP pro Kopf (berechnet)")
    ax.set_ylabel("Land")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    return True
