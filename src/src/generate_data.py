"""Generate the sample shipment dataset used by the Vivaan Logistics dashboard.

The data is synthetic. It is built so that the headline figures match the
internship report (9,678 shipments, January to May 2026, 88.3 % on time, and
so on). No real customer data is used.

Run:  python src/generate_data.py
"""
import numpy as np
import pandas as pd
from pathlib import Path

SEED = 2026
rng = np.random.default_rng(SEED)

MONTHS = {"2026-01": (1607, 167569), "2026-02": (1664, 170065), "2026-03": (1998, 213394),
          "2026-04": (2121, 218288), "2026-05": (2288, 236473)}
CITIES = {  # city: (zone, shipments)
    "Delhi": ("Local NCR", 1634), "Ghaziabad": ("Local NCR", 1234), "Noida": ("Local NCR", 926),
    "Gurugram": ("Local NCR", 719), "Faridabad": ("Local NCR", 403),
    "Jaipur": ("North Zone", 581), "Lucknow": ("North Zone", 574), "Chandigarh": ("North Zone", 414),
    "Dehradun": ("North Zone", 190), "Agra": ("North Zone", 125),
    "Mumbai": ("Metro / Rest of India", 817), "Bengaluru": ("Metro / Rest of India", 584),
    "Hyderabad": ("Metro / Rest of India", 425), "Chennai": ("Metro / Rest of India", 380),
    "Pune": ("Metro / Rest of India", 342), "Kolkata": ("Metro / Rest of India", 330),
}
SERVICES = {"Standard": 4938, "Express": 2392, "Surface Cargo": 1422, "Same Day": 926}
SERVICE_MEAN_COST = {"Standard": 82.0, "Express": 138.5, "Surface Cargo": 53.8, "Same Day": 208.3}
ZONE_MEAN_COST = {"Local NCR": 70.1, "North Zone": 112.9, "Metro / Rest of India": 155.9}
DELAYED_BY_ZONE = {"Local NCR": 369, "North Zone": 207, "Metro / Rest of India": 557}   # total 1,133
SERVICE_DELAY_WEIGHT = {"Standard": 1.0, "Express": 1.0, "Same Day": 1.5, "Surface Cargo": 1.6}
DELAY_REASONS = {"Wrong / incomplete address": 269, "Customer unavailable": 258,
                 "Traffic / hub congestion": 227, "Hub sorting delay": 204,
                 "Weather": 102, "Vehicle breakdown": 73}
PROMISED = {"Local NCR": 2, "North Zone": 3, "Metro / Rest of India": 5}
P_LATE_BASE = {"Local NCR": 0.07, "North Zone": 0.55, "Metro / Rest of India": 0.39}  # share on the slower day
DELAYED_BY_MONTH = {"2026-01": 195, "2026-02": 195, "2026-03": 232, "2026-04": 250, "2026-05": 261}
DELAYED_BY_SERVICE = {"Standard": 547, "Express": 268, "Same Day": 121, "Surface Cargo": 197}
RTO_BY_MONTH = {"2026-01": 57, "2026-02": 51, "2026-03": 79, "2026-04": 81, "2026-05": 80}
N = 9678
N_RTO, N_LOST, N_COD = 348, 174, 3629


def exact_counts(mapping):
    return np.repeat(list(mapping.keys()), list(mapping.values()))


