from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import yfinance as yf


COUNTRY_CONFIG = {
    "Argentina": {"iso3": "ARG", "bis": "AR", "ticker": "ARGT", "region": "Latin America"},
    "Australia": {"iso3": "AUS", "bis": "AU", "ticker": "EWA", "region": "Oceania"},
    "Austria": {"iso3": "AUT", "bis": "AT", "ticker": "EWO", "region": "Europe"},
    "Belgium": {"iso3": "BEL", "bis": "BE", "ticker": "EWK", "region": "Europe"},
    "Brazil": {"iso3": "BRA", "bis": "BR", "ticker": "EWZ", "region": "Latin America"},
    "Canada": {"iso3": "CAN", "bis": "CA", "ticker": "EWC", "region": "North America"},
    "Chile": {"iso3": "CHL", "bis": "CL", "ticker": "ECH", "region": "Latin America"},
    "China": {"iso3": "CHN", "bis": "CN", "ticker": "MCHI", "region": "East Asia"},
    "Colombia": {"iso3": "COL", "bis": "CO", "ticker": "GXG", "region": "Latin America"},
    "Denmark": {"iso3": "DNK", "bis": "DK", "ticker": "EDEN", "region": "Europe"},
    "Finland": {"iso3": "FIN", "bis": "FI", "ticker": "EFNL", "region": "Europe"},
    "France": {"iso3": "FRA", "bis": "FR", "ticker": "EWQ", "region": "Europe"},
    "Germany": {"iso3": "DEU", "bis": "DE", "ticker": "EWG", "region": "Europe"},
    "Greece": {"iso3": "GRC", "bis": "GR", "ticker": "GREK", "region": "Europe"},
    "Hong Kong": {"iso3": "HKG", "bis": "HK", "ticker": "EWH", "region": "East Asia"},
    "India": {"iso3": "IND", "bis": "IN", "ticker": "INDA", "region": "South East Asia"},
    "Indonesia": {"iso3": "IDN", "bis": "ID", "ticker": "EIDO", "region": "South East Asia"},
    "Ireland": {"iso3": "IRL", "bis": "IE", "ticker": "EIRL", "region": "Europe"},
    "Israel": {"iso3": "ISR", "bis": "IL", "ticker": "EIS", "region": "Middle East"},
    "Italy": {"iso3": "ITA", "bis": "IT", "ticker": "EWI", "region": "Europe"},
    "Japan": {"iso3": "JPN", "bis": "JP", "ticker": "EWJ", "region": "East Asia"},
    "Malaysia": {"iso3": "MYS", "bis": "MY", "ticker": "EWM", "region": "South East Asia"},
    "Mexico": {"iso3": "MEX", "bis": "MX", "ticker": "EWW", "region": "Latin America"},
    "Netherlands": {"iso3": "NLD", "bis": "NL", "ticker": "EWN", "region": "Europe"},
    "Norway": {"iso3": "NOR", "bis": "NO", "ticker": "ENOR", "region": "Europe"},
    "Philippines": {"iso3": "PHL", "bis": "PH", "ticker": "EPHE", "region": "South East Asia"},
    "Poland": {"iso3": "POL", "bis": "PL", "ticker": "EPOL", "region": "Europe"},
    "Singapore": {"iso3": "SGP", "bis": "SG", "ticker": "EWS", "region": "South East Asia"},
    "South Africa": {"iso3": "ZAF", "bis": "ZA", "ticker": "EZA", "region": "Africa"},
    "South Korea": {"iso3": "KOR", "bis": "KR", "ticker": "EWY", "region": "East Asia"},
    "Spain": {"iso3": "ESP", "bis": "ES", "ticker": "EWP", "region": "Europe"},
    "Sweden": {"iso3": "SWE", "bis": "SE", "ticker": "EWD", "region": "Europe"},
    "Switzerland": {"iso3": "CHE", "bis": "CH", "ticker": "EWL", "region": "Europe"},
    "Taiwan": {"iso3": "TWN", "bis": "TW", "ticker": "EWT", "region": "East Asia"},
    "Thailand": {"iso3": "THA", "bis": "TH", "ticker": "THD", "region": "South East Asia"},
    "Turkey": {"iso3": "TUR", "bis": "TR", "ticker": "TUR", "region": "Europe"},
    "United Kingdom": {"iso3": "GBR", "bis": "GB", "ticker": "EWU", "region": "Europe"},
    "United States": {"iso3": "USA", "bis": "US", "ticker": "IVV", "region": "North America"},
}


