import pytest
import psycopg2
import os
from dotenv import load_dotenv

@pytest.fixture(scope="session")
def db_conn():
    """Provide a database connection for tests"""
    load_dotenv()
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    yield conn
    conn.close()
