from tests.const import (
    TEST_LOGIN_DATA,
    TEST_REGISTER_DATA,
    TEST_PASS_RESET_DATA,
    TEST_EMAIL
)

from server.tools.settings import COOKIE_KEY_USER, COOKIE_KEY_SESSION, FLASK_SERVER
from server.tools.settings import create_auth_token, verify_auth_token


def test_login(client):
    response = client.post("/login", data=TEST_LOGIN_DATA)
    assert response.status_code == 200

    data = response.get_json()
    session_id = data[COOKIE_KEY_USER]
    session_token = data[COOKIE_KEY_SESSION]

    client.set_cookie(FLASK_SERVER, COOKIE_KEY_USER, value=session_id)
    client.set_cookie(FLASK_SERVER, COOKIE_KEY_SESSION, value=session_token)

    response = client.get(f"/account/u/id={COOKIE_KEY_USER}")
    assert response.status_code == 200


def test_register(client):
    response = client.post("/register", data=TEST_REGISTER_DATA)
    assert response.status_code == 200


def test_password_reset(client):
    test_user = Users.unique({"email": TEST_EMAIL})
    token = create_auth_token(test_user)

    response = client.post(f'/password/reset/token={token}', data=TEST_PASS_RESET_DATA)
    assert response.status_code == 200
