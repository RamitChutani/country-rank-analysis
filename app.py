import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import requests
from datetime import datetime

st.set_page_config(page_title="Macro ETF Strategy Dashboard", layout="wide")

st.title("🌍 Global Macro Strategy Dashboard")

# --- 1. SESSION STATE & DEFAULTS ---
DEFAULTS = {
    "w_macro": 0.20,
    "w_curr": 0.20,
    "w_val": 0.20,
    "w_nar": 0.30,
    "w_mcap": 0.10,
    "horizon": 10,
    "oil_scenario": 10.0
}

for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

if "calculate" not in st.session_state:
    st.session_state.calculate = False

# --- 2. CONFIGURATION & MAPPINGS ---
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
    "United States": {"iso3": "USA", "bis": "US", "ticker": "IVV", "region": "North America"}
}

# --- 3. WIDE DATA FETCHERS ---

@st.cache_data
def fetch_imf_gdp_journey():
    iso_list = [v['iso3'] for v in COUNTRY_CONFIG.values()]
    end_year = 2025
    start_year = end_year - 10
    url = f"https://api.imf.org/external/sdmx/2.1/data/WEO/{'+'.join(iso_list)}.NGDPD.A?startPeriod={start_year}&endPeriod={end_year}"
    try:
        response = requests.get(url, headers={"Accept": "application/json"}, timeout=15)
        response.raise_for_status()
        data = response.json()
        structure = data.get('structure', {})
        country_map = {i: v['id'] for i, v in enumerate(structure.get('dimensions', {}).get('series', [])[0].get('values', []))}
        time_map = {i: v['id'] for i, v in enumerate(structure.get('dimensions', {}).get('observation', [])[0].get('values', []))}
        iso_to_name = {v['iso3']: k for k, v in COUNTRY_CONFIG.items()}
        results = []
        series_data = data.get('dataSets', [{}])[0].get('series', {})
        for key, s_val in series_data.items():
            iso = country_map.get(int(key.split(':')[0]))
            name = iso_to_name.get(iso)
            if not name: continue
            obs = s_val.get('observations', {})
            row = {"Country": name}
            vals = {}
            for t_idx, v_list in obs.items():
                yr = int(time_map.get(int(t_idx)))
                val = float(v_list[0])
                row[f"GDP_{yr}"] = val / 1e9
                vals[yr] = val
            for n in [1, 3, 5, 10]:
                v_end, v_start = vals.get(2025), vals.get(2025-n)
                row[f"GDP_CAGR_{n}Y"] = (v_end/v_start)**(1/n) - 1 if v_end and v_start and v_start > 0 else np.nan
            results.append(row)
        return pd.DataFrame(results)
    except: return pd.DataFrame()

@st.cache_data
def fetch_etf_journey(terminal_date):
    term_dt = pd.to_datetime(terminal_date)
    start_date = term_dt - pd.DateOffset(years=11)
    ytd_start = datetime(2026, 1, 1)
    results = []
    progress_bar = st.progress(0, text="Fetching ETF prices...")
    tickers = list(COUNTRY_CONFIG.items())
    for i, (name, meta) in enumerate(tickers):
        try:
            df = yf.download(meta['ticker'], start=start_date.strftime("%Y-%m-%d"), progress=False, auto_adjust=True)
            if not df.empty:
                close = df['Close'][meta['ticker']] if isinstance(df.columns, pd.MultiIndex) else df['Close']
                valid = close[close.index <= term_dt]
                if not valid.empty and len(valid) > 20:
                    p_now = float(valid.iloc[-1])
                    row = {"Country": name, "P_Now": p_now}
                    for n in [1, 3, 5, 10]:
                        target_dt = valid.index[-1] - pd.DateOffset(years=n)
                        idx = valid.index.get_indexer([target_dt], method='nearest')[0]
                        p_start = float(valid.iloc[idx])
                        row[f"P_{n}Y"] = p_start
                        row[f"ETF_CAGR_{n}Y"] = (p_now/p_start)**(1/n) - 1 if p_start > 0 else np.nan
                    ytd_data = close[close.index >= ytd_start]
                    row["YTD_Return"] = (ytd_data.iloc[-1] / ytd_data.iloc[0]) - 1 if not ytd_data.empty else np.nan
                    results.append(row)
        except: continue
        progress_bar.progress((i + 1) / len(tickers))
    progress_bar.empty()
    return pd.DataFrame(results)

