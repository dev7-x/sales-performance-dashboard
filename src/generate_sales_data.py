# src/generate_sales_data.py
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os, uuid, random

OUT = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT, exist_ok=True)
RNG = np.random.default_rng(123)

start = datetime(2024,1,1)
end = datetime(2024,6,30)
days = (end - start).days + 1

# product catalog
n_skus = 120
categories = ["Electronics","Home","Clothing","Toys","Beauty"]
skus = []
for i in range(n_skus):
    skus.append({
        "sku_id": f"SKU-{1000+i}",
        "category": random.choice(categories),
        "price": round(float(abs(RNG.normal(50,30))) + 5,2)
    })
catalog = pd.DataFrame(skus)
catalog.to_csv(os.path.join(OUT,"catalog.csv"), index=False)

# regions
regions = ["US","EU","APAC"]

# generate daily orders (one row per order)
orders = []
order_id = 1
for d in range(days):
    day = (start + timedelta(days=d)).date().isoformat()
    # sim volume seasonality
    base_orders = 1000 + int(200 * np.sin(d/14))
    for _ in range(base_orders + RNG.integers(-100,100)):
        sku = catalog.sample(1).iloc[0]
        qty = int(max(1, abs(RNG.normal(1.4,0.9))))
        region = random.choice(regions)
        price = sku['price']
        # occasional sale promotion (10% chance)
        if RNG.random() < 0.1:
            price = round(price * (0.6 + RNG.random()*0.3),2)
        # occasional anomaly day for some SKUs: sudden drop
        if RNG.random() < 0.0005:
            qty = max(0, qty - RNG.integers(1,3))
        orders.append({
            "order_id": f"ORD-{order_id}",
            "order_date": day,
            "sku_id": sku['sku_id'],
            "category": sku['category'],
            "region": region,
            "qty": qty,
            "price": price,
            "revenue": round(qty*price,2)
        })
        order_id += 1

orders_df = pd.DataFrame(orders)
orders_df.to_csv(os.path.join(OUT,"orders.csv"), index=False)

# create some manual anomalies: drop revenue for a sku-region on a random date
for _ in range(6):
    pick_sku = catalog.sample(1).iloc[0]['sku_id']
    pick_region = random.choice(regions)
    anomaly_date = (start + timedelta(days=int(RNG.integers(0,days-1)))).date().isoformat()
    mask = (orders_df['sku_id']==pick_sku) & (orders_df['region']==pick_region) & (orders_df['order_date']==anomaly_date)
    orders_df.loc[mask,'revenue'] = orders_df.loc[mask,'revenue'] * RNG.random()*0.2
orders_df.to_csv(os.path.join(OUT,"orders.csv"), index=False)

print("Generated data/orders.csv and data/catalog.csv with", len(orders_df), "orders")
