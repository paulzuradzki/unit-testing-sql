import psycopg2
from importlib.resources import files
from app.format import format_sql


def run_sql(conn: psycopg2.connect, sql: str) -> dict[str, int]:
    """
    Execute SQL query and return the result as a list of dicts.

    Args:
        conn: Database connection
        sql: SQL query to execute

    Returns:
        List of dicts with the result of the SQL query
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        data = [dict(zip(cols, row)) for row in rows]

    return data

def sum_and_pivot(conn: psycopg2.connect, verbose: bool = False) -> dict[str, int]:
    """
    Execute pivot query on orders data.
    """
    sql = files("app").joinpath("sql/pivot.sql").read_text()
    if verbose:
        print(format_sql(sql))
    return run_sql(conn, sql)


def pivot_and_unpivot(conn: psycopg2.connect, verbose: bool = False) -> dict[str, int]:
    """
    Execute pivot and unpivot query on orders data.
    """
    sql = files("app").joinpath("sql/pivot_and_unpivot.sql").read_text()
    if verbose:
        print(format_sql(sql))
    return run_sql(conn, sql)


