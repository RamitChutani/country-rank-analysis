# Project Context & Knowledge Base: Global Macro ETF Strategy Dashboard

## 1. Project Overview
This project is a systematic, data-driven dashboard built in **Streamlit** (Python 3.13+) to rank 30+ countries for a Global Macro ETF strategy. The goal is to synthesize disparate economic data into a single, weighted investment ranking.

## 2. Core Pillars & Methodology
The dashboard ranks countries based on 5 pillars, each derived from a mix of live APIs and static qualitative data:

1.  **Macro Gap (20%):** Measures if the stock market (ETF) is keeping pace with economic growth.
    *   *Logic:* `GDP CAGR - ETF CAGR`. High positive gaps suggest undervalued markets.
2.  **Currency Score (20%):** Measures currency valuation and yield support.
    *   *Logic:* Average of REER Upside (Current vs 10Y Avg) and Bond yield differential vs the US.
3.  **Valuation Rank (20%):** Fundamental valuation metrics (P/E, P/B).
    *   *Source:* Static Excel (`Valuation Ranks.csv`).
4.  **Narrative Rank (30%):** Qualitative Buy/Sell conviction.
    *   *Source:* Static Excel (`Narrative.csv`).
5.  **Mcap Liquidity (10%):** Market capitalization filter to ensure tradeability.
    *   *Source:* Hardcoded `mcap_data.csv` (Wikipedia/Exchange estimates).

## 3. Data Infrastructure & Logic Journey
The dashboard is designed as a "glass box," meaning intermediate calculation steps are exposed in "Data Audit" tabs.

*   **IMF (GDP) Journey:** Fetches 10 years of data. Pre-computes 1Y, 3Y, 5Y, and 10Y CAGRs.
*   **Yahoo (ETF) Journey:** Fetches 11 years of daily price history. Uses `get_indexer(method='nearest')` to anchor historical prices and calculate corresponding CAGRs and YTD returns.
*   **BIS (REER) Journey:** Fixed 10Y mean reversion logic.
*   **Oil Impact Proxy:** 
    *   *Source:* `oil impact/Total Oil Imports by country 2024.xlsx`.
    *   *Conversion:* Back-calculated at 1 metric tonne $\approx$ 7.33 barrels.
    *   *Impact:* Calculated as `% of 2025 GDP` based on a variable \$Oil Price Change scenario (Sidebar slider).
    *   *Sanity Check:* Thailand is flagged and omitted due to erroneous import data in the source.

## 4. Operational & Technical Nuance
*   **Gated Calculation:** The app does not auto-recalculate ranks when sliders are moved. Users must hit the **"Calculate Rank"** button, which snapshots the current sidebar weights and horizon to prevent erratic output.
*   **Formatting Constraints:**
    *   All percentages are shown as unit-less numbers (multiplied by 100).
    *   All large absolute numbers (GDP/MCap) are rounded to integers.
    *   All ranks are integers (1-N).
*   **Data Integrity:** The app employs a strict 100% data completeness mode. Any country missing data across the 7 required pillars is excluded from the ranking table.
*   **Weight Reset:** A dedicated sidebar button restores the default weighting (20/20/20/30/10).

## 5. The Presentation Task
The objective is to produce a high-impact PowerPoint presentation based on this model. 

**Instructions for the AI Designer:**
1.  **Audience:** Internal Investment Committee.
2.  **Output:** A slide-by-slide deck structure.
3.  **Data Handling:** The AI must use the two provided CSVs (`strategy_output.csv` and `audit_master_data.csv`) as the data sources.
4.  **Guide:** The presentation must walk through the project methodology, the 4-pillar logic, the "Macro Gap" rationale, and the Oil Impact sensitivity analysis.
5.  **Validation:** The AI should highlight how weighting sensitivity confirms the predictive power of the model when compared against YTD performance.

---
*End of Memory Context - May 13, 2026*
