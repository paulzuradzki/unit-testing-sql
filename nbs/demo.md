# Unit Testing SQL

Say we have the following SQL. How would we test it with a real query engine?

```sql
WITH grouped AS
  (SELECT region, sum(amount) AS sale_amount
   FROM orders
   GROUP BY region
   ORDER BY region)
SELECT sum(CASE WHEN region = 'East' THEN sale_amount END) AS sales_east,
       sum(CASE WHEN region = 'North' THEN sale_amount END) AS sales_north,
       sum(CASE WHEN region = 'South' THEN sale_amount END) AS sales_south,
       sum(CASE WHEN region = 'West' THEN sale_amount END) AS sales_west
FROM grouped;
```

SQL can be tricky to test due to dependencies on schema, input data, and a database query engine. In addition, SQL in the wild is often verbose and hard to isolate into testable units. In this demo, we'll show how swapping in common table expression(s) (CTE) at test time is one way to achieve reproducible, isolated, and focused unit tests for SQL code. The example will be in Python but this technique is language-agnostic if you're coming from another ecosystem.

---

For our example, the `orders` table looks like this:

```
CREATE TABLE orders (id serial PRIMARY KEY, region text, item text, amount integer);

|id |region|item      |amount|
|---|------|----------|------|
|1  |North |Apple     |100   |
|2  |South |Banana    |200   |
|3  |East  |Cherry    |300   |
|4  |West  |Date      |400   |
|5  |East  |Elderberry|300   |
|6  |West  |Fig       |400   |

```

The result of the sum and pivot operation should look like this:

```
|sales_east|sales_north|sales_south|sales_west|
|----------|-----------|-----------|----------|
|600       |100        |200        |800       |
```

## The Plan

For a good unit test, we want a test that is fast, focused, isolated, and reproducible. It shouldn't collide with other tests over shared state/data issues or fail due to out-of-scope breakages like a schema change. Verifying schema is good but out of scope for this demo; it would arguably be more of an integration or end-to-end test. We'll focus on query behavior and assume schema correctness. We also won't be using a real remote database for our test.

To get reproducibility, we will define our input data and expected output data using Python collections (lists, dicts). Then we can use a test runner like `pytest`.

A precondition for running our queries is that we'll need our table dependencies seeded with data, like the `orders` table in our example. We should seed the dependency tables with just enough data to verify the behavior of the SQL code under test. We'll use a lightweight trick. Rather than create and seed a real table in the DB  -- this is a valid option too -- we will mock the `orders` table with a CTE built from our Python data.

We define our input data as follows. Using default dictionaries and pipe-merging them simplifies cases where only a few columns of data need to be varied for the test. That way, future readers don't have to scan and parse for what data is relevant to the behavior under test.


```python
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
```

See the diff for the original SQL under test and how -- during test time only -- a mocked table CTE gets prepended. Rather than query the real `orders` table, we query the CTE.

```diff
+WITH orders AS
+  (SELECT 'North' AS region, 'Apple' AS item, 100 AS amount
+   UNION ALL SELECT 'South' AS region, 'Apple' AS item, 200 AS amount
+   UNION ALL SELECT 'East' AS region, 'Apple' AS item, 300 AS amount
+   UNION ALL SELECT 'West' AS region, 'Apple' AS item, 400 AS amount
+   UNION ALL SELECT 'East' AS region, 'Apple' AS item, 300 AS amount
+   UNION ALL SELECT 'West' AS region, 'Apple' AS item, 400 AS amount),
+     grouped AS
-WITH grouped as
  (SELECT region, sum(amount) AS sale_amount
   FROM orders
   GROUP BY region
   ORDER BY region)
SELECT sum(CASE WHEN region = 'East' THEN sale_amount END) AS sales_east, sum(CASE WHEN region = 'North' THEN sale_amount END) AS sales_north,
       sum(CASE WHEN region = 'South' THEN sale_amount END) AS sales_south, sum(CASE WHEN region = 'West' THEN sale_amount END) AS sales_west
FROM grouped;
```

We define our expected output with Python. This could just as easily be defined in YAML too, as some other frameworks do. Then we check the return value of our Python function which executed the SQL.

```python
expected_output = [
    {
        "sales_east": Decimal("600"),
        "sales_north": Decimal("100"),
        "sales_south": Decimal("200"),
        "sales_west": Decimal("800"),
    }
]
```

## Alternatives

There are frameworks -- ie, Django ORM -- that come with an ORM and test runner that will set up test tables according to the ORM model/class definitions. You can seed your test data with ORM objects or raw SQL in the unit test setup step. If you're already working in a Django app or using Django-managed tables, this is definitely a strong option.

`dbt` and `SQLMesh` also have testing utilities for input-output style unit tests.

The CTE approach is nice, because it has few dependencies and doesn't tie you into a framework. Consider trying this lightweight method before adopting heavier frameworks.

## Worked Example

First, we need a few test helpers.


