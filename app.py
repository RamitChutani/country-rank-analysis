import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import wbgapi as wb
import requests
from datetime import datetime

st.set_page_config(page_title="Macro ETF Strategy Dashboard", layout="wide")

# --- 1. CONFIGURATION & MAPPINGS ---
COUNTRY_CONFIG = {
    "Argentina": {"iso3": "ARG", "bis": "AR", "ticker": "ARGT"},
    "Australia": {"iso3": "AUS", "bis": "AU", "ticker": "EWA"},
    "Austria": {"iso3": "AUT", "bis": "AT", "ticker": "EWO"},
    "Belgium": {"iso3": "BEL", "bis": "BE", "ticker": "EWK"},
    "Brazil": {"iso3": "BRA", "bis": "BR", "ticker": "EWZ"},
    "Canada": {"iso3": "CAN", "bis": "CA", "ticker": "EWC"},
    "Chile": {"iso3": "CHL", "bis": "CL", "ticker": "ECH"},
    "China": {"iso3": "CHN", "bis": "CN", "ticker": "MCHI"},
    "Colombia": {"iso3": "COL", "bis": "CO", "ticker": "GXG"},
    "Denmark": {"iso3": "DNK", "bis": "DK", "ticker": "EDEN"},
    "Finland": {"iso3": "FIN", "bis": "FI", "ticker": "EFNL"},
    "France": {"iso3": "FRA", "bis": "FR", "ticker": "EWQ"},
    "Germany": {"iso3": "DEU", "bis": "DE", "ticker": "EWG"},
    "Greece": {"iso3": "GRC", "bis": "GR", "ticker": "GREK"},
    "Hong Kong": {"iso3": "HKG", "bis": "HK", "ticker": "EWH"},
    "India": {"iso3": "IND", "bis": "IN", "ticker": "INDA"},
    "Indonesia": {"iso3": "IDN", "bis": "ID", "ticker": "EIDO"},
    "Ireland": {"iso3": "IRL", "bis": "IE", "ticker": "EIRL"},
    "Israel": {"iso3": "ISR", "bis": "IL", "ticker": "EIS"},
    "Italy": {"iso3": "ITA", "bis": "IT", "ticker": "EWI"},
    "Japan": {"iso3": "JPN", "bis": "JP", "ticker": "EWJ"},
    "Malaysia": {"iso3": "MYS", "bis": "MY", "ticker": "EWM"},
    "Mexico": {"iso3": "MEX", "bis": "MX", "ticker": "EWW"},
    "Netherlands": {"iso3": "NLD", "bis": "NL", "ticker": "EWN"},
    "Norway": {"iso3": "NOR", "bis": "NO", "ticker": "ENOR"},
    "Philippines": {"iso3": "PHL", "bis": "PH", "ticker": "EPHE"},
    "Poland": {"iso3": "POL", "bis": "PL", "ticker": "EPOL"},
    "Singapore": {"iso3": "SGP", "bis": "SG", "ticker": "EWS"},
    "South Africa": {"iso3": "ZAF", "bis": "ZA", "ticker": "EZA"},
    "South Korea": {"iso3": "KOR", "bis": "KR", "ticker": "EWY"},
    "Spain": {"iso3": "ESP", "bis": "ES", "ticker": "EWP"},
    "Sweden": {"iso3": "SWE", "bis": "SE", "ticker": "EWD"},
    "Switzerland": {"iso3": "CHE", "bis": "CH", "ticker": "EWL"},
    "Taiwan": {"iso3": "TWN", "bis": "TW", "ticker": "EWT"},
    "Thailand": {"iso3": "THA", "bis": "TH", "ticker": "THD"},
    "Turkey": {"iso3": "TUR", "bis": "TR", "ticker": "TUR"},
    "United Kingdom": {"iso3": "GBR", "bis": "GB", "ticker": "EWU"},
    "United States": {"iso3": "USA", "bis": "US", "ticker": "IVV"}
}

# --- 2. LIVE DATA FETCHERS ---

