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


def test_checkout_submit(client, auth):
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

    response = client.post("/checkout/submit")

    assert response.status_code == 200
