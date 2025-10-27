from decimal import Decimal
from app.transform import pivot_and_sum
from helpers import create_mock_cte

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

    #########
    # Act
    #########
    # Pass mock CTE to pivot_and_sum function
    actual_output = pivot_and_sum(conn=db_conn, mock_cte=mock_orders_cte)

    #########
    # Assert
    #########
    assert actual_output == expected_output    