DEFAULT_WEIGHTS = {
    "macro": 0.20,
    "currency": 0.20,
    "valuation": 0.20,
    "narrative": 0.30,
    "mcap": 0.10,
}


def fetch_imf_gdp() -> pd.DataFrame:
    iso_list = [v["iso3"] for v in COUNTRY_CONFIG.values()]
    end_year = 2025
    start_year = end_year - 10
    url = (
        "https://api.imf.org/external/sdmx/2.1/data/WEO/"
        f"{'+'.join(iso_list)}.NGDPD.A?startPeriod={start_year}&endPeriod={end_year}"
    )
    response = requests.get(url, headers={"Accept": "application/json"}, timeout=60)
    response.raise_for_status()
    data = response.json()
    structure = data.get("structure", {})
    country_map = {
        i: v["id"]
        for i, v in enumerate(structure.get("dimensions", {}).get("series", [])[0].get("values", []))
    }
    time_map = {
        i: v["id"]
        for i, v in enumerate(structure.get("dimensions", {}).get("observation", [])[0].get("values", []))
    }
    iso_to_name = {v["iso3"]: k for k, v in COUNTRY_CONFIG.items()}
    results = []
    for key, s_val in data.get("dataSets", [{}])[0].get("series", {}).items():
        iso = country_map.get(int(key.split(":")[0]))
        name = iso_to_name.get(iso)
        if not name:
            continue
        row = {"Country": name}
        vals = {}
        for t_idx, v_list in s_val.get("observations", {}).items():
            yr = int(time_map.get(int(t_idx)))
            val = float(v_list[0])
            row[f"GDP_{yr}"] = val / 1e9
            vals[yr] = val
        for n in [1, 3, 5, 10]:
            v_end, v_start = vals.get(2025), vals.get(2025 - n)
            row[f"GDP_CAGR_{n}Y"] = (v_end / v_start) ** (1 / n) - 1 if v_end and v_start and v_start > 0 else np.nan
        results.append(row)
    return pd.DataFrame(results)


def fetch_etf(terminal_date: str) -> pd.DataFrame:
    term_dt = pd.to_datetime(terminal_date)
    start_date = term_dt - pd.DateOffset(years=11)
    ytd_start = datetime(term_dt.year, 1, 1)
    results = []
    for name, meta in COUNTRY_CONFIG.items():
        try:
            df = yf.download(meta["ticker"], start=start_date.strftime("%Y-%m-%d"), progress=False, auto_adjust=True)
            if df.empty:
                continue
            close = df["Close"][meta["ticker"]] if isinstance(df.columns, pd.MultiIndex) else df["Close"]
            valid = close[close.index <= term_dt].dropna()
            if valid.empty or len(valid) <= 20:
                continue
            p_now = float(valid.iloc[-1])
            row = {"Country": name, "ETF_Ticker": meta["ticker"], "P_Now": p_now}
            for n in [1, 3, 5, 10]:
                target_dt = valid.index[-1] - pd.DateOffset(years=n)
                idx = valid.index.get_indexer([target_dt], method="nearest")[0]
                p_start = float(valid.iloc[idx])
                row[f"P_{n}Y"] = p_start
                row[f"ETF_CAGR_{n}Y"] = (p_now / p_start) ** (1 / n) - 1 if p_start > 0 else np.nan
            ytd_data = close[close.index >= ytd_start].dropna()
            row["YTD_Return"] = (float(ytd_data.iloc[-1]) / float(ytd_data.iloc[0])) - 1 if not ytd_data.empty else np.nan
            results.append(row)
        except Exception as exc:
            print(f"ETF fetch failed for {name}: {exc}")
    return pd.DataFrame(results)


def fetch_bis_reer() -> pd.DataFrame:
    url = "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_EER/1.0/M.R.B?format=csv"
    df = pd.read_csv(url)
    bis_codes = {v["bis"]: k for k, v in COUNTRY_CONFIG.items()}
    df = df[df["REF_AREA"].isin(bis_codes.keys())].copy()
    df["date"] = pd.to_datetime(df["TIME_PERIOD"])
    results = []
    for code, group in df.groupby("REF_AREA"):
        group = group.sort_values("date")
        current_reer = group.iloc[-1]["OBS_VALUE"]
        avg_10y = group[group["date"] >= (group["date"].max() - pd.DateOffset(years=10))]["OBS_VALUE"].mean()
        results.append(
            {
                "Country": bis_codes[code],
                "Current_REER": current_reer,
                "Avg_REER_10Y": avg_10y,
                "REER_Upside": (avg_10y - current_reer) / avg_10y if avg_10y > 0 else np.nan,
            }
        )
    return pd.DataFrame(results)


