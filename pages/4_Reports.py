import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# --- LOGIN CHECK ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ You must login first to access the system.")
    st.switch_page("Login.py")  # Redirect to login page
else:
    # --- Database Connection ---
    DB_PATH = "database/carwash.db"

    def get_connection():
        return sqlite3.connect(DB_PATH)

    # --- Data Fetching Functions ---
    def fetch_car_wash_sales(start_date, end_date, payment_status, payment_method):
        conn = get_connection()
        query = """
            SELECT date, car_type, plate_number, service_type, price, payment_status, payment_method
            FROM car_wash_sales
            WHERE DATE(date) BETWEEN DATE(?) AND DATE(?)
        """
        params = [start_date, end_date]

        if payment_status != "All":
            query += " AND payment_status = ?"
            params.append(payment_status)

        if payment_method != "All":
            query += " AND payment_method = ?"
            params.append(payment_method)

        query += " ORDER BY date DESC"
        df = pd.read_sql(query, conn, params=params)
        conn.close()

        # ✅ Flexible datetime parsing
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"], errors="coerce", format="mixed")
        return df

    def fetch_drink_sales(start_date, end_date, payment_status, payment_method):
        conn = get_connection()
        query = """
            SELECT date, drink_name, quantity, price, total, payment_status, payment_method
            FROM drink_sales
            WHERE date BETWEEN ? AND ?
        """
        params = [start_date, end_date]

        if payment_status != "All":
            query += " AND payment_status = ?"
            params.append(payment_status)

        if payment_method != "All":
            query += " AND payment_method = ?"
            params.append(payment_method)

        query += " ORDER BY date DESC"
        df = pd.read_sql(query, conn, params=params)
        conn.close()

        # ✅ Flexible datetime parsing
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"], errors="coerce", format="mixed")
        return df

    # --- Export Helpers ---
    def export_excel(df, sheet_name="Report"):
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
        buffer.seek(0)
        return buffer

    def export_pdf(df, title="Report"):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 40, title)

        c.setFont("Helvetica", 10)
        x, y = 50, height - 70
        for _, row in df.iterrows():
            row_text = " | ".join([str(val) for val in row.values])
            c.drawString(x, y, row_text[:100])  # truncate long rows
            y -= 15
            if y < 50:
                c.showPage()
                y = height - 50
        c.save()
        buffer.seek(0)
        return buffer

    # --- UI ---
    st.title("📊 Reports Dashboard")

    # --- Tabs for Reports ---
    tab1, tab2, tab3 = st.tabs(["🚗 Car Wash Report", "🥤 Drinks Report", "📊 Overall Summary"])

    # --- Car Wash Report ---
    with tab1:
        colf1, colf2, colf3 = st.columns(3)
        today = date.today()
        start_date = colf1.date_input("Start Date", today)
        end_date = colf2.date_input("End Date", today)
        payment_status = colf3.selectbox("Payment Status", ["All", "Paid", "Unpaid"])
        payment_method = st.selectbox("Payment Method", ["All", "Cash", "Mpesa", "Card"])

        car_df = fetch_car_wash_sales(str(start_date), str(end_date), payment_status, payment_method)

        if not car_df.empty:
            total_sales = car_df["price"].sum()
            paid_sales = car_df[car_df["payment_status"] == "Paid"]["price"].sum()
            unpaid_sales = car_df[car_df["payment_status"] == "Unpaid"]["price"].sum()
            payout = round(total_sales * 0.3, 2)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Sales", f"KES {total_sales:,.0f}")
            col2.metric("Paid", f"KES {paid_sales:,.0f}")
            col3.metric("Unpaid", f"KES {unpaid_sales:,.0f}")
            col4.metric("Payout (30%)", f"KES {payout:,.0f}")

            st.dataframe(car_df)

            weekly = car_df.copy()
            weekly = weekly.groupby(weekly["date"].dt.to_period("W"))["price"].sum().reset_index()
            weekly["date"] = weekly["date"].astype(str)

            fig, ax = plt.subplots()
            ax.bar(weekly["date"], weekly["price"])
            ax.set_title("Weekly Sales Trend")
            ax.set_ylabel("KES")
            st.pyplot(fig)

            st.download_button("📥 Export Excel", data=export_excel(car_df), file_name="car_wash_report.xlsx")
            st.download_button("📥 Export PDF", data=export_pdf(car_df, "Car Wash Report"), file_name="car_wash_report.pdf")
        else:
            st.info("No Car Wash records found for this period.")

    # --- Drinks Report ---
    with tab2:
        colf1, colf2, colf3 = st.columns(3)
        today = date.today()
        start_date = colf1.date_input("Start Date", today, key="drink_start")
        end_date = colf2.date_input("End Date", today, key="drink_end")
        payment_status = colf3.selectbox("Payment Status", ["All", "Paid", "Unpaid"], key="drink_status")
        payment_method = st.selectbox("Payment Method", ["All", "Cash", "Mpesa", "Card"], key="drink_method")

        drink_df = fetch_drink_sales(str(start_date), str(end_date), payment_status, payment_method)

        if not drink_df.empty:
            total_sales = drink_df["total"].sum()
            paid_sales = drink_df[drink_df["payment_status"] == "Paid"]["total"].sum()
            unpaid_sales = drink_df[drink_df["payment_status"] == "Unpaid"]["total"].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Sales", f"KES {total_sales:,.0f}")
            col2.metric("Paid", f"KES {paid_sales:,.0f}")
            col3.metric("Unpaid", f"KES {unpaid_sales:,.0f}")

            st.dataframe(drink_df)

            weekly = drink_df.copy()
            weekly = weekly.groupby(weekly["date"].dt.to_period("W"))["total"].sum().reset_index()
            weekly["date"] = weekly["date"].astype(str)

            fig, ax = plt.subplots()
            ax.bar(weekly["date"], weekly["total"])
            ax.set_title("Weekly Sales Trend")
            ax.set_ylabel("KES")
            st.pyplot(fig)

            st.download_button("📥 Export Excel", data=export_excel(drink_df), file_name="drinks_report.xlsx")
            st.download_button("📥 Export PDF", data=export_pdf(drink_df, "Drinks Report"), file_name="drinks_report.pdf")
        else:
            st.info("No Drinks records found for this period.")

    # --- Overall Summary ---
    with tab3:
        colf1, colf2, colf3 = st.columns(3)
        today = date.today()
        start_date = colf1.date_input("Start Date", today, key="overall_start")
        end_date = colf2.date_input("End Date", today, key="overall_end")
        payment_status = colf3.selectbox("Payment Status", ["All", "Paid", "Unpaid"], key="overall_status")
        payment_method = st.selectbox("Payment Method", ["All", "Cash", "Mpesa", "Card"], key="overall_method")

        car_df = fetch_car_wash_sales(str(start_date), str(end_date), payment_status, payment_method)
        drink_df = fetch_drink_sales(str(start_date), str(end_date), payment_status, payment_method)

        if not car_df.empty or not drink_df.empty:
            total_sales = car_df["price"].sum() + drink_df["total"].sum()
            paid_sales = car_df[car_df["payment_status"] == "Paid"]["price"].sum() + \
                         drink_df[drink_df["payment_status"] == "Paid"]["total"].sum()
            unpaid_sales = car_df[car_df["payment_status"] == "Unpaid"]["price"].sum() + \
                           drink_df[drink_df["payment_status"] == "Unpaid"]["total"].sum()
            payout = round(car_df["price"].sum() * 0.3, 2)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Sales", f"KES {total_sales:,.0f}")
            col2.metric("Paid", f"KES {paid_sales:,.0f}")
            col3.metric("Unpaid", f"KES {unpaid_sales:,.0f}")
            col4.metric("Car Wash Payout (30%)", f"KES {payout:,.0f}")

            combined_df = pd.concat([car_df, drink_df], ignore_index=True, sort=False)
            st.dataframe(combined_df)

            # ✅ Flexible datetime parsing for combined DF
            combined_df["date"] = pd.to_datetime(combined_df["date"], errors="coerce", format="mixed")

            if "price" in combined_df.columns and "total" in combined_df.columns:
                combined_df["amount"] = combined_df["price"].fillna(0) + combined_df["total"].fillna(0)
            elif "price" in combined_df.columns:
                combined_df["amount"] = combined_df["price"]
            else:
                combined_df["amount"] = combined_df["total"]

            weekly = combined_df.groupby(combined_df["date"].dt.to_period("W"))["amount"].sum().reset_index()
            weekly["date"] = weekly["date"].astype(str)

            fig, ax = plt.subplots()
            ax.bar(weekly["date"], weekly["amount"])
            ax.set_title("Overall Weekly Sales Trend")
            ax.set_ylabel("KES")
            st.pyplot(fig)

            st.download_button("📥 Export Excel", data=export_excel(combined_df), file_name="overall_report.xlsx")
            st.download_button("📥 Export PDF", data=export_pdf(combined_df, "Overall Report"), file_name="overall_report.pdf")
        else:
            st.info("No records found for this period.")
