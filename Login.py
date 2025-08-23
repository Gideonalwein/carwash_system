import streamlit as st
import sqlite3
from auth import login_user

st.set_page_config(page_title="Carwash System Login", page_icon="🧽", layout="centered")

# Session state to track login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

st.title("🔑 Carwash System Login")

if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Welcome {username}!")
            st.switch_page("pages/0_Home.py")  # Redirect to Home after login
        else:
            st.error("❌ Invalid username or password")

else:
    st.success(f"Already logged in as {st.session_state.username}")
    st.switch_page("pages/0_Home.py")
