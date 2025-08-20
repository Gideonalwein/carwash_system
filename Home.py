import streamlit as st

st.set_page_config(page_title="Carwash System", layout="wide")

# --- HIDE SIDEBAR + HEADER ---
hide_sidebar = """
    <style>
        section[data-testid="stSidebar"] {display: none;}
        header[data-testid="stHeader"] {visibility: hidden;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# --- CUSTOM CSS FOR CARDS ---
st.markdown("""
    <style>
        /* Background color for whole page */
    .stApp {
        background-color: #9ACBD0; /* Change this HEX code to your preferred background */
    }
    .card {
        background-color: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
        margin-bottom: 20px;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    .icon {
        font-size: 40px;
        margin-bottom: 15px;
        color: #2E86C1;
    }
    h3 {
        margin: 0;
        font-size: 22px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 Trude Carwash Management System")

# --- Create Clickable Cards using st.button + switch_page ---
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Utility: make a full-width button styled as card
def card_button(icon, title, page_name, key=None):
    if st.button(f"{icon} {title}", key=key, use_container_width=True):
        st.switch_page(page_name)
    st.markdown(
        """
        <style>
        div[data-testid="stButton"] > button {
            background-color: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            font-size: 22px;
            color: #2E86C1;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        div[data-testid="stButton"] > button:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }
        </style>
        """, unsafe_allow_html=True
    )

with col1:
    card_button("📊", "Dashboard", "pages/1_Dashboard.py", key="dashboard")

with col2:
    card_button("🚘", "Car Wash Sales", "pages/2_Car_Wash_Sales.py", key="carwash")

with col3:
    card_button("🥤", "Drink Sales", "pages/3_Drinks_Sales.py", key="drinks")

with col4:
    card_button("🧾", "Reports", "pages/4_Reports.py", key="reports")
