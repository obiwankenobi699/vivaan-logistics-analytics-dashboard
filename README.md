# Vivaan Logistics - Shipment Performance Analytics Dashboard

An interactive Streamlit dashboard that turns a shipment file into the numbers an operations team looks at every day: volume, revenue, on-time delivery, RTO and lost parcels, performance by service, zone and city, the reasons for delay, and booking patterns.

It was built as the project for an industrial internship at **Vivaan Logistics** (courier, cargo and supply chain services, Ghaziabad, Delhi NCR) by **Riddhi** (B.Tech CSE, SGT University), supervised by **Mukul Mishra**, June 2026. The project report describes the same dataset, KPIs and charts that this dashboard shows.

> **Data note:** the six files in `data/parts/` together make up a synthetic sample made for this project. It contains no real customers or real shipments. You can load your own file with the same columns from the sidebar.

## Credit

This project is a fork of [Delhivery Logistics Analysis Dashboard](https://github.com/Ratnesh-181998/Delhivery-Logistics-Analysis-Dashboard) by Ratnesh Singh, released under the MIT License. The repository structure, Streamlit setup, theme and license come from that project. The dashboard, dataset, data preparation code and documentation were rewritten for Vivaan Logistics. The original MIT license and copyright notice are kept in [LICENSE](LICENSE).

## What the dashboard shows

| Section | Content |
|---|---|
| 1. Overview | Eight headline KPIs and the monthly volume and revenue chart |
| 2. Volume and revenue | Monthly summary table: shipments, revenue, on-time %, RTO % |
| 3. Delivery performance | Outcome donut (delivered, RTO, lost or damaged) and performance by service |
| 4. Zones and cities | Delivery days and on-time % by zone, top 10 destination cities |
| 5. Delay analysis | Pareto chart and table of delay reasons |
| 6. Booking pattern | Weekday by hour heatmap, delivery-day and weight distributions |
| 7. Cost and weight | Cost versus weight scatter by service and a correlation matrix |
| 8. Data explorer | Filtered table with CSV download |

Sidebar filters (month, zone, service) apply to every section.

### Headline results on the sample data

| KPI | Value |
|---|---|
| Total shipments | 9,678 |
| Revenue (INR) | 1,005,789 |
| On-time delivery | 88.3 % |
| Average cost per shipment (INR) | 103.9 |
| RTO rate | 3.6 % |
| Lost or damaged rate | 1.8 % |
| Average parcel weight (kg) | 1.82 |
| Share of COD shipments | 37.5 % |

## Dataset

15 columns, one row per shipment (identified by the airway bill number).

| Column | Type | Description |
|---|---|---|
| awb | Text | Unique airway bill number |
| booking_date | Date | Date of booking |
| hour | Integer | Hour of booking (8 to 21) |
| city | Text | Destination city |
| zone | Text | Local NCR, North Zone or Metro / Rest of India |
| service | Text | Standard, Express, Same Day or Surface Cargo |
| weight_kg | Decimal | Chargeable weight in kg |
| promised_days | Integer | Delivery time promised to the customer |
| actual_days | Integer | Actual days taken |
| status | Text | Delivered, RTO or Lost/Damaged |
| cost_inr | Decimal | Shipping charge in INR |
| cod | Boolean | Cash on delivery or not |
| delay_reason | Text | Recorded reason if the shipment was late |
| delayed | Boolean | Derived: actual days greater than promised days |
| month, dow | Text | Derived: month and weekday of booking |

Cleaning rules (`src/data_prep.py`): lower-case column names, parse the booking date and drop invalid dates, remove duplicate AWB numbers, standardise city names, drop rows with zero or negative cost, then create `delayed`, `month` and `dow`.

## Project structure

```
.
├── app.py                    Streamlit dashboard
├── data/parts/               Sample shipment data in six CSV parts (synthetic)
├── src/
│   ├── data_prep.py          Loading and cleaning
│   └── generate_data.py      Script that creates the sample data
├── requirements.txt
├── .streamlit/config.toml    Theme and server settings
├── DEPLOYMENT.md  CONTRIBUTING.md  CHANGELOG.md
└── LICENSE                   MIT (original author)
```

## Run it

```bash
git clone https://github.com/obiwankenobi699/vivaan-logistics-analytics-dashboard.git
cd Vivaan-Logistics-Analytics-Dashboard
pip install -r requirements.txt
streamlit run app.py
```

To rebuild the sample data: `python src/generate_data.py`. See [DEPLOYMENT.md](DEPLOYMENT.md) for Streamlit Cloud and Docker.

## Tech stack

Python 3, pandas, NumPy, Plotly, Streamlit.

## License

MIT. Copyright (c) 2025 Ratnesh Singh for the original project. See [LICENSE](LICENSE).
