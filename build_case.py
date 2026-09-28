#!/usr/bin/env python3
"""Generate a reproducible synthetic transportation profitability case study."""

from __future__ import annotations

import csv
import math
import random
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "synthetic_shipments.csv"
OUT = ROOT / "outputs"
TARGET_MARGIN = 0.18
SEED = 20260927

LANES = {
    "Detroit-Chicago": (275, 2.08, 1.00),
    "Detroit-Cleveland": (170, 2.23, 1.08),
    "Detroit-Atlanta": (720, 1.91, 0.98),
    "Detroit-Toronto": (235, 2.35, 1.11),
    "Detroit-Nashville": (535, 1.98, 1.03),
    "Detroit-Indianapolis": (285, 2.02, 0.97),
}

FIELDS = [
    "shipment_id", "ship_date", "lane", "mode", "distance_miles", "weight_lb",
    "stops", "revenue_usd", "fuel_cost_usd", "driver_cost_usd",
    "maintenance_cost_usd", "tolls_usd", "accessorial_cost_usd", "on_time",
    "service_exception",
]


def money(value: float) -> float:
    return round(value, 2)


def generate() -> None:
    rng = random.Random(SEED)
    DATA.parent.mkdir(parents=True, exist_ok=True)
    with DATA.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        lane_names = list(LANES)
        for i in range(1, 1201):
            lane = lane_names[(i - 1) % len(lane_names)]
            base_miles, base_rate, complexity = LANES[lane]
            distance = max(60, int(rng.gauss(base_miles, base_miles * 0.10)))
            weight = int(rng.uniform(1800, 38500))
            stops = rng.choices([1, 2, 3], weights=[0.68, 0.25, 0.07])[0]
            mode = rng.choices(["Dry van", "Refrigerated"], weights=[0.79, 0.21])[0]
            mode_factor = 1.0 if mode == "Dry van" else 1.17
            revenue = distance * base_rate * mode_factor * (weight / 18000) ** 0.055
            revenue += 38 * max(0, stops - 1)
            revenue *= rng.uniform(0.92, 1.09)
            fuel = distance * rng.uniform(0.57, 0.70) * complexity
            driver = (70 + distance * rng.uniform(0.46, 0.56)) * complexity
            maintenance = distance * rng.uniform(0.12, 0.18) * complexity
            tolls = distance * rng.uniform(0.015, 0.065) * complexity
            accessorial = 14 * max(0, stops - 1) + (rng.uniform(45, 115) if rng.random() < 0.10 else 0)
            exception = rng.random() < (0.055 + 0.012 * (stops - 1))
            on_time = rng.random() < (0.935 - 0.055 * exception - 0.018 * (stops - 1))
            if exception:
                accessorial += rng.uniform(25, 95)
            writer.writerow({
                "shipment_id": f"S{i:05d}",
                "ship_date": f"2026-{((i - 1) % 12) + 1:02d}-{((i * 7 - 1) % 28) + 1:02d}",
                "lane": lane,
                "mode": mode,
                "distance_miles": distance,
                "weight_lb": weight,
                "stops": stops,
                "revenue_usd": money(revenue),
                "fuel_cost_usd": money(fuel),
                "driver_cost_usd": money(driver),
                "maintenance_cost_usd": money(maintenance),
                "tolls_usd": money(tolls),
                "accessorial_cost_usd": money(accessorial),
                "on_time": int(on_time),
                "service_exception": int(exception),
            })


def read_rows() -> list[dict]:
    with DATA.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key in FIELDS[4:13]:
            row[key] = float(row[key])
        row["on_time"] = int(row["on_time"])
        row["service_exception"] = int(row["service_exception"])
        row["direct_cost_usd"] = sum(row[k] for k in (
            "fuel_cost_usd", "driver_cost_usd", "maintenance_cost_usd", "tolls_usd", "accessorial_cost_usd"
        ))
        row["contribution_usd"] = row["revenue_usd"] - row["direct_cost_usd"]
        row["contribution_margin"] = row["contribution_usd"] / row["revenue_usd"]
    return rows


def bootstrap_mean_ci(values: list[float], rng: random.Random, draws: int = 1000) -> tuple[float, float]:
    if len(values) < 2:
        return (float("nan"), float("nan"))
    n = len(values)
    means = []
    for _ in range(draws):
        means.append(sum(values[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    return means[int(0.025 * draws)], means[min(draws - 1, int(0.975 * draws))]


def analyze() -> None:
    rows = read_rows()
    rng = random.Random(SEED + 1)
    OUT.mkdir(exist_ok=True)
    total_revenue = sum(r["revenue_usd"] for r in rows)
    total_cost = sum(r["direct_cost_usd"] for r in rows)
    total_contribution = total_revenue - total_cost
    overall_margin = total_contribution / total_revenue

    by_lane: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_lane[row["lane"]].append(row)

    lane_rows = []
    for lane, group in by_lane.items():
        rev = sum(r["revenue_usd"] for r in group)
        cost = sum(r["direct_cost_usd"] for r in group)
        contribution = rev - cost
        margins = [r["contribution_margin"] for r in group]
        low, high = bootstrap_mean_ci(margins, rng)
        needed_revenue = cost / (1 - TARGET_MARGIN)
        lane_rows.append({
            "lane": lane,
            "shipments": len(group),
            "revenue_usd": money(rev),
            "direct_cost_usd": money(cost),
            "contribution_usd": money(contribution),
            "contribution_margin": round(contribution / rev, 4),
            "margin_mean_bootstrap_ci_low": round(low, 4),
            "margin_mean_bootstrap_ci_high": round(high, 4),
            "on_time_rate": round(sum(r["on_time"] for r in group) / len(group), 4),
            "exception_rate": round(sum(r["service_exception"] for r in group) / len(group), 4),
            "revenue_uplift_to_target_margin": round(max(0, needed_revenue / rev - 1), 4),
        })
    lane_rows.sort(key=lambda x: x["contribution_margin"])
    with (OUT / "lane_scorecard.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(lane_rows[0]))
        writer.writeheader()
        writer.writerows(lane_rows)

    with (OUT / "executive_summary.txt").open("w", encoding="utf-8") as f:
        f.write("SYNTHETIC TRANSPORTATION PROFITABILITY CASE\n")
        f.write("All values are simulated and are not employer results.\n\n")
        f.write(f"Shipments: {len(rows):,}\n")
        f.write(f"Modeled revenue: ${total_revenue:,.0f}\n")
        f.write(f"Modeled direct cost: ${total_cost:,.0f}\n")
        f.write(f"Modeled contribution: ${total_contribution:,.0f}\n")
        f.write(f"Weighted contribution margin: {overall_margin:.1%}\n")
        f.write(f"On-time rate: {sum(r['on_time'] for r in rows) / len(rows):.1%}\n")
        f.write(f"Service-exception rate: {sum(r['service_exception'] for r in rows) / len(rows):.1%}\n")
        f.write(f"Target margin scenario: {TARGET_MARGIN:.0%}\n\n")
        f.write("Lane scorecard sorted from lowest to highest contribution margin:\n")
        for lane in lane_rows:
            f.write(
                f"- {lane['lane']}: margin {lane['contribution_margin']:.1%}; "
                f"on-time {lane['on_time_rate']:.1%}; "
                f"illustrative revenue uplift to target margin {lane['revenue_uplift_to_target_margin']:.1%}\n"
            )

    print((OUT / "executive_summary.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    generate()
    analyze()
