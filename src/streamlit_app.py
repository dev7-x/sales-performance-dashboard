# src/streamlit_app.py
import streamlit as st, pandas as pd, os, requests, plotly.express as px

DATAPATH = os.path.join(os.path.dirname(__file__), "..", "data")
st.set_page_config(layout="wide", page_title="Sales Performance Demo")
st.title("Sales Performance Dashboard (Demo)")

@st.cache_data
def load_all():
    daily = pd.read_csv(os.path.join(DATAPATH,"daily_metrics.csv"), parse_dates=["order_date"])
    catalog = pd.read_csv(os.path.join(DATAPATH,"catalog.csv"))
    alerts = pd.read_csv(os.path.join(DATAPATH,"alerts.csv")) if os.path.exists(os.path.join(DATAPATH,"alerts.csv")) else pd.DataFrame()
    return daily, catalog, alerts

daily, catalog, alerts = load_all()

# Top KPIs
latest_date = daily['order_date'].max()
tot_rev = daily[daily['order_date']==latest_date]['total_revenue'].sum()
tot_orders = daily[daily['order_date']==latest_date]['orders'].sum()
st.metric("Date", str(latest_date)[:10])
st.metric("Revenue (latest day)", f"${tot_rev:,.2f}", delta=None)
st.metric("Orders (latest day)", f"{int(tot_orders)}")

# revenue trend
rev_trend = daily.groupby('order_date')['total_revenue'].sum().reset_index()
fig = px.line(rev_trend, x='order_date', y='total_revenue', title="Total Revenue Over Time")
st.plotly_chart(fig, use_container_width=True)

# SKU performance table
st.subheader("Low-performing SKUs (last 7-day revenue)")
sku_rank = (daily.groupby('sku_id').agg(rev_7d=('rev_7d','max')).reset_index()
            .sort_values('rev_7d'))
st.dataframe(sku_rank.head(20))

# Region breakdown
st.subheader("Revenue by Region (latest day)")
region_latest = daily[daily['order_date']==latest_date].groupby('region')['total_revenue'].sum().reset_index()
fig2 = px.pie(region_latest, values='total_revenue', names='region', title="Revenue share by region")
st.plotly_chart(fig2, use_container_width=True)

# Alerts
st.subheader("Alerts")
if not alerts.empty:
    st.dataframe(alerts.sort_values('alert_time', ascending=False).head(20))
else:
    st.info("No alerts yet. Click 'Run anomaly check' to scan for anomalies.")

# Run check button
if st.button("Run anomaly check"):
    try:
        resp = requests.post("http://127.0.0.1:5100/run_check", timeout=10)
        if resp.status_code == 200:
            j = resp.json()
            st.success(f"Alerts returned: {len(j.get('alerts',[]))}")
            st.experimental_rerun()
        else:
            st.error("Failed to contact local alert endpoint. Start `python src/app.py`.")
    except Exception as e:
        st.error(f"Error: {e}")
