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
    url = f"https://www.imf.org/external/datamapper/api/v1/NGDPD/{'+'.join(iso_list)}"
    try:
        data = requests.get(url, timeout=10).json().get('values', {}).get('NGDPD', {})
        res = []
        for name, meta in COUNTRY_CONFIG.items():
            c_data = data.get(meta['iso3'], {})
            v1, v2 = c_data.get(str(start_year)), c_data.get(str(end_year))
            if v1 and v2:
                res.append({"Country": name, "GDP_CAGR": (v2/v1)**(1/horizon)-1})
        return pd.DataFrame(res)
    except Exception as e:
        st.error(f"❌ IMF API Error: {e}")
        return pd.DataFrame()

@st.cache_data
def fetch_etf_live(horizon, terminal_date):
    start_date = terminal_date - pd.DateOffset(years=horizon)
    res = []
    progress_bar = st.progress(0, text="Fetching ETF prices...")
    tickers = list(COUNTRY_CONFIG.items())
    
    for i, (name, meta) in enumerate(tickers):
        try:
            # Individual fetch ensures ticker alignment
            df = yf.download(meta['ticker'], start=start_date, end=terminal_date, progress=False)
            if not df.empty and len(df) > 10:
                p1, p2 = float(df['Close'].iloc[0]), float(df['Close'].iloc[-1])
                res.append({"Country": name, "ETF_CAGR": (p2/p1)**(1/horizon)-1})
        except: continue
        progress_bar.progress((i + 1) / len(tickers))
    progress_bar.empty()
    return pd.DataFrame(res)

@st.cache_data
def fetch_wb_mcap():
    try:
        iso_list = [v['iso3'] for v in COUNTRY_CONFIG.values()]
        df = wb.data.DataFrame('CM.MKT.LCAP.CD', iso_list, mrv=1).reset_index()
        df.columns = ['iso3', 'Mcap_Raw']
        df['Mcap_USD_Bn'] = df['Mcap_Raw'] / 1e9
        iso_to_name = {v['iso3']: k for k, v in COUNTRY_CONFIG.items()}
        df['Country'] = df['iso3'].map(iso_to_name)
        return df[['Country', 'Mcap_USD_Bn']].dropna()
    except Exception as e:
        st.error(f"❌ World Bank Error: {e}")
        return pd.DataFrame()

@st.cache_data
def fetch_bis_reer():
    url = "https://www.bis.org/statistics/full_bis_eer_csv.zip"
    try:
        df = pd.read_csv(url)
        bis_map = {v['bis']: k for k, v in COUNTRY_CONFIG.items()}
        df = df[df['REF_AREA'].isin(bis_map.keys())]
        res = []
        for code, group in df.groupby('REF_AREA'):
            vals = group['OBS_VALUE'].dropna()
            if len(vals) >= 120:
                curr, avg = vals.iloc[-1], vals.tail(120).mean()
                res.append({"Country": bis_map[code], "REER_Upside": (avg - curr) / avg})
        return pd.DataFrame(res)
    except: return pd.DataFrame()

# --- 3. UI LAYOUT ---

st.title("🌍 Global Macro Strategy")

with st.sidebar:
    st.header("Settings")
    horizon = st.number_input("Horizon (Years)", 1, 15, 10)
    term_date = st.date_input("ETF Terminal Date", datetime(2025, 12, 31))
    
    st.divider()
    st.header("Weights")
    w_macro = st.slider("Macro Gap", 0.0, 1.0, 0.25)
    w_curr = st.slider("Currency Score", 0.0, 1.0, 0.20)
    w_val = st.slider("Valuation Rank", 0.0, 1.0, 0.25)
    w_nar = st.slider("Narrative Rank", 0.0, 1.0, 0.15)
    w_mcap = st.slider("Mcap Liquidity", 0.0, 1.0, 0.15)
    
    # Normalize
    tw = w_macro + w_curr + w_val + w_nar + w_mcap
    weights = {k: v/tw if tw > 0 else 0 for k, v in 
               {'macro': w_macro, 'curr': w_curr, 'val': w_val, 'nar': w_nar, 'mcap': w_mcap}.items()}

