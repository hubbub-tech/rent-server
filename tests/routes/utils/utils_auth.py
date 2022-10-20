import random
import requests

from tests.const import TEST_EMAIL, TEST_PASSWORD, ReCAPTCHA_TEST_TOKEN

class UtilsAuth:

    def __init__(self):
        self.first_name = "Johnny"
        self.last_name = "Test"
        self.name = self.first_name + " " + self.last_name

        self.phone = "1111111111"
        self.email = TEST_EMAIL
        self.password = TEST_PASSWORD


    def get_registration_data(self):
        return {
            "user": {
                "firstName": self.first_name,
                "lastName": self.last_name,
                "phone": self.phone,
                "email": self.email,
                "password": self.password
            },
            "recaptchaToken": ReCAPTCHA_TEST_TOKEN
        }


    def get_login_data(self):
        return {
            "email": self.email,
            "password": self.password
        }


    @staticmethod
    def generate_email():

        EMAIL_GENERATOR_URL = "https://privatix-temp-mail-v1.p.rapidapi.com/request/domains/"

        headers = {
        	"X-RapidAPI-Key": TEMP_EMAIL_API_KEY,
        	"X-RapidAPI-Host": "privatix-temp-mail-v1.p.rapidapi.com"
        }

        response = requests.get(EMAIL_GENERATOR_URL, headers=headers)
        data = response.get_json()

        at_domain = random.choice(data)
        email = f"jtest{at_domain}"
        return email
