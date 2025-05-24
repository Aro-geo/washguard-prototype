# WASHGuard AI Prototype Streamlit App

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from transformers import pipeline
from email.mime.text import MIMEText
from twilio.rest import Client
import smtplib
import os
import database as db

# Load sentiment pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

# Page config
st.set_page_config(page_title="WASHGuard AI ", layout="wide")
st.title("🚰 WASHGuard AI")

# Sidebar navigation (replace your current tab definition)
tab = st.sidebar.radio("Select Module", [
    "Dashboard",
    "Water Treatment",
    "Feedback Analysis",
    "Infrastructure Monitor"
])

# --- Dashboard Tab ---
if tab == "Dashboard":
    import altair as alt
    from database import (
        insert_chlorine, get_all_chlorine,
        insert_quality, get_all_quality,
        insert_feedback, get_all_feedback,
        insert_infrastructure, get_all_infrastructure
    )
    from notification import send_alert_email, send_sms_alert

    st.title("📊 WASHGuard AI Dashboard")
    st.markdown("Last updated: " + pd.Timestamp.now().strftime("%m/%d/%Y, %I:%M:%S %p"))

    chlorine_data = get_all_chlorine()
    chlorine_df = pd.DataFrame(chlorine_data, columns=["tap_stand_id", "date", "time", "chlorine_level"])
    low_chlorine = chlorine_df[chlorine_df["chlorine_level"] < 0.2] if not chlorine_df.empty else pd.DataFrame()

    feedback_data = get_all_feedback()
    feedback_df = pd.DataFrame(feedback_data, columns=["household_id", "feedback_text"])
    negative_feedback = feedback_df[feedback_df["feedback_text"].str.contains("bad|dirty|no water", case=False, na=False)] if not feedback_df.empty else pd.DataFrame()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Chlorine Alerts", f"{len(low_chlorine)} of {len(chlorine_df)}", help="Tap stands with low chlorine levels")
    col2.metric("Turbidity Issues", "3 of 5", help="Placeholder - Turbidity data pending")
    col3.metric("Community Feedback", f"{len(negative_feedback)} negative", help="Feedback from households")
    col4.metric("Overall Risk Score", "High (100%)", help="Based on all system indicators")

 # --- Alert Composer ---
    st.markdown("### 🔔 Alert System")
    alert_subject = st.text_input("Alert Subject", "WASH Alert: Critical Infrastructure Issue")
    alert_msg = st.text_area("Alert Message", "Describe the issue and required actions...")
    send_email = st.toggle("Email", value=True)
    send_sms = st.toggle("SMS", value=True)

    if st.button("Send Alert"):
        if send_email:
            send_alert_email(alert_subject, alert_msg)
        if send_sms:
            send_sms_alert(alert_msg)
        st.success("Alert sent successfully!")

    st.markdown("---")
    st.caption("Prototype v1.2 | Developed by George Arogo")

# --- Water Treatment ---
if tab == "Water Treatment":
    st.header("Water Treatment Data")
    st.subheader("💧 Water Treatment Recommendations")

    # Chlorine Level
    st.markdown("### 🧪 Chlorine Level Monitor")
    with st.expander("➕ Add Chlorine Reading"):
        with st.form("chlorine_form"):
            tap_id = st.text_input("Tap Stand ID")
            date = st.date_input("Date")
            time = st.time_input("Time")
            level = st.number_input("Chlorine Level (mg/L)", min_value=0.0, max_value=2.0)
            submitted = st.form_submit_button("Submit")
            if submitted:
                if tap_id:
                    db.insert_chlorine(tap_id, date.isoformat(), time.isoformat(), level)
                    st.success("Chlorine reading submitted.")
                else:
                    st.error("Tap Stand ID required.")

    chlorine_data = db.get_all_chlorine()
    if chlorine_data:
        st.subheader("All Chlorine Entries")
        st.table(chlorine_data)
    else:
        st.info("No chlorine readings yet.")

    # Water Quality
    st.markdown("### 💧 Water Quality Entry")
    with st.expander("➕ Add Water Quality Reading"):
        with st.form("quality_form"):
            source_id = st.text_input("Source ID")
            turbidity = st.number_input("Turbidity (NTU)", 0.0, 100.0)
            odour = st.selectbox("Odour Present?", ["Yes", "No"])
            submitted = st.form_submit_button("Submit")
            if submitted:
                if source_id:
                    db.insert_quality(source_id, turbidity, odour)
                    st.success("Water quality submitted.")
                else:
                    st.error("Source ID required.")

    quality_data = db.get_all_quality()
    if quality_data:
        df_quality = pd.DataFrame(quality_data, columns=["source_id", "turbidity", "odour_present"])
        df_quality["treatment"] = df_quality["turbidity"].apply(lambda x: "PUR" if x > 5 else "Aqua Tabs")
        st.dataframe(df_quality)
    else:
        st.info("No water quality readings yet.")

