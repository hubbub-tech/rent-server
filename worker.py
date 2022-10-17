from src import create_app
from src.utils import celery

app = create_app()
app.app_context().push()


#!/usr/bin/env python
# concept sourced from Miguel Grinberg. Thank you!
# Open new terminal window and enter the following to run worker locally:
# rabbitmq-server
# Then enter the following in another terminal window:
# celery -A worker.celery worker --loglevel=DEBUG
