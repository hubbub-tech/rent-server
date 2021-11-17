import os
import logging
from flask import Flask
from flask_cors import CORS

from blubber_orm import get_db

from .tools.settings.config import Config

def internal_server_error(e):
    print("RUNNING EXCEPTION HANDLER")
    return "Internal Server Error", 500

def create_app(config_object=Config()):
    app = Flask(__name__)

    # Cross-Origin Config
    CORS(
        app,
        origins=[
            config_object.CORS_ALLOW_ORIGIN
        ],
        supports_credentials=config_object.CORS_SUPPORTS_CREDENTIALS
    )

    # Flask Config
    app.config.from_object(config_object)

    # Logger Config
    from .tools.build import build_mail_handler
    mail_handler = build_mail_handler()

    for logger in (
        app.logger,
        logging.getLogger('werkzeug'),
    ):
        logger.addHandler(mail_handler)

    # Celery Worker Config
    from .tools.settings import celery
    celery.conf.update(app.config)

    from .routes import main, auth, list, rent, process
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(list)
    app.register_blueprint(rent)
    app.register_blueprint(process)

    app.register_error_handler(500, internal_server_error)
    return app
