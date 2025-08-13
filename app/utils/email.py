import resend
import os

# Configure Resend API key from Render env vars
resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(to: str, subject: str, html_content: str, from_email: str = "Clutter Haven <noreply@clutterhaven.com>"):
    """
    Sends an email using Resend.
    """
    try:
        resend.Emails.send({
            "from": from_email,
            "to": [to],
            "subject": subject,
            "html": html_content
        })
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False
