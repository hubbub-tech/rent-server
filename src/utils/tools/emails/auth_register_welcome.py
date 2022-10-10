from datetime import datetime

from src.utils.settings import smtp_config

from ._email_data import EmailData
from ._email_body_formatter import EmailBodyFormatter


def get_welcome_email(user):

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    email_body_formatter.preview = f"Welcome to Hubbub! We're excited to have you join on {datetime.now().strftime('%B %-d, %Y')} - "

    email_body_formatter.user = user.name

    email_body_formatter.introduction = """
            Welcome to Hubbub! We are so excited to have you join our movement for
            flexible ownership! Hubbub is passionate about getting the maximum use
            out of our items and keeping the maximum number of items out of landfill.
        </p>
        <p>
            Our other driving mission is to make any item accessible to anyone while
            empowering communities. We are a brand that hopefully makes you feel
            good about shopping!
        """

    email_body_formatter.content = """
        <p>
            As a member, you can rent any item on the platform. Get started renting
            <a href="https://www.hubbub.shop/inventory">here</a>. We have more features
            in the works, so stay tuned!
        </p>
        """
        #and you can learn more about listing <a href="https://www.hubbub.shop/how-to-list">here</a>
    email_body_formatter.conclusion = f"""
        You can also go to your account portal on the website to view items you
        are renting with other features coming soon! If you have any questions, please
        contact us at {smtp_config.DEFAULT_RECEIVER}.
        """

    body = email_body_formatter.build()

    email_data.subject = f"[Hubbub] Welcome, {user.name}!"
    email_data.to = (user.email, smtp_config.DEFAULT_RECEIVER)
    email_data.body = body
    return email_data
