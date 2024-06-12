# test/test_endpoints.py
import pytest
from fastapi.testclient import TestClient
from fast_api import app
from dotenv import load_dotenv
import os
import sqlite3

# Load environment variables
load_dotenv()

# Read paths from environment variables
DB_PATH = "data/properties_db.db"

client = TestClient(app)

@pytest.fixture(scope='module')
def use_existing_db():
    # Ensure that the DB_PATH is used and exists
    if not os.path.isfile(DB_PATH):
        pytest.fail(f"The database file '{DB_PATH}' does not exist.")
    yield
    # No cleanup needed since we're using an existing database

def test_get_properties(use_existing_db):
    response = client.get("/properties")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Ensure response is a list
    if data:  # If data is not empty
        assert 'propertyid' in data[0]

def test_get_statistics(use_existing_db):
    response = client.get("/properties/statistics")
    assert response.status_code == 200

def test_get_graphs(use_existing_db):
    response = client.get("/graphs")
    assert response.status_code == 200
    assert '<html>' in response.text  # Check if the response contains HTML content
