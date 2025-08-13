from fastapi import APIRouter
from app.utils.email import send_email

router = APIRouter()

@router.get("/test-email")
def test_email():
    # Replace this email with yours to receive the test
    to = "your-email@example.com"
    subject = "Test Email from Clutter Haven"
    html = "<h1>Hello!</h1><p>This is a test email sent via Resend from Render.</p>"

    if send_email(to, subject, html):
        return {"message": "Email sent successfully!"}
    else:
        return {"message": "Email failed to send"}
