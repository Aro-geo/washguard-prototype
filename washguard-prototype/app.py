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
from dotenv import load_dotenv
import altair as alt
import time

# Load environment variables
load_dotenv()

# Load sentiment pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

# Page config
st.set_page_config(page_title="WASHGuard AI", layout="wide")

# --- User Login  ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.sidebar:
        st.title("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == os.getenv("APP_USER") and password == os.getenv("APP_PASS"):
                st.session_state.authenticated = True
                st.experimental_rerun()  
                st.stop()
            else:
                st.warning("Incorrect username or password")
                st.stop()
    st.stop()

st.title("🚰 WASHGuard AI")

# --- Logout Button ---
with st.sidebar:
    if st.button("🔓 Logout"):
        st.session_state.authenticated = False
        st.experimental_rerun()
        st.stop()

# Sidebar navigation
tab = st.sidebar.radio("📋 Select Module", [
    "📊 Dashboard",

    "💧  Water Treatment",

    "🗣️ Feedback Analysis",

    "⚙️ Infrastructure Monitor"
])

# --- Always load data for dashboard cards ---
chlorine_data = db.get_all_chlorine()
quality_data = db.get_all_quality()
feedback_data = db.get_all_feedback()
infra_data = db.get_all_infrastructure()

# Alert Functions
def send_alert_email(subject, body):
    sender_email = os.getenv("ALERT_EMAIL")
    receiver_email = os.getenv("ALERT_RECEIVER")
    password = os.getenv("ALERT_PASSWORD")
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
    account_sid = os.getenv("TWILIO_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE")
    to_number = os.getenv("ALERT_PHONE")

    try:
        client = Client(account_sid, auth_token)
        client.messages.create(
            body=body,
            from_=from_number,
            to=to_number
        )
    except Exception as e:
        print("❌ SMS failed:", e)

# --- Dashboard ---
if tab == "📊 Dashboard":
    # --- Dashboard Cards ---
    if chlorine_data:
        df_chlorine = pd.DataFrame(chlorine_data, columns=["tap_stand_id", "date", "time", "chlorine_level"])
        low_chlorine = df_chlorine[df_chlorine["chlorine_level"] < 0.2]
        chlorine_alerts = f"{len(low_chlorine)} of {len(df_chlorine)}"
    else:
        chlorine_alerts = "0"

    if quality_data:
        df_quality = pd.DataFrame(quality_data, columns=["source_id", "turbidity", "odour_present"])
        high_turbidity = df_quality[df_quality["turbidity"] > 5]
        turbidity_issues = f"{len(high_turbidity)} of {len(df_quality)}"
    else:
        turbidity_issues = "0"

    if feedback_data:
        df_feedback = pd.DataFrame(feedback_data, columns=["household_id", "feedback_text"])
        df_feedback["sentiment"] = df_feedback["feedback_text"].apply(lambda x: sentiment_analyzer(x)[0]["label"])
        negative_count = df_feedback[df_feedback["sentiment"] == "NEGATIVE"].shape[0]
        feedback_alerts = f"{negative_count} negative"
        feedback_total = f"{len(df_feedback)} total reports"
    else:
        feedback_alerts = "0"
        feedback_total = "No feedback"

    risk_high = False
    risk_percent = 0
    if chlorine_data and len(low_chlorine) > 0:
        risk_high = True
        risk_percent = 100
    if quality_data and len(high_turbidity) > 0:
        risk_high = True
        risk_percent = 100
    if feedback_data and negative_count > 0:
        risk_high = True
        risk_percent = 100
    if infra_data:
        df_infra = pd.DataFrame(infra_data, columns=["location", "generator_ok", "pump_ok", "pipe_leak", "road_condition", "comments", "water_available_liters"])
        df_infra["status"] = df_infra.apply(lambda row: "❗" if row["generator_ok"] == "No" or row["pump_ok"] == "No" or row["pipe_leak"] == "Yes" or row["water_available_liters"] < 10 else "✅", axis=1)
        alerts_count = df_infra[df_infra["status"] == "❗"].shape[0]
        if alerts_count > 0:
            risk_high = True
            risk_percent = 100

    # columns for cards
    st.subheader("📈 System Summary Dashboard")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Chlorine Alerts 💧", chlorine_alerts, help="Tap stands with low chlorine levels")
    with col2:
        st.metric("Turbidity Issues 🌀", turbidity_issues, help="Water sources with high turbidity")
    with col3:
        st.metric("Community Feedback 💬", feedback_alerts, help=feedback_total)
    with col4:
        st.metric("Overall Risk Score ⚠️", "High (100%)" if risk_high else "Low (0%)", help="Based on all system indicators")

    # Chlorine Table and Trend 
    if not df_chlorine.empty:
        with st.expander("📊 Chlorine Monitoring Summary"):
            selected_id = st.selectbox("Filter by Tap Stand ID", ["All"] + df_chlorine["tap_stand_id"].unique().tolist())
            filtered = df_chlorine if selected_id == "All" else df_chlorine[df_chlorine["tap_stand_id"] == selected_id]
            st.dataframe(filtered)

            # Combine date and time for x-axis
            filtered = filtered.copy()
            filtered["datetime"] = pd.to_datetime(filtered["date"] + " " + filtered["time"])

            min_thresh = 0.2
            max_thresh = 0.5

            base = alt.Chart(filtered).mark_line(point=True, color="#339af0").encode(
                x=alt.X('datetime:T', title="Time"),
                y=alt.Y('chlorine_level:Q', title="Chlorine Level (mg/L)", scale=alt.Scale(domain=[0, 0.8])),
                tooltip=['datetime:T', 'chlorine_level:Q', 'tap_stand_id:N']
            )

            min_line = alt.Chart(pd.DataFrame({'y': [min_thresh]})).mark_rule(
                color='red', strokeDash=[4,2]
            ).encode(y='y:Q')

            max_line = alt.Chart(pd.DataFrame({'y': [max_thresh]})).mark_rule(
                color='red', strokeDash=[4,2]
            ).encode(y='y:Q')

            min_text = alt.Chart(pd.DataFrame({'y': [min_thresh], 'label': ['Min Threshold']})).mark_text(
                align='left', baseline='bottom', dx=5, dy=-5, color='red'
            ).encode(
                y='y:Q',
                text='label:N',
                x=alt.value(60)
            )

            max_text = alt.Chart(pd.DataFrame({'y': [max_thresh], 'label': ['Max Threshold']})).mark_text(
                align='left', baseline='bottom', dx=5, dy=-5, color='red'
            ).encode(
                y='y:Q',
                text='label:N',
                x=alt.value(60)
            )

            chart = (base + min_line + max_line + min_text + max_text).properties(
                title="Chlorine Level Monitoring"
            ).configure_title(
                fontSize=16,
                anchor='start',
                color='white',
            )

            st.altair_chart(chart, use_container_width=True)

    # Feedback Table 
    if not df_feedback.empty:
        with st.expander("💬 Feedback Sentiment Summary"):
            sentiment_filter = st.selectbox("Filter by Sentiment", ["All", "POSITIVE", "NEGATIVE"])
            filtered_feedback = df_feedback if sentiment_filter == "All" else df_feedback[df_feedback["sentiment"] == sentiment_filter]
            st.dataframe(filtered_feedback)

            # Sentiment Pie Chart 
            st.markdown("### 🥧 Feedback Sentiment Analysis")
            sentiment_counts = df_feedback["sentiment"].value_counts()
            fig, ax = plt.subplots(figsize=(5, 5))  

            # Utility to detect mobile 
            def is_mobile_view():
                try:
                    ua = st.runtime.scriptrunner.get_script_run_ctx().session_info.user_agent
                    return "Mobile" in ua or "Android" in ua or "iPhone" in ua
                except Exception:
                    return False

            is_mobile = is_mobile_view()
            fig_size = (2, 2) if is_mobile else (2, 2)
            fig, ax = plt.subplots(figsize=fig_size)

            # Custom text color for each sentiment
            def sentiment_text_colors(labels):
                colors = []
                for label in labels:
                    if label == "POSITIVE":
                        colors.append("green")
                    elif label == "NEGATIVE":
                        colors.append("red")
                    else:
                        colors.append("black")
                return colors

            wedges, texts, autotexts = ax.pie(
                sentiment_counts,
                labels=sentiment_counts.index,
                autopct="%1.1f%%",
                startangle=140,
                colors=["#2ecc71" if label == "POSITIVE" else "#e74c3c" for label in sentiment_counts.index],
            )
            # Set text color for labels and percentages
            for i, text in enumerate(texts):
                text.set_color(sentiment_text_colors(sentiment_counts.index)[i])
                text.set_fontweight("bold")
            for i, autotext in enumerate(autotexts):
                autotext.set_color(sentiment_text_colors(sentiment_counts.index)[i])
                autotext.set_fontweight("bold")

            ax.axis("equal")
            fig.patch.set_facecolor('#f0f0f0')
            st.pyplot(fig, use_container_width=False)

    # Infrastructure Table 
    if not df_infra.empty:
        with st.expander("🔧 Infrastructure Status"):
            # --- High Risk Warning & Bar Chart ---
            high_risk_zones = df_infra[df_infra["water_available_liters"] < 10]
            if not high_risk_zones.empty:
                zone_names = ", ".join(high_risk_zones["location"].astype(str))
                st.error(
                    f"**High Risk Zones Detected**\n\n"
                    f"{len(high_risk_zones)} locations require immediate attention. "
                    f"Water availability is critical at {zone_names}."
                )

            # Bar chart for water availability by zone
            st.markdown("#### Water Availability by Zone")
            st.caption("Current water availability in liters per household")
            bar_chart = alt.Chart(df_infra).mark_bar(color="#0099f6").encode(
                x=alt.X("location:N", title="Zone"),
                y=alt.Y("water_available_liters:Q", title="Liters"),
                tooltip=["location", "water_available_liters"]
            ).properties(height=250)
            st.altair_chart(bar_chart, use_container_width=True)

            # Status filter and table
            status_filter = st.selectbox("Filter by Status", ["All", "❗", "✅"])
            filtered_infra = df_infra if status_filter == "All" else df_infra[df_infra["status"] == status_filter]
            st.dataframe(filtered_infra)

    # --- Alert System Form ---
    with st.container():
        st.subheader("🔔 Alert System")
        st.caption("Send notifications to field teams about critical issues")
        with st.form("alert_form"):
            subject = st.text_input("Alert Subject", value="WASH Alert: Critical Infrastructure Issue")
            message = st.text_area("Alert Message", placeholder="Describe the issue and required actions…")
            colA, colB = st.columns(2)
            with colA:
                send_email = st.toggle("Email", value=True)
            with colB:
                send_sms = st.toggle("SMS", value=True)
            submitted = st.form_submit_button("Send Alert", use_container_width=True)
            if submitted:
                if not message.strip():
                    st.error("Alert message cannot be empty.")
                else:
                    if send_email:
                        send_alert_email(subject, message)
                    if send_sms:
                        send_sms_alert(message)
                    st.success("Alert sent successfully.")
        

# --- Water Treatment ---
elif tab == "💧  Water Treatment":
    st.subheader("💧 Water Treatment Recommendations")

    # Chlorine Level
    st.markdown("### 🧪 Chlorine Level Monitor")
    with st.expander("➕ Add Chlorine Reading"):
        with st.form("chlorine_form"):
            tap_id = st.text_input("Tap Stand ID")
            date = st.date_input("Date")
            time_val = st.time_input("Time")
            level = st.number_input("Chlorine Level (mg/L)", min_value=0.0, max_value=2.0)
            submitted = st.form_submit_button("Submit")
            if submitted:
                if tap_id:
                    db.insert_chlorine(tap_id, date.isoformat(), time_val.isoformat(), level)
                    st.success("Chlorine reading submitted.")
                else:
                    st.error("Tap Stand ID required.")

    chlorine_data = db.get_all_chlorine()
    if chlorine_data:
        df = pd.DataFrame(chlorine_data, columns=["tap_stand_id", "date", "time", "chlorine_level"])
        df["status"] = df["chlorine_level"].apply(lambda x: "🔴 Low" if x < 0.2 else "🔴 High" if x > 0.5 else "✅ OK")
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), file_name="chlorine_data.csv")

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
        st.download_button("Download CSV", df_quality.to_csv(index=False), file_name="water_quality_data.csv")
    else:
        st.info("No water quality readings yet.")

