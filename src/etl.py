# src/etl.py
import pandas as pd, os
from datetime import datetime

DATAPATH = os.path.join(os.path.dirname(__file__), "..", "data")
orders = pd.read_csv(os.path.join(DATAPATH,"orders.csv"), parse_dates=["order_date"])
# aggregate
daily = (orders
         .groupby(["order_date","sku_id","category","region"], as_index=False)
         .agg(total_revenue=("revenue","sum"),
              units_sold=("qty","sum"),
              avg_price=("price","mean"),
              orders=("order_id","nunique"))
        )
# compute KPIs
daily['aov'] = daily['total_revenue'] / daily['orders'].replace(0,1)
daily['order_date'] = pd.to_datetime(daily['order_date'])
daily = daily.sort_values(["sku_id","region","order_date"])
daily.to_csv(os.path.join(DATAPATH,"daily_agg.csv"), index=False)
print("Saved", os.path.join(DATAPATH,"daily_agg.csv"))
