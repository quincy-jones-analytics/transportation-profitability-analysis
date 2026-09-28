-- SQLite analysis for the synthetic transportation profitability case.
-- Import data/synthetic_shipments.csv into a table named shipments first.

-- 1. Portfolio-level operating and financial scorecard.
SELECT
    COUNT(*) AS shipment_count,
    ROUND(SUM(revenue_usd), 2) AS modeled_revenue_usd,
    ROUND(SUM(fuel_cost_usd + driver_cost_usd + maintenance_cost_usd
        + tolls_usd + accessorial_cost_usd), 2) AS modeled_direct_cost_usd,
    ROUND(SUM(revenue_usd - fuel_cost_usd - driver_cost_usd
        - maintenance_cost_usd - tolls_usd - accessorial_cost_usd), 2) AS contribution_usd,
    ROUND(1.0 * SUM(revenue_usd - fuel_cost_usd - driver_cost_usd
        - maintenance_cost_usd - tolls_usd - accessorial_cost_usd)
        / SUM(revenue_usd), 4) AS contribution_margin,
    ROUND(AVG(on_time), 4) AS on_time_rate,
    ROUND(AVG(service_exception), 4) AS service_exception_rate
FROM shipments;

-- 2. Lane scorecard: weighted contribution margin and service measures.
SELECT
    lane,
    COUNT(*) AS shipment_count,
    ROUND(SUM(revenue_usd), 2) AS revenue_usd,
    ROUND(SUM(fuel_cost_usd + driver_cost_usd + maintenance_cost_usd
        + tolls_usd + accessorial_cost_usd), 2) AS direct_cost_usd,
    ROUND(SUM(revenue_usd - fuel_cost_usd - driver_cost_usd
        - maintenance_cost_usd - tolls_usd - accessorial_cost_usd), 2) AS contribution_usd,
    ROUND(1.0 * SUM(revenue_usd - fuel_cost_usd - driver_cost_usd
        - maintenance_cost_usd - tolls_usd - accessorial_cost_usd)
        / SUM(revenue_usd), 4) AS contribution_margin,
    ROUND(AVG(on_time), 4) AS on_time_rate,
    ROUND(AVG(service_exception), 4) AS exception_rate
FROM shipments
GROUP BY lane
ORDER BY contribution_margin ASC;

-- 3. Cost composition by lane for cost-to-serve investigation.
SELECT
    lane,
    ROUND(AVG(fuel_cost_usd), 2) AS avg_fuel_cost_per_shipment,
    ROUND(AVG(driver_cost_usd), 2) AS avg_driver_cost_per_shipment,
    ROUND(AVG(maintenance_cost_usd), 2) AS avg_maintenance_cost_per_shipment,
    ROUND(AVG(tolls_usd), 2) AS avg_tolls_per_shipment,
    ROUND(AVG(accessorial_cost_usd), 2) AS avg_accessorial_cost_per_shipment
FROM shipments
GROUP BY lane
ORDER BY lane;

-- 4. Illustrative revenue change required for an 18% contribution margin,
-- holding modeled cost and shipment mix constant. This is a scenario only.
WITH lane_totals AS (
    SELECT lane,
        SUM(revenue_usd) AS revenue,
        SUM(fuel_cost_usd + driver_cost_usd + maintenance_cost_usd
            + tolls_usd + accessorial_cost_usd) AS direct_cost
    FROM shipments
    GROUP BY lane
)
SELECT lane,
    ROUND(100.0 * MAX(0.0, (direct_cost / (1.0 - 0.18) / revenue) - 1.0), 2)
        AS illustrative_revenue_uplift_pct_to_18_margin
FROM lane_totals
ORDER BY illustrative_revenue_uplift_pct_to_18_margin DESC;