def build():
    assert sum(v[0] for v in MONTHS.values()) == N
    assert sum(v[1] for v in CITIES.values()) == N and sum(SERVICES.values()) == N
    month = exact_counts({m: v[0] for m, v in MONTHS.items()})
    city = exact_counts({c: v[1] for c, v in CITIES.items()})
    rng.shuffle(month); rng.shuffle(city)
    service = exact_counts(SERVICES); rng.shuffle(service)
    df = pd.DataFrame({"month": month, "city": city, "service": service})
    df["zone"] = df["city"].map({c: v[0] for c, v in CITIES.items()})

    # booking date: weekday pattern with a busier Saturday
    dates = []
    dow_w = np.array([1.0, 1.0, 1.0, 1.05, 1.1, 1.35, 0.55])  # Mon..Sun
    for m, grp in df.groupby("month"):
        days = pd.date_range(f"{m}-01", periods=pd.Period(m).days_in_month)
        w = dow_w[days.dayofweek]; w = w / w.sum()
        dates.append(pd.Series(rng.choice(days, size=len(grp), p=w), index=grp.index))
    df["booking_date"] = pd.concat(dates).sort_index()
    hours = np.arange(8, 22); hw = np.exp(-((hours - 13) ** 2) / (2 * 3.3 ** 2)); hw /= hw.sum()
    df["hour"] = rng.choice(hours, size=N, p=hw)

    # weight (right skewed, mean about 1.82 kg)
    w = rng.lognormal(mean=0.25, sigma=0.75, size=N)
    w = np.clip(w, 0.1, 25)
    df["weight_kg"] = np.round(w * 1.82 / w.mean(), 2).clip(0.1, 30)

    # status and COD (exact counts)
    status = np.array(["Delivered"] * N, dtype=object)
    for m, k in RTO_BY_MONTH.items():
        status[rng.choice(df.index[df.month == m].to_numpy(), size=k, replace=False)] = "RTO"
    free = np.flatnonzero(status == "Delivered")
    status[rng.choice(free, size=N_LOST, replace=False)] = "Lost/Damaged"
    df["status"] = status
    cod = np.zeros(N, dtype=bool); cod[rng.permutation(N)[:N_COD]] = True
    df["cod"] = cod

    # delayed shipments: exact count per zone, weighted by service
    delayed = np.zeros(N, dtype=bool)
    for z, k in DELAYED_BY_ZONE.items():
        ii = df.index[df.zone == z].to_numpy()
        p = df.loc[ii, "service"].map(SERVICE_DELAY_WEIGHT).to_numpy(); p = p / p.sum()
        delayed[rng.choice(ii, size=k, replace=False, p=p)] = True
    # move flags between rows of the same zone until month and service totals match the report
    mon = df["month"].to_numpy(); svc = df["service"].to_numpy(); zn = df["zone"].to_numpy()
    def err():
        em = sum(abs(int(((mon == m) & delayed).sum()) - k) for m, k in DELAYED_BY_MONTH.items())
        es = sum(abs(int(((svc == x) & delayed).sum()) - k) for x, k in DELAYED_BY_SERVICE.items())
        return em + es
    cur = err()
    for _ in range(60000):
        if cur == 0: break
        z = rng.choice(list(DELAYED_BY_ZONE))
        a = rng.choice(np.flatnonzero(delayed & (zn == z))); b = rng.choice(np.flatnonzero(~delayed & (zn == z)))
        delayed[a], delayed[b] = False, True
        new = err()
        if new <= cur: cur = new
        else: delayed[a], delayed[b] = True, False
    df["delayed"] = delayed
    reasons = np.repeat(list(DELAY_REASONS), list(DELAY_REASONS.values())); rng.shuffle(reasons)
    df["delay_reason"] = ""
    df.loc[df.delayed, "delay_reason"] = reasons

    # promised and actual days
    prom = df["zone"].map(PROMISED).to_numpy()
    base = np.where(rng.random(N) < df["zone"].map(P_LATE_BASE).to_numpy(), prom, prom - 1)
    base = np.where(df.zone == "Local NCR", np.where(rng.random(N) < 0.07, 2, 1), base)
    extra = rng.choice([1, 2, 3], size=N, p=[0.5, 0.3, 0.2])
    df["promised_days"] = prom
    df["actual_days"] = np.where(df.delayed, prom + extra, base).astype(int)

    # shipping cost: zone x service x weight, then fitted to the report totals
    raw = (df["zone"].map(ZONE_MEAN_COST) * df["service"].map(SERVICE_MEAN_COST)
           * (0.55 + 0.45 * df.weight_kg / df.weight_kg.mean()) * rng.normal(1, 0.06, N)).to_numpy()
    month_t = {m: v[1] for m, v in MONTHS.items()}
    total = sum(month_t.values())
    tz = {z: ZONE_MEAN_COST[z] * (df.zone == z).sum() for z in ZONE_MEAN_COST}
    sz = sum(tz.values()); tz = {z: v * total / sz for z, v in tz.items()}
    ts = {s: SERVICE_MEAN_COST[s] * n for s, n in SERVICES.items()}
    ss = sum(ts.values()); ts = {s: v * total / ss for s, v in ts.items()}
    for _ in range(60):
        for col, tgt in (("zone", tz), ("service", ts), ("month", month_t)):
            cur = pd.Series(raw).groupby(df[col].to_numpy()).sum()
            raw = raw * df[col].map({k: tgt[k] / cur[k] for k in tgt}).to_numpy()
    cost = np.round(raw, 2)
    cost = np.maximum(cost, 10.0)
    df["cost_inr"] = cost
    for m, t in month_t.items():   # make each month's revenue exact
        ii = df.index[df.month == m]
        diff = round(t - df.loc[ii, "cost_inr"].sum(), 2)
        df.loc[ii, "cost_inr"] = np.round(df.loc[ii, "cost_inr"] + diff / len(ii), 2)
        diff = round(t - df.loc[ii, "cost_inr"].sum(), 2)
        df.loc[ii[0], "cost_inr"] = round(df.loc[ii[0], "cost_inr"] + diff, 2)

    df = df.sort_values(["booking_date", "hour"]).reset_index(drop=True)
    df["awb"] = ["VL" + str(2026000000 + i * 7 + 1001) for i in range(N)]
    df["dow"] = df.booking_date.dt.day_name()
    df["booking_date"] = df.booking_date.dt.strftime("%Y-%m-%d")
    return df[["awb", "booking_date", "hour", "city", "zone", "service", "weight_kg", "promised_days",
               "actual_days", "status", "cost_inr", "cod", "delay_reason", "delayed", "month", "dow"]]


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "data" / "vivaan_shipments.csv"
    out.parent.mkdir(exist_ok=True)
    build().to_csv(out, index=False)
    print("wrote", out)