@st.cache_data
def fetch_imf_gdp(horizon, end_year):
    iso_list = [v['iso3'] for v in COUNTRY_CONFIG.values()]
    start_year = end_year - horizon
    url = f"https://api.imf.org/external/sdmx/2.1/data/WEO/{'+'.join(iso_list)}.NGDPD.A?startPeriod={start_year}&endPeriod={end_year}"
    try:
        response = requests.get(url, headers={"Accept": "application/json"}, timeout=15)
        response.raise_for_status()
        data = response.json()
        structure = data.get('structure', {})
        series_dims = structure.get('dimensions', {}).get('series', [])
        obs_dims = structure.get('dimensions', {}).get('observation', [])
        country_map = {i: v['id'] for i, v in enumerate(series_dims[0].get('values', []))}
        time_map = {i: v['id'] for i, v in enumerate(obs_dims[0].get('values', []))}
        iso_to_name = {v['iso3']: k for k, v in COUNTRY_CONFIG.items()}
        res = []
        datasets = data.get('dataSets', [])
        if not datasets: return pd.DataFrame(columns=["Country", "GDP_CAGR"])
        series_data = datasets[0].get('series', {})
        for key, s_val in series_data.items():
            indices = key.split(':')
            country_iso = country_map.get(int(indices[0]))
            country_name = iso_to_name.get(country_iso)
            if not country_name: continue
            obs = s_val.get('observations', {})
            vals = {}
            for t_idx, v_list in obs.items():
                year = time_map.get(int(t_idx))
                if year: vals[int(year)] = float(v_list[0])
            v1, v2 = vals.get(start_year), vals.get(end_year)
            if v1 and v2 and v1 > 0:
                res.append({"Country": country_name, "GDP_CAGR": (v2/v1)**(1/horizon)-1})
        return pd.DataFrame(res) if res else pd.DataFrame(columns=["Country", "GDP_CAGR"])
    except Exception as e:
        st.error(f"❌ IMF API Error: {e}")
        return pd.DataFrame(columns=["Country", "GDP_CAGR"])

@st.cache_data
def fetch_etf_live(horizon, terminal_date):
    term_dt = pd.to_datetime(terminal_date)
    start_date_fetch = term_dt - pd.DateOffset(years=horizon + 1)
    res = []
    progress_bar = st.progress(0, text="Fetching ETF prices...")
    tickers = list(COUNTRY_CONFIG.items())
    for i, (name, meta) in enumerate(tickers):
        try:
            df = yf.download(meta['ticker'], start=start_date_fetch.strftime("%Y-%m-%d"), end=datetime.now().strftime("%Y-%m-%d"), progress=False)
            if not df.empty:
                close_col = df['Close'][meta['ticker']] if isinstance(df.columns, pd.MultiIndex) else df['Close']
                valid_data = close_col[close_col.index <= term_dt]
                if not valid_data.empty and len(valid_data) > 20:
                    p2 = float(valid_data.iloc[-1])
                    p2_date = valid_data.index[-1]
                    p1_date_target = p2_date - pd.DateOffset(years=horizon)
                    p1_idx = valid_data.index.get_indexer([p1_date_target], method='nearest')[0]
                    p1 = float(valid_data.iloc[p1_idx])
                    if p1 > 0:
                        res.append({"Country": name, "ETF_CAGR": (p2/p1)**(1/horizon)-1})
        except: continue
        progress_bar.progress((i + 1) / len(tickers))
    progress_bar.empty()
    return pd.DataFrame(res) if res else pd.DataFrame(columns=["Country", "ETF_CAGR"])

@st.cache_data
def fetch_wb_mcap():
    try:
        iso_list = [v['iso3'] for v in COUNTRY_CONFIG.values()]
        df = wb.data.DataFrame('CM.MKT.LCAP.CD', iso_list, time=range(2023, 2025), labels=True)
        df = df.reset_index()
        year_cols = [c for c in df.columns if c.startswith('YR')]
        df['Mcap_Raw'] = df[year_cols].bfill(axis=1).iloc[:, 0]
        df['Mcap_USD_Bn'] = df['Mcap_Raw'] / 1e9
        iso_to_name = {v['iso3']: k for k, v in COUNTRY_CONFIG.items()}
        df['Country'] = df['economy'].map(iso_to_name)
        return df[['Country', 'Mcap_USD_Bn']].dropna()
    except Exception as e:
        st.error(f"❌ World Bank Error: {e}")
        return pd.DataFrame(columns=["Country", "Mcap_USD_Bn"])

