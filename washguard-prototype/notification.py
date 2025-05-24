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

def send_alert_email(subject, body):
    # Placeholder: Implement email sending logic here
    print(f"Email sent: {subject}\n{body}")

def send_sms_alert(message):
    # Placeholder: Implement SMS sending logic here
    print(f"SMS sent: {message}")
