import re

def create_mock_cte(table_name: str, rows: list[dict]) -> str:
    """
    Generate a SQL CTE from test data rows.

    Args:
        table_name: Name of the table to mock
        rows: List of dicts representing table rows

    Returns:
        SQL CTE string ready to inject into queries

    Example:
        >>> rows = [
        ...     {"region": "North", "item": "Apple", "amount": 100},
        ...     {"region": "South", "item": "Apple", "amount": 200},
        ... ]
        >>> cte = create_mock_cte("orders", rows)
        >>> print(cte)
        with orders as (
            select 'North' as region, 'Apple' as item, 100 as amount union all
            select 'South' as region, 'Apple' as item, 200 as amount
        )
    """
    if not rows:
        raise ValueError("rows must not be empty")

    select_statements = []
    for row in rows:
        # Build select clause with proper SQL literals
        columns = []
        for key, value in row.items():
            if isinstance(value, str):
                columns.append(f"'{value}' as {key}")
            else:
                columns.append(f"{value} as {key}")
        select_statements.append(f"    select {', '.join(columns)}")

    # Join with "union all" except for the last one
    cte_body = " union all\n".join(select_statements)

    return f"with {table_name} as (\n{cte_body}\n)"


def merge_mock_cte_with_sql(mock_cte: str, sql: str) -> str:
    """
    Merge a mock CTE with existing SQL that has WITH clause.

    This function prepends a mock CTE to SQL by replacing the first "with"
    keyword. Only the first occurrence is replaced, so this works correctly
    even if the SQL has multiple CTEs separated by commas.

    Args:
        mock_cte: Mock CTE starting with "with table_name as (...)"
        sql: Original SQL query that starts with "with ..."

    Returns:
        Merged SQL with mock CTE prepended

    Example:
        >>> mock = "with orders as (select 'North' as region, 100 as amount)"
        >>> sql = "with grouped as (select region from orders) select * from grouped"
        >>> result = merge_mock_cte_with_sql(mock, sql)
        >>> print(result)
        with orders as (select 'North' as region, 100 as amount),
        grouped as (select region from orders) select * from grouped

    Example with multiple CTEs:
        >>> sql = "with a as (...), b as (...) select * from b"
        >>> # Only the first "with" is replaced, preserving the comma-separated CTEs
    """
    

    # Remove trailing whitespace from mock CTE and add comma separator
    mock_cte = mock_cte.rstrip() + ","

    # Replace ONLY the first "with " (case-insensitive) to merge CTEs properly
    merged = re.sub(r'\bwith\s+', mock_cte + "\n", sql, count=1, flags=re.IGNORECASE)

    return merged
