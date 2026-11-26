"""Vivaan Logistics - Shipment Performance Analytics Dashboard.

Adapted from the Delhivery Logistics Analysis Dashboard by Ratnesh Singh (MIT).
Run:  streamlit run app.py
"""
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))
from data_prep import load_and_clean  # noqa: E402

DATA_DIR = Path(__file__).parent / "data"
DATA = sorted((DATA_DIR / "parts").glob("shipments_part*.csv"))
ZONES = ["Local NCR", "North Zone", "Metro / Rest of India"]
SERVICES = ["Standard", "Express", "Same Day", "Surface Cargo"]
DOW = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

st.set_page_config(page_title="Vivaan Logistics Dashboard", page_icon=":truck:", layout="wide")


@st.cache_data
def load(file):
    return load_and_clean(file)


def pct(x):
    return f"{x:.1f} %"


def kpis(d):
    n = len(d)
    return {
        "Total shipments": f"{n:,}",
        "Revenue (INR)": f"{d.cost_inr.sum():,.0f}",
        "On-time delivery": pct(100 * (1 - d.delayed.mean())),
        "Average cost per shipment (INR)": f"{d.cost_inr.mean():.1f}",
        "RTO rate": pct(100 * (d.status == "RTO").mean()),
        "Lost or damaged rate": pct(100 * (d.status == "Lost/Damaged").mean()),
        "Average parcel weight (kg)": f"{d.weight_kg.mean():.2f}",
        "Share of COD shipments": pct(100 * d.cod.mean()),
    }


# ------------------------------------------------------------------ sidebar
st.sidebar.title("Vivaan Logistics")
st.sidebar.caption("Shipment Performance Analytics")
upload = st.sidebar.file_uploader("Use your own shipment CSV (optional)", type="csv")
df = load(upload if upload is not None else DATA)

st.sidebar.markdown("### Filters")
months = sorted(df.month.unique())
f_month = st.sidebar.multiselect("Month", months, default=months)
f_zone = st.sidebar.multiselect("Zone", ZONES, default=ZONES)
f_serv = st.sidebar.multiselect("Service", SERVICES, default=SERVICES)
d = df[df.month.isin(f_month) & df.zone.isin(f_zone) & df.service.isin(f_serv)]

page = st.sidebar.radio("Section", [
    "1. Overview", "2. Volume and revenue", "3. Delivery performance", "4. Zones and cities",
    "5. Delay analysis", "6. Booking pattern", "7. Cost and weight", "8. Data explorer"])
st.sidebar.caption("Data is a synthetic sample prepared for the internship project.")

st.title("Shipment Performance Analytics Dashboard")
st.caption("Vivaan Logistics, Ghaziabad  |  Bookings from January to May 2026")
if d.empty:
    st.warning("No shipments match the filters.")
    st.stop()

# ------------------------------------------------------------------ pages
if page.startswith("1"):
    st.subheader("Headline KPIs")
    items = list(kpis(d).items())
    for row in (items[:4], items[4:]):
        cols = st.columns(4)
        for c, (k, v) in zip(cols, row):
            c.metric(k, v)
    late = int(d.delayed.sum())
    st.info(f"{late:,} of {len(d):,} shipments were delivered later than promised. "
            "The long-distance zone and address problems are the biggest causes (see sections 4 and 5).")
    m = d.groupby("month").agg(Shipments=("awb", "count"), Revenue=("cost_inr", "sum")).reset_index()
    fig = go.Figure()
    fig.add_bar(x=m.month, y=m.Shipments, name="Shipments")
    fig.add_scatter(x=m.month, y=m.Revenue, name="Revenue (INR)", yaxis="y2", mode="lines+markers")
    fig.update_layout(yaxis2=dict(overlaying="y", side="right"), height=380, legend=dict(orientation="h"))
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, width="stretch")

elif page.startswith("2"):
    st.subheader("Shipment volume and revenue by month")
    t = d.groupby("month").agg(Shipments=("awb", "count"), Revenue_INR=("cost_inr", "sum"),
                               On_time_pct=("delayed", lambda s: 100 * (1 - s.mean())),
                               RTO_pct=("status", lambda s: 100 * (s == "RTO").mean())).round(2).reset_index()
    fig = go.Figure()
    fig.add_bar(x=t.month, y=t.Shipments, name="Shipments")
    fig.add_scatter(x=t.month, y=t.Revenue_INR, name="Revenue (INR)", yaxis="y2", mode="lines+markers")
    fig.update_layout(yaxis2=dict(overlaying="y", side="right"), height=420, legend=dict(orientation="h"))
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, width="stretch")
    st.markdown("**Monthly summary**")
    st.dataframe(t, width="stretch", hide_index=True)

