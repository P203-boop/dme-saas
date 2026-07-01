import streamlit as st
import requests
import pandas as pd

# -------------------------
# API CONFIG
# -------------------------
API_URL = "https://your-app.onrender.com"

st.set_page_config(page_title="DME SaaS Dashboard", layout="wide")

st.title("🏥 DME SaaS Operations Dashboard")

# -------------------------
# SESSION STATE
# -------------------------
if "token" not in st.session_state:
    st.session_state.token = None


# -------------------------
# LOGIN FUNCTION
# -------------------------
def login(username, password):
    try:
        response = requests.post(
            f"{API_URL}/login",
            data={"username": username, "password": password},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except:
        return None


# -------------------------
# AUTH HEADERS
# -------------------------
def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


# -------------------------
# SAFE API CALLS
# -------------------------
def safe_get(url):
    try:
        r = requests.get(url, headers=get_headers(), timeout=5)
        return r.json()
    except:
        return []


def safe_post(url, payload):
    try:
        r = requests.post(url, json=payload, headers=get_headers(), timeout=5)
        return r
    except:
        return None


# -------------------------
# LOGIN SCREEN
# -------------------------
if not st.session_state.token:
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        token = login(username, password)

        if token:
            st.session_state.token = token
            st.success("Login successful! Refreshing dashboard...")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()


# -------------------------
# LOAD DATA
# -------------------------
patients = safe_get(f"{API_URL}/patients")
orders = safe_get(f"{API_URL}/orders")


# -------------------------
# METRICS
# -------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Patients", len(patients))
col2.metric("Total Orders", len(orders))
col3.metric("Flagged Orders", len(
    [o for o in orders if o.get("status") == "FLAGGED"]))
col4.metric("Routed Orders", len(
    [o for o in orders if o.get("status") == "ROUTED_TO_TRANSPORT"]))

st.divider()


# -------------------------
# PATIENTS TABLE
# -------------------------
st.subheader("Patients")

if patients:
    st.dataframe(pd.DataFrame(patients))
else:
    st.write("No patients found.")


# -------------------------
# ORDERS TABLE
# -------------------------
st.subheader("Orders")

if orders:
    st.dataframe(pd.DataFrame(orders))
else:
    st.write("No orders found.")

st.divider()


# -------------------------
# CREATE PATIENT
# -------------------------
st.subheader("➕ Create Patient")

with st.form("patient_form"):
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    insurance_id = st.text_input("Insurance ID")

    submit = st.form_submit_button("Create Patient")

    if submit:
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "insurance_id": insurance_id
        }

        r = safe_post(f"{API_URL}/patients", payload)

        if r and r.status_code == 200:
            st.success("Patient created successfully!")
            st.rerun()
        else:
            st.error("Failed to create patient")


# -------------------------
# CREATE ORDER
# -------------------------
st.subheader("📦 Create Order")

with st.form("order_form"):
    patient_id = st.text_input("Patient ID")
    dme_code = st.text_input("DME Code")
    qty = st.number_input("Quantity", min_value=1, step=1)

    submit = st.form_submit_button("Create Order")

    if submit:
        payload = {
            "patient_id": patient_id,
            "dme_code": dme_code,
            "qty": qty
        }

        r = safe_post(f"{API_URL}/orders", payload)

        if r and r.status_code == 200:
            st.success("Order created successfully!")
            st.rerun()
        else:
            st.error("Failed to create order")


# -------------------------
# PROCESS ORDER
# -------------------------
st.subheader("⚙️ Process Order")

order_id = st.text_input("Order ID")

if st.button("Process Order"):
    try:
        r = requests.post(
            f"{API_URL}/process/{order_id}",
            headers=get_headers(),
            timeout=5
        )

        if r.status_code == 200:
            st.success(r.json())
            st.rerun()
        else:
            st.error("Failed to process order")
    except:
        st.error("Backend not reachable or error occurred")
