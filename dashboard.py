import streamlit as st
import requests
import pandas as pd

# -------------------------
# API CONFIG
# -------------------------
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="DME SaaS Dashboard", layout="wide")

st.title("🏥 DME SaaS Operations Dashboard")

# -------------------------
# SAFE API LAYER
# -------------------------


def safe_get(url):
    try:
        return requests.get(url, timeout=3).json()
    except:
        return []


def safe_post(url, payload):
    try:
        return requests.post(url, json=payload, timeout=3)
    except:
        return None


def get_patients():
    return safe_get(f"{API_URL}/patients")


def get_orders():
    return safe_get(f"{API_URL}/orders")


# -------------------------
# LOAD DATA
# -------------------------
patients = get_patients()
orders = get_orders()

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
    st.write("No patients yet.")

# -------------------------
# ORDERS TABLE
# -------------------------
st.subheader("Orders")

if orders:
    st.dataframe(pd.DataFrame(orders))
else:
    st.write("No orders yet.")

st.divider()

# -------------------------
# CREATE PATIENT
# -------------------------
st.subheader("➕ Create Patient")

with st.form("patient_form"):
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    insurance_id = st.text_input("Insurance ID")

    submitted = st.form_submit_button("Create Patient")

    if submitted:
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "insurance_id": insurance_id
        }

        r = safe_post(f"{API_URL}/patients", payload)

        if r and r.status_code == 200:
            st.success("Patient created successfully!")
        else:
            st.error("Error creating patient")

# -------------------------
# CREATE ORDER
# -------------------------
st.subheader("📦 Create Order")

with st.form("order_form"):
    patient_id = st.text_input("Patient ID")
    dme_code = st.text_input("DME Code")
    qty = st.number_input("Quantity", min_value=1, step=1)

    submitted = st.form_submit_button("Create Order")

    if submitted:
        payload = {
            "patient_id": patient_id,
            "dme_code": dme_code,
            "qty": qty
        }

        r = safe_post(f"{API_URL}/orders", payload)

        if r and r.status_code == 200:
            st.success("Order created successfully!")
        else:
            st.error("Error creating order")

# -------------------------
# PROCESS ORDER
# -------------------------
st.subheader("⚙️ Process Order")

order_id = st.text_input("Order ID to Process")

if st.button("Process Order"):
    if order_id:
        try:
            r = requests.post(f"{API_URL}/process/{order_id}", timeout=3)

            if r.status_code == 200:
                st.success(r.json())
            else:
                st.error("Error processing order")
        except:
            st.error("Backend not running or request failed")
