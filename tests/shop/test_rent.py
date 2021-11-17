from tests.const import (
    MAX_ITEM_ID,
    TEST_RES_DATE_START,
    TEST_RES_DATE_END
)

from server.tools.settings import (
    COOKIE_KEY_USER,
    COOKIE_KEY_SESSION,
    FLASK_SERVER
)

from blubber_orm import Users


def test_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200


def test_add_to_cart(client, auth):
    item_id = 1
    while item_id < MAX_ITEM_ID:
        response = client.get(f"/inventory/i/id={item_id}")

        if response.status_code == 200: break
        elif response.status_code == 404: continue

        raise Exception(f"Broken item request at item_id = {item_id}.")

    response = auth.login()

    data = response.get_json()
    session_id = data[COOKIE_KEY_USER]
    session_token = data[COOKIE_KEY_SESSION]

    client.set_cookie(FLASK_SERVER, COOKIE_KEY_USER, value=session_id)
    client.set_cookie(FLASK_SERVER, COOKIE_KEY_SESSION, value=session_token)

    while True:
        response = client.post(f"/validate/i/id={item_id}", data={
            "startDate": TEST_RES_DATE_START,
            "endDate": TEST_RES_DATE_END,
            "isDiscounted": False
        })

        if response.status_code == 200: break
        elif response.status_code == 406: break

        raise Exception(f"Broken reservation validation at item_id {item_id}")

    if response.status_code == 200:
        response = client.post(f"/add/i/id={item_id}", data={
            "startDate": TEST_RES_DATE_START,
            "endDate": TEST_RES_DATE_END
        })
        assert response.status_code == 200 or response.status_code == 406


def test_update_to_cart(client, auth):
    response = auth.login()

    data = response.get_json()
    session_id = data[COOKIE_KEY_USER]

    test_user = Users.get({"id": session_id})
    if not test_user.cart.contents:
        test_add_to_cart(client, auth)

    assert test_user.cart.contents

    response = auth.login()

    data = response.get_json()
    session_id = data[COOKIE_KEY_USER]
    session_token = data[COOKIE_KEY_SESSION]

    client.set_cookie(FLASK_SERVER, COOKIE_KEY_USER, value=session_id)
    client.set_cookie(FLASK_SERVER, COOKIE_KEY_SESSION, value=session_token)

    item = test_user.cart.contents[0]
    response = client.post(f"/update/i/id={item.id}", data={
        "startDate": TEST_RES_DATE_START,
        "endDate": TEST_RES_DATE_END
    })

    assert response.status_code == 200


def test_remove_from_cart(client, auth):
    response = auth.login()

    data = response.get_json()
    session_id = data[COOKIE_KEY_USER]

    test_user = Users.get({"id": session_id})
    if not test_user.cart.contents:
        test_add_to_cart(client, auth)

    assert test_user.cart.contents

    response = auth.login()

    data = response.get_json()
    session_id = data[COOKIE_KEY_USER]
    session_token = data[COOKIE_KEY_SESSION]

    client.set_cookie(FLASK_SERVER, COOKIE_KEY_USER, value=session_id)
    client.set_cookie(FLASK_SERVER, COOKIE_KEY_SESSION, value=session_token)

    item = test_user.cart.contents[0]
    response = client.post(f"/remove/i/id={item.id}", data={
        "startDate": TEST_RES_DATE_START,
        "endDate": TEST_RES_DATE_END
    })

    assert response.status_code == 200


def test_checkout(client, auth):
    response = auth.login()

    data = response.get_json()
    session_id = data[COOKIE_KEY_USER]
    session_token = data[COOKIE_KEY_SESSION]

    client.set_cookie(FLASK_SERVER, COOKIE_KEY_USER, value=session_id)
    client.set_cookie(FLASK_SERVER, COOKIE_KEY_SESSION, value=session_token)

    response = client.get("/checkout")

    assert response.status_code == 200
