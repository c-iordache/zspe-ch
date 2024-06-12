# test/conftest.py
import pytest
import sqlite3

@pytest.fixture
def in_memory_db():
    # Create an in-memory SQLite database
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()
