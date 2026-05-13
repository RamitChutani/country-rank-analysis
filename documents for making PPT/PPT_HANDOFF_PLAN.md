# PPT Handoff Plan

Goal: produce a one-shot AI-ready package for an internal investment committee deck. The package should contain a corrected presentation guide plus clean supporting data files generated from the current Streamlit model, not from stale Excel exports.

## Current Clean Baseline

- Legacy PPT attempt files have been moved to `_previous_ai_attempt/`.
- Old Excel model files have been moved to `data/reference_workbooks/` and `data/reference_exports/`.
- Runtime static inputs now live in `data/static/`.
- The current ranking logic lives in `app.py`.

## Important Model Framing

Use a 5-component ranking model:

1. Macro Gap
2. Currency Score
3. Valuation Rank
4. Narrative Rank
5. Mcap Liquidity

## Required Handoff Files To Create

1. `strategy_output.csv`
   - One row per ranked country.
   - Must include final rank, country, region, final score, all component ranks, macro gap, currency score, YTD ETF return, and data completeness flags if relevant.

2. `audit_master_data.csv`
   - One row per configured country.
   - Must include raw/intermediate fields used to explain GDP CAGR, ETF CAGR, REER upside, bond differential, valuation input, narrative input, mcap, oil import values, and oil GDP impact.

3. `ppt_chart_data.xlsx`
   - Optional but useful for presentation software.
   - Separate tabs for top 10 rankings, macro gap, currency score, oil impact, weight sensitivity, and data coverage.

4. `PRESENTATION_GUIDE.md`
   - Slide-by-slide instructions for the AI presentation generator.
   - Must reference only the clean files above.
   - Must include exact chart/table specs and speaker-message bullets.

5. `AI_PROMPT_FOR_DECK.md`
   - A single paste-ready prompt telling the AI designer what deck to create, audience, tone, data files, charts, and constraints.

## Suggested Deck Structure

1. Executive summary and top-ranked markets
2. Why this model exists: country ETF selection problem
3. Methodology: data sources and ranking flow
4. Macro Gap: GDP growth versus ETF return
5. Currency Score: REER mean reversion plus bond yield support
6. Research Overlay: valuation and narrative ranks
7. Mcap Liquidity: investability and implementation sanity check
8. Final ranking table and regional grouping
9. Weight sensitivity and YTD performance comparison
10. Oil price sensitivity: GDP impact by importer
11. Limitations, caveats, and update process
12. Appendix: data dictionary and source notes

## Work Sequence

1. Build a real export script from the current app logic.
2. Generate the clean CSV/XLSX handoff files.
3. Validate exported columns against the slide guide.
4. Write the corrected `PRESENTATION_GUIDE.md`.
5. Write the one-shot `AI_PROMPT_FOR_DECK.md`.
6. Optionally run the deck prompt through the target AI and iterate once based on output quality.

## Known Cautions

- Do not use files in `_previous_ai_attempt/` as source of truth.
- Do not claim predictive validation unless the exported rank-versus-YTD relationship is actually calculated and shown.
- Be careful with oil impact formatting: `GDP_Impact_Pct` is a fraction and should be multiplied by 100 for percentage display.
- Thailand oil-import data should be flagged or excluded from oil sensitivity if it fails the sanity check.
