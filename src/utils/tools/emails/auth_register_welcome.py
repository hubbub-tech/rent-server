from datetime import datetime

from src.utils.settings import smtp_config
from src.utils.settings import CLIENT_DOMAIN

from ._email_body import EmailBodyMessenger, EmailBodyFormatter


def get_welcome_email(user):

    email_bod_messenger = EmailBodyMessenger()
    email_body_formatter = EmailBodyFormatter()

    dt_now = datetime.now()
    email_body_formatter.preview = f"Welcome to Hubbub! We're excited to have you join on {dt_now.strftime('%B %-d, %Y')}"

    email_body_formatter.user = user.name

    email_body_formatter.introduction = """
        <p>
            Welcome to Hubbub! We are so excited to have you join our movement for
            flexible ownership! Hubbub is passionate about getting the maximum use
            out of our items and keeping the maximum number of items out of landfill.
        </p>
        <p>
            Our other driving mission is to make any item accessible to anyone while
            empowering communities. We are a brand that hopefully makes you feel
            good about shopping!
        </p>
        """

    link_to_html = email_body_formatter.make_link(CLIENT_DOMAIN + "/items/feed", "here")
    email_body_formatter.content = f"""
        As a member, you can rent any item on the platform. Get started renting
        {link_to_html}. We have more features in the works, so stay tuned!
        """

    email_body_formatter.conclusion = f"If you have any questions, please contact us at {smtp_config.DEFAULT_RECEIVER}."

    body = email_body_formatter.build()

    email_bod_messenger.subject = f"[Hubbub] Welcome, {user.name}!"
    email_bod_messenger.to = (user.email, smtp_config.DEFAULT_RECEIVER)
    email_bod_messenger.body = body
    return email_bod_messenger
