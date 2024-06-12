# test/test_processing.py

import pytest
import sqlite3
import os
from processing import calculate_statistics, filter_properties, create_graphs

DB_PATH = os.path.abspath("data/properties_db.db")

@pytest.fixture(scope='module')
def db_connection():
    # Ensure that the DB_PATH is used and exists
    if not os.path.isfile(DB_PATH):
        pytest.fail(f"The database file '{DB_PATH}' does not exist.")

    # Return a connection object
    conn = sqlite3.connect(DB_PATH)
    yield conn
    conn.close()

def test_calculate_statistics(db_connection):
    stats = calculate_statistics(db_connection)
    assert isinstance(stats, dict)
    assert 'average_property_price' in stats
    assert 'median_property_price' in stats
    assert 'total_properties' in stats
    assert stats['average_property_price'] >= 0
    assert stats['median_property_price'] >= 0
    assert stats['total_properties'] > 0

def test_filter_properties(db_connection):
    df = filter_properties(db_connection, price_range=(100000, 500000), bedrooms=3, city="Miami")
    assert not df.empty
    assert 'propertyid' in df.columns
    assert df['price'].between(100000, 500000).all()
    assert df['bedrooms'].ge(3).all()
    assert (df['city'] == "Miami").all()

def test_create_graphs(db_connection):
    create_graphs(db_connection)
    assert os.path.exists('data/price_distribution_custom.png')
    assert os.path.exists('data/bedrooms_distribution.png')
    assert os.path.exists('data/price_trend_over_years.png')
    assert os.path.exists('data/size_trend_over_years.png')
