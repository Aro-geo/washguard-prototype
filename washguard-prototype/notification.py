import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from twilio.rest import Client
from dotenv import load_dotenv  

load_dotenv()  

# --- EMAIL CONFIGURATION ---
EMAIL_ADDRESS = os.getenv("ALERT_EMAIL")
EMAIL_PASSWORD = os.getenv("ALERT_PASSWORD")
EMAIL_RECEIVER = os.getenv("ALERT_RECEIVER")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# --- SMS CONFIGURATION (TWILIO) ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE")
ALERT_PHONE_NUMBER = os.getenv("ALERT_PHONE")

def send_alert_email(subject, body):
    print(f"Email sent: {subject}\n{body}")

def send_sms_alert(message):
    print(f"SMS sent: {message}")
