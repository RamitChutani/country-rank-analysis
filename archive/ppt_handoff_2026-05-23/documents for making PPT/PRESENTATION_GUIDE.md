# Presentation Guide: Global Macro ETF Country Ranking

## Audience And Tone

Audience: internal investment committee.

Tone: analytical, investment-focused, concise. The deck should explain the model clearly, show the ranking output, and surface caveats without overstating predictive evidence.

## Source Files

Use only these current files:

- `strategy_output.csv`
- `audit_master_data.csv`
- `ppt_chart_data.xlsx`
- `DATA_DICTIONARY.md`

Do not use files inside `_previous_ai_attempt/`.

## Model Framing

This is a 5-component ranking model. The final score is a weighted average of component ranks, where a lower score is better.

Default weights:

| Component | Weight | Logic |
|---|---:|---|
| Macro Gap | 20% | GDP CAGR minus ETF CAGR |
| Currency Score | 20% | REER upside plus 10Y bond differential support |
| Valuation Rank | 20% | Fundamental valuation rank |
| Narrative Rank | 30% | Qualitative investment conviction |
| Mcap Liquidity | 10% | Market size and investability |

## Slide 1: Executive Summary

Message: The model ranks country ETF markets by combining macro underperformance, currency support, valuation, narrative conviction, and liquidity.

Use `ppt_chart_data.xlsx`, tab `top_10_rankings`.

Visual: top-5 table with `Final_Rank`, `Country`, `Region`, `Final_Score`, `Macro_Gap`, `Currency_Rank`, `Valuation_Rank`, `Narrative_Rank`, `Mcap_Rank`.

Speaker points:

- Indonesia ranks first in the current export, followed by Brazil, India, Hong Kong, and Chile.
- Lower final score means stronger composite attractiveness.
- The output is a ranking framework, not a standalone buy list.

## Slide 2: Investment Problem

Message: Country ETF selection needs a disciplined way to compare growth, market pricing, currency setup, research view, and investability across regions.

Visual: simple process flow:

`Country Universe -> Data Inputs -> 5 Component Ranks -> Weighted Final Score -> Ranked ETF Markets`

Speaker points:

- The dashboard creates a repeatable process for comparing country ETF opportunities.
- Each component captures a different investment question.
- The model is designed to be transparent and auditable.

## Slide 3: Methodology Overview

Message: The model ranks each component separately, then combines those ranks with explicit weights.

Use `strategy_output.csv`.

Visual: 5-component weighting bar or matrix.

Speaker points:

- Macro Gap, Currency, Valuation, Narrative, and Mcap are all rank-based.
- Final score equals weighted component ranks.
- Lower score is better because it indicates stronger aggregate rank positioning.

## Slide 4: Component 1 - Macro Gap

Message: Macro Gap identifies markets where GDP growth has outpaced ETF performance.

Use `ppt_chart_data.xlsx`, tab `macro_gap`.

Visual: horizontal bar chart of top 10 countries by `Macro_Gap`.

Speaker points:

- Formula: `GDP_CAGR_10Y - ETF_CAGR_10Y`.
- A positive gap means the economy grew faster than the ETF proxy.
- This can indicate market underperformance relative to macro growth, but it needs confirmation from other components.

## Slide 5: Component 2 - Currency Score

Message: Currency Score combines real exchange-rate mean reversion with yield support.

Use `ppt_chart_data.xlsx`, tab `currency_score`.

Visual: table or scatter using `REER_Upside` and `differential with USA`; label the best `Currency_Rank` countries.

Speaker points:

- REER upside measures whether a currency is below its 10-year average.
- Bond differential measures yield support versus the US.
- The model averages the two ranks into `Currency_Score`, then ranks that score.

## Slide 6: Component 3 - Valuation Rank

Message: Valuation adds fundamental discipline to the macro signal.

Use `strategy_output.csv`.

Visual: top 10 by `Valuation_Rank`, with `Average Rank` as supporting detail.

Speaker points:

- Lower valuation rank means more attractive valuation profile.
- This component prevents the model from relying only on macro growth or currency signals.
- It is a static research input and should be refreshed when valuation work is updated.

## Slide 7: Component 4 - Narrative Rank

Message: Narrative captures qualitative conviction that pure data may miss.

Use `strategy_output.csv`.

