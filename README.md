# 🌍 Global Macro Strategy Dashboard

A quantitative macro-investment dashboard designed to rank global equity markets (via country-specific ETFs) based on a multi-factor scoring model. It aims to identify undervalued or high-potential international markets by combining live financial data with proprietary static analysis.

## 📊 Core Pillars
The dashboard calculates a Composite Score for over 30 countries based on five key investment pillars:
1. **Macro Gap (20%):** Difference between economic growth (GDP CAGR) and stock market performance (ETF CAGR).
2. **Currency & Yield (20%):** Composite of BIS REER (Real Effective Exchange Rate) over/undervaluation and 10Y government bond yield differentials.
3. **Fundamental Valuation (20%):** Re-ranked pricing metrics (CAPE, P/B, P/CF) from proprietary research.
4. **Qualitative Narrative (30%):** Subjective sentiment ranks accounting for geopolitical or structural factors.
5. **Market Liquidity (10%):** Live Market Cap data (World Bank) to ensure actionable opportunities.

## 🚀 Features
- **Live API Integration:** Real-time data from IMF (GDP), Yahoo Finance (ETFs), BIS (REER), and World Bank (Mcap).
- **Dynamic Re-weighting:** Adjust pillar weights and recalculate global ranks instantly.
- **Smart Date Logic:** Fetches the most recent valid trading day on or before the selected terminal date.
- **Data Audit:** Comprehensive transparency tabs showing the journey from raw API data to final rankings.

## ⚙️ Setup & Usage
1. **Requirements:** Python 3.13+ and [uv](https://github.com/astral-sh/uv).
2. **Installation:**
   ```bash
   uv sync
   ```
3. **Run Dashboard:**
   ```bash
   uv run streamlit run app.py
   ```
4. **Usage:**
   - Adjust weights in the sidebar (must sum to 100%).
   - Click **Calculate Rank** to update the strategy output.
   - Use the **Data Audit** tabs to verify logic and completeness.

## 🗺️ Roadmap & Future Improvements
- [ ] **Mcap Enrichment:** Integrate secondary sources (IMF FSI or Direct Exchange data) to recover missing countries currently excluded by World Bank gaps.
- [ ] **Horizon Performance:** Precompute fixed GDP windows (1Y, 3Y, 5Y, 10Y) to optimize loading speed.
- [ ] **Data Persistence:** Implement a long-term cache (SQLite/Parquet) for slow-moving macro data (GDP/BIS), only refreshing ETF data daily.
- [ ] **Logic Transparency:** Add intermediate tables showing the step-by-step transformation: `Raw Value -> Sector Metric -> Z-Score -> Final Pillar Rank`.
- [ ] **UI Polish:** Consistent 1-decimal percentage representation and integer-based ranking across all views.
