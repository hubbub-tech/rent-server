from src.models import Users
from src.utils.settings import COOKIE_KEY_USER_ID, COOKIE_KEY_SESSION

from .utils import UtilsList

utils_list = UtilsList()

def test_list(client, auth):
    response = auth.login()

    data = response.get_json()
    user_id = data[COOKIE_KEY_USER_ID]
    session_token = data[COOKIE_KEY_SESSION]

    test_user = Users.get({ "id": user_id })

    if test_user:

        test_list_item_data = utils_list.get_list_item_data()
        response = client.post("/list", json=test_list_item_data)

        data = response.get_json()
        assert response.status_code in [200, 402], data.message

    else:
        raise Exception("Failed while finding test user.")
