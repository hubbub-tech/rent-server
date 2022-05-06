from blubber_orm.dev.tools import date_range_generator

MAX_ITEM_ID = 500

test_res_date_start, test_res_date_end = date_range_generator()
TEST_RES_DATE_START = test_res_date_start.strftime("%Y-%m-%d")
TEST_RES_DATE_END = test_res_date_end.strftime("%Y-%m-%d")

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
        'line_1': '2020 Cherry Hill Way',
        'line_2': '',
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
