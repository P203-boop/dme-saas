import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("DME_API_URL", "https://dme-saas-r1ir.onrender.com")
REQUEST_TIMEOUT = 5

st.set_page_config(page_title="DME SaaS Dashboard", layout="wide")
st.title("DME SaaS Operations Dashboard")

if "token" not in st.session_state:
    st.session_state.token = None


def login(username, password):
    try:
        response = requests.post(
            f"{API_URL}/login",
            data={"username": username, "password": password},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException:
        return None

    if response.status_code == 200:
        return response.json().get("access_token")
    return None


def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def api_request(method, path, **kwargs):
    try:
        return requests.request(
            method,
            f"{API_URL}{path}",
            headers=get_headers(),
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )
    except requests.RequestException:
        return None


def get_json(path):
    response = api_request("GET", path)
    if not response:
        st.warning("Backend not reachable.")
        return []
    if response.status_code == 401:
        st.session_state.token = None
        st.error("Session expired. Please log in again.")
        st.rerun()
    if response.status_code != 200:
        st.warning(f"Failed to load {path}.")
        return []
    return response.json()


if not st.session_state.token:
    st.subheader("Login")

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


patients = get_json("/patients")
orders = get_json("/orders")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Patients", len(patients))
col2.metric("Total Orders", len(orders))
col3.metric(
    "Flagged Orders",
    len([order for order in orders if order.get("status") == "FLAGGED"]),
)
col4.metric(
    "Routed Orders",
    len(
        [
            order
            for order in orders
            if order.get("status") == "ROUTED_TO_TRANSPORT"
        ]
    ),
)

st.divider()

st.subheader("Patients")
if patients:
    st.dataframe(pd.DataFrame(patients))
else:
    st.write("No patients found.")

st.subheader("Orders")
if orders:
    st.dataframe(pd.DataFrame(orders))
else:
    st.write("No orders found.")

st.divider()

st.subheader("Create Patient")
with st.form("patient_form"):
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    insurance_id = st.text_input("Insurance ID")

    submit = st.form_submit_button("Create Patient")

    if submit:
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "insurance_id": insurance_id,
        }

        response = api_request("POST", "/patients", json=payload)

        if response and response.status_code in (200, 201):
            st.success("Patient created successfully!")
            st.rerun()
        else:
            st.error("Failed to create patient")

st.subheader("Create Order")
with st.form("order_form"):
    patient_id = st.text_input("Patient ID")
    dme_code = st.text_input("DME Code")
    qty = st.number_input("Quantity", min_value=1, step=1)

    submit = st.form_submit_button("Create Order")

    if submit:
        payload = {
            "patient_id": patient_id,
            "dme_code": dme_code,
            "qty": qty,
        }

        response = api_request("POST", "/orders", json=payload)

        if response and response.status_code in (200, 201):
            st.success("Order created successfully!")
            st.rerun()
        else:
            st.error("Failed to create order")

st.subheader("Process Order")

order_id = st.text_input("Order ID")

if st.button("Process Order"):
    response = api_request("POST", f"/process/{order_id}")

    if not response:
        st.error("Backend not reachable or error occurred")
    elif response.status_code == 200:
        st.success(response.json())
        st.rerun()
    else:
        st.error("Failed to process order")
