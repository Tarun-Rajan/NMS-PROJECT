import smtplib
from email.mime.text import MIMEText

def send_alert(device, ip):
    sender = "youremail@gmail.com"
    receiver = "admin@gmail.com"
    password = "your-app-password"  # Use Gmail App Password

    msg = MIMEText(f"⚠️ ALERT: {device} ({ip}) is not reachable!")
    msg["Subject"] = f"[ALERT] Network Device Failure: {device}"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(sender, password)
            s.send_message(msg)
        print(f"📩 Email alert sent for {device}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
