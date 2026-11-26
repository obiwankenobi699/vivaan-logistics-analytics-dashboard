"""Loading and cleaning rules for the Vivaan Logistics shipment file (report section 4.7)."""
import pandas as pd


def load_and_clean(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df["booking_date"] = pd.to_datetime(df["booking_date"], errors="coerce")
    df = df.dropna(subset=["booking_date"]).drop_duplicates("awb")
    df["city"] = df["city"].str.strip().str.title()
    df = df[df["cost_inr"] > 0].copy()
    df["delayed"] = df["actual_days"] > df["promised_days"]
    df["month"] = df["booking_date"].dt.to_period("M").astype(str)
    df["dow"] = df["booking_date"].dt.day_name()
    df["delay_reason"] = df["delay_reason"].fillna("")
    return df.reset_index(drop=True)
