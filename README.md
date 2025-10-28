# SQL Unit Testing

This is a demo of how to unit test raw SQL from scratch.

There are helper libraries that achieve this like below.
- [SQL Mock: Python Library for Mocking SQL Queries with Dictionary Inputs](https://github.com/DeepLcom/sql-mock)
    - supports testing SQL queries with Python dictionary inputs
    - replaces table references with CTEs and runs query in the database engine
- [SQLMesh](https://www.tobikodata.com/sqlmesh)
    - data transformation and modeling framework, backwards compatible with `dbt`
    - supports tests with mock data as CTEs and test cases define in YAML

The from-scratch approach is to illustrate for minimal dependencies and for learning.

## How it works

Say we want to unit test SQL like this:

```sql
/* Sum and pivot */
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

The `orders` table looks like this:

```sql
CREATE TABLE orders (id serial PRIMARY KEY, region text, item text, amount integer);
```

```
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

A good unit test has strong isolation; ie, a test that is focused, function-scoped and doesn't collide with others over shared state/data issues.

We will define our input data and expected output data using Python collections.

Then for the table dependencies -- like the `orders` table in our example -- we need to seed it with just enough data to verify the SQL code under test. We'll use lightweight trick which is that rather than create and seed a real table, we will create a common table expresion `orders` where we dynamically generate `SELECT` statements with the values from our Python input data.

We define our input data like so. The purpose of default dictionaries and pipe-concatenating them is for cases where we have a wide table but only a few columns of data need to be varied for our test.

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

We define our expected output with Python. This could just as easily be YAML too. Then we check the return value of our Python function which executed the SQL.

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

Some frameworks -- ie, Django ORM -- come with an ORM and test runner that will set up test tables according to the ORM model definitions. And you can seed your test data with ORM objects or raw SQL in the unit test. If you're working in a Django app or using Django-managed tables, this is definitely a strong option.

The nice thing about the CTE approach is it that is has few dependencies.

## Database Setup

### Starting PostgreSQL

Start the PostgreSQL container using Docker Compose:

```bash
docker-compose up -d
```

This will start PostgreSQL on port `5433`.

### Environment Configuration

Copy the example environment file and configure your database connection:

```bash
cp .env.example .env
```

Set the `DATABASE_URL` in your `.env` file to connect to your PostgreSQL database:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/test
```

The format is: `postgresql://username:password@host:port/database`

### Creating Test and Demo Databases

Create the test and demo databases (PostgreSQL is running on port 5433):

```bash
PGPORT=5433 createdb -h localhost test
PGPORT=5433 createdb -h localhost demo
```

Or set the PGPORT environment variable:

```bash
export PGPORT=5433
createdb -h localhost test
createdb -h localhost demo
```

### Running Setup Scripts

```bash
PGPORT=5433 psql -h localhost test < src/app/sql/seed_data.sql
PGPORT=5433 psql -h localhost demo < src/app/sql/seed_data.sql
```

## Testing

Run tests using uv:

```bash
# to show SQL print statements, add -s flag
uv run pytest -v
```

The tests use mock CTEs to replace database tables, allowing SQL logic testing without requiring seed data.

# References

Inspired by this talk: [Unleashing Confidence in SQL Development through Unit Testing - Tobias Lampert (Lotum)](https://www.youtube.com/watch?v=YRVTWwFFd8c)
