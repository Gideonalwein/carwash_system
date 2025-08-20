# pages/2_Car_Wash_Sales.py
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import matplotlib.pyplot as plt

# Connect to DB
conn = sqlite3.connect("database/carwash.db")
c = conn.cursor()

# Create table if not exists
c.execute("""
CREATE TABLE IF NOT EXISTS car_wash_sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    car_type TEXT,
    plate_number TEXT,
    service_type TEXT,
    price REAL,
    payment_method TEXT,
    payment_status TEXT
)
""")
conn.commit()

st.title("🚗 Car Wash Sales")

# --- Add New Sale Form ---
with st.form("add_sale_form"):
    car_type = st.selectbox("Car Type", ["Saloon","Bus","Van","Truck","Bike","Other"])
    plate_number = st.text_input("Plate Number")
    service_type = st.selectbox("Service Type", ["Full-service wash", "Half-service wash"])
    price = st.number_input("Amount", min_value=0.0, step=50.0)
    payment_method = st.selectbox("Payment Method", ["Cash", "M-Pesa"])
    payment_status = st.selectbox("Payment Status", ["Unpaid", "Paid"])
    submitted = st.form_submit_button("Add Sale")

    if submitted:
        # Store date in YYYY-MM-DD format
        c.execute("""
        INSERT INTO car_wash_sales (date, car_type, plate_number, service_type, price, payment_method, payment_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now().strftime("%Y-%m-%d"), car_type, plate_number, service_type, price, payment_method, payment_status))
        conn.commit()
        st.success("Sale added successfully!")

# --- Filters ---
st.subheader("🔎 Filter Sales")
col1, col2, col3 = st.columns(3)

with col1:
    filter_payment_method = st.selectbox("Filter by Payment Method", ["All", "Cash", "M-Pesa", "Card"])
with col2:
    filter_payment_status = st.selectbox("Filter by Payment Status", ["All", "Paid", "Unpaid"])
with col3:
    today = date.today()
    date_range = st.date_input("Filter by Date Range", [today, today])

# --- Display Sales Table ---
c.execute("SELECT * FROM car_wash_sales ORDER BY date DESC")
sales = c.fetchall()

df = pd.DataFrame(
    sales,
    columns=["ID", "Date", "Car Type", "Plate Number", "Service Type", "Price", "Payment Method", "Payment Status"]
)

if not df.empty:
    # Convert Date column (parse YYYY-MM-DD format)
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")

    # Apply filters
    if filter_payment_method != "All":
        df = df[df["Payment Method"] == filter_payment_method]
    if filter_payment_status != "All":
        df = df[df["Payment Status"] == filter_payment_status]
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)]

st.subheader("📊 Sales Records")

if not df.empty:
    # Format dates back to YYYY-MM-DD for display
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    # Editable table (except ID & Date)
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        disabled=["ID", "Date"],
        key="sales_editor"
    )

    # Save changes button
    if st.button("💾 Save All Changes"):
        for i, row in edited_df.iterrows():
            c.execute("""
                UPDATE car_wash_sales
                SET car_type = ?, plate_number = ?, service_type = ?, price = ?, payment_method = ?, payment_status = ?
                WHERE id = ?
            """, (row["Car Type"], row["Plate Number"], row["Service Type"], row["Price"], row["Payment Method"], row["Payment Status"], row["ID"]))
        conn.commit()
        st.success("All changes saved successfully!")
        st.rerun()

    # "Mark as Paid" buttons
    st.subheader("⚡ Quick Actions")
    for _, row in df[df["Payment Status"] == "Unpaid"].iterrows():
        if st.button(f"Mark Sale {row['ID']} as Paid", key=f"mark_paid_{row['ID']}"):
            c.execute("UPDATE car_wash_sales SET payment_status = 'Paid' WHERE id = ?", (row["ID"],))
            conn.commit()
            st.success(f"Sale {row['ID']} marked as Paid!")
            st.rerun()

    # --- Daily Sales Summary ---
    st.subheader("📅 Daily Sales Summary")
    daily_summary = df.groupby("Date")["Price"].sum().reset_index()
    daily_summary.columns = ["Date", "Total Sales"]
    daily_summary["Total Sales"] = daily_summary["Total Sales"].map("{:,.2f}".format)
    st.dataframe(daily_summary)

    # --- Daily Sales Chart ---
    st.subheader("📈 Daily Sales Trend")
    fig, ax = plt.subplots()
    ax.bar(daily_summary["Date"], daily_summary["Total Sales"].str.replace(",", "").astype(float))
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Sales")
    ax.set_title("Daily Sales Trend")
    plt.xticks(rotation=45)
    st.pyplot(fig)

else:
    st.info("No sales found with the selected filters.")
