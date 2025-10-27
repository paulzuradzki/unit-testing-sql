from decimal import Decimal
from importlib.resources import files
from app.transform import pivot_and_sum
from helpers import create_mock_cte, merge_mock_cte_with_sql

def test_pivot_and_sum(db_conn):

    #########
    # Arrange
    #########

    # We don't care about "item", so we use a default value
    default_order = {
        "region": "North",
        "item": "Apple",
        "amount": 100,
    }

    input_data = [
        default_order | {"region": "North", "amount": 100},
        default_order | {"region": "South",  "amount": 200},
        default_order | {"region": "East", "amount": 300},
        default_order | {"region": "West", "amount": 400},
        default_order | {"region": "East", "amount": 300},
        default_order | {"region": "West", "amount": 400},
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
    sql = files("app").joinpath("sql/transform.sql").read_text()
    test_sql = merge_mock_cte_with_sql(mock_orders_cte, sql)

    #########
    # Act
    #########
    actual_output = pivot_and_sum(conn=db_conn, sql=test_sql)

    #########
    # Assert
    #########
    assert actual_output == expected_output    