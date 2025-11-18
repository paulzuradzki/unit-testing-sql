# dbt Setup and Usage Guide

This guide covers how to set up and use dbt for this project.

## Prerequisites

- PostgreSQL running on `localhost:5433` (see main README for database setup)
- dbt installed (via `uv` or `pip install dbt-postgres`)

## Key Concepts

- **Model**: SQL SELECT statement in `models/`. dbt wraps it in CREATE TABLE/VIEW
- **Data test**: Assertion against real database data (e.g., not_null)
- **Unit test**: Tests model logic without database (dbt 1.8+)

## Configuration

### Profile Configuration

`~/.dbt/profiles.yml` (contains secrets - never commit):

```yaml
dbt_dev:
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5433
      user: postgres
      pass: postgres
      dbname: demo
      schema: public
      threads: 1
  target: dev
```

This connects to the PostgreSQL database running on port `5433` with database name `demo`.

## Project Structure

```
dbt_dev/
├── models/              # SQL models (tables/views)
│   ├── hello_world.sql  # Example model
│   ├── schema.yml       # Data tests configuration
│   └── unit_tests.yml   # Unit tests configuration
├── tests/               # Custom data tests
├── macros/              # Reusable SQL functions
├── seeds/               # CSV files to load as tables
└── dbt_project.yml      # Project configuration
```

## Common Commands

### Running Models

```bash
# Run all models
dbt run

# Run a specific model
dbt run --select hello_world

# Run models matching a pattern
dbt run --select models/example/*
```

### Testing

```bash
# Run all tests (data tests + unit tests)
dbt test

# Run tests for a specific model (data tests only)
dbt test --select hello_world

# Run a specific unit test
dbt test --select test_name:test_hello_world_output

# Run only unit tests
dbt test --select test_type:unit

# Run only data tests
dbt test --select test_type:generic,test_type:singular
```

### Other Useful Commands

```bash
# Compile SQL without running
dbt compile

# Show compiled SQL for a model
dbt compile --select hello_world
cat target/compiled/dbt_dev/models/hello_world.sql

# Clean generated files
dbt clean

# List available models
dbt ls --select model

# Show dependency graph
dbt list --select hello_world+  # downstream dependencies
dbt list --select +hello_world  # upstream dependencies
```

## Hello World Example

This project includes a simple hello world example to demonstrate dbt concepts:

### 1. Model (`models/hello_world.sql`)
Creates a table/view with sample data:

```sql
select
'Hello' as greeting,
'World' as subject,
current_timestamp as created_at
```

### 2. Data Tests (`models/schema.yml`)
Validates data quality on the model:

```yaml
version: 2

models:
  - name: hello_world
    columns:
      - name: greeting
        tests:
          - not_null
          - accepted_values:
              values: ['Hello']
      - name: subject
        tests:
          - not_null
```

### 3. Unit Tests (`models/unit_tests.yml`)
Tests the model logic without hitting the database:

```yaml
unit_tests:
  - name: test_hello_world_output
    model: hello_world
    given: []
    expect:
      rows:
        - {greeting: 'Hello', subject: 'World'}
```

## Workflow

1. **Create a model**: Add a `.sql` file in `models/`
2. **Run the model**: `dbt run --select your_model`
3. **Add data tests**: Define tests in `models/schema.yml`
4. **Run tests**: `dbt test --select your_model`
5. **Add unit tests** (optional): Define in `models/unit_tests.yml`
6. **Run unit tests**: `dbt test --select test_name:your_test`

## Tips

- **Models are just SELECT statements** - dbt wraps them in CREATE TABLE/VIEW
- **Data tests run against real data** in your database
- **Unit tests are isolated** - they don't need seed data
- **Use `--select` flag** to run specific models/tests instead of everything
- **Check `target/` folder** to see compiled SQL
- **Unit tests require dbt 1.8+**

## Troubleshooting

### Connection Issues

If you get connection errors:
1. Check PostgreSQL is running: `docker ps`
2. Verify port 5433 is correct: `psql -h localhost -p 5433 -U postgres -d demo`
3. Check profile config: `cat ~/.dbt/profiles.yml`

### Test Failures

If tests fail:
- Check test output for details: `dbt test --select your_model`
- Look at compiled test SQL: `cat target/compiled/dbt_dev/models/schema.yml/your_test.sql`
- Run the model first: `dbt run --select your_model`

## Resources

- [dbt CLI Documentation](https://docs.getdbt.com/reference/dbt-commands)
- [dbt Testing Documentation](https://docs.getdbt.com/docs/build/data-tests)
- [dbt Unit Tests](https://docs.getdbt.com/docs/build/unit-tests)