@st.cache_data
def fetch_bis_reer():
    start_date, end_date = "2016-01-01", datetime.now().strftime("%Y-%m-%d")
    url = f"https://stats.bis.org/api/v2/data/dataflow/BIS/WS_EER/1.0/M.R.B?startPeriod={start_date}&endPeriod={end_date}&format=csv"
    try:
        df = pd.read_csv(url)
        bis_codes = {v['bis'] for v in COUNTRY_CONFIG.values()}
        df = df[df['REF_AREA'].isin(bis_codes)].copy()
        df["date"] = pd.to_datetime(df["TIME_PERIOD"])
        df = df.sort_values(["REF_AREA", "date"])
        res = []
        iso2_to_name = {v['bis']: k for k, v in COUNTRY_CONFIG.items()}
        for code, group in df.groupby('REF_AREA'):
            if group.empty: continue
            current_reer, avg_10y_reer = group.iloc[-1]["OBS_VALUE"], group["OBS_VALUE"].mean()
            if not np.isnan(avg_10y_reer) and avg_10y_reer > 0:
                res.append({"Country": iso2_to_name[code], "REER_Upside": (avg_10y_reer - current_reer) / avg_10y_reer})
        return pd.DataFrame(res) if res else pd.DataFrame(columns=["Country", "REER_Upside"])
    except Exception as e:
        st.error(f"❌ BIS REER Error: {e}")
        return pd.DataFrame(columns=["Country", "REER_Upside"])

# --- 3. UI LAYOUT ---

st.title("🌍 Global Macro Strategy")

with st.sidebar:
    st.header("Settings")
    horizon = st.number_input("Horizon (Years)", 1, 15, 10)
    term_date = st.date_input("ETF Terminal Date", datetime(2025, 12, 31))
    st.divider()
    st.header("Weights")
    w_macro = st.slider("Macro Gap", 0.0, 1.0, 0.20)
    w_curr = st.slider("Currency Score", 0.0, 1.0, 0.20)
    w_val = st.slider("Valuation Rank", 0.0, 1.0, 0.20)
    w_nar = st.slider("Narrative Rank", 0.0, 1.0, 0.30)
    w_mcap = st.slider("Mcap Liquidity", 0.0, 1.0, 0.10)
    
    total_w = round(w_macro + w_curr + w_val + w_nar + w_mcap, 2)
    st.write(f"**Total Weight:** {total_w:.1%}")
    if total_w != 1.0:
        st.error("Total weight must equal 100%")

calc_pressed = st.button("Calculate Rank", disabled=(total_w != 1.0), use_container_width=True)

# --- 4. DATA PROCESSING ---

