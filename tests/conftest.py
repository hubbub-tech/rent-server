import os
import pytest

from blubber_orm import get_blubber

from src import create_app
from src.utils.settings import TestFlaskConfig

from .const import TEST_EMAIL, TEST_PASSWORD

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    # db_fd, db_path = tempfile.mkstemp()

    # create the app with common test config
    app = create_app(config_object=TestFlaskConfig())

    # create the database and load test data
    # with app.app_context():
    #     cur, conn = get_blubber()
    #     assert "localhost" in os.environ["DATABASE_URL"]
    #     cur.execute(open("schema.sql", "r").read())

    yield app

    # close and remove the temporary database
    # os.close(db_fd)
    # os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, email=TEST_EMAIL, password=TEST_PASSWORD):
        data = { "user": { "email": email, "password": password } }
        response =  self._client.post("/login", json=data)

        assert response.status_code == 200
        return response

    def logout(self):
        """No logout server-side; user must prove themselves with each request."""


@pytest.fixture
def auth(client):
    return AuthActions(client)
