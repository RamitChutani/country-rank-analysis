# Data Dictionary

Use these files as the source of truth for the deck:

- `strategy_output.csv`: ranked countries only.
- `audit_master_data.csv`: all configured countries, including countries excluded from final ranking.
- `ppt_chart_data.xlsx`: chart-ready tabs derived from the two CSVs.

## strategy_output.csv

- `Final_Rank`: model rank; 1 is most attractive.
- `Country`: country name.
- `Region`: model region bucket.
- `ETF_Ticker`: ETF proxy used for market performance.
- `Final_Score`: weighted average of component ranks; lower is better.
- `Macro_Gap`: `GDP_CAGR_10Y - ETF_CAGR_10Y`.
- `Macro_Gap_Rank`: rank of Macro Gap; higher Macro Gap is better.
- `Currency_Score`: average of REER rank and bond rank; lower is better.
- `Currency_Rank`: rank of Currency Score; lower is better.
- `REER_Rank`: REER upside rank; higher upside is better.
- `Bond_Rank`: 10Y bond differential rank; higher differential versus US is better.
- `Valuation_Rank`: valuation rank; lower valuation input rank is better.
- `Narrative_Rank`: qualitative narrative rank; lower narrative input rank is better.
- `Mcap_Rank`: market-cap rank; larger market cap is better.
- `YTD_Return`: ETF YTD return as a fraction; multiply by 100 for display.
- `GDP_CAGR_10Y`: 10-year GDP CAGR as a fraction.
- `ETF_CAGR_10Y`: 10-year ETF price CAGR as a fraction.
- `REER_Upside`: estimated REER mean-reversion upside as a fraction.
- `differential with USA`: 10Y government bond yield differential versus US.
- `Average Rank`: raw valuation input rank.
- `Rank`: raw narrative input rank.
- `Mcap_USD_Bn`: market capitalization in USD billions.

## audit_master_data.csv

Includes all raw/intermediate fields from `strategy_output.csv` plus:

- `GDP_2015` to `GDP_2025`: annual nominal GDP observations.
- `GDP_CAGR_1Y`, `GDP_CAGR_3Y`, `GDP_CAGR_5Y`, `GDP_CAGR_10Y`: GDP CAGRs.
- `P_Now`, `P_1Y`, `P_3Y`, `P_5Y`, `P_10Y`: ETF price anchors.
- `ETF_CAGR_1Y`, `ETF_CAGR_3Y`, `ETF_CAGR_5Y`, `ETF_CAGR_10Y`: ETF CAGRs.
- `Current_REER`, `Avg_REER_10Y`, `REER_Upside`: currency valuation inputs.
- `Crude (kg)`, `Crude (mb/d)`: 2024 crude oil import data.
- `Oil_Scenario_USD`: oil price move assumed in the export.
- `Oil_Annual_Impact_USD_Bn`: annualized crude import cost impact.
- `Oil_GDP_Impact_Pct`: oil impact as a fraction of 2025 GDP; multiply by 100 for display.
- `Oil_Data_Excluded`: flags oil outliers excluded from interpretation.
- `Has_*`: data completeness flags for final ranking inputs.
- `Ranked`: whether the country entered the final ranking.

## ppt_chart_data.xlsx

- `top_10_rankings`: compact top-10 ranking table.
- `macro_gap`: countries sorted by Macro Gap.
- `currency_score`: countries sorted by Currency Rank.
- `oil_impact`: oil-sensitivity data sorted by GDP impact.
- `data_coverage`: available-country counts by required field.
- `rank_ytd_correlation`: diagnostic correlation values.
