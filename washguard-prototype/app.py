# WASHGuard AI Prototype Streamlit App

import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from transformers import pipeline
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

# Load sentiment pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

# Title
st.set_page_config(page_title="WASHGuard AI Dashboard", layout="wide")
st.title("🚰 WASHGuard AI Dashboard")

# Load data (mock)
@st.cache_data
def load_data():
    chlorine_df = pd.DataFrame({
        "tap_stand_id": ["TS-001", "TS-002", "TS-003"],
        "timestamp": pd.to_datetime(["2025-05-22 09:00", "2025-05-22 09:10", "2025-05-22 09:15"]),
        "chlorine_level": [0.18, 0.26, 0.55]
    })

    water_quality_df = pd.DataFrame({
        "source_id": ["WS-001", "WS-002"],
        "turbidity": [7.2, 3.0],
        "odour_present": ["Yes", "No"]
    })

    feedback_df = pd.DataFrame({
        "household_id": ["HH-001", "HH-002", "HH-003"],
        "feedback_text": [
            "Water smells bad and no soap in stock",
            "Latrine is clean, but chlorine taste is strong",
            "Kids complain about dirty water and no aqua tabs"
        ]
    })

    infra_df = pd.DataFrame({
        "location": ["Zone A", "Zone B", "Zone C"],
        "generator_ok": ["Yes", "No", "Yes"],
        "pump_ok": ["Yes", "Yes", "No"],
        "pipe_leak": ["No", "Yes", "No"],
        "road_condition": ["Good", "Muddy", "Flooded"],
        "comments": [
            "All systems functional",
            "Generator won't start, needs oil",
            "Pump pressure low, maybe blockage"
        ],
        "water_available_liters": [20, 5, 8]
    })

    return chlorine_df, water_quality_df, feedback_df, infra_df

chlorine_df, water_quality_df, feedback_df, infra_df = load_data()

# Sidebar navigation
tab = st.sidebar.radio("Select Module", [
    "Chlorine Monitor",
    "Water Treatment",
    "Feedback Analysis",
    "Infrastructure Monitor"
])

# Email Alert Function (Real SMTP)
def send_alert_email(subject, body):
    sender_email = "your_email@gmail.com"
    receiver_email = "geokullo@gmail.com"
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("✅ Email sent to", receiver_email)
    except Exception as e:
        print("❌ Email failed:", e)

# SMS Alert Function (Twilio)
def send_sms_alert(body):
    account_sid = os.getenv("TWILIO_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE")
    to_number = "+254726796020"

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=body,
            from_=from_number,
            to=to_number
        )
        print("✅ SMS sent:", message.sid)
    except Exception as e:
        print("❌ SMS failed:", e)

# --- Chlorine Monitor ---
if tab == "Chlorine Monitor":
    st.subheader("🧪 Chlorine Level Monitor")

    def check_anomaly(level):
        if level < 0.2:
            return "🔴 Low – Re-dose"
        elif level > 0.5:
            return "🔴 High – Re-check"
        else:
            return "✅ OK"

    chlorine_df["status"] = chlorine_df["chlorine_level"].apply(check_anomaly)
    st.dataframe(chlorine_df)

# --- Water Treatment ---
elif tab == "Water Treatment":
    st.subheader("💧 Water Treatment Recommendations")

    def recommend(turbidity):
        return "PUR" if turbidity > 5 else "Aqua Tabs"

    water_quality_df["treatment"] = water_quality_df["turbidity"].apply(recommend)
    st.dataframe(water_quality_df)

# --- Feedback Analysis ---
elif tab == "Feedback Analysis":
    st.subheader("🗣️ Community Feedback NLP")

    feedback_df["sentiment"] = feedback_df["feedback_text"].apply(lambda x: sentiment_analyzer(x)[0]["label"])
    st.dataframe(feedback_df)

    text = " ".join(feedback_df["feedback_text"].tolist())
    wordcloud = WordCloud(background_color='white', width=800, height=400).generate(text)

    st.markdown("**Keyword Cloud**")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

# --- Infrastructure Monitor ---
elif tab == "Infrastructure Monitor":
    st.subheader("⚙️ Infrastructure Status")

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
        return ", ".join(flags) if flags else "✅ OK"

    infra_df["status"] = infra_df.apply(check_flag, axis=1)
    st.dataframe(infra_df)

    alerts = infra_df[infra_df["status"] != "✅ OK"]
    if not alerts.empty:
        st.warning("🚨 **Infrastructure Alerts**")
        for i, row in alerts.iterrows():
            st.write(f"🔧 **{row['location']}** – {row['status']}")
            subject = f"WASH Alert: {row['location']} – {row['status']}"
            body = f"Issue detected in {row['location']} with status: {row['status']}
Comments: {row['comments']}
Water Available: {row['water_available_liters']}L
Road Condition: {row['road_condition']}"
            send_alert_email(subject, body)
            send_sms_alert(body)

        st.markdown("---")
        st.markdown("**🔄 Maintenance Task Log (Mock)**")
        st.dataframe(alerts[["location", "status", "comments", "water_available_liters", "road_condition"]])

        st.markdown("**💡 Link to Risk Prediction**")
        st.markdown("Risk Score (Prototype): Zones with < 10L, active faults, or fuel blockage are High Risk")
        high_risk = alerts[alerts["water_available_liters"] < 10]
        st.dataframe(high_risk[["location", "water_available_liters", "status"]])

st.markdown("---")
st.caption("Prototype v1.1 | Developed by George Arogo")
