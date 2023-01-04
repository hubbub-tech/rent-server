import os
import json
import boto3

#SUPPORTING CONFIGS------------------------------

class AWSConfig:
    _instance = None
    S3_OBJECT = None

    def __init__(self):
        if AWSConfig._instance:
            #TODO: log that this problem happened
            raise Exception("AWS Connection should only be created once in the app.")
        else:
            self.S3_BUCKET = os.getenv('AWS_S3_BUCKET')
            self.S3_BASE_URL = f"https://{self.S3_BUCKET}.s3.amazonaws.com"

            self.ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
            self.SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

            AWSConfig._instance = self


    @staticmethod
    def get_instance():
        if AWSConfig._instance is None:
            AWSConfig()
        return AWSConfig._instance


    def get_base_url(self, bucket=None):
        if bucket:
            return f"https://{bucket}.s3.amazonaws.com"
        return self.S3_BASE_URL


    def get_s3(self):
        if AWSConfig.S3_OBJECT is None:
            try:
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=self.ACCESS_KEY_ID,
                    aws_secret_access_key=self.SECRET_ACCESS_KEY
                )
            except Exception as e:
                raise Exception(e)
        else:
            s3 = AWSConfig.S3_OBJECT
        return s3


    @staticmethod
    def get_s3_resource():
        if AWSConfig._instance:
            s3_resource = boto3.resource("s3")
            return s3_resource
        else:
            raise Exception("An instance of the AWSConfig must be created before accessing s3.")



class GCloudConfig:
    _instance = None

    def __init__(self):
        if GCloudConfig._instance:
            raise Exception("GCloud has already been created in this session.")
        else:
            self.STORAGE_BUCKET = "shop-items"
            self.PROJECT = "hubbub-assets"
            self.ACCESS_CREDENTIALS_PRIVATE_JSON = os.getenv("GCLOUD_ACCESS_CREDENTIALS_PRIVATE_JSON")
            self.ACCESS_CREDENTIALS_PRIVATE_KEY = os.getenv("GCLOUD_ACCESS_CREDENTIALS_PRIVATE_KEY")
            self.ACCESS_CREDENTIALS_PRIVATE_KEY_ID = os.getenv("GCLOUD_ACCESS_CREDENTIALS_PRIVATE_KEY_ID")
            GCloudConfig._instance = self

            self.inject_private_key_into_json()


    def inject_private_key_into_json(self):
        if self.ACCESS_CREDENTIALS_PRIVATE_KEY:
            with open(self.ACCESS_CREDENTIALS_PRIVATE_JSON, "r") as gcloud_auth_file:
                gcloud_auth_data = json.load(gcloud_auth_file)
                gcloud_auth_data["private_key_id"] = self.ACCESS_CREDENTIALS_PRIVATE_KEY_ID
                gcloud_auth_data["private_key"] = self.ACCESS_CREDENTIALS_PRIVATE_KEY

            with open(self.ACCESS_CREDENTIALS_PRIVATE_JSON, "w") as gcloud_auth_file:
                json.dump(gcloud_auth_data, gcloud_auth_file)
        else:
            return


    @staticmethod
    def get_instance():
        if GCloudConfig._instance is None:
            GCloudConfig()
        return GCloudConfig._instance



class CaptchaConfig:
    #ReCaptcha
    ReCAPTCHA_SERVER_APIKEY = os.environ['ReCAPTCHA_SERVER_APIKEY']
    ReCAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


class SMTPConfig:
    _instance = None
    DEFAULT_SENDER = None
    DEFAULT_SENDER_PASSWORD = None
    SMTP_SERVER = ''
    SMTP_PORT = None

    def __init__(self):
        if SMTPConfig._instance:
            #TODO: log that this problem happened
            raise Exception("MAIL CLIENT Connection should only be created once in the app.")
        else:
            SMTPConfig.DEFAULT_ADMIN = os.environ["MAIL_DEFAULT_ADMIN"]
            SMTPConfig.DEFAULT_RECEIVER = os.environ["MAIL_DEFAULT_RECEIVER"]
            SMTPConfig.DEFAULT_SENDER = os.environ["MAIL_DEFAULT_SENDER"]
            SMTPConfig.DEFAULT_SENDER_PASSWORD = os.environ["MAIL_DEFAULT_SENDER_PASSWORD"]
            SMTPConfig.SMTP_SERVER = os.environ["SMTP_SERVER"]
            SMTPConfig.SMTP_PORT = int(os.environ["SMTP_PORT"])
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

    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_ORIGIN = os.environ['CORS_ALLOW_ORIGIN']


class DevelopmentFlaskConfig:

    SECRET_KEY = os.environ['SECRET_KEY']
    TESTING = False

    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_ORIGIN = os.environ['CORS_ALLOW_ORIGIN']


class TestFlaskConfig:

    SECRET_KEY = 'dev'
    TESTING = True

    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_ORIGIN = 'http://localhost:3000'

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
