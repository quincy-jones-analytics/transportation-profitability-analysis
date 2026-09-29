# Power BI Build Guide

## Purpose

Build an executive report over the published 1,200-row synthetic shipment file. The source has one row per shipment and contains actualized demonstration fields only. It has no budget or plan columns, so this report does not claim budget-to-actual variance.

## Import and prepare the data

1. In Power BI Desktop, choose **Get data → Text/CSV** and import `data/synthetic_shipments.csv`.
2. Name the query/table `Shipments`.
3. Set `ship_date` to Date; currency fields to Fixed decimal number; `distance_miles`, `weight_lb`, and `stops` to Whole number; `on_time` and `service_exception` to Whole number.
4. Add `total_cost_usd` in Power Query with this custom column formula:

```powerquery
[fuel_cost_usd] + [driver_cost_usd] + [maintenance_cost_usd] + [tolls_usd] + [accessorial_cost_usd]
```

Set its type to Fixed decimal number. This is the sum of the five cost components present in the source file.
5. Create the Calendar table below, mark it as the date table, and relate `Calendar[Date]` one-to-many to `Shipments[ship_date]`.
6. Add the measures from [measures.dax](measures.dax).

```DAX
Calendar =
ADDCOLUMNS(
    CALENDAR(MIN(Shipments[ship_date]), MAX(Shipments[ship_date])),
    "Year", YEAR([Date]),
    "Month Number", MONTH([Date]),
    "Month", FORMAT([Date], "MMM"),
    "Year Month", FORMAT([Date], "YYYY-MM")
)
```

Sort `Calendar[Month]` by `Calendar[Month Number]`. Use `Calendar[Year Month]` as the month axis or slicer.

## Page 1 — Executive Overview

- KPI cards: Total Revenue, Gross Profit, Gross Margin %, On-Time %, Exception Rate
- Monthly revenue and gross profit trend
- Ranked lane gross profit bars
- Lane table with shipment count, gross margin, cost per mile, and on-time rate
- A short recommendation that identifies the lane for review, with the synthetic data notice visible

**Decision:** Where should leaders look first across lane economics and service?

## Page 2 — Lane Economics

- Scatterplot: revenue per mile vs. cost per mile; size by shipment count; color by gross margin
- Ranked lane table with revenue, total cost, gross profit, gross margin, cost per mile, and on-time rate
- Lane and mode slicers
- Drill-through to shipment rows

**Decision:** Which lanes warrant validation of pricing, cost-to-serve, or service design?

## Page 3 — Cost and Service

- Cost composition by fuel, driver, maintenance, tolls, and accessorials
- Cost per mile by lane and mode
- On-time rate and exception rate by lane and month
- Monthly trend of gross margin and on-time performance

**Decision:** Where do modeled cost and service patterns move together?

## Page 4 — Static-Cost Margin Scenario

- Add a disconnected `Margin Target` parameter table (for example, 10% to 30% in 1-point increments, default 18%).
- Display current revenue, cost, margin, required revenue at the selected target, and the gap to that level.
- Label the scenario **static-cost reference only**. It assumes cost and shipment mix do not change; it does not estimate demand response, contract outcomes, or a customer price.

**Decision:** What revenue level would mathematically correspond to the selected margin under a fixed-cost assumption?

## Slicers and presentation

Use year-month, lane, and mode slicers. Keep each page focused on one decision and 5–7 visuals. Use a navy/teal/amber palette, reserving red for unfavorable indicators. Add a visible **Synthetic portfolio data** notice.

## Limitations

All records and amounts are synthetic. The source has no budget, customer, carrier, region, or exception-category fields. Do not imply budget variance or attribute results to a real customer, employer, carrier, or realized savings. Validate cost allocation, demand, contract terms, capacity, service definitions, and customer impact before applying a real pricing decision.
