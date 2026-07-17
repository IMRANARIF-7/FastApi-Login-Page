import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()

SMPT_HOST = "smtp.gmail.com"
SMPT_PORT = 587
SMPT_USER = os.getenv("SMTP_USER")
SMPT_PASSWORD = os.getenv("SMTP_PASSWORD")

if not SMPT_USER or not SMPT_PASSWORD:
    raise ValueError("SMTP_USER and SMTP_PASSWORD must be set in .env")

def send_reset_email(to_email: str, reset_token: str):
    reset_link = f"http://localhost:8000/reset-password?token={reset_token}"
    subject = "Password Reset Request"
    body = f"Click the link below to reset your password:\n\n{reset_link}"
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMPT_USER
    msg["To"] = to_email
    
    with smtplib.SMTP(SMPT_HOST, SMPT_PORT) as server:
        server.starttls()
        server.login(SMPT_USER, SMPT_PASSWORD)
        server.send_message(msg)
        