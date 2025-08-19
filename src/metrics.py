# src/metrics.py
import pandas as pd, os
DATAPATH = os.path.join(os.path.dirname(__file__), "..", "data")
daily = pd.read_csv(os.path.join(DATAPATH,"daily_agg.csv"), parse_dates=["order_date"])
# rolling 7-day revenue per sku-region
daily = daily.sort_values(["sku_id","region","order_date"])
daily['rev_7d'] = daily.groupby(["sku_id","region"])['total_revenue'].transform(lambda x: x.rolling(7, min_periods=1).sum())
# percent change vs previous 7d
daily['rev_7d_prev'] = daily.groupby(["sku_id","region"])['rev_7d'].shift(1)
daily['rev_7d_pct_change'] = (daily['rev_7d'] - daily['rev_7d_prev']) / (daily['rev_7d_prev'].replace(0,1))
daily.to_csv(os.path.join(DATAPATH,"daily_metrics.csv"), index=False)
print("Saved", os.path.join(DATAPATH,"daily_metrics.csv"))
