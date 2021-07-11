import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from server.tools.settings import celery, MailConfig

@celery.task
def send_async_email(subject, to, body, error=None):
    MAIL = MailConfig.get_instance()
    msg = Mail(
        from_email=MAIL.DEFAULT_SENDER,
        to_emails=to,
        subject=subject,
        html_content=body
    )
    try:
        sg = SendGridAPIClient(MAIL.SENDGRID_API_KEY)
        response = sg.send(msg)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

@celery.task
def set_async_timeout(user_id):
    """Background task to unlock items if user does not transact."""
    from server import create_app
    app = create_app()
    try:
        with app.app_context():
            user = Users.get(user_id)
            cart_contents = user.cart.contents
            for item in cart_contents:
                item.unlock()
        print(f"All items in {user.name}'s cart have been unlocked again.") # TODO: log this
        return True
    except:
        #TODO: write a proper exception handling statement here
        print("The timeout failed.")
        return False
