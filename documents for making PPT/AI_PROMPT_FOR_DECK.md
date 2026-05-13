# One-Shot Deck Prompt

Create a polished PowerPoint presentation for an internal investment committee.

Topic: Global Macro ETF Country Ranking Model.

Audience: investment professionals evaluating country ETF allocation opportunities.

Tone: analytical, concise, committee-ready. Do not use marketing language. Do not overstate predictive power.

Use only these source files:

- `strategy_output.csv`
- `audit_master_data.csv`
- `ppt_chart_data.xlsx`
- `DATA_DICTIONARY.md`
- `PRESENTATION_GUIDE.md`

Do not use files inside `_previous_ai_attempt/`.

Core framing:

This is a 5-component ranking model. The final score is a weighted average of component ranks, where lower is better.

Components and weights:

- Macro Gap: 20%
- Currency Score: 20%
- Valuation Rank: 20%
- Narrative Rank: 30%
- Mcap Liquidity: 10%

Required deck:

1. Executive Summary
2. Investment Problem
3. Methodology Overview
4. Component 1 - Macro Gap
5. Component 2 - Currency Score
6. Component 3 - Valuation Rank
7. Component 4 - Narrative Rank
8. Component 5 - Mcap Liquidity
9. Final Ranking
10. Regional View
11. Sensitivity And YTD Diagnostic
12. Oil Price Sensitivity
13. Data Coverage And Caveats
14. Operating Process
15. Appendix - Data Dictionary

Design requirements:

- Use clean institutional styling: white or very light background, restrained color palette, strong tables, and readable charts.
- Use charts and tables from `ppt_chart_data.xlsx` wherever possible.
- Show percentages as multiplied by 100 with `%` labels. For example, `YTD_Return = 0.12` should display as `12.0%`.
- Use `Final_Rank` and `Final_Score` consistently: lower final score and lower final rank are better.
- For oil sensitivity, display `Oil_GDP_Impact_Pct` as a percentage and exclude or clearly flag rows where `Oil_Data_Excluded = TRUE`.
- For the YTD diagnostic slide, do not claim the model is proven predictive. Say the current snapshot shows weak final-rank/YTD correlation and should be monitored/backtested.

Key facts from current export:

- 36 of 38 configured countries entered the final ranking.
- Current top five: Indonesia, Brazil, India, Hong Kong, Chile.
- Current top-ranked country: Indonesia.
- The current export uses a 10-year horizon and a $10 oil price shock.

Deliver a complete slide-by-slide deck with:

- Slide title
- Main message
- Visual
- 2-4 concise speaker bullets
- Any chart formatting instructions needed to make the data readable
