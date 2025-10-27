import pytest
from helpers import create_mock_cte


def test_create_mock_cte_basic():
    """Test basic CTE generation with mixed data types"""
    rows = [
        {"region": "North", "item": "Apple", "amount": 100},
        {"region": "South", "item": "Banana", "amount": 200},
    ]

    result = create_mock_cte("orders", rows)

    expected = """\
with orders as (
    select 'North' as region, 'Apple' as item, 100 as amount union all
    select 'South' as region, 'Banana' as item, 200 as amount
)"""

    assert result == expected


def test_create_mock_cte_single_row():
    """Test CTE with single row (no union all)"""
    rows = [{"id": 1, "name": "Test"}]

    result = create_mock_cte("users", rows)

    expected = """\
with users as (
    select 1 as id, 'Test' as name
)"""

    assert result == expected


def test_create_mock_cte_numeric_only():
    """Test CTE with only numeric values"""
    rows = [
        {"id": 1, "count": 100, "price": 50},
        {"id": 2, "count": 200, "price": 75},
    ]

    result = create_mock_cte("metrics", rows)

    expected = """\
with metrics as (
    select 1 as id, 100 as count, 50 as price union all
    select 2 as id, 200 as count, 75 as price
)"""

    assert result == expected


def test_create_mock_cte_string_only():
    """Test CTE with only string values"""
    rows = [
        {"name": "Alice", "city": "NYC"},
        {"name": "Bob", "city": "LA"},
    ]

    result = create_mock_cte("people", rows)

    expected = """\
with people as (
    select 'Alice' as name, 'NYC' as city union all
    select 'Bob' as name, 'LA' as city
)"""

    assert result == expected


def test_create_mock_cte_empty_rows_raises_error():
    """Test that empty rows raises ValueError"""
    with pytest.raises(ValueError, match="rows must not be empty"):
        create_mock_cte("empty_table", [])
