# GEMINI.md - Project Context

## Project Overview
**Country Rank Analysis** is a quantitative macro-investment dashboard designed to rank global equity markets (via country-specific ETFs) using a multi-factor scoring model. The application identifies undervalued or high-potential international markets by synthesizing live financial data with proprietary static analysis.

### Core Pillars
- **Macroeconomic Divergence (Macro Gap):** Comparison between GDP CAGR and ETF CAGR.
- **Currency & Yield Valuation:** REER (Real Effective Exchange Rate) analysis and 10-year government bond differentials.
- **Fundamental Valuation:** Metric-based ranking (CAPE, P/B, P/CF).
- **Qualitative Sentiment (Narrative):** Subjective research-based overlay.
- **Market Liquidity (Mcap):** Live Market Capitalization data for weighting/filtering.

### Main Technologies
- **Language:** Python >= 3.13
- **Web Framework:** [Streamlit](https://streamlit.io/)
- **Data Processing:** Pandas, NumPy
- **Data Sources:** 
    - [Yahoo Finance (yfinance)](https://github.com/ranaroussi/yfinance) for ETF prices.
    - [World Bank (wbgapi)](https://github.com/t-solomon/wbgapi) for Market Cap.
    - [IMF API](https://www.imf.org/external/datamapper/api/v1/) for GDP data.
    - [BIS](https://www.bis.org/) for REER data.
    - Static files in `data/static/` for bond differentials, valuation ranks, narrative ranks, market cap, and oil imports.

---

## Building and Running

### Prerequisites
- [uv](https://github.com/astral-sh/uv) (recommended for package management)
- Python 3.13+

### Setup
1. **Install Dependencies:**
   ```bash
   uv sync
   ```
2. **Environment:**
   Ensure the static data files are present in `data/static/`.

### Running the Application
To launch the Streamlit dashboard:
```bash
uv run streamlit run app.py
```

### Testing
- No formal test suite (e.g., pytest) is currently implemented. 
- Validation is performed through the Streamlit UI and console logs.

---

## Development Conventions

### Data Pipeline
- **Caching:** Extensive use of `@st.cache_data` for API calls to optimize performance and respect rate limits.
- **Country Configuration:** The `COUNTRY_CONFIG` dictionary in `app.py` serves as the single source of truth for ISO3 codes, BIS codes, and ETF tickers.
- **Data Integrity:** The pipeline uses a "Strict Data Check" that drops any country missing critical data points (`GDP_CAGR`, `ETF_CAGR`, `Mcap_USD_Bn`, `REER_Upside`, `differential with USA`).

### Architecture
- `app.py`: Contains the Streamlit UI, live data fetchers, and the ranking logic.
- `main.py`: Current placeholder/entry point for CLI usage.
- `pyproject.toml`: Managed via `uv`, defining all project dependencies.

### File Structure Notes
- `data/static/`: Runtime static data sources.
- `data/reference_workbooks/`: Archived Excel model/reference files.
- `*.csv`: These files appear to be exports or reference snapshots of specific data points from the main Excel workbook.

---

## Usage Guidelines
- **Weights:** Users can adjust pillar weights in the sidebar to recalculate rankings in real-time.
- **Horizon:** The "Horizon (Years)" setting affects both GDP and ETF CAGR calculations (default is 10 years).
- **Output:** The "Final Score" is a weighted average of ranks; a lower score indicates a more attractive investment opportunity.
