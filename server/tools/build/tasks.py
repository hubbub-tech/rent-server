from flask_mail import Mail, Message

from server.tools.settings import celery

mail = Mail()

@celery.task
def send_async_email(subject, to, body, error=None):
    recipients = ['hubbubcu@gmail.com']
    try:
        msg = Message(subject, recipients=recipients, cc=to)
        msg.html = body
        mail.send(msg)
    except Exception as e:
        print(e)
