from src.models import Carts
from src.utils.settings import COOKIE_KEY_USER_ID, COOKIE_KEY_SESSION

from .utils import UtilsCheckout

utils_checkout = UtilsCheckout()

# TODO: can we turn checkout into a decorator?

def test_checkout_add(client, auth):
    response = auth.login()

    data = response.get_json()
    user_id = data[COOKIE_KEY_USER_ID]
    session_token = data[COOKIE_KEY_SESSION]

    test_user_cart = Carts.get({ "id": user_id })

    if test_user_cart:

        test_checkout_add_data = utils_checkout.get_checkout_add_data(item_id=1)
        response = client.post("/cart/add", json=test_checkout_add_data)

        data = response.get_json()
        assert response.status_code in [200, 402], data.message

    else:
        raise Exception("Failed while finding test user.")


def test_checkout_add_no_reservation(client, auth):
    response = auth.login()

    data = response.get_json()
    user_id = data[COOKIE_KEY_USER_ID]
    session_token = data[COOKIE_KEY_SESSION]

    test_user_cart = Carts.get({ "id": user_id })

    if test_user_cart:

        test_checkout_add_data = utils_checkout.get_checkout_add_data(item_id=1, with_reservation=False)
        response = client.post("/cart/add/no-reservation", json=test_checkout_add_data)

        data = response.get_json()
        assert response.status_code == 200, data.message
    else:
        raise Exception("Failed while finding test user.")


def test_checkout_remove(client, auth):
    response = auth.login()

    data = response.get_json()
    user_id = data[COOKIE_KEY_USER_ID]
    session_token = data[COOKIE_KEY_SESSION]

    test_user_cart = Carts.get({ "id": user_id })

    if test_user_cart:
        test_checkout_remove_data = utils_checkout.get_checkout_remove_data(item_id=1)
        response = client.post("/cart/remove", json=test_checkout_remove_data)

        data = response.get_json()
        assert response.status_code == 200, data.message

    else:
        raise Exception("Failed while finding test user.")
