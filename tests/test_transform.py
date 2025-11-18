"""
SQL Testing Approaches - Comparison
====================================

This test file demonstrates two different approaches to testing SQL queries:

1. **CTE Mocking Approach** (test_pivot_and_sum, test_pivot_and_sum_sqlite)
   - Injects test data as CTEs (WITH clauses) into the SQL
   - Pros: No table setup; fast; works across databases (SQLite/PostgreSQL)
   - Cons: Requires helper functions; modifies SQL before execution; can only mock base tables, not intermediate CTEs
   - Best for: Simple queries where you want to avoid table setup; testing SQL portability

2. **Real Tables Approach** (test_pivot_and_sum_sqlite_with_real_tables,
                              test_pivot_and_sum_postgres_with_real_tables)
   - Creates actual tables and inserts data
   - Pros: Simpler code; tests unmodified SQL; closer to production; easier to understand
   - Cons: Requires CREATE TABLE/INSERT setup (though this is trivial)
   - Best for: Most testing scenarios; validates the actual SQL that runs in production

Database Options:
- **SQLite**: Fast, no setup, in-memory. May have dialect differences.
- **PostgreSQL**: Production-like, full SQL support. Requires Docker/server.

Choose based on your needs: CTE mocking for isolation, real tables for realism.
"""

from decimal import Decimal
from importlib.resources import files
from app.transform import run_sql
from helpers import create_mock_cte, merge_mock_cte_with_sql
from app.format import format_sql

import sqlite3
import sqlglot


def test_pivot_and_sum(db_conn):
    #########
    # Arrange
    #########

    # We don't care about "item", so we use a default value
    default_order_item = {
        "region": "North",
        "item": "Apple",
        "amount": 100,
    }

    input_data = [
        default_order_item | {"region": "North", "amount": 100},
        default_order_item | {"region": "South", "amount": 200},
        default_order_item | {"region": "East", "amount": 300},
        default_order_item | {"region": "West", "amount": 400},
        default_order_item | {"region": "East", "amount": 300},
        default_order_item | {"region": "West", "amount": 400},
    ]

    expected_output = [
        {
            "sales_east": Decimal("600"),
            "sales_north": Decimal("100"),
            "sales_south": Decimal("200"),
            "sales_west": Decimal("800"),
        }
    ]

    # Create mock CTE that replaces the real 'orders' table
    mock_orders_cte = create_mock_cte("orders", input_data)

    # Load the real SQL file and merge with mock data
    sql = files("app").joinpath("sql/pivot.sql").read_text()
    test_sql = merge_mock_cte_with_sql(mock_orders_cte, sql)
    print("\n\n--------------------------------\n\n")
    print(format_sql(test_sql))

    #########
    # Act
    #########
    actual_output = run_sql(conn=db_conn, sql=test_sql)

    #########
    # Assert
    #########
    assert actual_output == expected_output


def test_pivot_and_sum_sqlite(db_conn_sqlite):
    """Same test as test_pivot_and_sum, but using SQLite instead of PostgreSQL.

    This demonstrates that the same SQL testing approach works with SQLite
    without modifying any source code - only the database fixture changes.
    """
    #########
    # Arrange
    #########

    # We don't care about "item", so we use a default value
    default_order_item = {
        "region": "North",
        "item": "Apple",
        "amount": 100,
    }

    input_data = [
        default_order_item | {"region": "North", "amount": 100},
        default_order_item | {"region": "South", "amount": 200},
        default_order_item | {"region": "East", "amount": 300},
        default_order_item | {"region": "West", "amount": 400},
        default_order_item | {"region": "East", "amount": 300},
        default_order_item | {"region": "West", "amount": 400},
    ]

    expected_output = [
        {
            "sales_east": Decimal("600"),
            "sales_north": Decimal("100"),
            "sales_south": Decimal("200"),
            "sales_west": Decimal("800"),
        }
    ]

    # Create mock CTE that replaces the real 'orders' table
    mock_orders_cte = create_mock_cte("orders", input_data)

    # Load the real SQL file and merge with mock data
    sql = files("app").joinpath("sql/pivot.sql").read_text()
    test_sql = merge_mock_cte_with_sql(mock_orders_cte, sql)
    print("\n\n--------------------------------\n\n")
    print(format_sql(test_sql))

    #########
    # Act
    #########
    actual_output = run_sql(conn=db_conn_sqlite, sql=test_sql)

    #########
    # Assert
    #########
    assert actual_output == expected_output


