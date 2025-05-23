import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from twilio.rest import Client

# --- EMAIL CONFIGURATION ---
EMAIL_ADDRESS = os.getenv("ALERT_EMAIL") or "geokullo@gmail.com.com"
EMAIL_PASSWORD = os.getenv("ALERT_PASSWORD") or "your_email_password"
EMAIL_RECEIVER = os.getenv("ALERT_RECEIVER") or "receiver@example.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# --- SMS CONFIGURATION (TWILIO) ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_SID", "AC90d1d2449012ddc5cb27ac9b4a52385d")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN") or "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE") or "+13083373418"
ALERT_PHONE_NUMBER = os.getenv("ALERT_PHONE") or "+254726796020"

def send_alert_email(subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email alert sent.")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_sms_alert(body: str):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=ALERT_PHONE_NUMBER
        )
        print(f"SMS sent: {message.sid}")
    except Exception as e:
        print(f"Error sending SMS: {e}")
