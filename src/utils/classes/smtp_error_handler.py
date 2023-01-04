import ssl
import smtplib
import logging
from logging.handlers import SMTPHandler

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.utils.settings import smtp_config

class SGSMTPHandler(SMTPHandler):

    def emit(self, record):

        mime_multipart_msg = MIMEMultipart("alternative")
        mime_multipart_msg["Subject"] = self.subject
        mime_multipart_msg["From"] = self.fromaddr
        mime_multipart_msg["To"] = ",".join(self.toaddrs)

        message_processed = MIMEText(record, "html")
        mime_multipart_msg.attach(message_processed)

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_config.SMTP_SERVER, smtp_config.SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()

            server.login(smtp_config.DEFAULT_SENDER, smtp_config.DEFAULT_SENDER_PASSWORD)
            server.sendmail(smtp_config.DEFAULT_SENDER, self.toaddrs, mime_multipart_msg.as_string())


def build_mail_handler():
    mail_handler = SGSMTPHandler(
        mailhost=smtp_config.SMTP_SERVER,
        fromaddr=smtp_config.DEFAULT_SENDER,
        toaddrs=[smtp_config.DEFAULT_RECEIVER, smtp_config.DEFAULT_ADMIN],
        subject="[Hubbub] Internal Server Error"
    )
    mail_handler.setLevel(logging.WARNING)
    mail_handler.setFormatter(logging.Formatter(
        '''
        <!doctype html>
        <html lang="en">
            <body>
                <main>
                    <h3>Message type: %(levelname)s</h3>
                    <p>Location: %(pathname)s:%(lineno)d</p>
                    <p>Module: %(module)s</p>
                    <p>Function: %(funcName)s</p>
                    <p>Time: %(asctime)s</p>
                    <hr />
                    <h4>Message:</h4>
                    <p>%(message)s</p>
                </main>
            </body>
        </html>
        '''
    ))
    return mail_handler