# --- 4. DATA PROCESSING ---

excel_file = "etf_dash_May_06.xlsx"

try:
    # Read Excel Sheets
    with st.spinner("Reading Excel sources..."):
        bond_df = pd.read_excel(excel_file, sheet_name="10y bond")[['Country', 'differential with USA']]
        val_df = pd.read_excel(excel_file, sheet_name="Valuation Ranks")[['Country', 'Average Rank']]
        nar_df = pd.read_excel(excel_file, sheet_name="Narrative")[['Country', 'Rank']]

    # Fetch Live Data
    with st.spinner("Querying Live APIs..."):
        gdp = fetch_imf_gdp(horizon, 2025)
        etf = fetch_etf_live(horizon, pd.to_datetime(term_date))
        mcap = fetch_wb_mcap()
        reer = fetch_bis_reer()

    # Merge Pipeline
    master = pd.DataFrame(COUNTRY_CONFIG.keys(), columns=["Country"])
    master = master.merge(gdp, on="Country", how="left")
    master = master.merge(etf, on="Country", how="left")
    master = master.merge(mcap, on="Country", how="left")
    master = master.merge(reer, on="Country", how="left")
    master = master.merge(bond_df, on="Country", how="left")
    master = master.merge(val_df, on="Country", how="left")
    master = master.merge(nar_df, on="Country", how="left", suffixes=('', '_Narrative'))

    # Strict Data Check: Drop countries missing any functional logic
    required = ['GDP_CAGR', 'ETF_CAGR', 'Mcap_USD_Bn', 'REER_Upside', 'differential with USA']
    master = master.dropna(subset=required).copy()

    if master.empty:
        st.error("No countries have sufficient data to be ranked.")
    else:
        # Ranking (1 is best)
        master['Macro_Gap'] = master['GDP_CAGR'] - master['ETF_CAGR']
        master['R_Macro'] = master['Macro_Gap'].rank(ascending=False)
        
        # Currency Rank (REER + Bonds)
        master['R_REER'] = master['REER_Upside'].rank(ascending=False)
        master['R_Bond'] = master['differential with USA'].rank(ascending=False)
        master['R_Curr'] = ((master['R_REER'] + master['R_Bond']) / 2).rank()
        
        master['R_Val'] = master['Average Rank'].rank()
        master['R_Nar'] = master['Rank'].rank()
        master['R_Mcap'] = master['Mcap_USD_Bn'].rank(ascending=False)

        # Composite
        master['Final_Score'] = (
            (master['R_Macro'] * weights['macro']) +
            (master['R_Curr'] * weights['curr']) +
            (master['R_Val'] * weights['val']) +
            (master['R_Nar'] * weights['nar']) +
            (master['R_Mcap'] * weights['mcap'])
        )
        
        master = master.sort_values("Final_Score")
        master['Final Rank'] = range(1, len(master) + 1)

        # Presentation
        st.subheader(f"Strategy Output (Horizon: {horizon}Y)")
        
        view_cols = ['Final Rank', 'Country', 'Macro_Gap', 'R_Curr', 'Average Rank', 'Rank', 'Mcap_USD_Bn', 'Final_Score']
        display = master[view_cols].rename(columns={
            "R_Curr": "Currency Rank",
            "Average Rank": "Valuation Rank",
            "Rank": "Narrative Rank",
            "Mcap_USD_Bn": "Market Cap"
        })

        st.dataframe(
            display.style.format({
                'Macro_Gap': '{:.2%}',
                'Market Cap': '${:,.1f}B',
                'Final_Score': '{:.2f}'
            }).background_gradient(subset=['Final_Score'], cmap='RdYlGn_r'),
            use_container_width=True, hide_index=True
        )

except Exception as e:
    st.error(f"❌ Critical Error: {e}")
    st.info("Check if 'etf_dash_May_06.xlsx' is present and sheet names match: '10y bond', 'Valuation Ranks', 'Narrative'.")