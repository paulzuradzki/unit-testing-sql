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
