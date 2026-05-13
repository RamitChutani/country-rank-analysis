# PowerPoint Presentation Guide: Global Macro ETF Strategy
**Colleague Note:** You have been provided with two data files: `strategy_output.csv` and `audit_master_data.csv`. Use these as your sole sources of truth to build the presentation.

---

## 🟢 Slide 1: Project Overview & Main Result
*   **Message:** We have developed a quantitative model to rank 30+ countries by merging fundamental and qualitative metrics.
*   **The "Winner":** Refer to `strategy_output.csv`. Look at the country with "Final Rank" = 1.
*   **Visual:** Create a table or chart showing the top 5 countries, including their `country`, `Final Rank`, and `Final Score`.

---

## 🟢 Slide 2: Methodology & Data Fusion
*   **The Framework:** A 4-Pillar Ranking Model:
    1. **Macro Gap:** Economic growth vs. Market returns.
    2. **Currency Score:** Value of currency & interest rate support.
    3. **Qualitative:** Fundamental value & sentiment narrative.
    4. **Liquidity:** Market Capitalization.
*   **Data Sources:** Refer to Slide 9 (Appendix) for full methodology.

---

## 🟢 Slide 3: Pillar 1 - The Macro Gap
*   **Logic:** A positive "Macro Gap" means the economy is growing faster than the stock market.
*   **Data:** Use `strategy_output.csv`. Plot `country` vs `Macro Gap`. 
*   **Explanation:** High gaps suggest the market is undervalued relative to real-world GDP growth.

---

## 🟢 Slide 4: Pillar 2 - Currency Score
*   **Logic:** We evaluate FX cheapness (REER) and yield support (Bond spreads).
*   **Data:** Use `strategy_output.csv`. Plot `country` vs `Currency Score`.
*   **Explanation:** A lower score implies the currency provides an extra buffer/cushion for USD-based investors.

---

## 🟢 Slide 5: Pillar 3 - Qualitative & Narrative
*   **Data:** Use `audit_master_data.csv`. Reference `Valuation Rank Score` and `Rank` (Narrative).
*   **Explanation:** These are static expert-derived ranks that balance our machine-learning macro signals with human fundamental research.

---

## 🟢 Slide 6: Pillar 4 - MCap Liquidity
*   **Data:** Use `audit_master_data.csv`. Reference the `2026 MCap ($ bn.)` column.
*   **Explanation:** This acts as a "sanity filter"—we prioritize highly liquid markets where institutional entry/exit is seamless.

---

## 🟢 Slide 7: Final Score & Rankings
*   **Visual:** Use `strategy_output.csv`. Create a heatmap or table showing the top 10 countries.
*   **Key Columns:** `country`, `Final Rank`, `Final Score`, and `Macro Gap Rank`.
*   **Note:** The "Final Score" is the weighted average of all pillar ranks.

---

## 🟢 Slide 8: Weight Sensitivity (Model Validation)
*   **Logic:** Our model is dynamic.
*   **Verification Task:** Compare the `Final Rank` from `strategy_output.csv` against the `YTD $ ETF Return (%)` column. A high correlation between our model's "Final Rank" and actual "YTD Return" confirms our weight configuration is predictive.

---

## 🟢 Slide 9 (Appendix): Data Infrastructure
| Data Point | Source | Method | Update Frequency |
| :--- | :--- | :--- | :--- |
| **GDP** | IMF WEO | IMF API | Biannual |
| **REER** | BIS Statistics | BIS API | Monthly |
| **ETF Prices** | Yahoo Finance | YFinance API | Daily |
| **MCap** | Wikipedia / Exchanges | Hardcoded CSV | Annual Review |

---

## 🟢 Slide 10 (Appendix): Oil Impact Analysis
*   **Logic:** Impact of a $10 oil price shock on GDP.
*   **Data:** Use `audit_master_data.csv`. Calculate: `(Crude (mb/d) * 1e6 * 10 * 365) / GDP_2025`.
*   **Note:** Thailand is omitted from the analysis due to identified data quality issues in the source imports file.
