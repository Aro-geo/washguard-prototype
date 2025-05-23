import streamlit as st
from database import (
    insert_chlorine, get_all_chlorine,
    insert_quality, get_all_quality,
    insert_feedback, get_all_feedback,
    insert_infrastructure, get_all_infrastructure
)

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
st.table(get_all_infrastructure())