# --- Feedback Analysis ---
elif tab == "🗣️ Feedback Analysis":
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
        st.download_button("Download CSV", df.to_csv(index=False), file_name="feedback_data.csv")
        words = " ".join(df["feedback_text"].tolist())
        wordcloud = WordCloud(background_color="white").generate(words)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info("No feedback yet.")

# --- Infrastructure Monitor ---
elif tab == "⚙️ Infrastructure Monitor":
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
        st.download_button("Download CSV", df.to_csv(index=False), file_name="infrastructure_data.csv")

        # --- Alerts Table ---
        alerts_df = df[df["status"] != "✅ OK"]
        if not alerts_df.empty:
            st.warning("🚨 Issues Detected in the Following Locations")
            st.dataframe(alerts_df[["location", "status", "comments", "water_available_liters", "road_condition"]])

            # --- Risk Score ---
            st.markdown("**💡 Risk Prediction**")
            st.markdown("Zones with < 10L, active faults, or fuel blockage are High Risk")
            high_risk = alerts_df[alerts_df["water_available_liters"] < 100]
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


# Add caption at the bottom of the sidebar
st.sidebar.markdown(
    """
    <div style='position: fixed; bottom: 0; width: 18rem;'>
        <small>Prototype v1.4 | Developed by George Arogo</small>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")
