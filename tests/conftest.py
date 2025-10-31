import pytest
import psycopg2
import sqlite3
import os
from unittest.mock import patch


# =============================================================================
# PostgreSQL Database Lifecycle Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def postgres_test_db():
    """Create and manage PostgreSQL test database for the entire test session.

    Lifecycle:
        - Runs once at the start of the test session
        - Creates 'test' database if it doesn't exist
        - Yields the database URL for other fixtures to use
        - Drops the database after all tests complete

    Behavior:
        - Skips all tests if PostgreSQL server is not available
        - Automatically terminates stale connections during cleanup

    Returns:
        str: Database connection URL (postgresql://postgres:postgres@localhost:5433/test)
    """
    test_db_url = "postgresql://postgres:postgres@localhost:5433/test"
    admin_db_url = "postgresql://postgres:postgres@localhost:5433/postgres"

    try:
        # Connect to default 'postgres' database to create test database
        admin_conn = psycopg2.connect(admin_db_url)
    except psycopg2.OperationalError:
        pytest.skip("PostgreSQL server not available")

    with patch.dict(os.environ, {"DATABASE_URL": test_db_url}):
        admin_conn.autocommit = True

        with admin_conn.cursor() as cur:
            # Check if test database exists
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'test'")
            exists = cur.fetchone()

            if not exists:
                cur.execute("CREATE DATABASE test")

        admin_conn.close()

        yield test_db_url

        # Cleanup: Drop test database after all tests
        admin_conn = psycopg2.connect(admin_db_url)
        admin_conn.autocommit = True

        with admin_conn.cursor() as cur:
            # Terminate existing connections to the test database
            cur.execute("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = 'test' AND pid <> pg_backend_pid()
            """)
            cur.execute("DROP DATABASE IF EXISTS test")

        admin_conn.close()


# =============================================================================
# PostgreSQL Connection Fixtures - No Table Setup
# =============================================================================


@pytest.fixture(scope="session")
def db_conn(postgres_test_db):
    """Provide a bare PostgreSQL connection without any table setup.

    Use Case:
        - Tests that create tables inline using CTEs (Common Table Expressions)
        - Tests that don't require persistent tables
        - Examples: CTE-based queries, ad-hoc data transformations

    Scope:
        - Session-scoped (shared across all tests)
        - Database is empty - no pre-created tables

    Lifecycle:
        - Opens connection at start of session
        - Yields connection for tests to use
        - Closes connection after all tests complete

    Returns:
        psycopg2.connection: PostgreSQL database connection
    """
    conn = psycopg2.connect(postgres_test_db)
    yield conn
    conn.close()


# =============================================================================
# PostgreSQL Connection Fixtures - With Table Setup
# =============================================================================


@pytest.fixture(scope="function")
def db_conn_postgres_with_setup(postgres_test_db):
    """Provide a PostgreSQL connection with automatic 'orders' table setup and cleanup.

    Use Case:
        - Tests that require a pre-existing 'orders' table
        - Tests that need a clean table state for each test
        - Examples: INSERT/UPDATE/DELETE operations, complex transformations

    Scope:
        - Function-scoped (fresh table for each test)
        - Each test gets an isolated, empty 'orders' table

    Table Schema:
        CREATE TABLE orders (
            region TEXT,
            item TEXT,
            amount INTEGER
        )

    Lifecycle:
        1. Opens new connection
        2. Creates 'orders' table (if not exists)
        3. Commits table creation
        4. Yields connection for test to use
        5. Drops 'orders' table after test completes
        6. Closes connection

    Returns:
        psycopg2.connection: PostgreSQL database connection with 'orders' table
    """
    conn = psycopg2.connect(postgres_test_db)

    # Create the orders table for testing
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                region TEXT,
                item TEXT,
                amount INTEGER
            )
        """)
        conn.commit()

    yield conn

    # Cleanup: Drop the table after the test
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS orders")
        conn.commit()

    conn.close()


# =============================================================================
# SQLite Compatibility Layer
# =============================================================================


class SQLiteCursorContextManager:
    """Wrapper to make sqlite3.Cursor support context manager protocol like psycopg2.

    SQLite cursors don't natively support 'with cursor:' syntax, but psycopg2
    cursors do. This wrapper enables consistent cursor usage across both databases.
    """

    def __init__(self, cursor):
        self.cursor = cursor

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        return False

    def __getattr__(self, name):
        return getattr(self.cursor, name)


class SQLiteConnectionWrapper:
    """Wrapper to make sqlite3.Connection behave like psycopg2.connection.

    Ensures that conn.cursor() returns a context-manager-compatible cursor,
    enabling 'with conn.cursor() as cur:' syntax to work with SQLite.
    """

    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        """Return a cursor wrapped in a context manager"""
        return SQLiteCursorContextManager(self._conn.cursor())

    def __getattr__(self, name):
        return getattr(self._conn, name)


@pytest.fixture(scope="session")
def db_conn_sqlite():
    """Provide an in-memory SQLite database connection for tests.

    Use Case:
        - Fast, lightweight tests that don't require PostgreSQL-specific features
        - CI/CD environments without PostgreSQL
        - Quick local testing without database setup

    Scope:
        - Session-scoped (shared across all tests)
        - In-memory database (data is lost when connection closes)

    Compatibility:
        - Uses SQLiteConnectionWrapper to provide psycopg2-like cursor behavior
        - Enables 'with conn.cursor() as cur:' syntax

    Returns:
        SQLiteConnectionWrapper: Wrapped sqlite3 connection with psycopg2-like interface
    """
    conn = sqlite3.connect(":memory:")
    wrapped_conn = SQLiteConnectionWrapper(conn)
    yield wrapped_conn
    conn.close()