```python
import re


def create_mock_cte(table_name: str, rows: list[dict]) -> str:
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


def merge_mock_cte_with_sql(mock_cte: str, sql: str) -> str:    # Remove trailing whitespace from mock CTE
    mock_cte = mock_cte.rstrip()

    # Check if SQL has a WITH clause
    has_with_clause = bool(re.search(r'\bwith\s+', sql, flags=re.IGNORECASE))

    if has_with_clause:
        # Add comma separator and replace the first "with"
        mock_cte_with_comma = mock_cte + ","
        merged = re.sub(r'\bwith\s+', mock_cte_with_comma + "\n", sql, count=1, flags=re.IGNORECASE)
    else:
        # No WITH clause, just prepend the mock CTE with a newline
        merged = mock_cte + "\n" + sql

    return merged
```

`create_mock_cte` builds up our CTE with our input data. This CTE fragment will get prepended to the real SQL under test later.


```python
table = "orders"
rows = [
    {"region": "North", "item": "Apple", "amount": 100},
    {"region": "South", "item": "Apple", "amount": 200},
]

mock_cte = create_mock_cte(table, rows)
print(mock_cte)
```

    with orders as (
        select 'North' as region, 'Apple' as item, 100 as amount union all
        select 'South' as region, 'Apple' as item, 200 as amount
    )


Next, see how the printed SQL shows `with orders...` and our sample data prepended to the production SQL.


```python
sql = """\
WITH grouped AS
  (SELECT region, sum(amount) AS sale_amount
   FROM orders
   GROUP BY region
   ORDER BY region)
SELECT sum(CASE WHEN region = 'East' THEN sale_amount END) AS sales_east,
       sum(CASE WHEN region = 'North' THEN sale_amount END) AS sales_north,
       sum(CASE WHEN region = 'South' THEN sale_amount END) AS sales_south,
       sum(CASE WHEN region = 'West' THEN sale_amount END) AS sales_west
FROM grouped;
"""

print(merge_mock_cte_with_sql(mock_cte, sql))
```

    with orders as (
        select 'North' as region, 'Apple' as item, 100 as amount union all
        select 'South' as region, 'Apple' as item, 200 as amount
    ),
    grouped AS
      (SELECT region, sum(amount) AS sale_amount
       FROM orders
       GROUP BY region
       ORDER BY region)
    SELECT sum(CASE WHEN region = 'East' THEN sale_amount END) AS sales_east,
           sum(CASE WHEN region = 'North' THEN sale_amount END) AS sales_north,
           sum(CASE WHEN region = 'South' THEN sale_amount END) AS sales_south,
           sum(CASE WHEN region = 'West' THEN sale_amount END) AS sales_west
    FROM grouped;
    


Next, we pass the SQL to a query runner. For unit tests, your database URL should point to a locally running database. I'm running a test DB using Docker. See the source code `README.md` for setup steps.


```python
import psycopg2
import os
from pprint import pprint

def run_sql(conn: psycopg2.connect, sql: str) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(sql)
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        data = [dict(zip(cols, row)) for row in rows]
    return data


conn = psycopg2.connect(os.environ["DATABASE_URL"])

result = run_sql(conn, merge_mock_cte_with_sql(mock_cte, sql))
pprint(result, sort_dicts=False)
```

    [{'sales_east': None,
      'sales_north': Decimal('100'),
      'sales_south': Decimal('200'),
      'sales_west': None}]


Voilà! We have testable output. With `pytest`, the complete unit test could look like this. In this example, I'm reading SQL from a package file. Whether you store your SQL in a file, string, or template string -- the main idea here is that we can modify the original SQL code-under-test at test time without cluttering our production code. The prod code doesn't need to "know" about the CTE testing shenanigans.


```python
# As a bonus, here is how to run tests in a notebook with the ipytest magic command.

import ipytest

ipytest.autoconfig()
```


```python
%%ipytest -q

from decimal import Decimal
from importlib.resources import files
from app.transform import run_sql

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


def test_sum_and_pivot(db_conn):
    # Arrange

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

    # Act
    actual_output = run_sql(conn=db_conn, sql=test_sql)

    # Assert
    assert actual_output == expected_output

```

## In Closing

To recap, TL;DR:

1. SQL can be tricky to test due to dependencies on schema, input data, and a database query engine. In addition, SQL in the wild is often verbose and hard to isolate into testable units.
2. Swapping in a common table expression for your table at test time is one way to achieve reproducible, isolated, and focused unit tests for SQL code.

Hopefully by seeing that you *can* unit test SQL, you might spot opportunities to strengthen your automated code verification.

How do you test your SQL? Drop me a note if you enjoyed the post or learned something new.

Links

- **Credits**: I originally encountered this technique in this talk: [Unleashing Confidence in SQL Development through Unit Testing - Tobias Lampert](https://www.youtube.com/watch?v=YRVTWwFFd8c). By following along in this post, you get more annotated, implementation detail.
- For source code behind this post, the repository is located here: [https://github.com/paulzuradzki/unit-testing-sql](https://github.com/paulzuradzki/unit-testing-sql)
