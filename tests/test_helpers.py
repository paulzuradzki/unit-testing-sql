import pytest
from helpers import create_mock_cte, merge_mock_cte_with_sql


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


def test_merge_mock_cte_with_sql_basic():
    """Test merging a mock CTE with SQL that has a single CTE"""
    mock_cte = """\
with orders as (
    select 'North' as region, 100 as amount
)"""

    sql = """\
with grouped as (
    select region from orders
)
select * from grouped"""

    result = merge_mock_cte_with_sql(mock_cte, sql)

    expected = """\
with orders as (
    select 'North' as region, 100 as amount
),
grouped as (
    select region from orders
)
select * from grouped"""

    assert result == expected

def test_merge_mock_cte_with_sql_no_with_keyword():
    """Test merging a mock CTE with SQL that doesn't have a with keyword"""
    mock_cte = """\
with orders as (
    select 'North' as region, 100 as amount
)"""

    sql = "select region from orders"

    result = merge_mock_cte_with_sql(mock_cte, sql)

    expected = """\
with orders as (
    select 'North' as region, 100 as amount
)
select region from orders"""

    assert result == expected


def test_merge_mock_cte_with_sql_multiple_ctes():
    """Test merging preserves multiple existing CTEs"""
    mock_cte = """\
with orders as (
    select 1 as id
)"""

    sql = """\
with grouped as (
    select id from orders
),
pivoted as (
    select id from grouped
)
select * from pivoted"""

    result = merge_mock_cte_with_sql(mock_cte, sql)

    # Should only replace the first "with", preserving the comma-separated CTEs
    expected = """\
with orders as (
    select 1 as id
),
grouped as (
    select id from orders
),
pivoted as (
    select id from grouped
)
select * from pivoted"""

    assert result == expected


def test_merge_mock_cte_with_sql_trailing_whitespace():
    """Test that trailing whitespace in mock CTE is handled"""
    mock_cte = """\
with orders as (
    select 1 as id
)
  """  # Extra whitespace at end

    sql = "with grouped as (select * from orders) select * from grouped"

    result = merge_mock_cte_with_sql(mock_cte, sql)

    # Should strip trailing whitespace and add comma
    expected = """\
with orders as (
    select 1 as id
),
grouped as (select * from orders) select * from grouped"""

    assert result == expected

def test_merge_mock_cte_with_sql_lowercase_with():
    """Test that merging is lowercase with"""
    mock_cte = """\
with orders as (
    select 1 as id
)"""

    sql = """\
with grouped as (select * from orders) select * from grouped"""

    result = merge_mock_cte_with_sql(mock_cte, sql) 

    expected = """\
with orders as (
    select 1 as id
),
grouped as (select * from orders) select * from grouped"""

    assert result == expected
    
def test_merge_mock_cte_with_sql_uppercase_with():
    """Test that merging is uppercase with"""
    mock_cte = """\
with orders as (
    select 1 as id
)"""

    sql = """\
WITH grouped as (select * from orders) select * from grouped"""

    result = merge_mock_cte_with_sql(mock_cte, sql) 
    
    expected = """\
with orders as (
    select 1 as id
),
grouped as (select * from orders) select * from grouped"""

    assert result == expected