elif page.startswith("3"):
    st.subheader("Shipment outcome and on-time delivery")
    c1, c2 = st.columns(2)
    out = d.status.value_counts().reset_index()
    c1.plotly_chart(px.pie(out, names="status", values="count", hole=0.5, title="Shipment outcome"),
                    width="stretch")
    s = d.groupby("service").agg(Shipments=("awb", "count"),
                                 On_time_pct=("delayed", lambda x: 100 * (1 - x.mean())),
                                 Avg_cost_INR=("cost_inr", "mean"), Avg_weight_kg=("weight_kg", "mean")).round(2)
    s = s.reindex([x for x in SERVICES if x in s.index]).reset_index()
    c2.plotly_chart(px.bar(s, x="service", y="On_time_pct", title="On-time % by service", text="On_time_pct",
                           range_y=[70, 100]), width="stretch")
    st.markdown("**Performance by service type**")
    st.dataframe(s, width="stretch", hide_index=True)

elif page.startswith("4"):
    st.subheader("Zone-wise analysis")
    z = d.groupby("zone").agg(Shipments=("awb", "count"), On_time_pct=("delayed", lambda x: 100 * (1 - x.mean())),
                              Avg_cost_INR=("cost_inr", "mean"), Avg_days=("actual_days", "mean")).round(2)
    z = z.reindex([x for x in ZONES if x in z.index]).reset_index()
    fig = go.Figure()
    fig.add_bar(x=z.zone, y=z.Avg_days, name="Average delivery days")
    fig.add_scatter(x=z.zone, y=z.On_time_pct, name="On-time %", yaxis="y2", mode="lines+markers")
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[60, 100]), height=400,
                      legend=dict(orientation="h"))
    st.plotly_chart(fig, width="stretch")
    st.dataframe(z, width="stretch", hide_index=True)
    st.subheader("Top 10 destination cities")
    c = d.groupby("city").agg(Shipments=("awb", "count"), On_time_pct=("delayed", lambda x: 100 * (1 - x.mean())),
                              Avg_days=("actual_days", "mean"), Avg_cost_INR=("cost_inr", "mean"))
    c = c.sort_values("Shipments", ascending=False).head(10).round(2).reset_index()
    st.plotly_chart(px.bar(c, x="Shipments", y="city", orientation="h", text="Shipments").update_yaxes(
        autorange="reversed"), width="stretch")
    st.dataframe(c, width="stretch", hide_index=True)

elif page.startswith("5"):
    st.subheader("Delay reasons (Pareto)")
    late = d[d.delayed & (d.delay_reason != "")]
    if late.empty:
        st.info("No delayed shipments in this selection.")
    else:
        r = late.delay_reason.value_counts().reset_index()
        r.columns = ["Reason", "Delayed shipments"]
        r["Share %"] = (100 * r["Delayed shipments"] / r["Delayed shipments"].sum()).round(1)
        r["Cumulative %"] = r["Share %"].cumsum().round(1)
        fig = go.Figure()
        fig.add_bar(x=r.Reason, y=r["Delayed shipments"], name="Delayed shipments")
        fig.add_scatter(x=r.Reason, y=r["Cumulative %"], name="Cumulative %", yaxis="y2", mode="lines+markers")
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105]), height=420,
                          legend=dict(orientation="h"))
        st.plotly_chart(fig, width="stretch")
        st.dataframe(r, width="stretch", hide_index=True)
        st.caption("Address and customer-availability problems come from the receiver side, so they can be "
                   "reduced by checking the address at booking and by sending a delivery time window.")

elif page.startswith("6"):
    st.subheader("Bookings by weekday and hour")
    h = d.pivot_table(index="dow", columns="hour", values="awb", aggfunc="count", fill_value=0)
    h = h.reindex([x for x in DOW if x in h.index])
    st.plotly_chart(px.imshow(h, aspect="auto", color_continuous_scale="Blues",
                              labels=dict(x="Hour of booking", y="Weekday", color="Bookings")),
                    width="stretch")
    busiest = d.hour.value_counts().idxmax()
    st.info(f"Busiest hour: {busiest}:00. Busiest weekday: {d.dow.value_counts().idxmax()}.")
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.histogram(d, x="actual_days", nbins=12, title="Distribution of delivery days"),
                    width="stretch")
    c2.plotly_chart(px.histogram(d, x="weight_kg", nbins=40, title="Distribution of parcel weight (kg)"),
                    width="stretch")

elif page.startswith("7"):
    st.subheader("Shipping cost versus parcel weight")
    sample = d.sample(min(len(d), 3000), random_state=1)
    st.plotly_chart(px.scatter(sample, x="weight_kg", y="cost_inr", color="service", opacity=0.6,
                               labels={"weight_kg": "Weight (kg)", "cost_inr": "Cost (INR)"}),
                    width="stretch")
    corr = d[["weight_kg", "cost_inr", "promised_days", "actual_days", "hour"]].corr().round(2)
    st.plotly_chart(px.imshow(corr, text_auto=True, color_continuous_scale="RdBu", zmin=-1, zmax=1,
                              title="Correlation of numeric variables"), width="stretch")

else:
    st.subheader("Data explorer")
    st.write(f"{len(d):,} shipments match the filters.")
    st.dataframe(d.head(1000), width="stretch", hide_index=True)
    st.download_button("Download filtered data (CSV)", d.to_csv(index=False).encode(), "vivaan_filtered.csv")
