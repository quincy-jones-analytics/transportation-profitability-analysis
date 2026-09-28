# Transportation Profitability & Service Reliability

## Executive brief

**Decision question:** Which transportation lanes merit a closer look at pricing, cost-to-serve, or service recovery?

This reproducible case study analyzes 1,200 simulated shipments across six lanes. It brings revenue and direct operating costs together with on-time performance and exception rates, then identifies where leaders could investigate trade-offs. The example is built to show how an operations question can be translated into a concise, auditable decision view.

> **Data integrity:** Every shipment and financial amount is synthetic. Results are illustrative portfolio outputs, not employer data, actual business performance, or realized savings.

## Demonstration snapshot

| Measure | Synthetic result |
|---|---:|
| Shipments | 1,200 |
| Revenue | $958,707 |
| Direct cost | $710,290 |
| Contribution | $248,417 |
| Weighted contribution margin | 25.9% |
| On-time rate | 91.6% |
| Service-exception rate | 6.0% |

The Detroit–Cleveland lane has the lowest modeled contribution margin at 17.6%, just below the scenario's 18% target. Holding cost and shipment mix constant, the model estimates a 0.5% revenue increase would bring that lane to the target. This is a starting point for review; actual pricing action would require contract terms, customer value, capacity, competitive rates, and demand response.

## What the analysis does

1. Generates a deterministic synthetic shipment dataset with a fixed random seed.
2. Calculates contribution, weighted margin, service rates, and lane-level scorecards.
3. Uses a bootstrap interval to show uncertainty around each lane's mean shipment margin.
4. Estimates the revenue change associated with an 18% margin scenario while holding modeled costs fixed.
5. Publishes the same core scorecards as portable CSV outputs and SQLite-ready SQL.

## Key files

- `build_case.py` — data generation, metric calculations, bootstrap intervals, and output creation.
- `data/synthetic_shipments.csv` — 1,200 simulated shipment records.
- `sql/analysis.sql` — SQLite queries for portfolio performance, lane economics, cost composition, and the target-margin scenario.
- `outputs/executive_summary.txt` — generated summary.
- `outputs/lane_scorecard.csv` — generated lane table with margin intervals and service measures.

## Reproduce

Requires Python 3.10 or newer; the analysis uses only the Python standard library.

```bash
python3 build_case.py
```

The script regenerates the CSV data and both outputs with the same seed (`20260927`). To use the SQL queries, import `data/synthetic_shipments.csv` into SQLite as a table named `shipments`, then run `sql/analysis.sql`.

## Metric definitions and limits

- **Direct cost** = fuel + driver + maintenance + tolls + accessorial costs in the synthetic file.
- **Contribution** = revenue − direct cost. This is a simplified measure; it excludes overhead, claims, empty miles, equipment utilization, and corporate allocations.
- **Weighted contribution margin** = total contribution ÷ total revenue.
- **Bootstrap interval** = 2.5th and 97.5th percentiles from 1,000 resamples of shipment-level margins, calculated separately for each lane. It describes simulated sampling variability and does not correct for omitted variables or model assumptions.
- **Target-margin scenario** = required revenue at unchanged costs and mix, calculated as direct cost ÷ (1 − target margin). It does not assume customer acceptance or estimate demand elasticity.

The generated patterns are deliberately illustrative. They should not be generalized to a real carrier or used for commercial pricing without validated cost, contract, service, and demand data.

## Leadership discussion

- Validate cost-to-serve and accessorial definitions before comparing lanes.
- Pair margin with on-time performance and customer context; don't optimize a single metric in isolation.
- Investigate whether the lowest-margin lane reflects pricing, shipment mix, stop density, or cost assumptions.
- Run a sensitivity review on fuel, labor, and customer rate assumptions before making a recommendation.

## Skills demonstrated

Transportation operations · SQL · Python · data validation · contribution margin · cost-to-serve · scenario analysis · bootstrap uncertainty · KPI design · executive communication
