from blubber_orm import Users

from tests.const import (
    TEST_LOGIN_DATA,
    TEST_REGISTER_DATA,
    TEST_PASS_RESET_DATA,
    TEST_EMAIL
)

from server.tools.settings import COOKIE_KEY_USER, COOKIE_KEY_SESSION, FLASK_SERVER
from server.tools.settings import create_auth_token, verify_auth_token

def test_register(client):
    response = client.post("/register", json=TEST_REGISTER_DATA)

    data = response.get_json()
    flash_messages = data.get("flashes")
    error_messages = data.get("errors")

    print("Messages: ", error_messages)
    assert response.status_code == 200

    test_email = TEST_REGISTER_DATA["user"]["email"]
    test_user = Users.unique({"email": test_email})
    Users.delete({"id": test_user.id})

def test_login(client):
    response = client.post("/login", json=TEST_LOGIN_DATA)

    data = response.get_json()
    flash_messages = data.get("flashes")
    print("Messages: ", flash_messages)
    assert response.status_code == 200

    data = response.get_json()
    session_id = data[COOKIE_KEY_USER]
    session_token = data[COOKIE_KEY_SESSION]

    print("session_id: ", session_id)
    print("session_token: ", session_token)
    client.set_cookie(FLASK_SERVER, COOKIE_KEY_USER, session_id)
    client.set_cookie(FLASK_SERVER, COOKIE_KEY_SESSION, session_token)

    response = client.get(f"/accounts/u/id={session_id}")

    data = response.get_json()
    flash_messages = data.get("flashes")
    print("Messages: ", flash_messages)
    assert response.status_code == 200


def test_password_reset(client):
    test_user = Users.unique({"email": TEST_EMAIL})
    token = create_auth_token(test_user)

    response = client.post(f'/password/reset/token={token}', data=TEST_PASS_RESET_DATA)

    data = response.get_json()
    flash_messages = data.get("flashes")
    print("Messages: ", flash_messages)
    assert response.status_code == 200
