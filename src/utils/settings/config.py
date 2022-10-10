import os
import boto3

#SUPPORTING CONFIGS------------------------------

class AWSS3Config:
    _instance = None
    S3_OBJECT = None
    S3_LINK = None
    AWS_ACCESS_KEY_ID = None
    AWS_SECRET_ACCESS_KEY = None

    def __init__(self):
        if AWSS3Config._instance:
            #TODO: log that this problem happened
            raise Exception("AWS Connection should only be created once in the app.")
        else:
            AWSS3Config.S3_LINK = "https://{}.s3.amazonaws.com".format(os.environ['S3_BUCKET'])
            AWSS3Config.AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
            AWSS3Config.AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
            AWSS3Config.S3_BUCKET = os.environ['S3_BUCKET']
            AWSS3Config.set_s3()

            AWSS3Config._instance = self

    @staticmethod
    def get_instance():
        if AWSS3Config._instance is None:
            AWSS3Config()
        return AWSS3Config._instance

    @staticmethod
    def set_s3():
        if AWSS3Config.S3_OBJECT is None:
            s3 = boto3.client(
                's3',
                aws_access_key_id=AWSS3Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWSS3Config.AWS_SECRET_ACCESS_KEY
            )
            AWSS3Config.S3_OBJECT = s3

    @staticmethod
    def get_s3_resource():
        if AWSS3Config._instance:
            s3_resource = boto3.resource("s3")
            return s3_resource
        else:
            raise Exception("An instance of the AWSConfig must be created before accessing s3.")

    @staticmethod
    def get_url(dir):
        url = "/".join([AWSS3Config.S3_LINK, dir])
        return url


class GCloudConfig:
    _instance = None

    def __init__(self):
        if GCloudConfig._instance:
            raise Exception("GCloud has already been created in this session.")
        else:
            GCloudConfig.STORAGE_BUCKETS = {
                "items": "shop-items"
            }
            GCloudConfig.PROJECT = "hubbub-assets"
            GCloudConfig.ACCESS_CREDENTIALS = os.getenv("GCLOUD_ACCESS_CREDENTIALS")
            GCloudConfig._instance = self


    @staticmethod
    def get_instance():
        if GCloudConfig._instance is None:
            GCloudConfig()
        return GCloudConfig._instance


class CaptchaConfig:
    #ReCaptcha
    ReCAPTCHA_SERVER_API_KEY = os.environ['ReCAPTCHA_SERVER_API_KEY']
    ReCAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


class SMTPConfig:
    _instance = None
    DEFAULT_SENDER = None
    SENDGRID_API_KEY = None

    def __init__(self):
        if SMTPConfig._instance:
            #TODO: log that this problem happened
            raise Exception("MAIL CLIENT Connection should only be created once in the app.")
        else:
            SMTPConfig.DEFAULT_RECEIVER = os.environ["MAIL_DEFAULT_RECEIVER"]
            SMTPConfig.DEFAULT_SENDER = os.environ["MAIL_DEFAULT_SENDER"]
            SMTPConfig.DEFAULT_ADMIN = os.environ["MAIL_DEFAULT_ADMIN"]
            SMTPConfig.SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
            SMTPConfig._instance = self

    @staticmethod
    def get_instance():
        if SMTPConfig._instance is None:
            SMTPConfig()
        return SMTPConfig._instance

#FLASK CONFIGS------------------------------------

class FlaskConfig:

    SECRET_KEY = os.environ['SECRET_KEY']
    TESTING = False

    #Celery
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_ORIGIN = os.environ['CORS_ALLOW_ORIGIN']

    CELERY_BROKER_URL = os.environ['CLOUDAMQP_URL']
    CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']
    BROKER_POOL_LIMIT = 1


class TestFlaskConfig:

    SECRET_KEY = 'dev'
    TESTING = True

    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_ORIGIN = 'http://localhost:3000'

    CELERY_BROKER_URL = 'amqp://localhost'
    CELERY_RESULT_BACKEND = 'rpc://localhost'
    BROKER_POOL_LIMIT = 1

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
