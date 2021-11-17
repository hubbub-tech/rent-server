import os
import boto3

#SUPPORTING CONFIGS------------------------------

class AWSConfig:
    _instance = None
    S3_OBJECT = None
    S3_LINK = None
    AWS_ACCESS_KEY_ID = None
    AWS_SECRET_ACCESS_KEY = None

    def __init__(self):
        if AWSConfig._instance:
            #TODO: log that this problem happened
            raise Exception("AWS Connection should only be created once in the app.")
        else:
            AWSConfig.S3_LINK = "https://{}.s3.amazonaws.com".format(os.environ['S3_BUCKET'])
            AWSConfig.AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
            AWSConfig.AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
            AWSConfig.S3_BUCKET = os.environ['S3_BUCKET']
            AWSConfig.set_s3()

            AWSConfig._instance = self

    @staticmethod
    def get_instance():
        if AWSConfig._instance is None:
            AWSConfig()
        return AWSConfig._instance

    @staticmethod
    def set_s3():
        if AWSConfig.S3_OBJECT is None:
            s3 = boto3.client(
                's3',
                aws_access_key_id=AWSConfig.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWSConfig.AWS_SECRET_ACCESS_KEY
            )
            AWSConfig.S3_OBJECT = s3

    @staticmethod
    def get_s3_resource():
        if AWSConfig._instance:
            s3_resource = boto3.resource("s3")
            return s3_resource
        else:
            raise Exception("An instance of the AWSConfig must be created before accessing s3.")

    @staticmethod
    def get_url(dir):
        url = "/".join([AWSConfig.S3_LINK, dir])
        return url

class MailConfig:
    _instance = None
    DEFAULT_SENDER = None
    SENDGRID_API_KEY = None

    def __init__(self):
        if MailConfig._instance:
            #TODO: log that this problem happened
            raise Exception("MAIL CLIENT Connection should only be created once in the app.")
        else:
            MailConfig.DEFAULT_RECEIVER = os.environ["MAIL_DEFAULT_RECEIVER"]
            MailConfig.DEFAULT_SENDER = os.environ["MAIL_DEFAULT_SENDER"]
            MailConfig.DEFAULT_ADMIN = os.environ["MAIL_DEFAULT_ADMIN"]
            MailConfig.SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
            MailConfig._instance = self

    @staticmethod
    def get_instance():
        if MailConfig._instance is None:
            MailConfig()
        return MailConfig._instance

#FLASK CONFIGS------------------------------------

class Config:

    SECRET_KEY = os.environ['SECRET_KEY']
    TESTING = False

    #Celery
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_ORIGIN = os.environ['CORS_ALLOW_ORIGIN']

    CELERY_BROKER_URL = os.environ['CLOUDAMQP_URL']
    CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']
    BROKER_POOL_LIMIT = 1

    #Upload management
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    #ReCaptcha
    ReCAPTCHA_SERVER_API_KEY= os.environ['ReCAPTCHA_SERVER_API_KEY']

class TestConfig:

    SECRET_KEY = 'dev'
    TESTING = True

    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_ORIGIN = 'http://localhost:3000'

    CELERY_BROKER_URL = 'amqp://localhost'
    CELERY_RESULT_BACKEND = 'rpc://localhost'
    BROKER_POOL_LIMIT = 1

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
