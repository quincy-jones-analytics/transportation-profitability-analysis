# Power BI Build Guide

## Purpose

Create an executive report that connects lane contribution, budget variance, service reliability, and shipment exceptions. One report page should answer one management question.

## Data model

1. Import the `data/synthetic_shipments.csv` file or the `Shipments` table from a Power BI-ready workbook.
2. Set `ship_date` to Date, currency fields to Fixed decimal/Currency, and `on_time_flag` to Whole number.
3. Create the Calendar table below, mark it as the date table, and relate `Calendar[Date]` one-to-many to `Shipments[ship_date]`.
4. Keep the fact grain at one row per shipment. Do not sum percentages; calculate them from the underlying numerators and denominators.
5. Add the measures from [measures.dax](measures.dax).

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

Sort `Calendar[Month]` by `Calendar[Month Number]`. Use `Calendar[Year Month]` as the month slicer.

## Page 1 — Executive Overview

- KPI cards: Total Revenue, Gross Profit, Gross Margin %, On-Time %, Cost per Mile
- Monthly revenue and gross profit trend
- Ranked lane gross profit bars
- Budget-to-actual gross profit bridge
- Recommendation panel with the current top review candidate

**Decision:** Is the operating portfolio financially and operationally healthy, and where should leaders focus first?

## Page 2 — Plan and Variance

- Matrix by month for actual revenue, budget revenue, variance, actual cost, budget cost, and favorable cost variance
- Profit variance waterfall
- Cost trend by fuel, labor, maintenance, accessorial, and overhead

**Decision:** Which periods or cost categories explain the variance?

## Page 3 — Lane Economics

- Scatterplot: revenue per mile vs. cost per mile; size by shipment count; color by gross margin
- Ranked lane table with margin, cost per mile, and on-time rate
- Bar chart of modeled revenue change required to reach a 20% margin floor
- Shipment detail drill-through

**Decision:** Which lanes merit review of pricing, service design, or cost assumptions?

## Page 4 — Service and Exceptions

- On-Time %, Exception Rate, and Exception Shipments cards
- On-time rate by carrier
- Exception type by shipment count and average gross profit
- Monthly on-time performance alongside gross margin

**Decision:** Which service failures carry the largest modeled financial impact?

## Slicers and presentation

Use year-month, region, lane, customer, carrier, and mode slicers. Keep each page to one decision and 5–7 visuals. Use a navy/teal/amber palette, reserving red for unfavorable variances. Add a visible **Synthetic portfolio data** notice. Export one 16:9 screenshot per report page after building.

## Limitations

All data are synthetic. A static-cost pricing floor is a review trigger, not a recommended customer rate. Validate demand, contract terms, competitor context, capacity, cost allocation, and customer impact before a real pricing decision.
