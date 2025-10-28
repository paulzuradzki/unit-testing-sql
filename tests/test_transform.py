from decimal import Decimal
from importlib.resources import files
from app.transform import _pivot_and_sum, _pivot_and_unpivot
from helpers import create_mock_cte, merge_mock_cte_with_sql
from app.format import format_sql

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
    actual_output = _pivot_and_sum(conn=db_conn, sql=test_sql)

    #########
    # Assert
    #########
    assert actual_output == expected_output


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
    result = _pivot_and_unpivot(conn=db_conn, sql=test_sql)

    # Assert
    assert result == expected