def test_pivot_and_sum_sqlite_with_real_tables(db_conn_sqlite):
    """Alternative approach: Use real tables instead of CTE mocking.

    Pros:
    - Simpler, more straightforward test code
    - Tests the actual SQL file without modification
    - Closer to how the code runs in production
    - No helper functions needed

    Cons:
    - Requires table setup/teardown (though CREATE/INSERT is simple)

    SQLite vs PostgreSQL for this approach:

    SQLite (shown here):
    - Pros: Zero setup, fast (in-memory), no Docker needed, great for CI/CD
    - Cons: Possible SQL dialect differences (e.g., DATE functions, ARRAY types)
    - Best for: Rapid development, local testing, standard SQL queries

    PostgreSQL (works identically - just swap fixture):
    - Pros: Production-realistic, full PostgreSQL feature set, catches dialect issues
    - Cons: Requires running database (Docker), slower than in-memory SQLite
    - Best for: Final validation, queries using PostgreSQL-specific features
    """
    #########
    # Arrange
    #########

    # Create the orders table
    db_conn_sqlite.execute(
        """
        CREATE TABLE orders (
            region TEXT,
            item TEXT,
            amount INTEGER
        )
        """
    )

    # Insert test data
    test_data = [
        ("North", "Apple", 100),
        ("South", "Apple", 200),
        ("East", "Apple", 300),
        ("West", "Apple", 400),
        ("East", "Banana", 300),
        ("West", "Orange", 400),
    ]

    db_conn_sqlite.executemany(
        "INSERT INTO orders (region, item, amount) VALUES (?, ?, ?)", test_data
    )

    expected_output = [
        {
            "sales_east": Decimal("600"),
            "sales_north": Decimal("100"),
            "sales_south": Decimal("200"),
            "sales_west": Decimal("800"),
        }
    ]

    # Load the real SQL file (no mocking needed!)
    sql = files("app").joinpath("sql/pivot.sql").read_text()

    #########
    # Act
    #########
    actual_output = run_sql(conn=db_conn_sqlite, sql=sql)

    #########
    # Assert
    #########
    assert actual_output == expected_output

    # Cleanup
    db_conn_sqlite.execute("DROP TABLE orders")


def test_pivot_and_sum_postgres_with_real_tables(db_conn_postgres_with_setup):
    """PostgreSQL version with automatic table setup - same approach as SQLite.

    This demonstrates that the real tables approach works identically with
    PostgreSQL. The fixture automatically:
    - Creates the 'orders' table
    - Cleans up after the test

    The test code is identical to the SQLite version (just swap the fixture!).

    Requires: PostgreSQL server running with DATABASE_URL configured in .env
    """
    #########
    # Arrange
    #########

    # Insert test data (table already created by fixture)
    test_data = [
        ("North", "Apple", 100),
        ("South", "Apple", 200),
        ("East", "Apple", 300),
        ("West", "Apple", 400),
        ("East", "Banana", 300),
        ("West", "Orange", 400),
    ]

    with db_conn_postgres_with_setup.cursor() as cur:
        cur.executemany(
            "INSERT INTO orders (region, item, amount) VALUES (%s, %s, %s)", test_data
        )
        db_conn_postgres_with_setup.commit()

    expected_output = [
        {
            "sales_east": Decimal("600"),
            "sales_north": Decimal("100"),
            "sales_south": Decimal("200"),
            "sales_west": Decimal("800"),
        }
    ]

    # Load the real SQL file (no mocking needed!)
    sql = files("app").joinpath("sql/pivot.sql").read_text()

    #########
    # Act
    #########
    actual_output = run_sql(conn=db_conn_postgres_with_setup, sql=sql)

    #########
    # Assert
    #########
    assert actual_output == expected_output
    # Fixture automatically drops table after test


def test_pivot_and_unpivot_data(db_conn):
    """Testing a multi-step CTE for demonstration."""

    # Arrange
    default_order_item = {
        "region": "North",
        "item": "Apple",
        "amount": 100,
    }

    input_data = [
        default_order_item | {"region": "North", "amount": 100},
        default_order_item | {"region": "South", "amount": 200},
        default_order_item | {"region": "East", "amount": 300},
        default_order_item | {"region": "West", "amount": 400},
        default_order_item | {"region": "East", "amount": 300},
        default_order_item | {"region": "West", "amount": 400},
    ]

    expected = [
        {"region": "East", "sale_amount": 600},
        {"region": "North", "sale_amount": 100},
        {"region": "South", "sale_amount": 200},
        {"region": "West", "sale_amount": 800},
    ]
    sql = files("app").joinpath("sql/pivot_and_unpivot.sql").read_text()
    mock_orders_cte = create_mock_cte("orders", input_data)
    test_sql = merge_mock_cte_with_sql(mock_orders_cte, sql)
    print("\n\n--------------------------------\n\n")
    print(format_sql(test_sql))

    # Act
    result = run_sql(conn=db_conn, sql=test_sql)

    # Assert
    assert result == expected


def test_pivot_and_unpivot_sqlglot():
    # ARRANGE - Setup database and data
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE orders (region TEXT, item TEXT, amount INTEGER)")

    default_order_item = {"region": "North", "item": "Apple", "amount": 100}

    input_data = [
        default_order_item | {"region": "North", "amount": 100},
        default_order_item | {"region": "South", "amount": 200},
        default_order_item | {"region": "East", "amount": 300},
        default_order_item | {"region": "West", "amount": 400},
        default_order_item | {"region": "East", "amount": 300},
        default_order_item | {"region": "West", "amount": 400},
    ]

    conn.executemany(
        "INSERT INTO orders (region, item, amount) VALUES (:region, :item, :amount)",
        input_data,
    )

    # Transpile and execute SQL
    source_sql = files("app").joinpath("sql/pivot_and_unpivot.sql").read_text()
    sql_stmt = sqlglot.transpile(source_sql, read="postgres", write="sqlite")[0]

    # ACT
    cursor = conn.execute(sql_stmt)
    result_data = [
        dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()
    ]

    # ASSERT
    expected_data = [
        {"region": "East", "sale_amount": 600},
        {"region": "North", "sale_amount": 100},
        {"region": "South", "sale_amount": 200},
        {"region": "West", "sale_amount": 800},
    ]
    assert result_data == expected_data