@st.cache_data
def fetch_bis_reer_journey():
    url = "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_EER/1.0/M.R.B?format=csv"
    try:
        df = pd.read_csv(url)
        bis_codes = {v['bis']: k for k, v in COUNTRY_CONFIG.items()}
        df = df[df['REF_AREA'].isin(bis_codes.keys())].copy()
        df["date"] = pd.to_datetime(df["TIME_PERIOD"])
        results = []
        for code, group in df.groupby('REF_AREA'):
            group = group.sort_values("date")
            p_now = group.iloc[-1]["OBS_VALUE"]
            avg_10y = group[group["date"] >= (group["date"].max() - pd.DateOffset(years=10))]["OBS_VALUE"].mean()
            results.append({"Country": bis_codes[code], "Current_REER": p_now, "Avg_REER_10Y": avg_10y, "REER_Upside": (avg_10y - p_now) / avg_10y if avg_10y > 0 else np.nan})
        return pd.DataFrame(results)
    except: return pd.DataFrame()

@st.cache_data
def fetch_oil_impact_journey():
    """Fetch crude oil import data and map to COUNTRY_CONFIG."""
    excel_path = 'data/static/oil_imports_2024.xlsx'
    try:
        df = pd.read_excel(excel_path, sheet_name='2024 imports')
        df.columns = [c.strip() for c in df.columns]
        mappings = {"Korea, Rep.": "South Korea", "Hong Kong, China": "Hong Kong", "Other Asia, nes": "Taiwan"}
        df['Country'] = df['Country'].replace(mappings)
        cols = ['Country', 'Crude (kg)', 'Crude (mb/d)']
        df_clean = df[df['Country'].isin(COUNTRY_CONFIG.keys())][cols].copy()
        df_clean['Conversion_Factor'] = 7.33
        return df_clean
    except Exception as e:
        st.error(f"❌ Oil Impact Data Error: {e}")
        return pd.DataFrame(columns=['Country', 'Crude (kg)', 'Crude (mb/d)', 'Conversion_Factor'])

# --- 4. SIDEBAR CONTROLS ---

with st.sidebar:
    st.header("Settings")
    st.session_state.horizon = st.selectbox("Horizon", options=[1, 3, 5, 10], index=[1, 3, 5, 10].index(st.session_state.horizon))
    term_date = st.date_input("ETF Terminal Date", datetime(2025, 12, 31))
    st.divider()
    
    st.header("Weights")
    st.session_state.w_macro = st.slider("Macro Gap", 0.0, 1.0, st.session_state.w_macro, key="s_macro")
    st.session_state.w_curr = st.slider("Currency Score", 0.0, 1.0, st.session_state.w_curr, key="s_curr")
    st.session_state.w_val = st.slider("Valuation Rank", 0.0, 1.0, st.session_state.w_val, key="s_val")
    st.session_state.w_nar = st.slider("Narrative Rank", 0.0, 1.0, st.session_state.w_nar, key="s_nar")
    st.session_state.w_mcap = st.slider("Mcap Liquidity", 0.0, 1.0, st.session_state.w_mcap, key="s_mcap")
    total_w = round(st.session_state.s_macro + st.session_state.s_curr + st.session_state.s_val + st.session_state.s_nar + st.session_state.s_mcap, 2)
    st.write(f"**Total Weight:** {total_w:.1%}")
    
    st.divider()
    st.header("Scenarios")
    st.session_state.oil_scenario = st.slider("Oil Price Change ($)", 0.0, 50.0, st.session_state.oil_scenario, step=1.0)
    
    st.divider()    
    col1, col2 = st.columns(2)
    if col1.button("Reset Weights"):
        for k, v in DEFAULTS.items(): 
            if k.startswith("w_"): st.session_state[f"s_{k.replace('w_', '')}"] = v
        st.rerun()
    if col2.button("Calculate Rank", type="primary", disabled=(total_w != 1.0)):
        st.session_state.calculate = True

# --- 5. DATA ORCHESTRATION ---

