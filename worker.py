from server import create_app
from server.tools.settings import celery

app = create_app()

if __name__ == "__main__":
    app.app_context().push()

#!/usr/bin/env python
#concept sourced from Miguel Grinberg. Thank you!
#Open new terminal window and enter the following to run worker locally:
#celery -A worker worker.celery --loglevel=DEBUG
