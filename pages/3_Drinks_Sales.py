import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt



# ==============================
# Database setup
# ==============================
conn = sqlite3.connect("database/carwash.db", check_same_thread=False)  # ✅ Correct path
c = conn.cursor()

# Updated schema with payment_method
c.execute('''CREATE TABLE IF NOT EXISTS drink_sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                drink_name TEXT,
                quantity INTEGER,
                price REAL,
                total REAL,
                payment_status TEXT,
                payment_method TEXT
            )''')
conn.commit()

# Predefined lists
drinks_list = ["Soda", "Water", "Juice", "Energy Drink", "Other"]
payment_methods = ["Cash", "M-Pesa"]

st.title("🥤 Drinks Sales Management")

# ==============================
# Add New Drink Sale Form
# ==============================
st.subheader("➕ Add New Drink Sale")

with st.form("add_drink_form", clear_on_submit=True):
    drink_name = st.selectbox("Drink Name", drinks_list)
    quantity = st.number_input("Quantity", min_value=1, value=1)
    price = st.number_input("Price per Unit", min_value=0.0, format="%.2f")
    total = round(quantity * price, 2)
    st.write(f"**Total: {total:.2f}**")
    payment_status = st.selectbox("Payment Status", ["Unpaid", "Paid"])
    payment_method = st.selectbox("Payment Method", payment_methods)
    submitted = st.form_submit_button("Add Sale")

    if submitted:
        c.execute(
            "INSERT INTO drink_sales (date, drink_name, quantity, price, total, payment_status, payment_method) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(date.today()), drink_name, quantity, price, total, payment_status, payment_method)
        )
        conn.commit()
        st.success("✅ Sale added successfully!")

# ==============================
# Filters
# ==============================
st.subheader("📊 Drinks Sales Records")
filter_status = st.selectbox("Filter by Payment Status", ["All", "Paid", "Unpaid"])
filter_method = st.selectbox("Filter by Payment Method", ["All"] + payment_methods)

# ✅ Date range filter
date_range = st.date_input("Filter by Date Range", value=(date.today(), date.today()))

query = "SELECT * FROM drink_sales WHERE 1=1"
params = []
if filter_status != "All":
    query += " AND payment_status=?"
    params.append(filter_status)

if filter_method != "All":
    query += " AND payment_method=?"
    params.append(filter_method)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    query += " AND date BETWEEN ? AND ?"
    params.extend([str(start_date), str(end_date)])

df = pd.read_sql(query, conn, params=params)

# ==============================
# Sales Records Table with Inline Editing + Daily Totals + Summary Row
# ==============================
if not df.empty:
    st.subheader("📄 Sales Records (Editable)")

    # Ensure latest sales appear first (by date desc, then id desc)
    df["date"] = pd.to_datetime(df["date"])  # Ensure proper datetime
    df = df.sort_values(by=["date", "id"], ascending=[False, False])

    # Drop "total" from editable columns
    editable_df = df.drop(columns=["total"])

    # Inline editing
    edited_df = st.data_editor(
        editable_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="sales_editor"
    )

    # --- Batch Save Button ---
    if st.button("💾 Save All Changes"):
        changes = edited_df.compare(editable_df, align_axis=0)

        if not changes.empty:
            for idx in changes.index.get_level_values(0).unique():
                row = edited_df.loc[idx]

                # Recalculate total before saving
                new_total = round(float(row["quantity"]) * float(row["price"]), 2)

                c.execute(
                    """UPDATE drink_sales 
                       SET drink_name=?, quantity=?, price=?, total=?, payment_status=?, payment_method=? 
                       WHERE id=?""",
                    (
                        row["drink_name"],
                        int(row["quantity"]),
                        float(row["price"]),
                        new_total,
                        row["payment_status"],
                        row["payment_method"],
                        int(row["id"])
                    )
                )
            conn.commit()
            st.success("✅ All changes saved successfully!")
            st.rerun()
        else:
            st.info("No changes detected.")

    # --- Delete Row(s) ---
    st.subheader("🗑 Delete Records")
    ids_to_delete = st.multiselect("Select record IDs to delete", df["id"].tolist())

    if st.button("Delete Selected"):
        if ids_to_delete:
            c.executemany("DELETE FROM drink_sales WHERE id=?", [(rid,) for rid in ids_to_delete])
            conn.commit()
            st.warning(f"Deleted records: {ids_to_delete}")
            st.rerun()
        else:
            st.info("No records selected for deletion.")

    # --- ✅ Mark as Paid ---
    st.subheader("💰 Mark as Paid")
    unpaid_df = df[df["payment_status"] == "Unpaid"]

    if not unpaid_df.empty:
        unpaid_ids = st.multiselect("Select unpaid sales to mark as Paid", unpaid_df["id"].tolist())
        if st.button("Mark Selected as Paid"):
            if unpaid_ids:
                c.executemany("UPDATE drink_sales SET payment_status='Paid' WHERE id=?", [(rid,) for rid in unpaid_ids])
                conn.commit()
                st.success(f"✅ Marked records as Paid: {unpaid_ids}")
                st.rerun()
            else:
                st.info("No records selected.")
    else:
        st.info("All sales are already Paid 🎉")

    # --- Daily Totals Summary ---
    st.subheader("📆 Daily Totals")
    preview_df = edited_df.copy()
    preview_df["total"] = round(preview_df["quantity"] * preview_df["price"], 2)
    preview_df["date"] = pd.to_datetime(preview_df["date"])

    daily_summary = (
        preview_df.groupby("date")
        .agg({"quantity": "sum", "total": "sum"})
        .reset_index()
        .sort_values("date", ascending=False)
    )

    styled_daily = daily_summary.style.format({
        "quantity": "{:.2f}",
        "total": "{:.2f}"
    })

    st.dataframe(styled_daily, use_container_width=True)

    # --- Read-only Preview with All Records ---
    st.subheader("👀 Preview with Auto-Calculated Totals (Latest on Top)")

    preview_df = preview_df.sort_values(by=["date", "id"], ascending=[False, False])

    styled_preview = preview_df.style.format({
        "quantity": "{:.2f}",
        "price": "{:.2f}",
        "total": "{:.2f}"
    })

    st.dataframe(styled_preview, use_container_width=True)

    # --- Frozen Grand Total ---
    total_quantity = preview_df["quantity"].sum()
    total_sales = preview_df["total"].sum()

    st.markdown(
        f"""
        <div style="background-color:#f9f9a8; padding:10px; border-radius:8px; font-weight:bold;">
            GRAND TOTAL — Quantity: {total_quantity:.2f} | Sales Amount: {total_sales:.2f}
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.info("No sales records found.")
