import os
from flask import Flask
from flask_cors import CORS

from .tools.settings.config import Config

def create_app(config_object=Config()):
    template_dir = os.path.abspath('../public') # or might be another level up, not sure
    app = Flask(__name__, template_folder=template_dir)
    CORS(app)

    app.config.from_object(config_object)

    from .tools.settings import celery
    celery.conf.update(app.config)

    from .tools.build import mail
    mail.init_app(app)

    from .routes import main, auth, list, rent, process
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(list)
    app.register_blueprint(rent)
    app.register_blueprint(process)

    return app
