from datetime import datetime

from src.utils.settings import smtp_config

from ._email_body import EmailBodyMessenger, EmailBodyFormatter

def get_password_reset_email(user, reset_link):

    email_body_messenger = EmailBodyMessenger()
    email_body_formatter = EmailBodyFormatter()

    dt_now = datetime.now()
    email_body_formatter.preview = f"Someone requested a password recovery on {dt_now.strftime('%Y-%m-%d %H:%M:%S.%f')}"

    email_body_formatter.user = user.name

    link_to_html = email_body_formatter.make_link(reset_link, "here")
    email_body_formatter.introduction = f"""
        Recently, you placed a request to recover your password. If you requested
        this, follow the link {link_to_html} to recover your password.
        """

    email_body_formatter.content = "The link will expire after you have changed your password. Please do not share."

    email_body_formatter.conclusion = f"If you did not place this request, please report to admins at {smtp_config.DEFAULT_RECEIVER}. Thanks!"

    body = email_formatter.build()

    email_body_messenger.subject = "[Hubbub] Recover Your Password"
    email_body_messenger.to = (user.email, smtp_config.DEFAULT_RECEIVER)
    email_body_messenger.body = body

    return email_body_messenger
