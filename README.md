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
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/dev
```

The format is: `postgresql://username:password@host:port/database`

### Creating Dev and Demo Databases

Create the development and demo databases (PostgreSQL is running on port 5433):

```bash
PGPORT=5433 createdb -h localhost dev
PGPORT=5433 createdb -h localhost demo
```

Or set the PGPORT environment variable:

```bash
export PGPORT=5433
createdb -h localhost dev
createdb -h localhost demo
```

### Running Setup Scripts

```bash
PGPORT=5433 psql -h localhost dev < seed_data.sql
PGPORT=5433 psql -h localhost demo < seed_data.sql
```

## Testing

Run tests using uv:

```bash
uv run pytest tests/ -v
```

The tests use mock CTEs to replace database tables, allowing SQL logic testing without requiring seed data.

# References

Inspired by this talk: [Unleashing Confidence in SQL Development through Unit Testing - Tobias Lampert (Lotum)](https://www.youtube.com/watch?v=YRVTWwFFd8c)
