# Changelog

## 1.0.0 - 2026-11
- Forked from the Delhivery Logistics Analysis Dashboard by Ratnesh Singh (MIT) and adapted for Vivaan Logistics.
- New dashboard (`app.py`) for shipment performance: KPIs, monthly volume and revenue, service and zone performance, top cities, delay Pareto, booking heatmap, cost versus weight and a data explorer.
- New cleaning module `src/data_prep.py` that follows the report's cleaning rules.
- New synthetic dataset `data/vivaan_shipments.csv` (9,678 shipments, January to May 2026) and its generator `src/generate_data.py`.
- Removed the Delhivery trip dataset, notebooks, reports and route/OSRM analysis.
