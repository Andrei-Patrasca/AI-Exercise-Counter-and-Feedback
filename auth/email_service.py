import smtplib
import random
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_SMTP, EMAIL_PORT


def is_valid_email_format(email):
    """Basic format check before even trying to send."""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def generate_code():
    """Generates a 6-digit verification code."""
    return str(random.randint(100000, 999999))


def send_verification_email(to_email, code):
    """
    Sends a verification code email.
    Returns (True, "sent") or (False, "error message").
    """
    subject = "FitTrack — Verify your email"
    body    = f"""
Hello!

Welcome to FitTrack. Your verification code is:

    {code}

Enter this code in the app to complete your registration.
The code expires after 10 minutes.

If you did not request this, ignore this email.

— The FitTrack Team
"""
    try:
        msg = MIMEMultipart()
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to_email, msg.as_string())

        return True, "sent"
    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed. Check your App Password in config.py."
    except smtplib.SMTPException as e:
        return False, f"Email error: {str(e)}"
    except Exception as e:
        return False, f"Could not send email: {str(e)}"


def send_reminder_email(to_email, username, reminder_time):
    """Sends a daily workout reminder email."""
    subject = "💪 FitTrack — Time to work out!"
    body    = f"""
Hey {username}!

This is your daily reminder to work out at {reminder_time}.

Open FitTrack and start your session. Let's go!

— The FitTrack Team
"""
    try:
        msg = MIMEMultipart()
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to_email, msg.as_string())

        return True, "sent"
    except Exception as e:
        return False, str(e)