excel_file = "etf_dash_May_06.xlsx"
try:
    with st.spinner("Reading Excel sources..."):
        bond_df = pd.read_excel(excel_file, sheet_name="10y bond")[['Country', 'differential with USA']]
        val_df = pd.read_excel(excel_file, sheet_name="Valuation Ranks")[['Country', 'Average Rank']]
        nar_df = pd.read_excel(excel_file, sheet_name="Narrative")[['Country', 'Rank']]
    with st.spinner("Querying Live APIs..."):
        gdp, etf, mcap, reer = fetch_imf_gdp(horizon, 2025), fetch_etf_live(horizon, pd.to_datetime(term_date)), fetch_wb_mcap(), fetch_bis_reer()

    master = pd.DataFrame(COUNTRY_CONFIG.keys(), columns=["Country"])
    for d in [gdp, etf, mcap, reer, bond_df, val_df]:
        master = master.merge(d, on="Country", how="left")
    master = master.merge(nar_df, on="Country", how="left", suffixes=('', '_Narrative'))

    required = ['GDP_CAGR', 'ETF_CAGR', 'Mcap_USD_Bn', 'REER_Upside', 'differential with USA', 'Average Rank', 'Rank']
    master_clean = master.dropna(subset=required).copy()

    # --- MAIN OUTPUT ---
    if master_clean.empty:
        st.error("No countries have 100% data completeness across all factors.")
    else:
        # Calculate All Pillar Ranks (1 is BEST)
        master_clean['Macro_Gap'] = master_clean['GDP_CAGR'] - master_clean['ETF_CAGR']
        master_clean['R_Macro'] = master_clean['Macro_Gap'].rank(ascending=False).astype(int)
        
        master_clean['R_REER'] = master_clean['REER_Upside'].rank(ascending=False).astype(int)
        master_clean['R_Bond'] = master_clean['differential with USA'].rank(ascending=False).astype(int)
        master_clean['R_Curr'] = ((master_clean['R_REER'] + master_clean['R_Bond']) / 2).rank().astype(int)
        
        # Explicitly re-rank the Excel-based Valuation and Narrative scores
        master_clean['R_Val'] = master_clean['Average Rank'].rank(ascending=True).astype(int)
        master_clean['R_Nar'] = master_clean['Rank'].rank(ascending=True).astype(int)
        
        master_clean['R_Mcap'] = master_clean['Mcap_USD_Bn'].rank(ascending=False).astype(int)

        weights = {'macro': w_macro, 'curr': w_curr, 'val': w_val, 'nar': w_nar, 'mcap': w_mcap}
        master_clean['Final_Score'] = (
            (master_clean['R_Macro'] * weights['macro']) + 
            (master_clean['R_Curr'] * weights['curr']) + 
            (master_clean['R_Val'] * weights['val']) + 
            (master_clean['R_Nar'] * weights['nar']) + 
            (master_clean['R_Mcap'] * weights['mcap'])
        )
        master_clean = master_clean.sort_values("Final_Score")
        master_clean['Final Rank'] = range(1, len(master_clean) + 1)

        st.divider()
        st.subheader(f"🏆 Strategy Output (Horizon: {horizon}Y)")
        
        # Display Columns: Added REER and Bond Ranks for visual verification of Currency Rank
        view_cols = ['Final Rank', 'Country', 'Macro_Gap', 'R_Macro', 'R_REER', 'R_Bond', 'R_Curr', 'R_Val', 'R_Nar', 'Mcap_USD_Bn', 'Final_Score']
        display = master_clean[view_cols].rename(columns={
            "R_Macro": "Macro Rank",
            "R_REER": "REER Rank",
            "R_Bond": "Bond Rank",
            "R_Curr": "Currency Rank", 
            "R_Val": "Valuation Rank", 
            "R_Nar": "Narrative Rank", 
            "Mcap_USD_Bn": "Market Cap"
        })
        
        st.dataframe(
            display.style.format({
                'Final Rank': '{:d}',
                'Macro Rank': '{:d}',
                'REER Rank': '{:d}',
                'Bond Rank': '{:d}',
                'Currency Rank': '{:d}',
                'Valuation Rank': '{:d}',
                'Narrative Rank': '{:d}',
                'Macro_Gap': '{:.1%}',
                'Market Cap': '${:,.1f}B',
                'Final_Score': '{:.2f}'
            }).background_gradient(subset=['Final_Score'], cmap='RdYlGn_r'),
            use_container_width=True, hide_index=True
        )

    # --- DATA AUDIT SECTION ---
    st.divider()
    st.header("🔍 Data Audit & Debugging")
    tab_summary, tab_gdp, tab_etf, tab_mcap, tab_reer, tab_excel = st.tabs(["Merge Summary", "IMF (GDP)", "Yahoo (ETF)", "WB (Mcap)", "BIS (REER)", "Excel Sources"])
    with tab_summary:
        st.subheader("Data Completeness")
        stats = [{"Factor": col, "Available Countries": master[col].notna().sum()} for col in required]
        st.table(pd.DataFrame(stats))
        st.subheader("Full Merged Dataset")
        st.dataframe(master.style.format({
            'GDP_CAGR': '{:.1%}', 'ETF_CAGR': '{:.1%}', 'REER_Upside': '{:.1%}',
            'Mcap_USD_Bn': '${:,.1f}B', 'differential with USA': '{:.1f}'
        }), use_container_width=True)
    with tab_gdp: st.dataframe(gdp.style.format({'GDP_CAGR': '{:.1%}'}), use_container_width=True)
    with tab_etf: st.dataframe(etf.style.format({'ETF_CAGR': '{:.1%}'}), use_container_width=True)
    with tab_mcap: st.dataframe(mcap.style.format({'Mcap_USD_Bn': '${:,.1f}B'}), use_container_width=True)
    with tab_reer: st.dataframe(reer.style.format({'REER_Upside': '{:.1%}'}), use_container_width=True)
    with tab_excel:
        c1, c2, c3 = st.columns(3)
        c1.write("Bonds"); c1.dataframe(bond_df)
        c2.write("Valuation"); c2.dataframe(val_df)
        c3.write("Narrative"); c3.dataframe(nar_df)

except Exception as e:
    st.error(f"❌ Critical Error: {e}")
