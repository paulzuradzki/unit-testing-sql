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

See the related post here: [Unit Testing SQL](https://paulzuradzki.com/2025/10/unit-testing-sql/)

<details>

<summary>

## Database Setup
</summary>

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
</details>

<details>
<summary>

## Testing
</summary>

Run tests using uv:

```bash
# to show SQL print statements, add -s flag
uv run pytest -v
```

The tests use mock CTEs to replace database tables, allowing SQL logic testing without requiring seed data.

</details>

# References

Inspired by this talk: [Unleashing Confidence in SQL Development through Unit Testing - Tobias Lampert (Lotum)](https://www.youtube.com/watch?v=YRVTWwFFd8c)