try:
    with st.spinner("Fetching Data..."):
        gdp_j, etf_j, reer_j = fetch_imf_gdp_journey(), fetch_etf_journey(term_date), fetch_bis_reer_journey()
        oil_j = fetch_oil_impact_journey()
        mcap_static = pd.read_csv("data/static/mcap_data.csv")
        bond_df = pd.read_csv("data/static/bond_10y_differentials.csv")
        val_df = pd.read_csv("data/static/valuation_ranks.csv")
        nar_df = pd.read_csv("data/static/narrative_ranks.csv")

    master = pd.DataFrame(COUNTRY_CONFIG.keys(), columns=["Country"])
    master["Region"] = master["Country"].map(lambda x: COUNTRY_CONFIG[x]["region"])
    for d in [gdp_j, etf_j, reer_j, oil_j, mcap_static, bond_df, val_df]:
        if not d.empty: master = master.merge(d, on="Country", how="left")
    master = master.merge(nar_df, on="Country", how="left")

    # --- 6. STRATEGY OUTPUT (GATED) ---
    if not st.session_state.calculate:
        st.info("💡 Adjust weights in the sidebar and click **Calculate Rank** to generate the strategy output.")
    else:
        h = st.session_state.horizon
        required = [f'GDP_CAGR_{h}Y', f'ETF_CAGR_{h}Y', 'Mcap_USD_Bn', 'REER_Upside', 'differential with USA', 'Average Rank', 'Rank']
        calc_df = master.dropna(subset=required).copy()
        
        if not calc_df.empty:
            calc_df['Macro_Gap'] = calc_df[f'GDP_CAGR_{h}Y'] - calc_df[f'ETF_CAGR_{h}Y']
            calc_df['R_Macro'] = calc_df['Macro_Gap'].rank(ascending=False).astype(int)
            calc_df['R_REER'] = calc_df['REER_Upside'].rank(ascending=False).astype(int)
            calc_df['R_Bond'] = calc_df['differential with USA'].rank(ascending=False).astype(int)
            calc_df['Currency_Score'] = (calc_df['R_REER'] + calc_df['R_Bond']) / 2
            calc_df['R_Curr'] = calc_df['Currency_Score'].rank().astype(int)
            calc_df['R_Val'] = calc_df['Average Rank'].rank(ascending=True).astype(int)
            calc_df['R_Nar'] = calc_df['Rank'].rank(ascending=True).astype(int)
            calc_df['R_Mcap'] = calc_df['Mcap_USD_Bn'].rank(ascending=False).astype(int)
            calc_df['Final_Score'] = (calc_df['R_Macro']*st.session_state.s_macro + calc_df['R_Curr']*st.session_state.s_curr + calc_df['R_Val']*st.session_state.s_val + calc_df['R_Nar']*st.session_state.s_nar + calc_df['R_Mcap']*st.session_state.s_mcap)
            calc_df = calc_df.sort_values("Final_Score")
            calc_df['Final Rank'] = range(1, len(calc_df) + 1)

            st.header(f"🏆 Strategy Output ({h}Y Horizon)")
            final_map = {
                'Final Rank': 'Final Rank', 'Country': 'country', 'Region': 'region',
                'Macro_Gap': 'Macro Gap', 'R_Macro': 'Macro Gap Rank',
                'Currency_Score': 'Currency Score', 'R_Curr': 'Currency Rank',
                'R_Val': 'Valuation Rank', 'R_Nar': 'Narrative Rank',
                'R_Mcap': 'MCap Rank', 'Final_Score': 'Final Score',
                'YTD_Return': 'YTD $ ETF Return (%)'
            }
            display = calc_df[list(final_map.keys())].rename(columns=final_map)
            pct_cols = ['Macro Gap', 'YTD $ ETF Return (%)']
            for col in pct_cols: display[col] = display[col] * 100
            
            st.dataframe(
                display.style.format({
                    'Final Rank': '{:d}', 'Final Score': '{:.1f}', 'Currency Score': '{:.1f}',
                    **{c: '{:.1f}' for c in pct_cols},
                    **{c: '{:d}' for c in ['Macro Gap Rank', 'Currency Rank', 'Valuation Rank', 'Narrative Rank', 'MCap Rank']}
                }).background_gradient(subset=['Final Score', 'Final Rank'], cmap='RdYlGn_r'),
                use_container_width=True, hide_index=True
            )

    st.divider()
    st.header("🔍 Data Audit & Debugging")
    t_gdp, t_etf, t_curr, t_qual, t_oil, t_master = st.tabs(["GDP Journey", "ETF Journey", "Currency Audit", "Qualitative Audit", "Oil Impact Audit", "Master Table"])
    
    with t_gdp:
        st.subheader("Raw nGDP (bn) -> CAGRs")
        g_cols = ["Country"] + [c for c in gdp_j.columns if "GDP_" in c]
        st.dataframe(gdp_j[g_cols].style.format({c: "{:,.0f}" if "CAGR" not in c else "{:.1%}" for c in g_cols if c != "Country"}), use_container_width=True)
    with t_etf:
        st.subheader("Anchor Prices -> CAGRs")
        st.dataframe(etf_j.style.format({c: "{:.1f}" if c.startswith("P_") else "{:.1%}" for c in etf_j.columns if c != "Country"}), use_container_width=True)
    with t_curr:
        if st.session_state.calculate:
            st.subheader("REER & Bond Rank Journey")
            curr_map = {
                'Country': 'Country', 'Current_REER': 'Current REER', 'Avg_REER_10Y': '10Y Avg REER',
                'REER_Upside': 'REER Upside (%)', 'R_REER': 'REER Rank',
                'differential with USA': 'Bond Diff vs US', 'R_Bond': 'Bond Rank', 'Currency_Score': 'Currency Score (Avg Rank)'
            }
            st.dataframe(calc_df[list(curr_map.keys())].rename(columns=curr_map).style.format({
                'REER Upside (%)': '{:.1%}', 'REER Rank': '{:d}', 'Bond Rank': '{:d}',
                'Current REER': '{:.1f}', '10Y Avg REER': '{:.1f}', 'Bond Diff vs US': '{:.1f}', 'Currency Score (Avg Rank)': '{:.1f}'
            }), use_container_width=True)
    with t_qual:
        if st.session_state.calculate:
            st.subheader("Valuation, Narrative & MCap Journey")
            qual_map = {
                'Country': 'Country', 'Average Rank': 'Valuation Rank Score', 'R_Val': 'Valuation Rank',
                'R_Nar': 'Narrative Rank', 'Mcap_USD_Bn': '2026 MCap ($ bn.)', 'R_Mcap': 'MCap Rank'
            }
            st.dataframe(calc_df[list(qual_map.keys())].rename(columns=qual_map).style.format({
                'Valuation Rank Score': '{:.1f}', '2026 MCap ($ bn.)': '{:,.0f}',
                'Valuation Rank': '{:d}', 'Narrative Rank': '{:d}', 'MCap Rank': '{:d}'
            }), use_container_width=True)
            
    with t_oil:
        st.subheader("Crude Oil Impact Proxy")
        oil_cols = ['Country', 'Crude (kg)', 'Crude (mb/d)', 'Conversion_Factor', 'GDP_2025']
        if all(col in master.columns for col in oil_cols):
            scenario = st.session_state.oil_scenario
            oil_calc = master[oil_cols].copy()
            oil_calc['Annual_Impact_USD_Bn'] = (oil_calc['Crude (mb/d)'] * 1e6 * scenario * 365) / 1e9
            oil_calc['GDP_Impact_Pct'] = (oil_calc['Annual_Impact_USD_Bn'] / oil_calc['GDP_2025'])
            
            faulty_countries = oil_calc[ (oil_calc['Country'] == 'Thailand') | (oil_calc['Crude (mb/d)'] > 3.0) & (oil_calc['Country'] != 'China') & (oil_calc['Country'] != 'United States') & (oil_calc['Country'] != 'India') ]
            flagged_list = faulty_countries['Country'].tolist()
            oil_clean = oil_calc[~oil_calc['Country'].isin(flagged_list)].dropna(subset=['Crude (mb/d)', 'GDP_2025'])
            
            oil_view_map = {
                'Country': 'Country', 'Crude (kg)': '2024 Crude Imports (kg)', 
                'Conversion_Factor': 'Factor (Barrels/Tonne)', 'Crude (mb/d)': '2024 Imports (mb/d)',
                'Annual_Impact_USD_Bn': f'${scenario:.0f} Price Move Annual Impact ($ bn)',
                'GDP_Impact_Pct': 'Impact on 2025 GDP (%)'
            }
            st.dataframe(oil_clean[list(oil_view_map.keys())].rename(columns=oil_view_map).style.format({
                '2024 Crude Imports (kg)': '{:,.0f}', 'Factor (Barrels/Tonne)': '{:.2f}',
                '2024 Imports (mb/d)': '{:.1f}', f'${scenario:.0f} Price Move Annual Impact ($ bn)': '{:.1f}',
                'Impact on 2025 GDP (%)': '{:.1%}'
            }), use_container_width=True)
            if flagged_list:
                st.info(f"⚠️ **Note:** The following countries were omitted due to unrealistic crude import data (Sanity Check Failure): {', '.join(flagged_list)}")
        else:
            st.warning("Oil columns not found in master dataset.")
            
    with t_master: st.dataframe(master, use_container_width=True)

except Exception as e: st.error(f"❌ Error: {e}")