Visual: top 10 by `Narrative_Rank`.

Speaker points:

- Lower narrative rank reflects stronger qualitative conviction.
- This component incorporates policy, geopolitical, structural, and market-cycle views.
- It has the highest default weight at 30%, so committee review of this input matters.

## Slide 8: Component 5 - Mcap Liquidity

Message: Liquidity ensures that ranked opportunities are institutionally actionable.

Use `strategy_output.csv`.

Visual: bubble or bar chart using `Mcap_USD_Bn` and `Mcap_Rank`.

Speaker points:

- Larger market cap ranks better.
- This component acts as an implementation sanity check.
- It reduces the chance that attractive macro signals point to impractical markets.

## Slide 9: Final Ranking

Message: The final rank balances the five components rather than optimizing one metric.

Use `ppt_chart_data.xlsx`, tab `top_10_rankings`.

Visual: heatmap-style top-10 table with component ranks and `Final_Score`.

Speaker points:

- Indonesia leads because its Macro Gap, Currency, and Valuation ranks are all strong, despite weaker Narrative and Mcap ranks.
- Brazil ranks second because strong Currency, Valuation, and Narrative ranks offset a weaker Macro Gap rank.
- India scores well on Currency and Narrative but is held back by Valuation.

## Slide 10: Regional View

Message: The ranking is globally diversified but current top-ranked markets skew toward Latin America and South/Southeast Asia.

Use `strategy_output.csv`.

Visual: grouped bar or region summary table showing average `Final_Rank` and count by `Region`.

Speaker points:

- Regional grouping helps avoid treating the model as a single-country screen only.
- The committee can compare regional clusters against portfolio exposure limits.

## Slide 11: Sensitivity And YTD Diagnostic

Message: The current snapshot should be read as a ranking framework, not a proven short-term predictor.

Use `ppt_chart_data.xlsx`, tab `rank_ytd_correlation`.

Visual: small diagnostics table plus scatter of `Final_Rank` versus `YTD_Return`.

Speaker points:

- Current export shows weak positive correlation between final rank and YTD return.
- Macro Gap has a moderately negative relationship with YTD return in this snapshot.
- This is useful diagnostic feedback: the framework should be monitored and backtested before making predictive claims.

## Slide 12: Oil Price Sensitivity

Message: Oil sensitivity estimates which importers are most exposed to a crude price shock.

Use `ppt_chart_data.xlsx`, tab `oil_impact`.

Visual: bar chart of `Oil_GDP_Impact_Pct` multiplied by 100 for display. Exclude or separately flag rows where `Oil_Data_Excluded = TRUE`.

Speaker points:

- Formula: `(Crude mb/d * 1,000,000 * oil price move * 365) / GDP_2025`.
- Current export uses a $10 oil price move.
- Thailand is flagged as excluded due to a sanity-check issue in crude import data.

## Slide 13: Data Coverage And Caveats

Message: The model is transparent about what is included and excluded.

Use `ppt_chart_data.xlsx`, tab `data_coverage`, and `audit_master_data.csv`.

Visual: data coverage table.

Speaker points:

- 36 of 38 configured countries entered the current final ranking.
- Countries missing required fields are excluded from the final rank.
- Static inputs require a disciplined refresh process.

## Slide 14: Operating Process

Message: The dashboard supports repeatable committee updates.

Visual: refresh cadence table.

| Input | Source Type | Suggested Refresh |
|---|---|---|
| GDP | IMF API | WEO release cycle |
| ETF prices | Yahoo Finance | Daily / before committee |
| REER | BIS API | Monthly |
| Bond differential | Static curated input | Monthly or before committee |
| Valuation | Static research input | Quarterly |
| Narrative | Static research input | Committee cycle |
| Mcap | Static curated input | Quarterly / annual |
| Oil imports | Static workbook | Annual |

## Slide 15: Appendix - Data Dictionary

Message: Include the key formulas and field definitions.

Use `DATA_DICTIONARY.md`.

Visual: compact formula table.

Required formulas:

- `Macro_Gap = GDP_CAGR_10Y - ETF_CAGR_10Y`
- `Currency_Score = average(REER_Rank, Bond_Rank)`
- `Final_Score = weighted average of five component ranks`
- `Oil_GDP_Impact_Pct = Oil_Annual_Impact_USD_Bn / GDP_2025`
