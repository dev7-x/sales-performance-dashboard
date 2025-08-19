# src/anomaly_detector.py
import pandas as pd, os
import numpy as np

DATAPATH = os.path.join(os.path.dirname(__file__), "..", "data")
df = pd.read_csv(os.path.join(DATAPATH,"daily_metrics.csv"), parse_dates=["order_date"])
out_alerts = []

# For each sku-region, compute median and MAD and flag large drops
grouped = df.groupby(["sku_id","region"])
for (sku,region), g in grouped:
    # use last 30 days to compute baseline if available
    g = g.sort_values("order_date")
    if len(g) < 8:
        continue
    # baseline = median of rev_7d excluding last day
    baseline = g['rev_7d'].iloc[:-1]
    if baseline.sum() == 0:
        continue
    med = baseline.median()
    mad = np.median(np.abs(baseline - med)) if len(baseline) else 0
    latest = g.iloc[-1]
    # define anomaly if latest rev_7d < med - 3*MAD or percent drop > 0.5
    pct_drop = (latest['rev_7d_prev'] - latest['rev_7d']) / max(1, latest['rev_7d_prev']) if 'rev_7d_prev' in latest else 0
    is_anomaly = False
    if mad > 0 and latest['rev_7d'] < med - 3*mad:
        is_anomaly = True
    if pct_drop > 0.5:
        is_anomaly = True
    if is_anomaly:
        out_alerts.append({
            "alert_time": pd.Timestamp.now().isoformat(),
            "sku_id": sku,
            "region": region,
            "order_date": latest['order_date'].isoformat(),
            "rev_7d": float(latest['rev_7d']),
            "rev_prev_7d": float(latest.get('rev_7d_prev',0)),
            "pct_drop": float(pct_drop)
        })

alerts_df = pd.DataFrame(out_alerts)
if not alerts_df.empty:
    alerts_df.to_csv(os.path.join(DATAPATH,"anomaly_alerts.csv"), index=False)
    print("Anomalies found:", len(alerts_df))
else:
    print("No anomalies found.")