# --- Feedback Analysis ---
elif tab == "Feedback Analysis":
    st.header("💬 Community Feedback")
    st.subheader("🗣️ Community Feedback NLP")

    with st.expander("➕ Add Feedback"):
        with st.form("feedback_form"):
            household_id = st.text_input("Household ID")
            text = st.text_area("Feedback Text")
            submitted = st.form_submit_button("Submit")
            if submitted:
                if household_id and text:
                    db.insert_feedback(household_id, text)
                    st.success("Feedback submitted.")
                else:
                    st.error("All fields required.")

    feedback_data = db.get_all_feedback()
    if feedback_data:
        df = pd.DataFrame(feedback_data, columns=["household_id", "feedback_text"])
        df["sentiment"] = df["feedback_text"].apply(lambda x: sentiment_analyzer(x)[0]["label"])
        st.dataframe(df)
        words = " ".join(df["feedback_text"].tolist())
        wordcloud = WordCloud(background_color="white").generate(words)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

        # ADDITIONAL: Show all feedback as a table
        st.subheader("🗂️ All Feedback")
        st.table(feedback_data)
    else:
        st.info("No feedback yet.")

# --- Infrastructure Monitor ---
elif tab == "Infrastructure Monitor":
    st.header("🛠️ Infrastructure Monitoring")
    st.subheader("⚙️ Infrastructure Status")

    with st.expander("➕ Add Infrastructure Status"):
        with st.form("infra_form"):
            location = st.text_input("Location")
            generator_ok = st.selectbox("Generator OK?", ["Yes", "No"])
            pump_ok = st.selectbox("Pump OK?", ["Yes", "No"])
            pipe_leak = st.selectbox("Pipe Leak?", ["No", "Yes"])
            road_condition = st.selectbox("Road Condition", ["Good", "Muddy", "Flooded"])
            comments = st.text_area("Comments")
            water_liters = st.number_input("Water Available (Liters)", 0, 1000)
            submitted = st.form_submit_button("Submit")
            if submitted:
                if location:
                    db.insert_infrastructure(location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_liters)
                    st.success("Status submitted.")
                else:
                    st.error("Location required.")

    infra_data = db.get_all_infrastructure()
    if infra_data:
        st.subheader("All Infrastructure Entries")
        st.table(infra_data)

        infra_df = pd.DataFrame(
            infra_data,
            columns=[
                "location", "generator_ok", "pump_ok", "pipe_leak",
                "road_condition", "comments", "water_available_liters"
            ]
        )

        def check_flag(row):
            flags = []
            if row["generator_ok"] == "No":
                flags.append("🛑 Generator Failure")
            if row["pump_ok"] == "No":
                flags.append("🛑 Pump Fault")
            if row["pipe_leak"] == "Yes":
                flags.append("💧 Pipe Leak")
            if row["road_condition"] in ["Flooded", "Muddy"] and row["generator_ok"] == "Yes":
                flags.append("🚫 Fuel Delivery Blocked")
            if row["water_available_liters"] < 10:
                flags.append("❗ Low Water Reserves")
            return ", ".join(flags) if flags else "✅ OK"

        infra_df["status"] = infra_df.apply(check_flag, axis=1)
        st.dataframe(
    infra_df.style.applymap(
        lambda v: 'background-color: #ffcccc' if '🛑' in v or '💧' in v or '❗' in v else 'background-color: #ccffcc',
        subset=['status']
    )
)

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

if infra_data is not None and len(infra_data) > 0:
    # Convert to list of dicts if needed
    if isinstance(infra_data, pd.DataFrame):
        records = infra_data.to_dict(orient="records")
    elif isinstance(infra_data, list):
        # If it's a list of tuples, convert to dicts
        if infra_data and not isinstance(infra_data[0], dict):
            columns = ["location", "generator_ok", "pump_ok", "pipe_leak", "road_condition", "comments", "water_available_liters"]
            records = [dict(zip(columns, row)) for row in infra_data]
        else:
            records = infra_data
    else:
        records = []

    infra_alerts = []
    for entry in records:
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
else:
    st.info("No infrastructure data available yet.")
    

st.markdown("---")
st.caption("Prototype v1.2 | Developed by George Arogo")
