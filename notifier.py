import os
import smtplib
from email.message import EmailMessage
import requests

def send_email(subject: str, body: str, to_addr: str):
    host = os.getenv('SMTP_HOST')
    port = int(os.getenv('SMTP_PORT', '587'))
    user = os.getenv('SMTP_USER')
    pwd = os.getenv('SMTP_PASS')
    if not host or not to_addr:
        return False
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = user or 'noreply@example.com'
    msg['To'] = to_addr
    msg.set_content(body)
    try:
        with smtplib.SMTP(host, port) as s:
            s.starttls()
            if user and pwd:
                s.login(user, pwd)
            s.send_message(msg)
        return True
    except Exception:
        return False

def send_whatsapp(message: str, to_number: str):
    # Placeholder for WhatsApp API integration (e.g., Twilio)
    api_url = os.getenv('WHATSAPP_API_URL')
    api_key = os.getenv('WHATSAPP_API_KEY')
    if not api_url or not api_key or not to_number:
        return False
    try:
        resp = requests.post(api_url, json={
            'to': to_number,
            'message': message,
        }, headers={'Authorization': f'Bearer {api_key}'})
        return resp.status_code in (200, 201)
    except Exception:
        return False
