MAX_ITEM_ID = 500
TEST_RES_DATE_START = "2023-01-01"
TEST_RES_DATE_END = "2023-10-01"

TEST_EMAIL = 'johnny.test@hubbub.shop'
TEST_PASSWORD = 'HubbubRulez1!'
TEST_PASSWORD2 = 'HubbubRulez1!'

ReCAPTCHA_TEST_TOKEN = ' 6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'

TEST_LOGIN_DATA = {
    'user': {
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD
    }
}

TEST_REGISTER_DATA = {
    'user': {
        'email': 'johnny.to.delete@hubbub.shop',
        'password': TEST_PASSWORD,
        'payment': 'NA',
        'firstName': 'Johnny',
        'lastName': 'Test'
    },
    'profile': {
        'phone': '1111111111'
    },
    'address': {
        'num': 2020,
        'street': 'Cherry Hill Way',
        'apt': '10A',
        'zip': '10000',
        'city': 'New York',
        'state': 'NY'
    },
    'token': ReCAPTCHA_TEST_TOKEN
}

TEST_PASS_RESET_DATA = {
    'email': TEST_EMAIL,
    'newPassword': TEST_PASSWORD2
}
