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
    def get_url(path):
        url = "/".join([AWSConfig.S3_LINK, path])
        return url

class MailConfig:
    _instance = None
    SERVER = None
    PORT = None
    USE_TLS = None
    USE_SSL = None
    USERNAME = None
    PASSWORD = None
    DEFAULT_SENDER = None
    MAX_EMAILS = None
    ASCII_ATTACHMENTS = None

    def __init__(self):
        if MailConfig._instance:
            #TODO: log that this problem happened
            raise Exception("MAIL CLIENT Connection should only be created once in the app.")
        else:
            SERVER  = os.environ['MAIL_SERVER']
            PORT  = int(os.environ['MAIL_PORT']) #587?
            USERNAME  = os.environ['MAIL_USERNAME']
            PASSWORD  = os.environ['MAIL_PASSWORD']
            DEFAULT_SENDER  = ('Hubbub', os.environ['MAIL_DEFAULT_SENDER'])
            MAX_EMAILS  = None
            ASCII_ATTACHMENTS  = False

            if os.environ.get('MAIL_USE_TLS') == '1':
                USE_TLS = True
                USE_SSL = False #gmail: true
            elif os.environ.get('MAIL_USE_SSL') == '1':
                USE_TLS = False #gmail: false
                USE_SSL = True
            else:
                raise Exception("You must select either TLS or SSL connection. Check client.")

            MailConfig._instance = self

    @staticmethod
    def get_instance():
        if MailConfig._instance is None:
            MailConfig()
        return MailConfig._instance

#FLASK CONFIGS------------------------------------

class Config:
    #ReCaptcha
    RECAPTCHA_SITE_KEY = os.environ['RECAPTCHA_PUBLIC_KEY']
    RECAPTCHA_SECRET_KEY = os.environ['RECAPTCHA_PRIVATE_KEY']

    #Celery
    CELERY_BROKER_URL = os.environ['CLOUDAMQP_URL']
    BROKER_POOL_LIMIT = 1
    #CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']

    DEBUG = False
    TESTING  =  False

    #Upload management
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    #email quick config
    MAIL = MailConfig.get_instance()
    MAIL_SERVER = MAIL.SERVER
    MAIL_PORT = MAIL.PORT
    MAIL_USE_TLS = MAIL.USE_TLS
    MAIL_USE_SSL = MAIL.USE_SSL
    MAIL_USERNAME = MAIL.USERNAME
    MAIL_PASSWORD = MAIL.PASSWORD
    MAIL_DEFAULT_SENDER = MAIL.DEFAULT_SENDER
    MAIL_MAX_EMAILS = MAIL.MAX_EMAILS
    MAIL_ASCII_ATTACHMENTS = MAIL.ASCII_ATTACHMENTS

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'dev'

class ProductionConfig(Config):
    SECRET_KEY = os.environ['SECRET_KEY']

class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = 'dev'
