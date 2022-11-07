from src.models import Users
from src.utils.settings import COOKIE_KEY_USER_ID, COOKIE_KEY_SESSION

from .utils import UtilsAuth

TRIES = 5
utils_auth = UtilsAuth()

def test_register(client):
    global TRIES
    
    while TRIES > 0:
        test_registration_data = utils_auth.get_registration_data()
        response = client.post("/register", json=test_registration_data)

        if response.status_code == 403:
            TRIES -= 1
            new_email = utils_auth.generate_email()
            utils_auth.email = new_email
        else:
            break

    data = response.get_json()
    assert response.status_code == 200, f"Failed with status code: {response.status_code}"

    test_user = Users.unique({ "email": utils_auth.email })
    Users.delete({"id": test_user.id})


def test_login(client):
    test_login_data = utils_auth.get_login_data()
    response = client.post("/login", json=test_login_data)

    data = response.get_json()
    assert response.status_code == 200