def load_oil(static_dir: Path) -> pd.DataFrame:
    df = pd.read_excel(static_dir / "oil_imports_2024.xlsx", sheet_name="2024 imports")
    df.columns = [c.strip() for c in df.columns]
    mappings = {"Korea, Rep.": "South Korea", "Hong Kong, China": "Hong Kong", "Other Asia, nes": "Taiwan"}
    df["Country"] = df["Country"].replace(mappings)
    cols = ["Country", "Crude (kg)", "Crude (mb/d)"]
    df_clean = df[df["Country"].isin(COUNTRY_CONFIG.keys())][cols].copy()
    df_clean["Conversion_Factor"] = 7.33
    return df_clean


def build_master(static_dir: Path, terminal_date: str, oil_scenario: float) -> pd.DataFrame:
    gdp = fetch_imf_gdp()
    etf = fetch_etf(terminal_date)
    reer = fetch_bis_reer()
    oil = load_oil(static_dir)
    mcap = pd.read_csv(static_dir / "mcap_data.csv")
    bond = pd.read_csv(static_dir / "bond_10y_differentials.csv")
    us_bond_yield = bond.loc[bond["Country"] == "United States", "10Y bond yield"].iloc[0]
    bond["differential with USA"] = bond["10Y bond yield"] - us_bond_yield
    val = pd.read_csv(static_dir / "valuation_ranks.csv")
    nar = pd.read_csv(static_dir / "narrative_ranks.csv")

    master = pd.DataFrame(COUNTRY_CONFIG.keys(), columns=["Country"])
    master["Region"] = master["Country"].map(lambda x: COUNTRY_CONFIG[x]["region"])
    for frame in [gdp, etf, reer, oil, mcap, bond, val]:
        master = master.merge(frame, on="Country", how="left")
    master = master.merge(nar, on="Country", how="left")

    if {"Crude (mb/d)", "GDP_2025"}.issubset(master.columns):
        master["Oil_Scenario_USD"] = oil_scenario
        master["Oil_Annual_Impact_USD_Bn"] = (master["Crude (mb/d)"] * 1e6 * oil_scenario * 365) / 1e9
        master["Oil_GDP_Impact_Pct"] = master["Oil_Annual_Impact_USD_Bn"] / master["GDP_2025"]
        master["Oil_Data_Excluded"] = (
            (master["Country"] == "Thailand")
            | (
                (master["Crude (mb/d)"] > 3.0)
                & (~master["Country"].isin(["China", "United States", "India"]))
            )
        )
    return master


def rank_strategy(master: pd.DataFrame, horizon: int, weights: dict[str, float]) -> pd.DataFrame:
    required = [
        f"GDP_CAGR_{horizon}Y",
        f"ETF_CAGR_{horizon}Y",
        "Mcap_USD_Bn",
        "REER_Upside",
        "differential with USA",
        "Average Rank",
        "Rank",
    ]
    calc = master.dropna(subset=required).copy()
    calc["Macro_Gap"] = calc[f"GDP_CAGR_{horizon}Y"] - calc[f"ETF_CAGR_{horizon}Y"]
    calc["Macro_Gap_Rank"] = calc["Macro_Gap"].rank(ascending=False).astype(int)
    calc["REER_Rank"] = calc["REER_Upside"].rank(ascending=False).astype(int)
    calc["Bond_Rank"] = calc["differential with USA"].rank(ascending=False).astype(int)
    calc["Currency_Score"] = (calc["REER_Rank"] + calc["Bond_Rank"]) / 2
    calc["Currency_Rank"] = calc["Currency_Score"].rank().astype(int)
    calc["Valuation_Rank"] = calc["Average Rank"].rank(ascending=True).astype(int)
    calc["Narrative_Rank"] = calc["Rank"].rank(ascending=True).astype(int)
    calc["Mcap_Rank"] = calc["Mcap_USD_Bn"].rank(ascending=False).astype(int)
    calc["Final_Score"] = (
        calc["Macro_Gap_Rank"] * weights["macro"]
        + calc["Currency_Rank"] * weights["currency"]
        + calc["Valuation_Rank"] * weights["valuation"]
        + calc["Narrative_Rank"] * weights["narrative"]
        + calc["Mcap_Rank"] * weights["mcap"]
    )
    calc = calc.sort_values("Final_Score").reset_index(drop=True)
    calc["Final_Rank"] = np.arange(1, len(calc) + 1)
    calc["Ranked"] = True
    return calc


