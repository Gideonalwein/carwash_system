import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

DB_PATH = "database/carwash.db"

# Function to fetch data
def fetch_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --- Page title ---
st.title("🚗 Car Wash & 🥤 Drinks Sales Dashboard")

# --- Load Data ---
car_wash_df = fetch_data("SELECT date, price, payment_method, payment_status FROM car_wash_sales")
drinks_df = fetch_data("SELECT date, total as price, payment_method, payment_status FROM drink_sales")

# Preprocess dates
car_wash_df["date"] = pd.to_datetime(car_wash_df["date"])
drinks_df["date"] = pd.to_datetime(drinks_df["date"])

# Add source column
car_wash_df["source"] = "Car Wash"
drinks_df["source"] = "Drinks"

# Standardize column names
car_wash_df.rename(columns={"price": "amount"}, inplace=True)
drinks_df.rename(columns={"price": "amount"}, inplace=True)

# Merge into one dataset
sales_df = pd.concat([car_wash_df, drinks_df], ignore_index=True)

# --- Filter defaults ---
if not sales_df.empty:
    min_date = sales_df["date"].min().date()
    max_date = sales_df["date"].max().date()
else:
    min_date = max_date = date.today()

# ✅ Clamp today into the DB’s available range
today = date.today()
default_start = max(min_date, min(today, max_date))
default_end = max(min_date, min(today, max_date))

# --- Horizontal filter row ---
st.markdown("### 🔍 Filters")

filter_cols = st.columns([1, 1, 2, 1])  # proportional widths

with filter_cols[0]:
    source_filter = st.selectbox(
        "Sales Type",
        ["All", "Car Wash", "Drinks"],
        key="source_filter"
    )

with filter_cols[1]:
    payment_methods = ["All"] + sorted(sales_df["payment_method"].dropna().unique().tolist())
    payment_filter = st.selectbox(
        "Payment Method",
        payment_methods,
        key="payment_filter"
    )

with filter_cols[2]:
    date_range = st.date_input(
        "Date Range",
        [default_start, default_end],  # ✅ always valid
        min_value=min_date,
        max_value=max_date,
        key="date_range"
    )

# --- Apply Filters ---
filtered_df = sales_df.copy()

if source_filter != "All":
    filtered_df = filtered_df[filtered_df["source"] == source_filter]

if payment_filter != "All":
    filtered_df = filtered_df[filtered_df["payment_method"] == payment_filter]

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["date"].dt.date >= start_date) &
        (filtered_df["date"].dt.date <= end_date)
    ]
elif isinstance(date_range, date):  # single date selected
    filtered_df = filtered_df[filtered_df["date"].dt.date == date_range]

# --- KPIs ---
total_revenue = filtered_df["amount"].sum()
total_carwash = filtered_df[filtered_df["source"] == "Car Wash"]["amount"].sum()
total_drinks = filtered_df[filtered_df["source"] == "Drinks"]["amount"].sum()
payout = 0.3 * total_carwash  # ✅ payout = 30% of car wash

# NEW: Unpaid metrics
unpaid_carwash = filtered_df[
    (filtered_df["source"] == "Car Wash") & (filtered_df["payment_status"].str.lower() == "unpaid")
]["amount"].sum()

unpaid_drinks = filtered_df[
    (filtered_df["source"] == "Drinks") & (filtered_df["payment_status"].str.lower() == "unpaid")
]["amount"].sum()

# --- KPI Layout ---
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("💰 Total Revenue", f"KES {total_revenue:,.0f}")
col2.metric("🚘 Car Wash Revenue", f"KES {total_carwash:,.0f}")
col3.metric("🥤 Drinks Revenue", f"KES {total_drinks:,.0f}")
col4.metric("💸 Payout (30% Car Wash)", f"KES {payout:,.0f}")
col5.metric("🚫 Unpaid Car Wash", f"KES {unpaid_carwash:,.0f}")
col6.metric("🚫 Unpaid Drinks", f"KES {unpaid_drinks:,.0f}")

st.markdown("---")

# --- NEW: Daily Sales Trend Chart ---
st.subheader("📊 Daily Sales Trend")
if not filtered_df.empty:
    daily_sales = filtered_df.groupby([filtered_df["date"].dt.date, "source"])["amount"].sum().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(8, 4))
    daily_sales.plot(kind="bar", stacked=False, ax=ax)
    ax.set_title("Daily Sales Trend (Car Wash vs Drinks)")
    ax.set_xlabel("Date")
    ax.set_ylabel("KES")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)
else:
    st.info("No data available for selected filters.")

# --- Payment Distribution ---
st.subheader("💳 Payment Method Distribution")
if not filtered_df.empty:
    payment_data = filtered_df.groupby("payment_method")["amount"].sum()
    fig2, ax2 = plt.subplots()
    ax2.pie(payment_data, labels=payment_data.index, autopct="%1.1f%%", startangle=90)
    ax2.set_title("Sales by Payment Method")
    st.pyplot(fig2)
else:
    st.info("No data available for selected filters.")

# --- Sales Breakdown ---
st.subheader("🔍 Sales Breakdown by Source")
if not filtered_df.empty:
    source_data = filtered_df.groupby("source")["amount"].sum()

    fig3, ax3 = plt.subplots()
    ax3.bar(source_data.index, source_data.values, color=["#1f77b4", "#ff7f0e"])
    ax3.set_title("Revenue by Source")
    ax3.set_ylabel("KES")
    st.pyplot(fig3)
else:
    st.info("No data available for selected filters.")

# --- Data Preview ---
st.subheader("📋 Filtered Sales Records")
st.dataframe(filtered_df.sort_values("date", ascending=False))
