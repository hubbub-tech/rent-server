import os
import logging
from flask import Flask

from .utils.settings.config import FlaskConfig

def internal_server_error(e):
    print("RUNNING EXCEPTION HANDLER")
    return "Internal Server Error", 500

def create_app(config_object=FlaskConfig()):
    app = Flask(__name__)

    # Flask Config
    app.config.from_object(config_object)

    # Logger Config
    from .utils.classes import build_mail_handler
    mail_handler = build_mail_handler()

    for logger in (
        app.logger,
        logging.getLogger('werkzeug'),
        logging.getLogger('blubber-orm'),
    ):
        logger.addHandler(mail_handler)

    # Celery Worker Config
    from .utils.settings import celery
    celery.conf.update(app.config)

    from .routes import account
    from .routes import api
    from .routes import auth
    from .routes import checkout
    from .routes import delivery
    from .routes import items
    from .routes import list
    from .routes import main
    from .routes import orders

    app.register_blueprint(account)
    app.register_blueprint(api)
    app.register_blueprint(auth)
    app.register_blueprint(checkout)
    app.register_blueprint(delivery)
    app.register_blueprint(items)
    app.register_blueprint(list)
    app.register_blueprint(main)
    app.register_blueprint(orders)

    app.register_error_handler(500, internal_server_error)
    return app
