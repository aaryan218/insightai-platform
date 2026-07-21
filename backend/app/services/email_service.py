from typing import Optional


class EmailService:
    """Simple email service abstraction for dev and production wiring.

    In development this can just log emails; in production replace with
    an implementation that sends via an SMTP provider or API.
    """

    def __init__(self):
        self.last_sent: Optional[dict] = None

    def send(self, to: str, subject: str, body: str) -> None:
        # Development-friendly: store last_sent and print to logs.
        self.last_sent = {"to": to, "subject": subject, "body": body}
        # For now, print so devs can copy the verification/reset link.
        print(f"[EMAIL] To: {to} Subject: {subject}\n{body}")


email_service = EmailService()
