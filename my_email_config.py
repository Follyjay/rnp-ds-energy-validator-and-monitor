import logging
import smtplib
from email.mime.text import MIMEText
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENTS, SMTP_SERVER, SMTP_PORT

def send_email(msg_text, hour):
    """
    Sends an email alert when a mismatch between RNP (CSV) and DS (XML) data is detected.
    
    Parameters:
        msg_text (str): The body of the alert message.
        hour (str): The hour label (e.g., "14:00 - 15:00") for which the mismatch occurred.
    Sends:
        An email to the predefined recipients with subject and message content.
    """
    # Create a plain-text email message
    msg = MIMEText(msg_text)
    msg['Subject'] = f"[ALERT] RNP-DS Mismatch at {hour}"
    msg['From'] = EMAIL_SENDER
    msg['To'] = ", ".join(EMAIL_RECIPIENTS)

    try:
        # Connect securely to SMTP server using SSL
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENTS, msg.as_string())
            print("✅ Alert email sent.", end="\r")
    except Exception as e:
        print(f"🚨 Email sending failed: {e}")
        logging.error(f"Email sending failed: {e}")