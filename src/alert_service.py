# src/alert_service.py
import pandas as pd, os
DATAPATH = os.path.join(os.path.dirname(__file__), "..", "data")

def send_alerts(alerts):
    if not alerts:
        print("No alerts to send.")
        return
    path = os.path.join(DATAPATH, "alerts.csv")
    df = pd.DataFrame(alerts)
    # append to existing file
    if os.path.exists(path):
        existing = pd.read_csv(path)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv(path, index=False)
    print(f"Saved {len(alerts)} alerts to {path}")
    # print a summary (simulate notification)
    for a in alerts:
        print("ALERT:", a['sku_id'], a['region'], "date:", a['order_date'], "pct_drop:", round(a['pct_drop'],3))
