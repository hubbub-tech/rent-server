TEST_EMAIL = "jtest@hubbub.shop"
TEST_PASSWORD = "passw0rd"

ReCAPTCHA_TEST_TOKEN = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'


class TestAuth:

    def __init__(self):
        pass

    @staticmethod
    def get_registration_data():
        return {
            "user": {
                "firstName": "Johnny",
                "lastName": "Test",
                "phone": "+1 (111) 111-1111",
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            "recaptchaToken": ReCAPTCHA_TEST_TOKEN
        }


    @staticmethod
    def get_login_data():
        return {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
