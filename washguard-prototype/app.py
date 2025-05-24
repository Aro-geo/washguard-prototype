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

# Sidebar navigation
tab = st.sidebar.radio("Select Module", [
    "Water Treatment",
    "Feedback Analysis",
    "Infrastructure Monitor"
])

# Alert Functions
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
    except Exception as e:
        print("❌ Email failed:", e)

def send_sms_alert(body):
    account_sid = os.getenv("TWILIO_SID", "AC90d1d2449012ddc5cb27ac9b4a52385d")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE", "+13083373418")
    to_number = os.getenv("ALERT_PHONE", "+254726796020")

    try:
        client = Client(account_sid, auth_token)
        client.messages.create(
            body=body,
            from_=from_number,
            to=to_number
        )
    except Exception as e:
        print("❌ SMS failed:", e)

# --- Water Treatment ---
if tab == "Water Treatment":
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
        df = pd.DataFrame(chlorine_data, columns=["tap_stand_id", "date", "time", "chlorine_level"])
        df["status"] = df["chlorine_level"].apply(lambda x: "🔴 Low" if x < 0.2 else "🔴 High" if x > 0.5 else "✅ OK")
        st.dataframe(df)
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
    else:
        st.info("No feedback yet.")

# --- Infrastructure Monitor ---
elif tab == "Infrastructure Monitor":
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
        df = pd.DataFrame(infra_data, columns=["location", "generator_ok", "pump_ok", "pipe_leak", "road_condition", "comments", "water_available_liters"])
        def flag(row):
            issues = []
            if row["generator_ok"] == "No":
                issues.append("🛑 Generator")
            if row["pump_ok"] == "No":
                issues.append("🛑 Pump")
            if row["pipe_leak"] == "Yes":
                issues.append("💧 Leak")
            if row["road_condition"] in ["Muddy", "Flooded"] and row["generator_ok"] == "Yes":
                issues.append("🚫 Fuel Delivery Blocked")
            if row["water_available_liters"] < 10:
                issues.append("❗ Low Water Reserves")
            return ", ".join(issues) if issues else "✅ OK"
        df["status"] = df.apply(flag, axis=1)
        st.dataframe(df)

        # --- Alerts Table ---
        alerts_df = df[df["status"] != "✅ OK"]
        if not alerts_df.empty:
            st.warning("🚨 Issues Detected in the Following Locations")
            st.dataframe(alerts_df[["location", "status", "comments", "water_available_liters", "road_condition"]])

            # --- Risk Score ---
            st.markdown("**💡 Risk Prediction**")
            st.markdown("Zones with < 10L, active faults, or fuel blockage are High Risk")
            high_risk = alerts_df[alerts_df["water_available_liters"] < 10]
            if not high_risk.empty:
                st.dataframe(high_risk[["location", "water_available_liters", "status"]])

        # --- Send Alerts (avoid duplicates) ---
        alerted_locations = set()
        for _, row in alerts_df.iterrows():
            if row['location'] not in alerted_locations:
                subject = f"WASH Alert: {row['location']} – {row['status']}"
                body = (
                    f"Issue at {row['location']}: {row['status']}\n"
                    f"{row['comments']}\n"
                    f"Water: {row['water_available_liters']}L\n"
                    f"Road: {row['road_condition']}"
                )
                send_alert_email(subject, body)
                send_sms_alert(body)
                alerted_locations.add(row['location'])
    else:
        st.info("No infrastructure data yet.")

st.markdown("---")
st.caption("Prototype v1.2 | Developed by George Arogo")
