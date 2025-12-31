import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from streamlit_autorefresh import st_autorefresh  # pip install streamlit-autorefresh

# ------------------------
# CONFIGURATION
# ------------------------
BACKEND_URL = "http://localhost:8000"  # Replace with your FastAPI backend URL
# BACKEND_URL = "https://chancellor-actress-versus-porter.trycloudflare.com"  # Replace with your FastAPI backend URL
REFRESH_INTERVAL = 5000  # milliseconds for auto-refresh

# ------------------------
# APP TITLE
# ------------------------
st.set_page_config(page_title="AI Voice Calling", page_icon="📞")
st.title("📞 AI Voice Calling – Excel Upload & Call Status")

# ------------------------
# EXCEL UPLOAD
# ------------------------
uploaded_file = st.file_uploader("Upload Excel with Phone Numbers", type=["xlsx"])

if uploaded_file:
    try:
        # Read Excel into a DataFrame
        df = pd.read_excel(uploaded_file)
        st.subheader("Preview of uploaded Excel")
        st.dataframe(df.head())

        # Upload button
        if st.button("Upload to Server"):
            files = {
                "file": (
                    uploaded_file.name,
                    BytesIO(uploaded_file.getvalue()),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            }
            try:
                res = requests.post(f"{BACKEND_URL}/upload/excel", files=files, timeout=30)
                if res.status_code == 200:
                    st.success(res.json().get("message", "Excel uploaded successfully!"))
                else:
                    st.error(f"Upload failed! {res.status_code} - {res.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")

    except Exception as e:
        st.error(f"Failed to read Excel file: {e}")

# ------------------------
# MANUAL OUTBOUND CALL TRIGGER
# ------------------------
st.subheader("📞 Trigger Outbound Calls")

if st.button("Start Outbound Calls"):
    try:
        res = requests.post(f"{BACKEND_URL}/calls/start", timeout=30)
        if res.status_code == 200:
            st.success(res.json().get("message", "Outbound call process started in background!"))
        else:
            st.error(f"Failed to start calls! {res.status_code} - {res.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")

# ------------------------
# CALL STATUS SECTION
# ------------------------
st.subheader("📋 Call Status")

def fetch_call_status():
    try:
        res = requests.get(f"{BACKEND_URL}/status/all", timeout=10)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list) and data:
                df_status = pd.DataFrame(data)
                st.table(df_status)
            else:
                st.info("No leads found.")
        else:
            st.error(f"Failed to fetch call status: {res.status_code} - {res.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")

# ------------------------
# AUTO-REFRESH CALL STATUS
# ------------------------
# Refreshes the status every REFRESH_INTERVAL milliseconds
# st_autorefresh(interval=REFRESH_INTERVAL, key="auto_refresh")

# Show current call status
# fetch_call_status()

# ------------------------
# MANUAL REFRESH BUTTON (optional)
# ------------------------
if st.button("Refresh Status"):
    fetch_call_status()
