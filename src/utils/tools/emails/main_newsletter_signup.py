from datetime import datetime

from src.utils.settings import smtp_config

from ._email_body import EmailBodyMessenger, EmailBodyFormatter


def get_newsletter_welcome(newsletter_data):

    email_body_messenger = EmailBodyMessenger()
    email_body_formatter = EmailBodyFormatter()

    dt_now = datetime.now()
    email_body_formatter.preview = f"New newsletter signup!: '{newsletter_data['email']}' on {dt_now.strftime('%B %-d, %Y')}"

    email_body_formatter.user = "Hubbub Team"

    email_body_formatter.introduction = "New signup in town! Check it below."

    email_body_formatter.content = f"""
        <p>New Name: <bold>{newsletter_data['name']}</bold></p>
        <p>New Email: <bold>{newsletter_data['email']}</bold></p>
        """

    email_body_formatter.conclusion = "Thanks!"

    body = email_body_formatter.build()

    email_body_messenger.subject = "[Internal] Newsletter Signup"
    email_body_messenger.to = (smtp_config.DEFAULT_RECEIVER,)
    email_body_messenger.body = body
    return email_body_messenger
