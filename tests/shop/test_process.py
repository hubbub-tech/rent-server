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

from blubber_orm import Users, Orders


def test_checkout_submit(client, auth):
    response = auth.login()

    data = response.get_json()
    session_id = data[COOKIE_KEY_USER]

    test_user = Users.get({"id": session_id})

    if test_user.cart.contents:

        response = auth.login()

        data = response.get_json()
        session_id = data[COOKIE_KEY_USER]
        session_token = data[COOKIE_KEY_SESSION]

        response = client.post("/checkout/submit")

        assert response.status_code == 200


def test_order_history(client, auth):
    response = auth.login()

    data = response.get_json()
    session_id = data[COOKIE_KEY_USER]
    session_token = data[COOKIE_KEY_SESSION]

    client.set_cookie(FLASK_SERVER, COOKIE_KEY_USER, value=session_id)
    client.set_cookie(FLASK_SERVER, COOKIE_KEY_SESSION, value=session_token)

    response = client.get("/accounts/u/orders")

    assert response.status_code == 200


def test_manage_order(client, auth):
    response = auth.login()

    data = response.get_json()
    session_id = data[COOKIE_KEY_USER]
    session_token = data[COOKIE_KEY_SESSION]

    test_orders = Orders.filter({"renter_id": session_id})

    if test_orders:
        test_order = test_orders.pop()

        client.set_cookie(FLASK_SERVER, COOKIE_KEY_USER, value=session_id)
        client.set_cookie(FLASK_SERVER, COOKIE_KEY_SESSION, value=session_token)

        response = client.get(f"/accounts/o/id={test_order}")

        assert response.status_code == 200
