from datetime import datetime

from src.utils import SMTP

from ._email_data import EmailData
from ._email_body_formatter import EmailBodyFormatter

def get_auth_password_reset_email(user, reset_link):

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    email_body_formatter.preview = f"Someone requested a password recovery on {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - "

    email_body_formatter.user = user.name

    email_body_formatter.introduction = f"""
        Recently, you placed a request to recover your password. If you requested
        this, follow the link <a href='{reset_link}'>here</a> to recover your password.
        """

    email_body_formatter.content = ""

    email_body_formatter.conclusion = f"I service, please report to admins at {SMTP.DEFAULT_RECEIVER} if you did not place this request. Thanks!"

    body = email_formatter.build()

    email_data.subject = "[Hubbub] Recover Your Password"
    email_data.to = (user.email, SMTP.DEFAULT_RECEIVER)
    email_data.body = body

    return email_data
