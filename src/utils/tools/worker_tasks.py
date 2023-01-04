from .files import base64_to_file
from .files import upload_to_awss3

from src.utils.settings import celery

@celery.task
def upload_file_async(filename, file_base64):

    from src import create_app
    app = create_app()

    try:
        with app.app_context():
            file, file_format = base64_to_file(file_base64)
            upload_to_awss3(file, filename, file_format)

        return True
    except:
        print("There was an error.")
        return False
