import logging
from logging.handlers import SMTPHandler

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from server.tools.settings import MailConfig

class SGSMTPHandler(SMTPHandler):

    def emit(self, record):
        """Custom email logging through SendGrid API."""
        MAIL = MailConfig.get_instance()
        msg = Mail(
            from_email=self.fromaddr,
            to_emails=self.toaddrs,
            subject=self.subject,
            html_content=self.format(record)
        )
        try:
            sg = SendGridAPIClient(MAIL.SENDGRID_API_KEY)
            response = sg.send(msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def build_mail_handler():
    MAIL = MailConfig.get_instance()

    mail_handler = SGSMTPHandler(
        mailhost='smtp.sendgrid.net',
        fromaddr=MAIL.DEFAULT_SENDER,
        toaddrs=['hubbubcu@gmail.com', 'adb2189@columbia.edu'],
        subject='Hubbub Server Error'
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
    print("built the damn thing...")
    return mail_handler
    
