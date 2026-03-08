import pytest
import os
import sys
import app as app_module
from app import app

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

TEST_DB = "test_aceest.db"


@pytest.fixture(autouse=True)
def setup_test_db():
    app_module.DB_NAME = TEST_DB
    app_module.init_db()
    yield
    app_module.DB_NAME = "aceest_fitness.db"
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c