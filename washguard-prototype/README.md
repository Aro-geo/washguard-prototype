# WashGuard AI
WashGuard AI is a smart monitoring system for vehicle wash stations that detects anomalies, sends real-time alerts, and tracks usage trends. It helps prevent water waste, system failures, and downtime through automated intelligence.

Key Features
🔍 Real-time sensor data monitoring

⚠️ Automated anomaly detection (leaks, overuse, malfunctions)

📧 Instant alerts via email/SMS

📊 Wash cycle analytics and usage reports

🧠 AI-powered insights for preventive maintenance

## Setup

1. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your credentials:

```
EMAIL_PASSWORD=your_email_password_here
TWILIO_SID=your_twilio_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE=your_twilio_phone_number_here
```

4. Run the app:

```bash
streamlit run app.py
```
