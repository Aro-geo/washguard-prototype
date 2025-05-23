import streamlit as st
from database import (
    insert_chlorine, get_all_chlorine,
    insert_quality, get_all_quality,
    insert_feedback, get_all_feedback,
    insert_infrastructure, get_all_infrastructure
)
from notifications import send_alert_email, send_sms_alert
import pandas as pd

st.set_page_config(page_title="Water Monitoring System", layout="wide")

st.title("🚰 Water Treatment, Feedback & Infrastructure Monitoring")

# --- Water Treatment Section ---
st.header("Water Treatment Data")
with st.form("chlorine_form"):
    st.subheader("Add Chlorine Level")
    tap_stand_id = st.text_input("Tap Stand ID")
    date = st.date_input("Date")
    time = st.time_input("Time")
    chlorine_level = st.number_input("Chlorine Level (mg/L)", min_value=0.0, format="%.2f")
    submit_chlorine = st.form_submit_button("Submit Chlorine Data")

    if submit_chlorine:
        insert_chlorine(tap_stand_id, str(date), str(time), chlorine_level)
        st.success("Chlorine data submitted.")

st.subheader("All Chlorine Entries")
st.table(get_all_chlorine())

# --- Feedback Analysis Section ---
st.header("Community Feedback")
with st.form("feedback_form"):
    st.subheader("Add Feedback")
    household_id = st.text_input("Household ID")
    feedback_text = st.text_area("Feedback")
    submit_feedback = st.form_submit_button("Submit Feedback")

    if submit_feedback:
        insert_feedback(household_id, feedback_text)
        st.success("Feedback submitted.")

st.subheader("All Feedback")
st.table(get_all_feedback())

# --- Infrastructure Monitoring Section ---
st.header("Infrastructure Monitoring")
with st.form("infra_form"):
    st.subheader("Add Infrastructure Status")
    location = st.text_input("Location")
    generator_ok = st.radio("Generator OK?", ["Yes", "No"])
    pump_ok = st.radio("Pump OK?", ["Yes", "No"])
    pipe_leak = st.radio("Pipe Leak?", ["Yes", "No"])
    road_condition = st.selectbox("Road Condition", ["Good", "Muddy", "Flooded", "Blocked"])
    comments = st.text_area("Additional Comments")
    water_available_liters = st.number_input("Water Available (Liters)", min_value=0, step=1)
    submit_infra = st.form_submit_button("Submit Infrastructure Data")

    if submit_infra:
        insert_infrastructure(location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_available_liters)
        st.success("Infrastructure data submitted.")

st.subheader("All Infrastructure Entries")
infra_data = get_all_infrastructure()
st.table(infra_data)

# --- Alerts ---
st.subheader("Infrastructure Alerts")
def check_infra_alerts(entry):
    alerts = []
    if entry['generator_ok'] == 'No':
        alerts.append("🛑 Generator Failure")
    if entry['pump_ok'] == 'No':
        alerts.append("🛑 Pump Fault")
    if entry['pipe_leak'] == 'Yes':
        alerts.append("💧 Pipe Leak")
    if entry['road_condition'] in ["Flooded", "Muddy", "Blocked"] and entry['generator_ok'] == 'Yes':
        alerts.append("🚫 Fuel Delivery Blocked")
    if entry['water_available_liters'] < 10:
        alerts.append("❗ Low Water Reserves")
    return ", ".join(alerts) if alerts else "✅ OK"

if isinstance(infra_data, list) and infra_data:
    infra_alerts = []
    for entry in infra_data:
        alert = check_infra_alerts(entry)
        if alert != "✅ OK":
            infra_alerts.append({**entry, "alerts": alert})

            subject = f"WASH Alert: {entry['location']} – {alert}"
            body = (
                f"Issue detected in {entry['location']}:\n\n"
                f"Alerts: {alert}\n"
                f"Comments: {entry['comments']}\n"
                f"Water Available: {entry['water_available_liters']}L\n"
                f"Road Condition: {entry['road_condition']}"
            )
            send_alert_email(subject, body)
            send_sms_alert(body)

    if infra_alerts:
        st.warning("🚨 Issues Detected in the Following Locations")
        st.dataframe(pd.DataFrame(infra_alerts))
    else:
        st.success("✅ No Current Infrastructure Alerts")