def make_exports(master: pd.DataFrame, ranked: pd.DataFrame, out_dir: Path, horizon: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    strategy_cols = [
        "Final_Rank",
        "Country",
        "Region",
        "ETF_Ticker",
        "Final_Score",
        "Macro_Gap",
        "Macro_Gap_Rank",
        "Currency_Score",
        "Currency_Rank",
        "REER_Rank",
        "Bond_Rank",
        "Valuation_Rank",
        "Narrative_Rank",
        "Mcap_Rank",
        "YTD_Return",
        f"GDP_CAGR_{horizon}Y",
        f"ETF_CAGR_{horizon}Y",
        "REER_Upside",
        "differential with USA",
        "Average Rank",
        "Rank",
        "Mcap_USD_Bn",
    ]
    strategy = ranked[[c for c in strategy_cols if c in ranked.columns]].copy()
    strategy.to_csv(out_dir / "strategy_output.csv", index=False)

    audit = master.copy()
    required = [
        f"GDP_CAGR_{horizon}Y",
        f"ETF_CAGR_{horizon}Y",
        "Mcap_USD_Bn",
        "REER_Upside",
        "differential with USA",
        "Average Rank",
        "Rank",
    ]
    for col in required:
        audit[f"Has_{col}"] = audit[col].notna()
    audit["Ranked"] = audit["Country"].isin(ranked["Country"])
    audit.to_csv(out_dir / "audit_master_data.csv", index=False)

    top10 = strategy.head(10)
    macro = strategy[["Country", "Macro_Gap", "Macro_Gap_Rank", "YTD_Return"]].sort_values("Macro_Gap", ascending=False)
    currency = strategy[["Country", "Currency_Score", "Currency_Rank", "REER_Upside", "differential with USA"]].sort_values("Currency_Rank")
    oil_cols = ["Country", "Region", "Crude (mb/d)", "Oil_Annual_Impact_USD_Bn", "Oil_GDP_Impact_Pct", "Oil_Data_Excluded"]
    oil = audit[[c for c in oil_cols if c in audit.columns]].dropna(subset=["Crude (mb/d)"]).sort_values("Oil_GDP_Impact_Pct", ascending=False)
    coverage = pd.DataFrame(
        {
            "Field": required,
            "Available_Countries": [int(audit[col].notna().sum()) for col in required],
        }
    )
    corr = pd.DataFrame(
        {
            "Metric": ["Final_Rank_vs_YTD_Return", "Final_Score_vs_YTD_Return", "Macro_Gap_vs_YTD_Return"],
            "Correlation": [
                strategy["Final_Rank"].corr(strategy["YTD_Return"]),
                strategy["Final_Score"].corr(strategy["YTD_Return"]),
                strategy["Macro_Gap"].corr(strategy["YTD_Return"]),
            ],
        }
    )
    with pd.ExcelWriter(out_dir / "ppt_chart_data.xlsx") as writer:
        top10.to_excel(writer, sheet_name="top_10_rankings", index=False)
        macro.to_excel(writer, sheet_name="macro_gap", index=False)
        currency.to_excel(writer, sheet_name="currency_score", index=False)
        oil.to_excel(writer, sheet_name="oil_impact", index=False)
        coverage.to_excel(writer, sheet_name="data_coverage", index=False)
        corr.to_excel(writer, sheet_name="rank_ytd_correlation", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export clean PPT handoff data from the current macro ETF model.")
    parser.add_argument("--horizon", type=int, choices=[1, 3, 5, 10], default=10)
    parser.add_argument("--terminal-date", default="2025-12-31")
    parser.add_argument("--oil-scenario", type=float, default=10.0)
    parser.add_argument("--static-dir", type=Path, default=Path("data/static"))
    parser.add_argument("--out-dir", type=Path, default=Path("documents for making PPT"))
    args = parser.parse_args()

    master = build_master(args.static_dir, args.terminal_date, args.oil_scenario)
    ranked = rank_strategy(master, args.horizon, DEFAULT_WEIGHTS)
    make_exports(master, ranked, args.out_dir, args.horizon)
    print(f"Wrote PPT handoff data to {args.out_dir}")
    print(f"Ranked countries: {len(ranked)} / {len(master)}")
    if not ranked.empty:
        print("Top 5:")
        print(ranked[["Final_Rank", "Country", "Final_Score"]].head(5).to_string(index=False))


if __name__ == "__main__":
    main()
